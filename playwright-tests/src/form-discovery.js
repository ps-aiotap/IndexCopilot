const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

class FormDiscovery {
  constructor() {
    this.discoveredForms = [];
    this.visitedUrls = new Set();
    this.baseUrl = 'http://localhost:8501';
    this.maxPages = 20;
  }

  async discover() {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    try {
      console.log('🔍 Starting form discovery...');
      await this.crawlPage(page, this.baseUrl);
      
      const results = {
        timestamp: new Date().toISOString(),
        baseUrl: this.baseUrl,
        totalPages: this.visitedUrls.size,
        totalForms: this.discoveredForms.length,
        forms: this.discoveredForms
      };
      
      // Save results
      const outputPath = path.join(__dirname, '../generated/discovered-forms.json');
      fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
      
      console.log(`✅ Discovery complete: ${this.discoveredForms.length} forms found on ${this.visitedUrls.size} pages`);
      console.log(`📄 Results saved to: ${outputPath}`);
      
    } finally {
      await browser.close();
    }
  }

  async crawlPage(page, url) {
    if (this.visitedUrls.has(url) || this.visitedUrls.size >= this.maxPages) {
      return;
    }

    this.visitedUrls.add(url);
    console.log(`🌐 Crawling: ${url}`);

    try {
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.waitForTimeout(2000); // Wait for Streamlit to load
      
      // Discover forms on current page
      await this.discoverFormsOnPage(page, url);
      
      // Find navigation links
      const links = await this.extractNavigationLinks(page);
      
      // Recursively crawl discovered links
      for (const link of links) {
        if (link.startsWith(this.baseUrl) && !this.visitedUrls.has(link)) {
          await this.crawlPage(page, link);
        }
      }
      
    } catch (error) {
      console.log(`⚠️  Error crawling ${url}: ${error.message}`);
    }
  }

  async discoverFormsOnPage(page, url) {
    // Wait longer for Streamlit to fully load
    await page.waitForTimeout(5000);
    
    // Click through tabs to discover all forms
    const tabs = await page.locator('[data-testid="stTabs"] button, .stTabs button').all();
    console.log(`  Found ${tabs.length} tabs to explore`);
    
    const allForms = [];
    
    // Discover forms on current tab
    const currentForms = await this.extractFormsFromPage(page);
    allForms.push(...currentForms);
    
    // Click each tab and discover forms
    for (let i = 0; i < tabs.length; i++) {
      try {
        await tabs[i].click();
        await page.waitForTimeout(2000);
        const tabForms = await this.extractFormsFromPage(page);
        allForms.push(...tabForms);
        console.log(`    Tab ${i + 1}: Found ${tabForms.length} forms`);
      } catch (error) {
        console.log(`    Tab ${i + 1}: Error - ${error.message}`);
      }
    }
    
    // Add forms to discovery results
    allForms.forEach(form => {
      form.url = url;
      this.discoveredForms.push(form);
    });
    
    if (allForms.length > 0) {
      console.log(`  📝 Found ${allForms.length} forms total on this page`);
    }
  }
  
