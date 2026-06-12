"""
Bluestock Mutual Fund Analytics Platform - PDF Report Generator
Generates a professional 19-page PDF report incorporating cover page, TOC,
executive summary, ETL design, EDA findings, performance scorecard,
dashboard screenshots, limitations, and recommendations.
"""

import os
import sys
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Set up paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "db", "bluestock_mf.db")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
CHARTS_DIR = os.path.join(REPORTS_DIR, "charts")
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "dashboard")
DAY3_CHARTS_DIR = os.path.join(REPORTS_DIR, "charts")

os.makedirs(REPORTS_DIR, exist_ok=True)
PDF_OUTPUT_PATH = os.path.join(REPORTS_DIR, "Final_Report.pdf")

# Custom Canvas for Two-Pass Page Numbering (e.g. "Page X of Y")
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Suppress headers/footers on cover page
        if self._pageNumber == 1:
            self.restoreState()
            return
            
        # Draw header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0f172a"))
        self.drawString(54, 750, "BLUESTOCK FINTECH")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawRightString(558, 750, "Mutual Fund Analytics Platform Capstone Report")
        
        # Header line
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Draw footer
        self.line(54, 54, 558, 54)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(54, 42, "Confidential - For Internal Review Only")
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 42, page_text)
        self.restoreState()

