const { test, expect } = require('@playwright/test');

test.describe('Quick Form Test', () => {
  test('Basic form interaction test', async ({ page }) => {
    await page.goto('http://localhost:8501');
    await page.waitForTimeout(3000);
    
    // Take screenshot to see what's available
    await page.screenshot({ path: 'debug-screenshot.png' });
    
    // Try to find and interact with visible text inputs
    const textInputs = await page.locator('input[type="text"]:visible').all();
    console.log(`Found ${textInputs.length} visible text inputs`);
    
    if (textInputs.length > 0) {
      await textInputs[0].fill('Test data');
      console.log('Successfully filled first text input');
    }
    
    // Look for buttons
    const buttons = await page.locator('button:visible').all();
    console.log(`Found ${buttons.length} visible buttons`);
    
    // Test passed if we can interact with elements
    expect(textInputs.length + buttons.length).toBeGreaterThan(0);
  });
});