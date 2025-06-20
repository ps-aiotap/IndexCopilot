import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from typing import Dict


class ExportManager:
    def __init__(self):
        self.unicode_font_registered = self._register_unicode_font()
    
    def _register_unicode_font(self) -> bool:
        """Try to register a Unicode-capable font"""
        font_paths = [
            'C:/Windows/Fonts/arial.ttf',  # Windows
            '/System/Library/Fonts/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                    return True
            except:
                continue
        return False
    
    def export_to_csv(self, portfolio: Dict) -> str:
        """Export portfolio to CSV format"""
        if not portfolio["holdings"]:
            return ""
        
        df = pd.DataFrame(portfolio["holdings"])
        return df.to_csv(index=False)
    
    def generate_pdf_report(self, portfolio: Dict) -> bytes:
        """Generate PDF report from portfolio data"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Set Unicode font if available
            if self.unicode_font_registered:
                styles['Normal'].fontName = 'UnicodeFont'
                styles['Title'].fontName = 'UnicodeFont'
                styles['Heading2'].fontName = 'UnicodeFont'
            
            story = []
            
            # Title
            title = Paragraph(f"Portfolio Report: {portfolio['name']}", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Portfolio summary
            total_value = sum(h["quantity"] * h["current_price"] for h in portfolio["holdings"])
            currency = "₹" if self.unicode_font_registered else "Rs."
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
            font_name = 'UnicodeFont' if self.unicode_font_registered else 'Helvetica'
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
            raise Exception(f"Error generating PDF: {str(e)}")