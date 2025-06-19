# IndexCopilot

A simple portfolio manager.

## Overview

IndexCopilot is a Streamlit-based application that helps users manage and visualize their investment portfolios. The application provides a clean interface for tracking mutual funds, equities, and other investments.

## Features

- Portfolio management with visual analytics
- CSV upload for bulk import of holdings
- Manual entry of individual holdings
- Asset allocation visualization
- Export to CSV and PDF
- Local file storage for portfolio data

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
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Add holdings to your portfolio:

   - Upload a CSV file with your holdings
   - Add holdings manually

4. View your portfolio analytics:

   - Total value
   - Asset allocation
   - Holdings breakdown

5. Export your portfolio:
   - Download as CSV
   - Generate PDF report

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

- `app.py`: Streamlit UI and main application logic
- `requirements.txt`: Python dependencies
- `portfolio.json`: Local storage for portfolio data (created when saving)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
