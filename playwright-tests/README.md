# 🧪 IndexCopilot Form Testing Pipeline

Comprehensive Playwright-based form testing system that discovers, generates, and executes tests automatically.

## ✨ Features

- **🔍 Smart Discovery**: Crawls application following real navigation
- **🔧 Auto-Generation**: Creates comprehensive test suites for every form
- **🛡️ Security Testing**: XSS, SQL injection, and CSRF protection tests
- **📊 Rich Reporting**: HTML reports with detailed metrics
- **🚀 One-Command Pipeline**: Complete workflow in single step

## 🚀 Quick Start

### Prerequisites
```bash
# Install Node.js dependencies
cd playwright-tests
npm install
npx playwright install
```

### One-Command Execution
```bash
# Run complete pipeline
node run-pipeline.js

# Or use npm script
npm run pipeline
```

## 📋 Pipeline Steps

### 1. Form Discovery
```bash
npm run discover
```
- Crawls from homepage following navigation
- Discovers all forms and input fields
- Maps field types and validation requirements
- Saves results to `generated/discovered-forms.json`

### 2. Test Generation
```bash
npm run generate
```
- Generates comprehensive test suites
- Creates tests for validation, security, edge cases
- Outputs `.spec.js` files to `generated/` directory

### 3. Test Execution
```bash
npm run test
```
- Runs all generated tests with Playwright
- Tests across Chrome, Firefox, Safari
- Captures screenshots and videos on failure

### 4. Report Generation
```bash
npm run report
```
- Opens HTML report with detailed results
- Summary report at `reports/pipeline-summary.html`

## 🧪 Test Categories

### Happy Path Tests
- Valid form submissions
- Successful data entry
- Expected user workflows

### Validation Tests
- Required field validation
- Email format validation
- Number range validation
- Date format validation

### Security Tests
- **XSS Prevention**: Script injection attempts
- **SQL Injection**: Database attack prevention
- **CSRF Protection**: Cross-site request forgery
- **Input Sanitization**: Malicious payload handling

### Edge Case Tests
- Maximum length inputs
- Special character handling
- Boundary value testing
- Error condition handling

## 📊 Reports

### HTML Dashboard
- Form discovery summary
- Test execution results
- Security vulnerability analysis
- Performance metrics

### Playwright Reports
- Detailed test results
- Screenshots and videos
- Trace files for debugging
- Cross-browser compatibility

## 🔧 Configuration

### Playwright Config
```javascript
// playwright.config.js
module.exports = defineConfig({
  testDir: './generated',
  reporter: [['html'], ['json']],
  use: {
    baseURL: 'http://localhost:8501',
    screenshot: 'only-on-failure'
  }
});
```

### Discovery Settings
```javascript
// Modify in form-discovery.js
const maxPages = 20;        // Maximum pages to crawl
const baseUrl = 'http://localhost:8501';
```

## 🚀 CI/CD Integration

### GitHub Actions
Workflow automatically runs on:
- Push to main/develop branches
- Pull requests
- Daily schedule

```yaml
# .github/workflows/form-testing.yml
- name: Run Form Testing Pipeline
  run: |
    cd playwright-tests
    node run-pipeline.js
```

## 📁 Directory Structure

```
playwright-tests/
├── src/
│   ├── form-discovery.js      # Navigation crawler
│   └── test-generator.js      # Test suite generator
├── generated/                 # Auto-generated tests
│   ├── discovered-forms.json  # Discovery results
│   └── *.spec.js             # Generated test files
├── reports/                   # Test reports
│   ├── html-report/          # Playwright reports
│   └── pipeline-summary.html # Pipeline summary
├── package.json              # Dependencies
├── playwright.config.js      # Playwright configuration
└── run-pipeline.js          # One-command runner
```

## 🛠️ Customization

### Adding Custom Tests
```javascript
// In test-generator.js
generateCustomTests(form) {
  return `
  test('Custom validation', async ({ page }) => {
    // Your custom test logic
  });`;
}
```

### Modifying Discovery
```javascript
// In form-discovery.js
async discoverFormsOnPage(page, url) {
  // Add custom form discovery logic
}
```

## 🐛 Troubleshooting

### Common Issues

**Streamlit not starting**
```bash
# Check if port 8501 is available
netstat -an | grep 8501
```

**Tests failing**
```bash
# Run with debug mode
DEBUG=pw:api npm run test
```

**Discovery not finding forms**
```bash
# Check discovery results
cat generated/discovered-forms.json
```

## 📈 Metrics

The pipeline tracks:
- Forms discovered per page
- Test coverage percentage
- Security vulnerabilities found
- Performance benchmarks
- Cross-browser compatibility

## 🤝 Contributing

1. Add new test patterns in `test-generator.js`
2. Enhance discovery logic in `form-discovery.js`
3. Improve reporting in `run-pipeline.js`
4. Update documentation

## 📄 License

Same as parent project (MIT License)