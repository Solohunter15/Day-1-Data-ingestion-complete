# Day 5: Interactive Dashboard Development
### Relational Star Schema BI Dashboard & Python Web Deployment

This directory contains the deliverables for **Day 5** of the Bluestock Capstone Project. It focuses on connecting the cleaned Star Schema database and CSV files to an interactive BI dashboard environment, implementing standard fintech key metrics and layouts, and deploying a local web server to make the application accessible.

---

## 📁 Day 5 Deliverables & Folder Structure

All assets, screenshots, scripts, and compiled files for Day 5 are organized here:

```text
day 5/
├── Dashboard.pdf                         # Combined 4-page exported report
├── page_1.png                            # Page 1: Industry Overview Screenshot
├── page_2.png                            # Page 2: Fund Performance Screenshot
├── page_3.png                            # Page 3: Investor Analytics Screenshot
├── page_4.png                            # Page 4: SIP & Market Trends Screenshot
│
├── dashboard/                            # Core dashboard scripts & application
│   ├── dashboard_app.py                  # Live Streamlit python web application
│   ├── export_dashboard.py              # Automated Playwright PDF/screenshot compiler
│   ├── generate_pbip.py                  # Power BI project folder structure generator
│   └── compile_pbix.ps1                  # PowerShell script for Power BI Desktop save-as
│
├── bluestock_mf_dashboard.pbix.pbip      # Power BI developer project descriptor
├── bluestock_mf_dashboard.pbix.Report/   # Power BI visual definition files
└── bluestock_mf_dashboard.pbix.SemanticModel/ # Power BI relational data model
```

---

## 🖥️ Web App Dashboard Pages

The web application (Streamlit) contains the following fully interactive pages:

1. **🏢 Industry Overview**:
   - **KPI Cards**: Total AUM (₹81L Cr), Monthly SIP Inflows (₹31,002 Cr), Total Folios (26.12 Cr), Active Schemes (1,908).
   - **Line Chart**: Industry AUM Growth Trend (2022–2025).
   - **Bar Chart**: AUM Distribution by Asset Management Company (AMC).

2. **📈 Fund Performance**:
   - **Scatter Plot**: Return (X) vs Risk/StdDev (Y) colored by risk grade with bubble size proportional to AUM.
   - **Interactive Table**: Sortable fund scorecard table.
   - **Slicers**: Interactive selectors for AMC, Category, and Plan Type.

3. **👥 Investor Analytics**:
   - **Horizontal Bar**: Transaction Volume by Indian State.
   - **Donut Chart**: Transaction Type split (SIP vs Lumpsum vs Redemption).
   - **Vertical Bar**: Age Group vs Average SIP Ticket Size.
   - **Line Chart**: Monthly Transaction Volume Trend.
   - **Slicers**: Filter by State, Age Group, and City Tier.

4. **🔥 SIP & Market Trends**:
   - **Dual-Axis Chart**: Monthly SIP Inflow (Bar) vs Nifty 50 Close (Line) from 2022 to 2025.
   - **Heatmap**: Monthly Category Inflow splits.
   - **Bar Chart**: Top 5 Categories by Net Inflow.
   - **KPI Cards**: YoY growth of active SIP accounts (17.17% in Dec 2025).

5. **🔍 Fund Deep-Dive (Drill-Through)**:
   - Deep-dive for selected schemes showing normalized NAV vs. Nifty 50 benchmark (Base 100) and sector concentration weights.

---

## 🚀 Running the Web App

To start the interactive web application, run the following command from your terminal:

```bash
python -m streamlit run "day 5/dashboard/dashboard_app.py" --server.port 8501
```

Once started, open your browser and navigate to:
**[http://localhost:8501](http://localhost:8501)**
