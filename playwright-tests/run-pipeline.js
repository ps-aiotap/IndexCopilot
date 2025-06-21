#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class TestPipeline {
  constructor() {
    this.startTime = Date.now();
    this.results = {
      discovery: null,
      generation: null,
      testing: null,
      reporting: null
    };
  }

  async run() {
    console.log('🚀 Starting IndexCopilot Form Testing Pipeline...\n');
    
    try {
      // Step 1: Form Discovery
      console.log('📋 Step 1: Form Discovery');
      await this.runStep('npm run discover', 'discovery');
      
      // Step 2: Test Generation
      console.log('\n🔧 Step 2: Test Generation');
      await this.runStep('npm run generate', 'generation');
      
      // Step 3: Test Execution
      console.log('\n🧪 Step 3: Test Execution');
      await this.runStep('npm run test', 'testing');
      
      // Step 4: Report Generation
      console.log('\n📊 Step 4: Report Generation');
      await this.generateSummaryReport();
      
      console.log('\n✅ Pipeline completed successfully!');
      this.printSummary();
      
    } catch (error) {
      console.error('\n❌ Pipeline failed:', error.message);
      process.exit(1);
    }
  }

  async runStep(command, stepName) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const process = spawn(command, { shell: true, stdio: 'inherit' });
      
      process.on('close', (code) => {
        const duration = Date.now() - startTime;
        this.results[stepName] = {
          success: code === 0,
          duration: duration,
          exitCode: code
        };
        
        if (code === 0) {
          console.log(`✅ ${stepName} completed in ${duration}ms`);
          resolve();
        } else {
          reject(new Error(`${stepName} failed with exit code ${code}`));
        }
      });
      
      process.on('error', (error) => {
        reject(new Error(`Failed to start ${stepName}: ${error.message}`));
      });
    });
  }

  async generateSummaryReport() {
    const reportData = {
      timestamp: new Date().toISOString(),
      totalDuration: Date.now() - this.startTime,
      steps: this.results,
      summary: await this.collectTestSummary()
    };

    // Generate HTML summary report
    const htmlReport = this.generateHtmlReport(reportData);
    const reportPath = path.join(__dirname, 'reports/pipeline-summary.html');
    
    // Ensure reports directory exists
    if (!fs.existsSync(path.dirname(reportPath))) {
      fs.mkdirSync(path.dirname(reportPath), { recursive: true });
    }
    
    fs.writeFileSync(reportPath, htmlReport);
    console.log(`📄 Summary report generated: ${reportPath}`);
  }

  async collectTestSummary() {
    try {
      // Read discovered forms
      const formsPath = path.join(__dirname, 'generated/discovered-forms.json');
      const formsData = fs.existsSync(formsPath) ? JSON.parse(fs.readFileSync(formsPath, 'utf8')) : null;
      
      // Read test results
      const resultsPath = path.join(__dirname, 'reports/test-results.json');
      const testResults = fs.existsSync(resultsPath) ? JSON.parse(fs.readFileSync(resultsPath, 'utf8')) : null;
      
      return {
        formsDiscovered: formsData?.totalForms || 0,
        pagesScanned: formsData?.totalPages || 0,
        testsGenerated: this.countGeneratedTests(),
        testResults: testResults ? {
          total: testResults.stats?.total || 0,
          passed: testResults.stats?.passed || 0,
          failed: testResults.stats?.failed || 0,
          skipped: testResults.stats?.skipped || 0
        } : null
      };
    } catch (error) {
      console.warn('Warning: Could not collect test summary:', error.message);
      return {};
    }
  }

  countGeneratedTests() {
    try {
      const generatedDir = path.join(__dirname, 'generated');
      const files = fs.readdirSync(generatedDir).filter(f => f.endsWith('.spec.js'));
      return files.length;
    } catch {
      return 0;
    }
  }

  generateHtmlReport(data) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IndexCopilot Form Testing Pipeline Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        .warning { color: #ffc107; }
        .step { margin-bottom: 20px; padding: 15px; border-left: 4px solid #007bff; background: #f8f9fa; }
        .step.success { border-color: #28a745; }
        .step.error { border-color: #dc3545; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 IndexCopilot Form Testing Pipeline Report</h1>
            <p>Generated on ${new Date(data.timestamp).toLocaleString()}</p>
            <p>Total Duration: ${Math.round(data.totalDuration / 1000)}s</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">${data.summary.formsDiscovered || 0}</div>
                <div class="stat-label">Forms Discovered</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${data.summary.pagesScanned || 0}</div>
                <div class="stat-label">Pages Scanned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${data.summary.testsGenerated || 0}</div>
                <div class="stat-label">Test Files Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-number ${data.summary.testResults?.passed ? 'success' : 'error'}">${data.summary.testResults?.total || 0}</div>
                <div class="stat-label">Total Tests</div>
            </div>
        </div>

        <h2>Pipeline Steps</h2>
        ${Object.entries(data.steps).map(([step, result]) => `
            <div class="step ${result?.success ? 'success' : 'error'}">
                <h3>${step.charAt(0).toUpperCase() + step.slice(1)} ${result?.success ? '✅' : '❌'}</h3>
                <p>Duration: ${result?.duration ? Math.round(result.duration / 1000) + 's' : 'N/A'}</p>
                ${result?.exitCode !== undefined ? `<p>Exit Code: ${result.exitCode}</p>` : ''}
            </div>
        `).join('')}

        ${data.summary.testResults ? `
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
                <tr>
                    <td>✅ Passed</td>
                    <td>${data.summary.testResults.passed}</td>
                    <td>${Math.round((data.summary.testResults.passed / data.summary.testResults.total) * 100)}%</td>
                </tr>
                <tr>
                    <td>❌ Failed</td>
                    <td>${data.summary.testResults.failed}</td>
                    <td>${Math.round((data.summary.testResults.failed / data.summary.testResults.total) * 100)}%</td>
                </tr>
                <tr>
                    <td>⏭️ Skipped</td>
                    <td>${data.summary.testResults.skipped}</td>
                    <td>${Math.round((data.summary.testResults.skipped / data.summary.testResults.total) * 100)}%</td>
                </tr>
            </table>
        ` : ''}

        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>Generated by IndexCopilot Form Testing Pipeline</p>
        </div>
    </div>
</body>
</html>`;
  }

  printSummary() {
    console.log('\n📊 Pipeline Summary:');
    console.log('==================');
    console.log(`Total Duration: ${Math.round((Date.now() - this.startTime) / 1000)}s`);
    
    Object.entries(this.results).forEach(([step, result]) => {
      const status = result?.success ? '✅' : '❌';
      const duration = result?.duration ? `(${Math.round(result.duration / 1000)}s)` : '';
      console.log(`${step}: ${status} ${duration}`);
    });
    
    console.log('\n📄 Reports available:');
    console.log('- HTML Report: playwright-tests/reports/pipeline-summary.html');
    console.log('- Playwright Report: playwright-tests/reports/html-report/index.html');
  }
}

// Run pipeline if called directly
if (require.main === module) {
  const pipeline = new TestPipeline();
  pipeline.run().catch(console.error);
}

module.exports = TestPipeline;