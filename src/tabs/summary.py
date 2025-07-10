import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def render_summary_tab(portfolio_manager):
    """Render the Portfolio Summary tab"""
    st.subheader("My Portfolio")

    # Inline editable portfolio name
    col1, col2 = st.columns([4, 1])
    with col1:
        portfolio_name = st.text_input(
            "Portfolio Name", 
            value=st.session_state.portfolio["name"], 
            key="portfolio_name_input"
        )
        st.session_state.portfolio["name"] = portfolio_name
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Edit"):
            st.info("Click in the text field above to edit the portfolio name")

    # Display holdings if available
    if st.session_state.portfolio["holdings"]:
        holdings_df = pd.DataFrame(st.session_state.portfolio["holdings"])
        total_value = sum(h["quantity"] * h["current_price"] for h in st.session_state.portfolio["holdings"])

        # Display portfolio summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", f"₹{total_value:,.2f}")
        with col2:
            st.metric("Number of Holdings", len(holdings_df))
        with col3:
            st.metric("Last Updated", datetime.now().strftime("%Y-%m-%d"))

        # Display holdings table
        st.subheader("Holdings")
        _display_holdings_table(holdings_df, portfolio_manager)
        
        # Asset allocation chart
        _display_asset_allocation_chart(holdings_df, total_value)
    else:
        st.info("No holdings in your portfolio yet. Add holdings in the 'Add Holdings' tab.")


def _display_holdings_table(holdings_df, portfolio_manager):
    """Display the holdings table with gain/loss calculations"""
    # Create a copy to avoid modifying original data
    display_df = holdings_df.copy()
    
    # Add value and gain/loss columns
    display_df["value"] = display_df["quantity"] * display_df["current_price"]
    display_df["gain_loss"] = display_df.apply(
        lambda row: portfolio_manager.calculate_gain_loss(row.to_dict()), axis=1
    )
    
    # Create color-coded gain/loss display
    gain_loss_display = []
    for _, row in display_df.iterrows():
        if row['gain_loss'] > 0:
            gain_loss_display.append(f"▲ ₹{row['gain_loss']:,.2f}")
        elif row['gain_loss'] < 0:
            gain_loss_display.append(f"▼ ₹{abs(row['gain_loss']):,.2f}")
        else:
            gain_loss_display.append(f"₹{row['gain_loss']:,.2f}")
    
    display_df['gain_loss_display'] = gain_loss_display

    # Display table
    st.dataframe(
        display_df,
        column_config={
            "asset_id": st.column_config.TextColumn("Asset ID"),
            "asset_name": st.column_config.TextColumn("Asset Name"),
            "asset_type": st.column_config.TextColumn("Type"),
            "quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
            "purchase_price": st.column_config.NumberColumn("Purchase Price", format="₹%.2f"),
            "current_price": st.column_config.NumberColumn("Current Price", format="₹%.2f"),
            "purchase_date": st.column_config.TextColumn("Purchase Date"),
            "value": st.column_config.NumberColumn("Value", format="₹%.2f"),
            "gain_loss_display": st.column_config.TextColumn("Gain/Loss"),
        },
        hide_index=True,
        use_container_width=True,
    )


def _display_asset_allocation_chart(holdings_df, total_value):
    """Display the asset allocation doughnut chart"""
    st.subheader("Asset Allocation")
    
    # Center the chart with limited width
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Ensure value column exists
        if "value" not in holdings_df.columns:
            holdings_df["value"] = holdings_df["quantity"] * holdings_df["current_price"]
        
        # Group by asset type
        asset_allocation = holdings_df.groupby("asset_type")["value"].sum()
        
        # Create doughnut chart
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Create labels with percentage and amount
        labels = []
        for asset_type, value in asset_allocation.items():
            percentage = (value / total_value) * 100
            labels.append(f"{asset_type}: {percentage:.1f}% - ₹{value:,.0f}")
        
        wedges, texts, autotexts = ax.pie(
            asset_allocation,
            labels=labels,
            autopct="",
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(width=0.5)
        )
        
        # Add center text
        ax.text(0, 0, f"Total\n₹{total_value:,.0f}", 
               horizontalalignment='center', verticalalignment='center',
               fontsize=12, fontweight='bold')
        
        ax.axis("equal")
        plt.tight_layout()
        st.pyplot(fig)
        
        # Add legend with matching colors
        st.markdown("**Asset Breakdown:**")
        for i, (asset_type, value) in enumerate(asset_allocation.items()):
            percentage = (value / total_value) * 100
            # Get the actual color from the wedge
            color = wedges[i].get_facecolor()
            color_hex = f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"
            st.markdown(f"<span style='color: {color_hex}'>●</span> **{asset_type}**: {percentage:.1f}% (₹{value:,.2f})", unsafe_allow_html=True)