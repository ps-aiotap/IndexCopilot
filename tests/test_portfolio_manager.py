import pytest
import pandas as pd
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.portfolio_manager import PortfolioManager


class TestPortfolioManager:
    
    def setup_method(self):
        """Setup test data"""
        self.portfolio_manager = PortfolioManager("test_portfolio.json")
        self.sample_holding = {
            "asset_type": "equity",
            "asset_id": "RELIANCE",
            "asset_name": "Reliance Industries Ltd",
            "quantity": 10,
            "purchase_price": 2000.0,
            "current_price": 2500.0,
            "purchase_date": "2023-01-15"
        }
    
    def test_calculate_gain_loss_positive(self):
        """Test gain calculation for profitable holding"""
        gain_loss = self.portfolio_manager.calculate_gain_loss(self.sample_holding)
        expected = (2500.0 - 2000.0) * 10  # 5000.0
        assert gain_loss == expected
    
    def test_calculate_gain_loss_negative(self):
        """Test loss calculation for unprofitable holding"""
        losing_holding = self.sample_holding.copy()
        losing_holding["current_price"] = 1500.0
        
        gain_loss = self.portfolio_manager.calculate_gain_loss(losing_holding)
        expected = (1500.0 - 2000.0) * 10  # -5000.0
        assert gain_loss == expected
    
    def test_calculate_gain_loss_zero(self):
        """Test zero gain/loss when prices are equal"""
        neutral_holding = self.sample_holding.copy()
        neutral_holding["current_price"] = 2000.0
        
        gain_loss = self.portfolio_manager.calculate_gain_loss(neutral_holding)
        assert gain_loss == 0.0
    
    def test_calculate_cagr_positive(self):
        """Test CAGR calculation for positive returns"""
        cagr = self.portfolio_manager.calculate_cagr(2000.0, 2500.0, "2023-01-15")
        assert cagr > 0  # Should be positive
        assert isinstance(cagr, float)
    
    def test_calculate_cagr_negative(self):
        """Test CAGR calculation for negative returns"""
        cagr = self.portfolio_manager.calculate_cagr(2000.0, 1500.0, "2023-01-15")
        assert cagr < 0  # Should be negative
    
    def test_validate_csv_data_valid(self):
        """Test CSV validation with valid data"""
        valid_data = {
            "asset_type": ["equity", "mutual_fund"],
            "asset_id": ["RELIANCE", "HDFC123"],
            "asset_name": ["Reliance Industries", "HDFC Fund"],
            "quantity": [10, 100],
            "purchase_price": [2000.0, 150.0],
            "purchase_date": ["2023-01-15", "2023-02-20"]
        }
        df = pd.DataFrame(valid_data)
        
        is_valid, message = self.portfolio_manager.validate_csv_data(df)
        assert is_valid == True
        assert message == "Valid"
    
    def test_validate_csv_data_missing_columns(self):
        """Test CSV validation with missing required columns"""
        invalid_data = {
            "asset_type": ["equity"],
            "asset_name": ["Reliance Industries"],
            # Missing asset_id, quantity, purchase_price
        }
        df = pd.DataFrame(invalid_data)
        
        is_valid, message = self.portfolio_manager.validate_csv_data(df)
        assert is_valid == False
        assert "Missing required columns" in message
    
    def test_validate_csv_data_invalid_numeric(self):
        """Test CSV validation with invalid numeric data"""
        invalid_data = {
            "asset_type": ["equity"],
            "asset_id": ["RELIANCE"],
            "asset_name": ["Reliance Industries"],
            "quantity": ["invalid"],  # Should be numeric
            "purchase_price": [2000.0]
        }
        df = pd.DataFrame(invalid_data)
        
        is_valid, message = self.portfolio_manager.validate_csv_data(df)
        assert is_valid == False
        assert "Invalid numeric data" in message
    
    def test_validate_csv_data_negative_values(self):
        """Test CSV validation with negative values"""
        invalid_data = {
            "asset_type": ["equity"],
            "asset_id": ["RELIANCE"],
            "asset_name": ["Reliance Industries"],
            "quantity": [-10],  # Should be positive
            "purchase_price": [2000.0]
        }
        df = pd.DataFrame(invalid_data)
        
        is_valid, message = self.portfolio_manager.validate_csv_data(df)
        assert is_valid == False
        assert "Quantity must be positive" in message
    
    def test_validate_csv_data_invalid_date(self):
        """Test CSV validation with invalid date format"""
        invalid_data = {
            "asset_type": ["equity"],
            "asset_id": ["RELIANCE"],
            "asset_name": ["Reliance Industries"],
            "quantity": [10],
            "purchase_price": [2000.0],
            "purchase_date": ["invalid-date"]
        }
        df = pd.DataFrame(invalid_data)
        
        is_valid, message = self.portfolio_manager.validate_csv_data(df)
        assert is_valid == False
        assert "Invalid date format" in message
    
    def teardown_method(self):
        """Clean up test files"""
        if os.path.exists("test_portfolio.json"):
            os.remove("test_portfolio.json")