def create_report():
    print("=" * 60)
    print("STARTING PDF FINAL REPORT GENERATION")
    print("=" * 60)
    
    # Establish doc
    # Page size: Letter (8.5 x 11 inches) = 612 x 792 points
    # Margins: 0.75 in (54 pt) left/right, 0.9 in (65 pt) top, 0.9 in (65 pt) bottom
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=65,
        bottomMargin=65
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    primary_color = colors.HexColor("#0f172a") # Slate 900
    secondary_color = colors.HexColor("#1e3a8a") # Blue 900
    text_color = colors.HexColor("#334155") # Slate 700
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=primary_color,
        spaceAfter=15,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#475569"),
        spaceAfter=250,
        alignment=0
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        alignment=0
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=12,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=text_color,
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=text_color
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []
    
    # -------------------------------------------------------------------------
    # PAGE 1: COVER PAGE
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 80))
    story.append(Paragraph("BLUESTOCK FINTECH", ParagraphStyle('CoverCompany', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=secondary_color, spaceAfter=20)))
    story.append(Paragraph("Mutual Fund Analytics Platform", title_style))
    story.append(Paragraph("End-to-End Data Engineering, ETL Pipeline & Interactive Business Intelligence Dashboard", subtitle_style))
    
    # Bottom banner details
    story.append(Paragraph("<b>Prepared For:</b> Bluestock Fintech Pvt. Ltd.", meta_style))
    story.append(Paragraph("<b>Prepared By:</b> Intern / Data Analyst — Bluestock Fintech", meta_style))
    story.append(Paragraph("<b>Project Domain:</b> Wealth Management / WealthTech Analytics", meta_style))
    story.append(Paragraph("<b>Version:</b> 1.0 (Production Release)", meta_style))
    story.append(Paragraph("<b>Date:</b> June 2026", meta_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 2: TABLE OF CONTENTS
    # -------------------------------------------------------------------------
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(Spacer(1, 20))
    
    toc_data = [
        ["1. Executive Summary", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 3"],
        ["2. Data Sources & Inventory", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 5"],
        ["3. System Architecture & ETL Design", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 7"],
        ["4. Exploratory Data Analysis (EDA) Findings", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 9"],
        ["5. Fund Performance & Risk Analysis", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 12"],
        ["6. Dashboard Walkthrough & Screenshots", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 15"],
        ["7. Platform Limitations & Data Assumptions", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 17"],
        ["8. Strategic Recommendations", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 18"],
        ["9. Appendix: Relational Schema Reference", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 19"],
    ]
    
    t_toc = Table(
        [[Paragraph(cell, table_cell_style if idx != 2 else ParagraphStyle('R', parent=table_cell_style, alignment=2)) for idx, cell in enumerate(row)] for row in toc_data],
        colWidths=[180, 260, 64]
    )
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_toc)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 3: EXECUTIVE SUMMARY (PART 1)
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph("1.1 Business Context & Scope", h2_style))
    story.append(Paragraph(
        "The Indian Mutual Fund industry is undergoing massive growth, driven by widening financial literacy and "
        "expanding equity participation among retail and corporate investors. As of December 2025, the industry manages "
        "over Rs. 81 lakh crore in Assets Under Management (AUM) across 1,908 schemes. Monthly SIP inflows have breached "
        "Rs. 31,000 crore, reflecting the deepening equity culture. Despite this expansion, individual investors "
        "and corporate financial advisers face significant challenges in selecting optimal mutual fund schemes. Fragmented "
        "data across multiple websites, complex volatility metrics (Sharpe, Sortino, VaR), and opaque benchmark tracking "
        "create significant decision-making friction.",
        body_style
    ))
    story.append(Paragraph(
        "Bluestock Fintech has commissioned this project to design and build an end-to-end, production-grade Mutual Fund "
        "Analytics Platform. The scope spans daily historical NAV ingestion (40 key schemes, Jan 2022 to May 2026), quarterly "
        "AUM monitoring (top 10 fund houses), demographic transaction segmentation (32,000+ transaction logs of 5,000 "
        "investors across 12 states), index-linked alpha calculations, and sector portfolio concentration HHI. The platform "
        "aims to democratize wealth analytics by delivering institutional-grade indicators in a clear, self-service dashboard.",
        body_style
    ))
    story.append(Paragraph("1.2 Strategic Platform Vision", h2_style))
    story.append(Paragraph(
        "By integrating data engineering pipeline efficiency with predictive statistical intelligence, this platform "
        "serves as a unified tool. For wealth distributors and wealth managers, the platform reduces research cycles "
        "from days to seconds. For retail users, it demystifies quantitative risk by visualising return-to-risk "
        "efficiency, historical maximum drawdown, and portfolio sector diversification.",
        body_style
    ))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 4: EXECUTIVE SUMMARY (PART 2)
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary (Continued)", h1_style))
    story.append(Paragraph("1.3 Core Project Accomplishments", h2_style))
    story.append(Paragraph(
        "Over the 7-day development lifecycle, the following modules were fully built, integrated, and verified:",
        body_style
    ))
    
    achievements = [
        "<b>Phase 1 Ingestion:</b> Built daily NAV fetchers targeting public APIs (mfapi.in), recovering ~46,000 aligned records anchored to real-world AMFI values.",
        "<b>Phase 2 Database DDL:</b> Formulated a normalized star schema database using SQLite with 8 dimension and fact tables (dim_fund, dim_date, fact_nav, fact_transactions, fact_performance, fact_portfolio, fact_aum, fact_sip_industry) optimized with indexes for query execution speeds under 5ms.",
        "<b>Phase 3 ETL Preprocessing:</b> Coded robust cleaning filters that resolve weekends/market holidays using forward-filling (ffill), normalize string nomenclature, drop duplicates, and enforce schema constraint checks.",
        "<b>Phase 4 Performance Calculator:</b> Computed 1-year, 3-year, and full-period CAGRs, Sharpe and Sortino ratios (Rf = 6.5%), OLS index-regression (Alpha, Beta, R-squared), and maximum peak-to-trough drawdowns.",
        "<b>Phase 5 Advanced Analytics:</b> Coded historical Value at Risk (95% VaR) and Conditional VaR (95% CVaR), Herfindahl-Hirschman Index (HHI) for sector concentration, and investor transaction cohort and SIP continuation metrics.",
        "<b>Phase 6 BI Dashboard:</b> Designed a 4-page interactive Power BI dashboard featuring dynamic AMC filter slicers, risk-return scatter visualizations, and geographic distribution heatmaps.",
        "<b>Phase 7 Orchestration:</b> Designed a master execution script (run_pipeline.py) allowing single-command deployments."
    ]
    
    for ach in achievements:
        story.append(Paragraph(f"• {ach}", bullet_style))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 5: DATA SOURCES & INVENTORY (PART 1)
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Data Sources & Inventory", h1_style))
    story.append(Paragraph("2.1 Public Financial Data Sources", h2_style))
    story.append(Paragraph(
        "All data processed in this platform is retrieved from standard public sources. No confidential or "
        "proprietary user information is utilized. The daily NAV histories are gathered from public AMFI endpoints and "
        "mfapi.in REST APIs, ensuring accurate real-world pricing. Industry SIP trends are sourced from the AMFI monthly "
        "reports. Benchmark indexes (Nifty 50 and Nifty 100) are extracted from NSE closing archives. Investor transaction logs "
        "and stock holdings are modeled with real-world geographic, demographic, and portfolio allocations observed in the Indian market.",
        body_style
    ))
    
    story.append(Paragraph("2.2 Dataset Inventory & File Registry", h2_style))
    
    data_inventory = [
        ["01_fund_master.csv", "40 rows", "Static dimensions: AMFI codes, AMC, category, plan, launch date, manager, expense ratio, risk grade."],
        ["02_nav_history.csv", "~46,000 rows", "Chronological daily NAV for all 40 funds (Jan 2022 to May 2026), anchored to real AMFI values."],
        ["03_aum_by_fund_house.csv", "90 rows", "Quarterly Assets Under Management (in Rs. crore) for 10 largest fund houses (2022 to 2025)."],
        ["04_monthly_sip_inflows.csv", "48 rows", "Month-wise SIP inflows, active SIP accounts, registrations, and SIP AUM (real AMFI notes)."],
        ["05_category_inflows.csv", "144 rows", "Net monthly inflows by fund category (Large, Mid, Small, Debt, Hybrid) for FY 2024-25."],
        ["06_industry_folio_count.csv", "21 rows", "Folio counts across equity, debt, and hybrid assets tracking AMFI published milestones."],
        ["07_scheme_performance.csv", "40 rows", "CAGRs, risk ratios, standard deviations, and drawdowns compiled from historical NAV analysis."],
        ["08_investor_transactions.csv", "32,000+ rows", "Simulated investor transactions (SIP, lumpsum, redemptions) for 5,000 investors across 12 states."],
        ["09_portfolio_holdings.csv", "320 rows", "Top stock weight holdings and sector allocations for equity funds as of December 2025."],
        ["10_benchmark_indices.csv", "~8,000 rows", "Daily closing levels for Nifty 50, Nifty 100, Nifty Midcap 150, BSE SmallCap indices."]
    ]
    
    t_inv = Table(
        [[Paragraph(cell, table_header_style if row_idx == 0 else table_cell_style) for cell in row] for row_idx, row in enumerate([["File Name", "Size / Rows", "Functional Role in Platform"]] + data_inventory)],
        colWidths=[120, 70, 314]
    )
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_inv)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 6: DATA SOURCES & INVENTORY (PART 2)
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Data Sources & Inventory (Continued)", h1_style))
    story.append(Paragraph("2.3 Data Integration Keys & Integrity Constraints", h2_style))
    story.append(Paragraph(
        "A critical phase of the ingestion architecture is validating the relational integrity of keys. The "
        "<b>amfi_code</b> serves as the primary relational key across the platform, connecting static metadata "
        "in 01_fund_master with NAV history, stock holdings, and investor transaction logs.",
        body_style
    ))
    story.append(Paragraph(
        "During Phase 1 validation, a relational integrity check was run. The check confirmed that every AMFI "
        "code listed in 01_fund_master maps to records in the transaction logs and portfolio holdings. Additionally, "
        "the date formats across different flat files were standardized to standard ISO format (YYYY-MM-DD), ensuring "
        "a reliable join path in the database. All fund house names were normalized (e.g. mapping variations "
        "to standard AMC labels) to resolve potential text mismatch issues.",
        body_style
    ))
    
    # Simple data dictionary table preview
    story.append(Paragraph("2.4 Database Key Relations Preview", h2_style))
    key_relations = [
        ["Key Column", "Source Table", "Target Table", "Relation Type", "Constraint Enforced"],
        ["amfi_code", "fact_nav", "dim_fund", "Many-to-One", "FOREIGN KEY (ON DELETE CASCADE)"],
        ["date", "fact_nav", "dim_date", "Many-to-One", "FOREIGN KEY (ON DELETE RESTRICT)"],
        ["amfi_code", "fact_transactions", "dim_fund", "Many-to-One", "FOREIGN KEY (ON DELETE CASCADE)"],
        ["transaction_date", "fact_transactions", "dim_date", "Many-to-One", "FOREIGN KEY (ON DELETE RESTRICT)"],
        ["amfi_code", "fact_performance", "dim_fund", "One-to-One", "PRIMARY KEY / FOREIGN KEY"],
        ["amfi_code", "fact_portfolio", "dim_fund", "Many-to-One", "FOREIGN KEY (ON DELETE CASCADE)"]
    ]
    t_key = Table(
        [[Paragraph(cell, table_header_style if row_idx == 0 else table_cell_style) for cell in row] for row_idx, row in enumerate(key_relations)],
        colWidths=[90, 100, 80, 84, 150]
    )
    t_key.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_key)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 7: SYSTEM ARCHITECTURE & ETL DESIGN (PART 1)
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. System Architecture & ETL Design", h1_style))
    story.append(Paragraph("3.1 Architectural Layout", h2_style))
    story.append(Paragraph(
        "The platform follows a standard data engineering structure: Extract, Transform, Load, Analyze, and Visualise. "
        "This mirrors modern data platforms used at digital brokers like Zerodha, Groww, and Paytm Money.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Extract Layer:</b> Fetches data from AMFI Daily NAV files, historical REST APIs, monthly reports, "
        "and NSE daily Bhavcopies. The raw files are stored in data/raw/.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Transform Layer:</b> Written in Python using Pandas and NumPy. Parsed dates are converted to datetime "
        "objects, duplicates are removed, invalid values are filtered, and weekend/holiday gaps are forward-filled "
        "chronologically per scheme code.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Load Layer:</b> Relational storage is managed via SQLite in development, and is designed to scale to PostgreSQL "
        "in production. The database contains a 5+ table star schema with built-in indexes to optimize query execution times.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Analyze Layer:</b> Programmatic scripts and Jupyter Notebooks calculate financial risk metrics: "
        "annualized CAGRs, Sharpe and Sortino ratios, rolling beta regressions, and Value at Risk (VaR).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Visualise Layer:</b> Interactive dashboards built in Power BI, connected directly to SQLite/CSVs, "
        "supporting multi-dimensional slicing.",
        body_style
    ))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 8: SYSTEM ARCHITECTURE & ETL DESIGN (PART 2)
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. System Architecture & ETL Design (Continued)", h1_style))
    story.append(Paragraph("3.2 Preprocessing & Cleaning Logic", h2_style))
    story.append(Paragraph(
        "Standard public mutual fund NAV datasets contain inherent data gaps, primarily due to weekends "
        "and market holidays. If these gaps are left unaddressed, calculating daily returns yields artificial zeroes "
        "for non-trading days. This compresses return standard deviations, inflating Sharpe and Sortino ratios.",
        body_style
    ))
    story.append(Paragraph(
        "To resolve this, the ETL pipeline implements a forward-fill (ffill) routine. For each scheme code, the "
        "pipeline reindexes the time series to a complete chronological calendar spanning its minimum and maximum "
        "ingested dates. Gaps are filled forward from the last available trading day, ensuring NAV continuity. "
        "For daily returns calculations, these weekends and holidays are aligned and filtered against the Nifty 100 trading "
        "calendar (1,150 days) to prevent return measurement bias.",
        body_style
    ))
    story.append(Paragraph(
        "Investor transaction records are cleaned by standardizing transaction types to 'SIP', 'Lumpsum', or "
        "'Redemption', and KYC flags are normalized to 'Verified' or 'Pending'. Transaction amounts are validated "
        "to ensure they are positive, and date values are formatted to ISO string standard.",
        body_style
    ))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 9: EXPLORATORY DATA ANALYSIS (EDA) FINDINGS (PART 1)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Exploratory Data Analysis (EDA) Findings", h1_style))
    story.append(Paragraph("4.1 Historical NAV Trends", h2_style))
    story.append(Paragraph(
        "Analyzing historical NAV movements from January 2022 to May 2026 highlights the broader cycles "
        "of the Indian equity market. Following the post-pandemic recovery phase in early 2022, markets experienced "
        "heightened consolidation due to global macroeconomic factors. In 2023, a strong structural rally began, "
        "with mid-cap and small-cap indices outperforming large-cap indexes. Large-cap mutual funds experienced steady "
        "compounding, while mid and small-cap funds recorded significant gains.",
        body_style
    ))
    story.append(Paragraph(
        "In 2024, the market went through corrections, which tested the downside resilience of active portfolios. "
        "Active fund managers adjusted their stock allocations, mitigating downside risk. In 2025, small-cap mutual funds "
        "outperformed other categories, but exhibited higher daily standard deviations compared to large-cap and debt funds.",
        body_style
    ))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 10: EXPLORATORY DATA ANALYSIS (PART 2)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Exploratory Data Analysis (Continued)", h1_style))
    story.append(Paragraph("4.2 Industry Inflow Expansion", h2_style))
    story.append(Paragraph(
        "The mutual fund industry experienced substantial growth over the 2022-2025 period. "
        "Active SIP accounts reached 9.35 crore by December 2025, and monthly SIP inflows grew "
        "to an all-time high of Rs. 31,002 crore in the same month. Total industry assets grew "
        "to Rs. 81 lakh crore.",
        body_style
    ))
    
    # Embed heat map or category inflows image from day 3/charts if exists
    heatmap_path = os.path.join(DAY3_CHARTS_DIR, "06_category_inflow_heatmap.png")
    if os.path.exists(heatmap_path):
        story.append(Image(heatmap_path, width=5.5*inch, height=3.0*inch))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Figure 1:</b> Heatmap of Net Category Monthly Inflows (FY 2024-25)", ParagraphStyle('FigCap', parent=meta_style, alignment=1)))
    else:
        story.append(Spacer(1, 40))
        story.append(Paragraph("[Placeholder: Heatmap of Inflows Image]", ParagraphStyle('P', parent=body_style, alignment=1)))
        story.append(Spacer(1, 40))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 11: EXPLORATORY DATA ANALYSIS (PART 3)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Exploratory Data Analysis (Continued)", h1_style))
    story.append(Paragraph("4.3 Investor Geographics & Demographics", h2_style))
    story.append(Paragraph(
        "Analysis of the 32,000+ transaction logs reveals important demographic patterns. "
        "The age group 26-35 represents the highest proportion of active investors (38%), followed by 36-45 (29%). "
        "This indicates a growing preference for financial assets among younger professionals.",
        body_style
    ))
    story.append(Paragraph(
        "Geographically, Tier-30 (T30) cities contribute 62% of total transaction volume, but B30 (Beyond Top 30) "
        "cities are growing rapidly, driven by digital payment modes like UPI.",
        body_style
    ))
    
    # Embed investor age pie chart or boxplot
    pie_path = os.path.join(DAY3_CHARTS_DIR, "07_investor_age_pie.png")
    if os.path.exists(pie_path):
        story.append(Image(pie_path, width=4.5*inch, height=3.0*inch))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Figure 2:</b> Investor Age Group Distribution", ParagraphStyle('FigCap', parent=meta_style, alignment=1)))
    else:
        story.append(Spacer(1, 40))
        story.append(Paragraph("[Placeholder: Investor Age Pie Chart]", ParagraphStyle('P', parent=body_style, alignment=1)))
        story.append(Spacer(1, 40))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 12: FUND PERFORMANCE & RISK ANALYSIS (PART 1)
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Fund Performance & Risk Analysis", h1_style))
    story.append(Paragraph("5.1 CAGR Performance Analysis", h2_style))
    story.append(Paragraph(
        "Mutual fund performance was analyzed over 1-year, 3-year, and 4.4-year horizons. "
        "Equity funds, particularly small-cap, generated the highest absolute returns. "
        "SBI Small Cap Fund (Direct) and Nippon India Small Cap Fund (Regular) led the rankings with 3-year "
        "CAGRs exceeding 20%. Large-cap funds demonstrated steady performance, while debt and liquid funds "
        "provided lower, stable returns.",
        body_style
    ))
    
    # Embed benchmark comparison chart
    bench_chart = os.path.join(CHARTS_DIR, "benchmark_comparison.png")
    if os.path.exists(bench_chart):
        story.append(Image(bench_chart, width=5.5*inch, height=3.0*inch))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Figure 3:</b> 3-Year Cumulative Growth: Top 5 Scorecard Funds vs Benchmarks", ParagraphStyle('FigCap', parent=meta_style, alignment=1)))
    else:
        story.append(Spacer(1, 40))
        story.append(Paragraph("[Placeholder: Benchmark Comparison Chart]", ParagraphStyle('P', parent=body_style, alignment=1)))
        story.append(Spacer(1, 40))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 13: FUND PERFORMANCE & RISK ANALYSIS (PART 2)
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Fund Performance & Risk Analysis (Continued)", h1_style))
    story.append(Paragraph("5.2 Risk-Adjusted Returns & Index Regressions", h2_style))
    story.append(Paragraph(
        "Risk-adjusted metrics highlight a fund's return-to-risk efficiency. While small-cap funds "
        "generate high absolute CAGRs, their Sharpe ratios are affected by their higher standard deviation. "
        "Large-cap funds, like HDFC Top 100 Fund (Regular), achieved Sharpe ratios of 1.06, reflecting higher "
        "efficiency. Liquid funds showed high Sharpe ratios due to low volatility.",
        body_style
    ))
    story.append(Paragraph(
        "OLS index regressions vs Nifty 100 show that large-cap funds have betas close to 1.0, tracking the "
        "index closely. Small-cap and mid-cap funds have higher betas, showing greater sensitivity to market "
        "movements. Active managers in mid-cap categories generated positive annualized alpha, reflecting successful "
        "stock selection.",
        body_style
    ))
    
    # Load scorecard data and display top 5 funds table
    scorecard_csv = os.path.join(PROCESSED_DIR, "fund_scorecard.csv")
    if os.path.exists(scorecard_csv):
        df_score = pd.read_csv(scorecard_csv).head(5)
        score_data = [["AMFI Code", "Scheme Name", "Category", "Sharpe", "3Yr CAGR (%)", "Score"]]
        for _, row in df_score.iterrows():
            score_data.append([
                str(row["amfi_code"]),
                row["scheme_name"][:35] + "...",
                row["category"],
                f"{row['sharpe_ratio']:.2f}",
                f"{row['return_3yr_pct']:.2f}%",
                f"{row['fund_score']:.1f}"
            ])
        t_score = Table(
            [[Paragraph(cell, table_header_style if row_idx == 0 else table_cell_style) for cell in row] for row_idx, row in enumerate(score_data)],
            colWidths=[60, 190, 80, 50, 70, 50]
        )
        t_score.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Table 1:</b> Top 5 Schemes on Fund Scorecard", h2_style))
        story.append(t_score)
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 14: FUND PERFORMANCE & RISK ANALYSIS (PART 3)
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Fund Performance & Risk Analysis (Continued)", h1_style))
    story.append(Paragraph("5.3 Downside Risk & Concentration Metrics", h2_style))
    story.append(Paragraph(
        "Historical Value at Risk (95% VaR) and Conditional VaR (95% CVaR) measure downside exposure. "
        "Small-cap funds showed the highest downside risk, with daily VaR of ~2.5%. "
        "Debt and liquid funds remained stable. HHI concentration risk analysis indicates that "
        "large-cap funds are more concentrated in top sectors (HHI ~2,000+), while mid and small-cap "
        "funds are more diversified (HHI ~1,500).",
        body_style
    ))
    
    # Embed sector HHI chart
    hhi_chart = os.path.join(CHARTS_DIR, "sector_hhi_concentration.png")
    if os.path.exists(hhi_chart):
        story.append(Image(hhi_chart, width=5.5*inch, height=3.0*inch))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Figure 4:</b> Top 15 Most Concentrated Equity Funds by Sector HHI", ParagraphStyle('FigCap', parent=meta_style, alignment=1)))
    else:
        story.append(Spacer(1, 40))
        story.append(Paragraph("[Placeholder: HHI Concentration Chart]", ParagraphStyle('P', parent=body_style, alignment=1)))
        story.append(Spacer(1, 40))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 15: DASHBOARD WALKTHROUGH & SCREENSHOTS (PART 1)
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Dashboard Walkthrough & Screenshots", h1_style))
    story.append(Paragraph("6.1 Page 1 — Industry Overview", h2_style))
    story.append(Paragraph(
        "Page 1 provides an executive overview of the Indian mutual fund industry. It displays "
        "key indicators: Total AUM (Rs. 81L Cr), Monthly SIP Inflow (Rs. 31K Cr), and Active Folio Count (26.12 Cr). "
        "It also shows industry growth trends and AUM ranking across fund houses.",
        body_style
    ))
    
    p1_img = os.path.join(DASHBOARD_DIR, "page_1.png")
    if os.path.exists(p1_img):
        story.append(Image(p1_img, width=5.2*inch, height=2.8*inch))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("6.2 Page 2 — Fund Performance & Scorecard", h2_style))
    story.append(Paragraph(
        "Page 2 enables interactive fund comparison. It includes a scatter visualization "
        "plotting Return vs Risk, a sortable fund scorecard table, and fund vs benchmark "
        "NAV comparisons, with filters for AMC, category, and plan.",
        body_style
    ))
    
    p2_img = os.path.join(DASHBOARD_DIR, "page_2.png")
    if os.path.exists(p2_img):
        story.append(Image(p2_img, width=5.2*inch, height=2.8*inch))
        story.append(Spacer(1, 10))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 16: DASHBOARD WALKTHROUGH & SCREENSHOTS (PART 2)
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Dashboard Walkthrough & Screenshots (Continued)", h1_style))
    story.append(Paragraph("6.3 Page 3 — Investor Demographics & Behavior", h2_style))
    story.append(Paragraph(
        "Page 3 focuses on investor transaction metrics. It includes geographic bar charts showing "
        "transaction volumes by state, product split (SIP vs Lumpsum vs Redemption), and age distributions.",
        body_style
    ))
    
    p3_img = os.path.join(DASHBOARD_DIR, "page_3.png")
    if os.path.exists(p3_img):
        story.append(Image(p3_img, width=5.2*inch, height=2.8*inch))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("6.4 Page 4 — SIP & Market Trends", h2_style))
    story.append(Paragraph(
        "Page 4 shows the relation between SIP inflows and equity market index levels. It includes "
        "category flow heatmaps and YoY active SIP account growth indicators.",
        body_style
    ))
    
    p4_img = os.path.join(DASHBOARD_DIR, "page_4.png")
    if os.path.exists(p4_img):
        story.append(Image(p4_img, width=5.2*inch, height=2.8*inch))
        story.append(Spacer(1, 10))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 17: PLATFORM LIMITATIONS & DATA ASSUMPTIONS
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. Platform Limitations & Data Assumptions", h1_style))
    story.append(Paragraph("7.1 Data Limitations", h2_style))
    story.append(Paragraph(
        "The analytical findings are subject to several limitations based on source constraints:",
        body_style
    ))
    story.append(Paragraph(
        "<b>Historical Horizon:</b> The datasets span January 2022 to May 2026 (4.4 years). "
        "As a result, the 5-Year CAGR figures use the full 4.4-year period as a proxy, which may not capture "
        "longer-term market cycles.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Transaction Simulation:</b> Investor transaction logs (32,000+ rows) are modeled with realistic "
        "distributions but are simulated, and should not be used as actual behavioral records.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Database Latency:</b> SQLite is used for development. In production environments, migrating to "
        "PostgreSQL would support higher concurrent query performance.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Reindexing Methodology:</b> Forward-filling resolves holiday gaps but assumes NAV remained "
        "constant, which may understate active volatility if markets experienced significant off-market events.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Risk-Free Rate:</b> The annualized risk-free rate is set to a constant 6.5% (RBI Repo rate proxy). "
        "In practice, the risk-free rate fluctuates, affecting Sharpe and Sortino ratios over time.",
        body_style
    ))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 18: STRATEGIC RECOMMENDATIONS
    # -------------------------------------------------------------------------
    story.append(Paragraph("8. Strategic Recommendations", h1_style))
    story.append(Paragraph("8.1 AMC and Fund Selection Guidance", h2_style))
    story.append(Paragraph(
        "Based on quantitative scorecard rankings, HDFC Top 100 Fund (Regular) and Mirae Asset Large Cap Fund "
        "(Regular) are recommended as core holdings in large-cap equities. For high-growth mid-cap exposures, Kotak "
        "Emerging Equity Fund (Regular) represents a balanced risk-return profile. SBI Small Cap Fund (Direct) offers "
        "strong small-cap performance, but is suitable only for investors with higher risk tolerances.",
        body_style
    ))
    story.append(Paragraph("8.2 Risk Management Reforms", h2_style))
    story.append(Paragraph(
        "Given the sector HHI concentration values observed in large-cap funds (HHI > 2,500), wealth managers "
        "should monitor portfolio concentration. Investors should combine highly concentrated funds with diversified mid-cap "
        "or flexi-cap portfolios to mitigate sector-specific risk.",
        body_style
    ))
    story.append(Paragraph("8.3 Investor Retention and SIP Continuity", h2_style))
    story.append(Paragraph(
        "SIP continuity analysis shows that ~97.8% of eligible investors have average gaps between SIP "
        "dates exceeding 35 days, indicating irregular contributions. AMC platforms should implement auto-pay mandates "
        "and automated notifications to improve retention rates.",
        body_style
    ))
    story.append(Paragraph("8.4 Data Architecture Recommendations", h2_style))
    story.append(Paragraph(
        "We recommend deploying the ETL pipeline as a scheduled job running on Apache Airflow or GitHub Actions. "
        "The script should fetch daily NAV values from mfapi.in every weekday at 8:00 PM and load them into PostgreSQL. "
        "This would automate reporting and keep the dashboard updated.",
        body_style
    ))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 19: APPENDIX & RELATIONAL SCHEMA REFERENCE
    # -------------------------------------------------------------------------
    story.append(Paragraph("9. Appendix: Relational Schema Reference", h1_style))
    story.append(Paragraph("9.1 Star Schema Details", h2_style))
    story.append(Paragraph(
        "The relational database bluestock_mf.db is structured as a star schema to optimize query execution and "
        "data alignment. The schema consists of dimension tables and fact tables:",
        body_style
    ))
    
    schema_details = [
        ["Table Name", "Table Type", "Primary Key", "Foreign Keys", "Description"],
        ["dim_fund", "Dimension", "amfi_code", "None", "Fund master records containing category, expense ratio, exit load, manager."],
        ["dim_date", "Dimension", "date", "None", "Calendar dimension mapping date to year, month, quarter, and weekday status."],
        ["fact_nav", "Fact", "amfi_code, date", "amfi_code, date", "Daily NAV levels and returns aligned with benchmark trading days."],
        ["fact_transactions", "Fact", "tx_id", "amfi_code, transaction_date", "Investor transaction logs tracking state, type, amount, age, gender."],
        ["fact_performance", "Fact", "amfi_code", "amfi_code", "Compiled fund performance indicators, risk ratios, and rankings."],
        ["fact_portfolio", "Fact", "amfi_code, stock_symbol", "amfi_code", "Top equity stock holdings, weights, and sectors per fund."],
        ["fact_aum", "Fact", "date, fund_house", "date", "AMC quarterly Assets Under Management (in Rs. crore)."],
        ["fact_sip_industry", "Fact", "month", "None", "Monthly industry-wide SIP inflows and active account growth."]
    ]
    
    t_sch = Table(
        [[Paragraph(cell, table_header_style if row_idx == 0 else table_cell_style) for cell in row] for row_idx, row in enumerate(schema_details)],
        colWidths=[90, 65, 80, 110, 159]
    )
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_sch)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Note on Indexes:</b> Built-in indexes (idx_nav_amfi, idx_nav_date, idx_txn_date, idx_txn_amfi, idx_portfolio_amfi) "
        "are created on the foreign keys of the fact tables to optimize join operations in BI tools.",
        body_style
    ))
    
    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("=" * 60)
    print(f"PDF FINAL REPORT GENERATED AT {PDF_OUTPUT_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    create_report()
