import streamlit as st
import pandas as pd


def render_add_holdings_tab(portfolio_manager):
    """Render the Add Holdings tab"""
    st.subheader("Add Holdings")

    # Two methods: Upload CSV or add manually
    method = st.radio("Choose method", ["Upload CSV", "Add Manually"])

    if method == "Upload CSV":
        _render_csv_upload(portfolio_manager)
    else:
        _render_manual_entry()


def _render_csv_upload(portfolio_manager):
    """Render CSV upload section with validation"""
    st.write("Upload a CSV file with your holdings")

    # CSV format instructions with styled table
    st.markdown("**CSV Format Requirements:**")
    
    # Sample CSV data
    sample_data = {
        "asset_type": ["mutual_fund", "equity", "insurance"],
        "asset_id": ["HDFC123", "RELIANCE", "LIC001"],
        "asset_name": ["HDFC Nifty 50 Index Fund", "Reliance Industries Ltd", "LIC Term Plan"],
        "quantity": [100, 10, 1],
        "purchase_price": [150.0, 2500.0, 50000.0],
        "purchase_date": ["2023-01-15", "2023-02-20", "2023-03-10"]
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, use_container_width=True)
    
    # Download sample CSV button
    sample_csv = sample_df.to_csv(index=False)
    st.download_button(
        label="💾 Download Sample CSV",
        data=sample_csv,
        file_name="sample_portfolio.csv",
        mime="text/csv",
    )

    uploaded_file = st.file_uploader("Upload CSV file", type="csv")

    if uploaded_file is not None:
        try:
            holdings_df = pd.read_csv(uploaded_file)
            
            # Validate CSV data
            is_valid, error_message = portfolio_manager.validate_csv_data(holdings_df)
            
            if not is_valid:
                st.error(f"❌ CSV validation failed: {error_message}")
                return
            
            # Convert to list of dictionaries
            holdings = holdings_df.to_dict(orient="records")

            # Add current_price equal to purchase_price for now
            for holding in holdings:
                holding["current_price"] = holding["purchase_price"]
                # Ensure purchase_date is string
                if "purchase_date" in holding:
                    holding["purchase_date"] = str(holding["purchase_date"])

            # Update session state
            st.session_state.portfolio["holdings"] = holdings
            st.success(f"✓ Successfully loaded {len(holdings)} holdings from CSV!")
            
        except Exception as e:
            st.error(f"❌ Error loading CSV: {str(e)}")


def _render_manual_entry():
    """Render manual entry form"""
    st.write("Add a holding manually")

    # Form for manual entry
    with st.form("add_holding_form"):
        asset_type = st.selectbox(
            "Asset Type", ["Mutual Fund", "Equity", "Insurance"]
        )
        asset_id = st.text_input("Asset ID (Fund Code/Stock Symbol)")
        asset_name = st.text_input("Asset Name")
        quantity = st.number_input("Quantity", min_value=0.0, value=100.0, step=1.0)
        purchase_price = st.number_input(
            "Purchase Price (₹)", min_value=0.0, value=100.0, step=1.0
        )
        purchase_date = st.date_input("Purchase Date")

        submit = st.form_submit_button("Add Holding")

        if submit:
            if asset_id and asset_name and quantity > 0 and purchase_price > 0:
                # Create new holding
                new_holding = {
                    "asset_type": asset_type,
                    "asset_id": asset_id,
                    "asset_name": asset_name,
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "current_price": purchase_price,  # Set current price equal to purchase price initially
                    "purchase_date": purchase_date.isoformat(),
                }

                # Add to session state
                st.session_state.portfolio["holdings"].append(new_holding)
                st.success(f"✓ Successfully added {asset_name} to portfolio!")
            else:
                st.error("Please fill in all required fields")