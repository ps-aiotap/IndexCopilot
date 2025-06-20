import streamlit as st
import pandas as pd


def render_reports_tab(portfolio_manager, export_manager):
    """Render the Reports & Export tab"""
    st.subheader("Reports & Export")
    
    if st.session_state.portfolio["holdings"]:
        # Export options
        col1, col2 = st.columns(2)

        with col1:
            # Export to CSV
            csv_data = export_manager.export_to_csv(st.session_state.portfolio)
            if csv_data:
                st.download_button(
                    label="📊 Download CSV Report",
                    data=csv_data,
                    file_name=f"{st.session_state.portfolio['name'].replace(' ', '_')}_portfolio.csv",
                    mime="text/csv",
                )

        with col2:
            # Export to PDF
            if st.button("📄 Generate PDF Report"):
                try:
                    pdf_data = export_manager.generate_pdf_report(st.session_state.portfolio)
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_data,
                        file_name=f"{st.session_state.portfolio['name'].replace(' ', '_')}_report.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
    else:
        st.info("Add holdings to generate reports")
    
    st.markdown("---")
    
    # Save/Load portfolio
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Portfolio"):
            try:
                portfolio_manager.save_portfolio(st.session_state.portfolio)
                st.success("✓ Portfolio saved successfully!")
            except Exception as e:
                st.error(f"Error saving portfolio: {str(e)}")
    
    with col2:
        if st.button("🔄 Reload Portfolio"):
            try:
                st.session_state.portfolio = portfolio_manager.load_portfolio()
                st.success("✓ Portfolio reloaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading portfolio: {str(e)}")