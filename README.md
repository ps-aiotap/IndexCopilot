# IndexCopilot

A professional portfolio management system with real-time analytics, intelligent data validation, and automated testing. Built with Streamlit, it handles everything from CSV imports to institutional-level financial calculations and professional PDF reporting.

## Overview

IndexCopilot transforms raw portfolio data into actionable insights with CAGR calculations, gain/loss tracking, and interactive visualizations - all backed by comprehensive automated testing that ensures reliability.

## Features

### Portfolio Management
- **Gain/Loss Tracking**: Real-time profit/loss calculation with visual indicators (▲/▼)
- **CAGR Analysis**: Compound Annual Growth Rate calculation per asset
- **Interactive Dashboard**: 4-tab modular interface (Portfolio Summary, Add Holdings, Analytics, Reports)
- **Asset Allocation**: Doughnut chart with center totals and color-matched legends
- **Performance Metrics**: Total investment vs current value with percentage gains

### Data Management
- **Enhanced CSV Upload**: Robust validation with pandas-based error checking
- **Manual Entry**: Individual holding addition with comprehensive validation
- **Auto-save/Load**: Automatic portfolio persistence with success notifications
- **Export Options**: CSV and PDF reports with Unicode currency support

### User Experience
- **Modular Architecture**: Clean separation of concerns with testable components
- **Sidebar Stats**: Quick portfolio overview and settings
- **Color-coded Display**: Green/red indicators for gains and losses
- **Responsive Layout**: Organized tabs with centered charts and proper spacing
- **Clean Interface**: Professional, distraction-free design

## Demo

▶️ [Watch the demo](https://www.loom.com/share/46d0423ca6cb462e91ce86a7cc565f04)  
This short video walks through the main features, including

## Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/IndexCopilot.git
cd IndexCopilot
pip install -r requirements.txt

# Run the application
streamlit run app_modular.py
```

Open `http://localhost:8501` and start managing your portfolio.

## Sample Use Cases

- **Upload portfolio CSV** → Get instant validation and real-time analytics
- **Track performance** → View CAGR, gain/loss indicators, and asset allocation
- **Generate reports** → Export professional PDF reports for stakeholders
- **Automated testing** → Built-in form testing ensures reliability across updates

3. Add holdings to your portfolio:
   - **Upload CSV**: Use the sample CSV download or follow the format guide
   - **Manual Entry**: Add individual holdings with the form

4. View your portfolio analytics:
   - **Portfolio Summary**: Holdings table with gain/loss indicators
   - **Analytics**: Performance metrics and best/worst performers
   - **Asset Allocation**: Interactive doughnut chart with detailed breakdown

5. Export and manage:
   - **Reports Tab**: Download CSV or generate PDF reports
   - **Auto-save**: Portfolio automatically loads on startup
   - **Settings**: Access dark mode and quick stats in sidebar

## Technology Stack

- **Frontend**: Streamlit for responsive web interface
- **Data Processing**: Pandas for robust validation and calculations
- **Visualization**: Matplotlib for interactive charts and asset allocation
- **Reporting**: ReportLab for professional PDF generation
- **Testing**: Playwright for automated form discovery and security testing
- **Architecture**: Modular design with clean separation of concerns

## CSV Data Format

```csv
asset_type,asset_id,asset_name,quantity,purchase_price,purchase_date
Mutual Fund,HDFC123,HDFC Nifty 50 Index Fund,100,150.0,2023-01-15
Equity,RELIANCE,Reliance Industries Ltd,10,2000.0,2023-02-20
Insurance,LIC001,LIC Term Plan,1,50000.0,2023-01-01
```

## Project Structure

```
IndexCopilot/
├── src/
│   ├── utils/
│   │   ├── portfolio_manager.py    # Portfolio data management and calculations
│   │   └── export_manager.py       # CSV/PDF export functionality
│   └── tabs/
│       ├── summary.py              # Portfolio Summary tab
│       ├── add_holdings.py         # Add Holdings tab with CSV validation
│       ├── analytics.py            # Analytics tab with CAGR calculations
│       └── reports.py              # Reports & Export tab
├── tests/
│   ├── test_portfolio_manager.py # Unit tests for portfolio logic
│   └── test_export_manager.py    # Unit tests for export functionality
├── playwright-tests/
│   ├── src/
│   │   ├── form-discovery.js       # Smart form discovery crawler
│   │   ├── test-generator.js       # Comprehensive test generator
│   │   └── simple-discovery.js     # Simplified discovery script
│   ├── package.json                # Playwright dependencies
│   ├── playwright.config.js        # Test configuration
│   ├── run-pipeline.js            # One-command test pipeline
│   └── README.md                   # Form testing documentation
├── .github/workflows/
│   └── form-testing.yml           # CI/CD pipeline for form tests
├── app.py                      # Original monolithic app (legacy)
├── app_modular.py              # New modular app entry point
├── requirements.txt            # Python dependencies
├── portfolio.json              # Auto-loading portfolio data storage
└── README.md                   # Project documentation
```

## Testing

### Unit Tests

Run the Python unit test suite:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_portfolio_manager.py
```

### Form Testing (Playwright)

Comprehensive form testing with automatic discovery and security testing:

```bash
# Navigate to form testing directory
cd playwright-tests

# Install dependencies (one-time setup)
npm install
npx playwright install

# Run complete form testing pipeline
node run-pipeline.js

# Or run individual steps
node src/simple-discovery.js    # Discover forms
node src/test-generator.js      # Generate tests
npx playwright test             # Run tests
npx playwright show-report      # View results
```

#### Automated Testing Pipeline
- **Form Discovery**: Automatically maps application forms and inputs
- **Security Testing**: XSS, SQL injection, and CSRF protection validation
- **Cross-browser**: Chrome, Firefox, and Safari compatibility testing
- **Self-updating**: Tests adapt automatically when UI changes
- **CI/CD Integration**: GitHub Actions workflow for continuous testing

## Development

### Key Components

- **PortfolioManager**: Handles data persistence, validation, and calculations
- **ExportManager**: Manages CSV and PDF export functionality
- **Tab Components**: Modular UI components for each application section
- **Form Testing Pipeline**: Automated discovery and testing of UI forms

### Adding New Features

1. Add business logic to appropriate manager class
2. Create/update tab component
3. Add unit tests
4. Update main app routing
5. Run form tests to ensure UI compatibility

### How It Works

1. **Data Import** → Intelligent CSV validation with real-time error checking
2. **Analytics Engine** → CAGR calculations, gain/loss tracking, performance metrics
3. **Visualization** → Interactive charts, asset allocation, professional dashboards
4. **Export System** → PDF reports with proper formatting and currency symbols
5. **Testing Layer** → Automated form discovery and comprehensive security validation

## Configuration Example

```python
# Add custom asset types in src/utils/portfolio_manager.py
VALID_ASSET_TYPES = [
    "Mutual Fund", "Equity", "Insurance", 
    "Bonds", "ETF", "Crypto"  # Add new types here
]

# Customize CAGR calculation periods
CAGR_PERIODS = {
    "short_term": 1,    # 1 year
    "medium_term": 3,   # 3 years  
    "long_term": 5      # 5 years
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
