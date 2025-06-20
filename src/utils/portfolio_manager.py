import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional


class PortfolioManager:
    def __init__(self, file_path: str = "portfolio.json"):
        self.file_path = file_path
    
    def load_portfolio(self) -> Dict:
        """Load portfolio from JSON file"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                raise Exception(f"Error loading portfolio: {str(e)}")
        return {"name": "My Portfolio", "holdings": []}
    
    def save_portfolio(self, portfolio: Dict) -> None:
        """Save portfolio to JSON file"""
        try:
            with open(self.file_path, "w") as f:
                json.dump(portfolio, f, indent=2)
        except Exception as e:
            raise Exception(f"Error saving portfolio: {str(e)}")
    
    def validate_csv_data(self, df: pd.DataFrame) -> tuple[bool, str]:
        """Validate CSV data format and types"""
        required_columns = ["asset_type", "asset_id", "asset_name", "quantity", "purchase_price"]
        
        # Check required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}"
        
        # Validate data types
        try:
            df["quantity"] = pd.to_numeric(df["quantity"], errors="raise")
            df["purchase_price"] = pd.to_numeric(df["purchase_price"], errors="raise")
        except ValueError as e:
            return False, f"Invalid numeric data in quantity or purchase_price: {str(e)}"
        
        # Check for negative values
        if (df["quantity"] <= 0).any():
            return False, "Quantity must be positive"
        if (df["purchase_price"] <= 0).any():
            return False, "Purchase price must be positive"
        
        # Validate date format if present
        if "purchase_date" in df.columns:
            try:
                pd.to_datetime(df["purchase_date"], errors="raise")
            except ValueError:
                return False, "Invalid date format in purchase_date. Use YYYY-MM-DD"
        
        return True, "Valid"
    
    def calculate_gain_loss(self, holding: Dict) -> float:
        """Calculate gain/loss for a single holding"""
        return (holding["current_price"] - holding["purchase_price"]) * holding["quantity"]
    
    def calculate_cagr(self, purchase_price: float, current_price: float, purchase_date: str) -> float:
        """Calculate Compound Annual Growth Rate"""
        try:
            purchase_dt = datetime.fromisoformat(purchase_date.replace('/', '-'))
            current_dt = datetime.now()
            years = (current_dt - purchase_dt).days / 365.25
            
            if years <= 0:
                return 0.0
            
            cagr = ((current_price / purchase_price) ** (1 / years)) - 1
            return cagr * 100  # Return as percentage
        except:
            return 0.0