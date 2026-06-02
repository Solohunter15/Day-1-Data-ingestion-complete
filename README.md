# Mutual Fund Analytics

This repository houses the **Mutual Fund Analytics** Capstone Project, developed as part of the Bluestock Fintech Internship program. 

The project focuses on creating an end-to-end data pipeline (ETL) and analytics system to ingest, clean, store, and visualize Indian Mutual Fund datasets.

---

## 📁 Repository Directory Structure

```text
Bluestock Internship/
│
├── data/
│   ├── raw/             # Ingested raw datasets (local CSVs + live fetched CSVs)
│   └── processed/       # Downstream transformed datasets (Day 2)
│
├── notebooks/           # Jupyter/Colab staging workspace
├── sql/                 # PostgreSQL table schemas and staging queries
├── dashboard/           # Visual analytics and UI config staging
├── reports/             # Detailed reports & data quality summaries
│   └── day1_data_quality_summary.md
│
├── data_ingestion.py    # Local ETL bootstrapping, loading, & validation pipeline
├── live_nav_fetch.py    # Live NAV scraper from mfapi.in
├── requirements.txt     # Python package dependencies
└── README.md            # Project documentation index
```

---

## 🚀 Day 1 Ingestion Workflow & Setup

### 1. Prerequisites & Installation
Ensure you have Python 3.8+ installed on your system. 

Install the required Python libraries using the unified package configuration:
```bash
pip install -r requirements.txt
```

### 2. Running Local ETL & Data Ingestion
The file `data_ingestion.py` acts as the ingestion pipeline. To facilitate immediate local execution without external file dependencies, it features an automated bootstrap generator. On first run, it generates 10 realistic raw CSV datasets inside `data/raw/` and outputs file metrics:

To run the local ingestion and explore statistics:
```bash
python data_ingestion.py
```

This will output:
*   File shape, dtypes, and head preview for all 10 raw CSVs.
*   Explorer dimensions (unique AMC, categories, sub-categories, risk grades).
*   Detected anomalies (missing values, duplicated transaction rows, type anomalies).
*   AMFI relational consistency check (referential integrity between `fund_master` and `nav_history`).

### 3. Fetching Live NAV Data
To scrap real-time daily Net Asset Values (NAV) for target schemes from the free public API `mfapi.in`, run the fetcher:
```bash
python live_nav_fetch.py
```

This fetches daily historical NAV, fund house, and scheme metadata for:
1.  **HDFC Top 100 Direct** (125497)
2.  **SBI Bluechip** (119551)
3.  **ICICI Bluechip** (120503)
4.  **Nippon Large Cap** (118632)
5.  **Axis Bluechip** (119092)
6.  **Kotak Bluechip** (120841)

All live data is parsed from JSON and written as structured raw CSV files inside `data/raw/`.

---

## 📈 Quality & Validation Reports
For a deep dive into the ingested dataset profiles, relational code mismatches, and data cleanliness reports, check out:
*   [Day 1 Data Quality Summary](file:///C:/Users/jibum/OneDrive/Desktop/Bluestock%20Internship/reports/day1_data_quality_summary.md)
