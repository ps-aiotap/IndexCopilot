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
tab1, tab2 = st.tabs(["Portfolio", "Add Holdings"])

with tab1:
    st.subheader("My Portfolio")

    # Portfolio name
    portfolio_name = st.text_input(
        "Portfolio Name", value=st.session_state.portfolio["name"]
    )
    st.session_state.portfolio["name"] = portfolio_name

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

        # Add value column
        holdings_df["value"] = holdings_df["quantity"] * holdings_df["current_price"]

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
            },
            hide_index=True,
            use_container_width=True,
        )

        # Asset allocation chart
        st.subheader("Asset Allocation")

        # Group by asset type
        asset_allocation = holdings_df.groupby("asset_type")["value"].sum()

        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(
            asset_allocation,
            labels=asset_allocation.index,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.axis("equal")
        st.pyplot(fig)

        # Export options
        st.subheader("Export Portfolio")
        col1, col2 = st.columns(2)

        with col1:
            # Export to CSV
            csv = holdings_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{portfolio_name.replace(' ', '_')}_portfolio.csv",
                mime="text/csv",
            )

        with col2:
            # Export to PDF
            if st.button("Generate PDF Report"):
                pdf_data = generate_pdf(st.session_state.portfolio)
                if pdf_data:
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_data,
                        file_name=f"{portfolio_name.replace(' ', '_')}_report.pdf",
                        mime="application/pdf",
                    )
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

        # Example CSV format
        st.markdown(
            """
        **CSV Format Example:**
        ```
        asset_type,asset_id,asset_name,quantity,purchase_price,purchase_date
        mutual fund,HDFC123,HDFC Nifty 50 Index Fund,100,150.0,2023-01-15
        equity,RELIANCE,Reliance Industries Ltd,10,2500.0,2023-02-20
        ```
        """
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

                    st.success(f"Loaded {len(holdings)} holdings from CSV")
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

                    st.success(f"Added {asset_name} to portfolio")
                else:
                    st.error("Please fill in all required fields")

# Save portfolio to file
if st.button("Save Portfolio"):
    try:
        with open("portfolio.json", "w") as f:
            json.dump(st.session_state.portfolio, f)
        st.success("Portfolio saved to file")
    except Exception as e:
        st.error(f"Error saving portfolio: {str(e)}")

# Manual reload button (optional)
if os.path.exists("portfolio.json"):
    if st.button("Reload Portfolio from File"):
        try:
            with open("portfolio.json", "r") as f:
                st.session_state.portfolio = json.load(f)
            st.success("Portfolio reloaded from file")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading portfolio: {str(e)}")

# Footer
st.markdown("---")
st.caption("IndexCopilot - Portfolio Manager")
