import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime
import os
import json

# Set page configuration
st.set_page_config(
    page_title="IndexCopilot - Portfolio Manager", page_icon="📊", layout="wide"
)

# Initialize session state
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {"name": "My Portfolio", "holdings": []}
    
    # Auto-load portfolio from file on first run
    if os.path.exists("portfolio.json"):
        try:
            with open("portfolio.json", "r") as f:
                st.session_state.portfolio = json.load(f)
        except Exception as e:
            st.error(f"Error loading portfolio: {str(e)}")



# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Dark mode toggle (note: limited support in Streamlit)
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
    if dark_mode:
        st.info("💡 Dark mode is enabled. Note: Streamlit has limited dark mode support.")
    
    st.markdown("---")
    
    # Quick stats in sidebar
    if st.session_state.portfolio["holdings"]:
        st.subheader("Quick Stats")
        total_holdings = len(st.session_state.portfolio["holdings"])
        total_value = sum(h["quantity"] * h["current_price"] for h in st.session_state.portfolio["holdings"])
        st.metric("Holdings", total_holdings)
        st.metric("Portfolio Value", f"₹{total_value:,.0f}")

# App title and description
st.title("IndexCopilot")
st.markdown("### Portfolio Manager")
st.markdown("---")


# Function to generate PDF report
def generate_pdf(portfolio):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Try to register a Unicode-capable font
        unicode_font_registered = False
        font_paths = [
            'C:/Windows/Fonts/arial.ttf',  # Windows
            '/System/Library/Fonts/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                    styles['Normal'].fontName = 'UnicodeFont'
                    styles['Title'].fontName = 'UnicodeFont'
                    styles['Heading2'].fontName = 'UnicodeFont'
                    unicode_font_registered = True
                    break
            except:
                continue
            
        story = []

        # Title
        title = Paragraph(f"Portfolio Report: {portfolio['name']}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Portfolio summary
        total_value = sum(h["quantity"] * h["current_price"] for h in portfolio["holdings"])
        currency = "₹" if unicode_font_registered else "Rs."
        summary = Paragraph(f"<b>Total Value:</b> {currency}{total_value:,.2f}<br/><b>Number of Holdings:</b> {len(portfolio['holdings'])}", styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 12))

        # Holdings table
        holdings_title = Paragraph("<b>Holdings</b>", styles['Heading2'])
        story.append(holdings_title)
        story.append(Spacer(1, 6))

        # Table data
        data = [['Asset Name', 'Type', 'Quantity', 'Price', 'Value']]
        for holding in portfolio["holdings"]:
            value = holding["quantity"] * holding["current_price"]
            data.append([
                holding["asset_name"][:25],
                holding["asset_type"],
                f"{holding['quantity']:.2f}",
                f"{currency}{holding['current_price']:,.2f}",
                f"{currency}{value:,.2f}"
            ])

        table = Table(data)
        font_name = 'UnicodeFont' if unicode_font_registered else 'Helvetica'
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None


# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Summary", "Add Holdings", "Analytics", "Reports"])

with tab1:
    st.subheader("My Portfolio")

    # Inline editable portfolio name
    col1, col2 = st.columns([4, 1])
    with col1:
        portfolio_name = st.text_input(
            "Portfolio Name", value=st.session_state.portfolio["name"], key="portfolio_name_input"
        )
        st.session_state.portfolio["name"] = portfolio_name
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Edit"):
            st.info("Click in the text field above to edit the portfolio name")

    # Display holdings if available
    if st.session_state.portfolio["holdings"]:
        # Convert holdings to DataFrame for display
        holdings_df = pd.DataFrame(st.session_state.portfolio["holdings"])

        # Calculate total value
        total_value = sum(
            h["quantity"] * h["current_price"]
            for h in st.session_state.portfolio["holdings"]
        )

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

        # Add value and gain/loss columns
        holdings_df["value"] = holdings_df["quantity"] * holdings_df["current_price"]
        holdings_df["gain_loss"] = (holdings_df["current_price"] - holdings_df["purchase_price"]) * holdings_df["quantity"]
        
        # Add gain/loss indicators with colors
        def format_gain_loss(value):
            if value > 0:
                return f"▲ ₹{value:,.2f}"
            elif value < 0:
                return f"▼ ₹{abs(value):,.2f}"
            else:
                return f"₹{value:,.2f}"
        
        holdings_df["gain_loss_formatted"] = holdings_df["gain_loss"].apply(format_gain_loss)
        
        # Create a custom display for gain/loss with colors
        for idx, row in holdings_df.iterrows():
            if row['gain_loss'] > 0:
                holdings_df.at[idx, 'gain_loss_display'] = f":green[▲ ₹{row['gain_loss']:,.2f}]"
            elif row['gain_loss'] < 0:
                holdings_df.at[idx, 'gain_loss_display'] = f":red[▼ ₹{abs(row['gain_loss']):,.2f}]"
            else:
                holdings_df.at[idx, 'gain_loss_display'] = f"₹{row['gain_loss']:,.2f}"

        # Display as table
        st.dataframe(
            holdings_df,
            column_config={
                "asset_id": st.column_config.TextColumn("Asset ID"),
                "asset_name": st.column_config.TextColumn("Asset Name"),
                "asset_type": st.column_config.TextColumn("Type"),
                "quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
                "purchase_price": st.column_config.NumberColumn(
                    "Purchase Price", format="₹%.2f"
                ),
                "current_price": st.column_config.NumberColumn(
                    "Current Price", format="₹%.2f"
                ),
                "purchase_date": st.column_config.TextColumn("Purchase Date"),
                "value": st.column_config.NumberColumn("Value", format="₹%.2f"),
                "gain_loss_display": st.column_config.TextColumn("Gain/Loss"),
            },
            hide_index=True,
            use_container_width=True,
        )

        # Asset allocation chart
        st.subheader("Asset Allocation")
        
        # Center the chart with limited width
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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


    else:
        st.info(
            "No holdings in your portfolio yet. Add holdings in the 'Add Holdings' tab."
        )

with tab2:
    st.subheader("Add Holdings")

    # Two methods: Upload CSV or add manually
    method = st.radio("Choose method", ["Upload CSV", "Add Manually"])

    if method == "Upload CSV":
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
                required_columns = [
                    "asset_type",
                    "asset_id",
                    "asset_name",
                    "quantity",
                    "purchase_price",
                ]

                if all(col in holdings_df.columns for col in required_columns):
                    # Convert to list of dictionaries
                    holdings = holdings_df.to_dict(orient="records")

                    # Add current_price equal to purchase_price for now
                    for holding in holdings:
                        holding["current_price"] = holding["purchase_price"]

                    # Update session state
                    st.session_state.portfolio["holdings"] = holdings

                    st.success(f"✓ Successfully loaded {len(holdings)} holdings from CSV!")
                else:
                    st.error(
                        "CSV must contain asset_type, asset_id, asset_name, quantity, and purchase_price columns"
                    )
            except Exception as e:
                st.error(f"Error loading CSV: {str(e)}")
    else:
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

# Move export and save options to Reports tab
with tab3:
    st.subheader("Analytics")
    
    if st.session_state.portfolio["holdings"]:
        holdings_df = pd.DataFrame(st.session_state.portfolio["holdings"])
        holdings_df["value"] = holdings_df["quantity"] * holdings_df["current_price"]
        holdings_df["gain_loss"] = (holdings_df["current_price"] - holdings_df["purchase_price"]) * holdings_df["quantity"]
        
        # Portfolio performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_investment = sum(h["quantity"] * h["purchase_price"] for h in st.session_state.portfolio["holdings"])
        total_current_value = sum(h["quantity"] * h["current_price"] for h in st.session_state.portfolio["holdings"])
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
            best_performer = holdings_df.loc[holdings_df['gain_loss'].idxmax()]
            st.metric("Best Performer", best_performer['asset_name'][:15], f"₹{best_performer['gain_loss']:,.2f}")
    else:
        st.info("Add holdings to view analytics")

with tab4:
    st.subheader("Reports & Export")
    
    if st.session_state.portfolio["holdings"]:
        # Export options
        col1, col2 = st.columns(2)

        with col1:
            # Export to CSV
            holdings_df = pd.DataFrame(st.session_state.portfolio["holdings"])
            csv = holdings_df.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV Report",
                data=csv,
                file_name=f"{st.session_state.portfolio['name'].replace(' ', '_')}_portfolio.csv",
                mime="text/csv",
            )

        with col2:
            # Export to PDF
            if st.button("📄 Generate PDF Report"):
                pdf_data = generate_pdf(st.session_state.portfolio)
                if pdf_data:
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_data,
                        file_name=f"{st.session_state.portfolio['name'].replace(' ', '_')}_report.pdf",
                        mime="application/pdf",
                    )
    else:
        st.info("Add holdings to generate reports")
    
    st.markdown("---")
    
    # Save/Load portfolio
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Portfolio"):
            try:
                with open("portfolio.json", "w") as f:
                    json.dump(st.session_state.portfolio, f)
                st.success("✓ Portfolio saved successfully!")
            except Exception as e:
                st.error(f"Error saving portfolio: {str(e)}")
    
    with col2:
        if os.path.exists("portfolio.json"):
            if st.button("🔄 Reload Portfolio"):
                try:
                    with open("portfolio.json", "r") as f:
                        st.session_state.portfolio = json.load(f)
                    st.success("✓ Portfolio reloaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading portfolio: {str(e)}")

# Footer
st.markdown("---")
st.caption("IndexCopilot - Portfolio Manager")