  async extractFormsFromPage(page) {
    return await page.evaluate(() => {
      const discoveredForms = [];
      
      // Streamlit-specific selectors
      const inputSelectors = [
        'input[type="text"]',
        'input[type="number"]',
        'input[type="email"]',
        'input[type="password"]',
        'input[type="date"]',
        'input[type="file"]',
        'textarea',
        'select',
        '[data-testid="stTextInput"] input',
        '[data-testid="stNumberInput"] input',
        '[data-testid="stSelectbox"] select',
        '[data-testid="stFileUploader"] input',
        '[data-testid="stDateInput"] input'
      ];
      
      const allInputs = [];
      inputSelectors.forEach(selector => {
        const inputs = document.querySelectorAll(selector);
        allInputs.push(...Array.from(inputs));
      });
      
      console.log(`Found ${allInputs.length} input elements`);
      
      if (allInputs.length > 0) {
        // Group inputs by their container/form
        const containers = new Map();
        
        allInputs.forEach((input, index) => {
          // Find the closest container
          const container = input.closest('[data-testid="stForm"], form, .element-container, [data-testid="column"]') || document.body;
          const containerId = container.getAttribute('data-testid') || container.className || `container_${index}`;
          
          if (!containers.has(containerId)) {
            containers.set(containerId, {
              id: `form_${containers.size}`,
              container: container,
              fields: []
            });
          }
          
          const field = {
            id: `field_${index}`,
            type: input.type || input.tagName.toLowerCase(),
            name: input.name || input.getAttribute('aria-label') || input.placeholder || `field_${index}`,
            selector: generateSelector(input),
            required: input.required || input.hasAttribute('required'),
            placeholder: input.placeholder || '',
            testId: input.getAttribute('data-testid') || ''
          };
          
          // Find label
          const label = findFieldLabel(input);
          if (label) {
            field.label = label;
            field.purpose = detectFieldPurpose(label, field.name, field.placeholder);
          }
          
          containers.get(containerId).fields.push(field);
        });
        
        // Convert containers to forms
        containers.forEach((containerData, containerId) => {
          if (containerData.fields.length > 0) {
            discoveredForms.push({
              id: containerData.id,
              url: window.location.href,
              selector: containerId,
              fields: containerData.fields
            });
          }
        });
      }
      
      // Helper functions
      function generateSelector(element) {
        if (element.id) return '#' + element.id;
        if (element.getAttribute('data-testid')) return '[data-testid="' + element.getAttribute('data-testid') + '"]';
        
        let selector = element.tagName.toLowerCase();
        if (element.type) selector += '[type="' + element.type + '"]';
        if (element.className) selector += '.' + element.className.split(' ').join('.');
        return selector;
      }
      
      function findFieldLabel(input) {
        // Look for associated label
        if (input.id) {
          const label = document.querySelector('label[for="' + input.id + '"]');
          if (label) return label.textContent.trim();
        }
        
        // Look for nearby text in Streamlit containers
        const container = input.closest('.element-container, [data-testid="stTextInput"], [data-testid="stNumberInput"], [data-testid="stSelectbox"]');
        if (container) {
          const labelElement = container.querySelector('label, [data-testid="stMarkdownContainer"] p');
          if (labelElement) return labelElement.textContent.trim();
        }
        
        return input.placeholder || input.getAttribute('aria-label') || '';
      }
      
      function detectFieldPurpose(label, name, placeholder) {
        const text = (label + ' ' + name + ' ' + placeholder).toLowerCase();
        
        if (text.includes('email')) return 'email';
        if (text.includes('password')) return 'password';
        if (text.includes('name')) return 'name';
        if (text.includes('phone')) return 'phone';
        if (text.includes('address')) return 'address';
        if (text.includes('date')) return 'date';
        if (text.includes('price') || text.includes('amount') || text.includes('quantity')) return 'number';
        if (text.includes('file') || text.includes('upload')) return 'file';
        
        return 'text';
      }
      
      return discoveredForms;
    });
    
    // Add forms to discovery results
    forms.forEach(form => {
      form.url = url;
      this.discoveredForms.push(form);
    });
    
    if (forms.length > 0) {
      console.log(`  📝 Found ${forms.length} forms on this page`);
    }
  }

  async extractNavigationLinks(page) {
    return await page.evaluate(() => {
      const links = new Set();
      
      // Streamlit navigation elements
      const navSelectors = [
        'a[href]',
        '[data-testid="stSidebar"] a',
        '.stTabs a',
        'button[role="tab"]',
        '[class*="nav"] a',
        '[class*="menu"] a'
      ];
      
      navSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
          const href = element.href || element.getAttribute('href');
          if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
            links.add(href);
          }
        });
      });
      
      return Array.from(links);
    });
  }
}

// Helper functions for form analysis
const helperFunctions = `
  generateSelector(element) {
    if (element.id) return '#' + element.id;
    if (element.getAttribute('data-testid')) return '[data-testid="' + element.getAttribute('data-testid') + '"]';
    
    let selector = element.tagName.toLowerCase();
    if (element.className) {
      selector += '.' + element.className.split(' ').join('.');
    }
    return selector;
  }
  
  findFieldLabel(input) {
    // Look for associated label
    const label = document.querySelector('label[for="' + input.id + '"]');
    if (label) return label.textContent.trim();
    
    // Look for nearby text
    const parent = input.closest('.element-container, .stTextInput, .stNumberInput, .stSelectbox');
    if (parent) {
      const labelElement = parent.querySelector('label, .stMarkdown p, [data-testid="stMarkdownContainer"]');
      if (labelElement) return labelElement.textContent.trim();
    }
    
    return '';
  }
  
  detectFieldPurpose(label, name, placeholder) {
    const text = (label + ' ' + name + ' ' + placeholder).toLowerCase();
    
    if (text.includes('email')) return 'email';
    if (text.includes('password')) return 'password';
    if (text.includes('name')) return 'name';
    if (text.includes('phone')) return 'phone';
    if (text.includes('address')) return 'address';
    if (text.includes('date')) return 'date';
    if (text.includes('price') || text.includes('amount') || text.includes('quantity')) return 'number';
    if (text.includes('file') || text.includes('upload')) return 'file';
    
    return 'text';
  }
`;

// Run discovery if called directly
if (require.main === module) {
  const discovery = new FormDiscovery();
  discovery.discover().catch(console.error);
}

module.exports = FormDiscovery;