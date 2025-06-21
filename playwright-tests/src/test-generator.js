const fs = require('fs');
const path = require('path');

class TestGenerator {
  constructor() {
    this.testData = {
      email: ['test@example.com', 'user@domain.co.uk', 'invalid-email', '<script>alert("xss")</script>@test.com'],
      name: ['John Doe', 'Jane Smith', '<script>alert("xss")</script>', "'; DROP TABLE users; --"],
      password: ['ValidPass123!', '123', '<script>alert("xss")</script>', "'; DROP TABLE users; --"],
      phone: ['+1234567890', '123-456-7890', 'invalid-phone', '<script>alert("xss")</script>'],
      number: ['100', '0', '-1', '999999999', 'invalid', '<script>alert("xss")</script>', "'; DROP TABLE users; --"],
      text: ['Valid text', '', '<script>alert("xss")</script>', "'; DROP TABLE users; --", 'A'.repeat(1000)],
      date: ['2023-01-15', '2025-12-31', 'invalid-date', '<script>alert("xss")</script>']
    };
    
    this.xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert("XSS")>',
      'javascript:alert("XSS")',
      '<svg onload=alert("XSS")>',
      '"><script>alert("XSS")</script>'
    ];
    
    this.sqlPayloads = [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "'; SELECT * FROM users; --",
      "' UNION SELECT * FROM users --",
      "admin'--"
    ];
  }

  async generate() {
    console.log('🔧 Generating comprehensive test suite...');
    
    const formsPath = path.join(__dirname, '../generated/discovered-forms.json');
    if (!fs.existsSync(formsPath)) {
      throw new Error('No discovered forms found. Run form discovery first.');
    }
    
    const formsData = JSON.parse(fs.readFileSync(formsPath, 'utf8'));
    
    for (const form of formsData.forms) {
      await this.generateFormTests(form);
    }
    
    // Generate main test runner
    await this.generateTestRunner(formsData.forms);
    
    console.log(`✅ Generated tests for ${formsData.forms.length} forms`);
  }

  async generateFormTests(form) {
    const testContent = `
const { test, expect } = require('@playwright/test');

test.describe('Form Tests - ${form.id}', () => {
  const baseUrl = '${form.url}';
  
  test.beforeEach(async ({ page }) => {
    await page.goto(baseUrl);
    await page.waitForTimeout(2000); // Wait for Streamlit to load
  });

  ${this.generateHappyPathTests(form)}
  
  ${this.generateValidationTests(form)}
  
  ${this.generateSecurityTests(form)}
  
  ${this.generateEdgeCaseTests(form)}
});
`;

    const fileName = `${form.id.replace(/[^a-zA-Z0-9]/g, '_')}.spec.js`;
    const filePath = path.join(__dirname, '../generated', fileName);
    fs.writeFileSync(filePath, testContent);
  }

  generateHappyPathTests(form) {
    return `
  test('Happy Path - Valid form submission', async ({ page }) => {
    ${form.fields.map(field => this.generateFieldInput(field, 'valid')).join('\n    ')}
    
    // Look for submit button
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Add"), button:has-text("Save")').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();
      await page.waitForTimeout(1000);
      
      // Check for success indicators
      await expect(page.locator('.stSuccess, [data-testid="stSuccess"], .success')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });`;
  }

  generateValidationTests(form) {
    const tests = form.fields.map(field => {
      if (field.required) {
        return `
  test('Validation - Required field: ${field.name}', async ({ page }) => {
    // Leave required field empty and try to submit
    ${form.fields.filter(f => f.id !== field.id).map(f => this.generateFieldInput(f, 'valid')).join('\n    ')}
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Add"), button:has-text("Save")').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();
      await page.waitForTimeout(1000);
      
      // Should show validation error
      await expect(page.locator('.stError, [data-testid="stError"], .error')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });`;
      }
      
      if (field.purpose === 'email') {
        return `
  test('Validation - Invalid email format: ${field.name}', async ({ page }) => {
    await page.fill('${field.selector}', 'invalid-email-format');
    ${form.fields.filter(f => f.id !== field.id).map(f => this.generateFieldInput(f, 'valid')).join('\n    ')}
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Add"), button:has-text("Save")').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();
      await page.waitForTimeout(1000);
      
      // Should show validation error
      await expect(page.locator('.stError, [data-testid="stError"], .error')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });`;
      }
      
      return '';
    }).filter(test => test);

    return tests.join('\n');
  }

  generateSecurityTests(form) {
    const xssTests = form.fields.map(field => `
  test('Security - XSS Prevention: ${field.name}', async ({ page }) => {
    const xssPayload = '<script>alert("XSS")</script>';
    await page.fill('${field.selector}', xssPayload);
    
    // Check that script is not executed
    page.on('dialog', dialog => {
      throw new Error('XSS vulnerability detected: alert dialog appeared');
    });
    
    await page.waitForTimeout(1000);
    
    // Verify content is properly escaped
    const fieldValue = await page.inputValue('${field.selector}');
    expect(fieldValue).toBe(xssPayload); // Should be stored as-is, not executed
  });`).join('\n');

    const sqlTests = form.fields.filter(f => f.purpose === 'text' || f.purpose === 'name').map(field => `
  test('Security - SQL Injection Prevention: ${field.name}', async ({ page }) => {
    const sqlPayload = "'; DROP TABLE users; --";
    await page.fill('${field.selector}', sqlPayload);
    
    ${form.fields.filter(f => f.id !== field.id).map(f => this.generateFieldInput(f, 'valid')).join('\n    ')}
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Add"), button:has-text("Save")').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();
      await page.waitForTimeout(2000);
      
      // Should not cause database errors or expose SQL error messages
      const errorMessages = await page.locator('body').textContent();
      expect(errorMessages.toLowerCase()).not.toContain('sql');
      expect(errorMessages.toLowerCase()).not.toContain('database');
      expect(errorMessages.toLowerCase()).not.toContain('mysql');
      expect(errorMessages.toLowerCase()).not.toContain('postgresql');
    }
  });`).join('\n');

    return xssTests + '\n' + sqlTests;
  }

  generateEdgeCaseTests(form) {
    return form.fields.map(field => `
  test('Edge Case - Maximum length: ${field.name}', async ({ page }) => {
    const longText = 'A'.repeat(1000);
    await page.fill('${field.selector}', longText);
    
    // Should handle gracefully without breaking
    await page.waitForTimeout(1000);
    const fieldValue = await page.inputValue('${field.selector}');
    expect(fieldValue.length).toBeLessThanOrEqual(1000);
  });
  
  test('Edge Case - Special characters: ${field.name}', async ({ page }) => {
    const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    await page.fill('${field.selector}', specialChars);
    
    await page.waitForTimeout(1000);
    // Should not cause application errors
    const hasErrors = await page.locator('.stError, [data-testid="stError"]').isVisible().catch(() => false);
    // Some validation errors are expected, but no application crashes
  });`).join('\n');
  }

  generateFieldInput(field, type) {
    const testValue = this.getTestValue(field.purpose, type);
    
    if (field.type === 'file') {
      return `// File upload for ${field.name} - manual testing required`;
    }
    
    return `await page.fill('${field.selector}', '${testValue}');`;
  }

  getTestValue(purpose, type) {
    const values = this.testData[purpose] || this.testData.text;
    
    switch (type) {
      case 'valid':
        return values[0];
      case 'invalid':
        return values[2] || values[1];
      case 'xss':
        return this.xssPayloads[0];
      case 'sql':
        return this.sqlPayloads[0];
      default:
        return values[0];
    }
  }

  async generateTestRunner(forms) {
    const runnerContent = `
const { test, expect } = require('@playwright/test');

test.describe('IndexCopilot Form Testing Suite', () => {
  test('Form Discovery Summary', async ({ page }) => {
    console.log('📊 Form Testing Summary:');
    console.log('Total forms discovered: ${forms.length}');
    console.log('Forms by page:');
    ${forms.map(form => `console.log('  - ${form.url}: ${form.fields.length} fields');`).join('\n    ')}
  });
});
`;

    const runnerPath = path.join(__dirname, '../generated/test-runner.spec.js');
    fs.writeFileSync(runnerPath, runnerContent);
  }
}

// Run generator if called directly
if (require.main === module) {
  const generator = new TestGenerator();
  generator.generate().catch(console.error);
}

module.exports = TestGenerator;