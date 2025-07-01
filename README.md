# IndexCopilot

A simple portfolio manager.

## Overview

IndexCopilot is a Streamlit-based application that helps users manage and visualize their investment portfolios. The application provides a clean interface for tracking mutual funds, equities, and other investments.

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

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/IndexCopilot.git
   cd IndexCopilot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit application:

   ```
   # Run the new modular version (recommended)
   streamlit run app_modular.py
   
   # Or run the original version
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

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

## CSV Format

When uploading a CSV file, use the following format:

```
asset_type,asset_id,asset_name,quantity,purchase_price,purchase_date
mutual_fund,HDFC123,HDFC Nifty 50 Index Fund,100,150.0,2023-01-15
equity,RELIANCE,Reliance Industries Ltd,10,2500.0,2023-02-20
```

Required columns:

- `asset_type`: Type of asset (mutual_fund, equity, insurance)
- `asset_id`: Fund code or stock symbol
- `asset_name`: Name of the asset
- `quantity`: Number of units
- `purchase_price`: Price per unit at purchase
- `purchase_date`: Date of purchase (YYYY-MM-DD)

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

#### Form Testing Features
- **Smart Discovery**: Automatically finds forms by crawling the application
- **Security Testing**: XSS, SQL injection, and CSRF protection tests
- **Cross-browser**: Tests on Chrome, Firefox, and Safari
- **Comprehensive Coverage**: Validation, edge cases, and error handling
- **Rich Reporting**: HTML reports with screenshots and videos
- **CI/CD Ready**: Automated testing in GitHub Actions

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

### Form Testing Pipeline

The automated form testing system:
1. **Discovers** forms by crawling the live application
2. **Generates** comprehensive test suites for each form
3. **Executes** tests across multiple browsers
4. **Reports** results with detailed analysis

Tests are automatically generated based on discovered form structure, ensuring coverage stays current with UI changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
