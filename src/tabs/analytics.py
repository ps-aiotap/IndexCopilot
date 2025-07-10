import streamlit as st
import pandas as pd


def render_analytics_tab(portfolio_manager):
    """Render the Analytics tab with CAGR calculations"""
    st.subheader("Analytics")
    
    if st.session_state.portfolio["holdings"]:
        # Create fresh dataframe from current session state
        holdings_df = pd.DataFrame(st.session_state.portfolio["holdings"]).copy()
        holdings_df["value"] = holdings_df["quantity"] * holdings_df["current_price"]
        holdings_df["gain_loss"] = holdings_df.apply(
            lambda row: portfolio_manager.calculate_gain_loss(row.to_dict()), axis=1
        )
        
        # Calculate CAGR for each holding
        holdings_df["cagr"] = holdings_df.apply(
            lambda row: portfolio_manager.calculate_cagr(
                row["purchase_price"], 
                row["current_price"], 
                row.get("purchase_date", "2023-01-01")
            ), axis=1
        )
        
        # Portfolio performance metrics - recalculate from fresh data
        col1, col2, col3, col4 = st.columns(4)
        
        # Recalculate totals from current holdings
        current_holdings = st.session_state.portfolio["holdings"]
        total_investment = sum(h["quantity"] * h["purchase_price"] for h in current_holdings)
        total_current_value = sum(h["quantity"] * h["current_price"] for h in current_holdings)
        total_gain_loss = total_current_value - total_investment
        gain_loss_percentage = (total_gain_loss / total_investment) * 100 if total_investment > 0 else 0
        
        with col1:
            st.metric("Total Investment", f"₹{total_investment:,.2f}")
        with col2:
            st.metric("Current Value", f"₹{total_current_value:,.2f}")
        with col3:
            delta_color = "normal" if total_gain_loss >= 0 else "inverse"
            st.metric("Total Gain/Loss", f"₹{total_gain_loss:,.2f}", f"{gain_loss_percentage:.2f}%", delta_color=delta_color)
        with col4:
            if not holdings_df.empty:
                best_performer = holdings_df.loc[holdings_df['gain_loss'].idxmax()]
                st.metric("Best Performer", best_performer['asset_name'][:15], f"₹{best_performer['gain_loss']:,.2f}")
        
        # CAGR Analysis
        st.subheader("CAGR Analysis")
        
        # Display CAGR table
        cagr_df = holdings_df[['asset_name', 'asset_type', 'cagr', 'gain_loss']].copy()
        cagr_df = cagr_df.sort_values('cagr', ascending=False)
        
        # Format CAGR display with colors - create once to avoid flickering
        cagr_display_data = []
        for _, row in cagr_df.iterrows():
            if row['cagr'] > 0:
                cagr_display_data.append(f"{row['cagr']:.2f}%")
            elif row['cagr'] < 0:
                cagr_display_data.append(f"{row['cagr']:.2f}%")
            else:
                cagr_display_data.append(f"{row['cagr']:.2f}%")
        
        cagr_df['cagr_display'] = cagr_display_data
        
        st.dataframe(
            cagr_df[['asset_name', 'asset_type', 'cagr_display', 'gain_loss']],
            column_config={
                "asset_name": st.column_config.TextColumn("Asset Name"),
                "asset_type": st.column_config.TextColumn("Type"),
                "cagr_display": st.column_config.TextColumn("CAGR"),
                "gain_loss": st.column_config.NumberColumn("Total Gain/Loss", format="₹%.2f"),
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Performance insights
        st.subheader("Performance Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top performers
            st.markdown("**🏆 Top Performers (CAGR)**")
            top_performers = cagr_df.head(3)
            for _, row in top_performers.iterrows():
                color = "🟢" if row['cagr'] > 0 else "🔴"
                st.write(f"{color} {row['asset_name'][:20]}: {row['cagr']:.2f}%")
        
        with col2:
            # Asset type performance
            st.markdown("**📊 Asset Type Performance**")
            type_performance = holdings_df.groupby('asset_type').agg({
                'cagr': 'mean',
                'gain_loss': 'sum'
            }).round(2)
            
            for asset_type, data in type_performance.iterrows():
                color = "🟢" if data['cagr'] > 0 else "🔴"
                st.write(f"{color} {asset_type}: {data['cagr']:.2f}% avg CAGR")
        
    else:
        st.info("Add holdings to view analytics")