import pytest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.export_manager import ExportManager


class TestExportManager:
    
    def setup_method(self):
        """Setup test data"""
        self.export_manager = ExportManager()
        self.sample_portfolio = {
            "name": "Test Portfolio",
            "holdings": [
                {
                    "asset_type": "equity",
                    "asset_id": "RELIANCE",
                    "asset_name": "Reliance Industries Ltd",
                    "quantity": 10,
                    "purchase_price": 2000.0,
                    "current_price": 2500.0,
                    "purchase_date": "2023-01-15"
                },
                {
                    "asset_type": "mutual_fund",
                    "asset_id": "HDFC123",
                    "asset_name": "HDFC Nifty 50 Index Fund",
                    "quantity": 100,
                    "purchase_price": 150.0,
                    "current_price": 180.0,
                    "purchase_date": "2023-02-20"
                }
            ]
        }
    
    def test_export_to_csv_with_holdings(self):
        """Test CSV export with valid portfolio data"""
        csv_data = self.export_manager.export_to_csv(self.sample_portfolio)
        
        assert csv_data is not None
        assert len(csv_data) > 0
        assert "asset_type" in csv_data
        assert "RELIANCE" in csv_data
        assert "HDFC123" in csv_data
    
    def test_export_to_csv_empty_portfolio(self):
        """Test CSV export with empty portfolio"""
        empty_portfolio = {"name": "Empty Portfolio", "holdings": []}
        csv_data = self.export_manager.export_to_csv(empty_portfolio)
        
        assert csv_data == ""
    
    def test_generate_pdf_report_with_holdings(self):
        """Test PDF generation with valid portfolio data"""
        pdf_data = self.export_manager.generate_pdf_report(self.sample_portfolio)
        
        assert pdf_data is not None
        assert len(pdf_data) > 0
        assert isinstance(pdf_data, bytes)
        # PDF files start with %PDF
        assert pdf_data.startswith(b'%PDF')
    
    def test_generate_pdf_report_empty_portfolio(self):
        """Test PDF generation with empty portfolio"""
        empty_portfolio = {"name": "Empty Portfolio", "holdings": []}
        pdf_data = self.export_manager.generate_pdf_report(empty_portfolio)
        
        assert pdf_data is not None
        assert isinstance(pdf_data, bytes)
        assert pdf_data.startswith(b'%PDF')