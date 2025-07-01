import streamlit as st
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.portfolio_manager import PortfolioManager
from utils.export_manager import ExportManager
from tabs.summary import render_summary_tab
from tabs.add_holdings import render_add_holdings_tab
from tabs.analytics import render_analytics_tab
from tabs.reports import render_reports_tab

# Set page configuration
st.set_page_config(
    page_title="IndexCopilot - Portfolio Manager", page_icon="📊", layout="wide"
)

# Initialize managers
portfolio_manager = PortfolioManager()
export_manager = ExportManager()

# Initialize session state
if "portfolio" not in st.session_state:
    try:
        st.session_state.portfolio = portfolio_manager.load_portfolio()
    except Exception as e:
        st.error(f"Error loading portfolio: {str(e)}")
        st.session_state.portfolio = {"name": "My Portfolio", "holdings": []}

# Remove sidebar - it's redundant with main content

# App title and description
st.title("IndexCopilot")
st.markdown("### Portfolio Manager")
st.markdown("---")

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Summary", "Add Holdings", "Analytics", "Reports"])

with tab1:
    render_summary_tab(portfolio_manager)

with tab2:
    render_add_holdings_tab(portfolio_manager)

with tab3:
    render_analytics_tab(portfolio_manager)

with tab4:
    render_reports_tab(portfolio_manager, export_manager)

# Footer
st.markdown("---")
st.caption("IndexCopilot - Portfolio Manager")