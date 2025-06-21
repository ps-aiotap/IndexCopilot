const { chromium } = require('@playwright/test');
const fs = require('fs');

async function quickDiscovery() {
  console.log('🔍 Starting quick form discovery...');
  
  const browser = await chromium.launch({ headless: false, timeout: 10000 });
  const page = await browser.newPage();
  
  try {
    // Set shorter timeouts
    page.setDefaultTimeout(5000);
    
    console.log('📱 Navigating to Streamlit app...');
    await page.goto('http://localhost:8501', { waitUntil: 'domcontentloaded', timeout: 10000 });
    
    // Wait for Streamlit to load
    await page.waitForTimeout(3000);
    
    console.log('🔍 Looking for forms...');
    
    // Simple form discovery
    const forms = await page.evaluate(() => {
      const inputs = document.querySelectorAll('input, textarea, select');
      console.log(`Found ${inputs.length} input elements`);
      
      const formData = {
        totalInputs: inputs.length,
        fields: []
      };
      
      inputs.forEach((input, i) => {
        formData.fields.push({
          id: `field_${i}`,
          type: input.type || input.tagName.toLowerCase(),
          name: input.name || input.placeholder || `field_${i}`,
          selector: input.tagName.toLowerCase() + (input.type ? `[type="${input.type}"]` : '')
        });
      });
      
      return formData;
    });
    
    console.log(`✅ Found ${forms.totalInputs} input fields`);
    
    // Save results
    const results = {
      timestamp: new Date().toISOString(),
      totalForms: forms.totalInputs > 0 ? 1 : 0,
      forms: forms.totalInputs > 0 ? [{
        id: 'streamlit_form',
        url: 'http://localhost:8501',
        fields: forms.fields
      }] : []
    };
    
    fs.writeFileSync('./generated/discovered-forms.json', JSON.stringify(results, null, 2));
    console.log('📄 Results saved to discovered-forms.json');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
}

quickDiscovery();