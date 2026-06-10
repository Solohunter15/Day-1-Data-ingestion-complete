import os
import json
import uuid

# Define base paths
BASE_DIR = r"c:\Users\jibum\OneDrive\Desktop\Bluestock Internship"
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
PBIP_DIR = os.path.join(DASHBOARD_DIR, "bluestock_mf_dashboard.pbip")
REPORT_DIR = os.path.join(DASHBOARD_DIR, "bluestock_mf_dashboard.Report")
MODEL_DIR = os.path.join(DASHBOARD_DIR, "bluestock_mf_dashboard.SemanticModel")
CSV_DIR = os.path.join(BASE_DIR, "day 2", "data", "processed").replace("\\", "\\\\")

def create_pbip_structure():
    # Create directories
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 1. Write bluestock_mf_dashboard.pbip pointer file (nested in artifacts)
    pbip_content = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "bluestock_mf_dashboard.Report"
                }
            }
        ],
        "settings": {
            "enableAutoRecovery": True
        }
    }
    with open(os.path.join(DASHBOARD_DIR, "bluestock_mf_dashboard.pbip"), "w") as f:
        json.dump(pbip_content, f, indent=2)
        
    # 2. Write Report/definition.pbir
    pbir_content = {
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": "../bluestock_mf_dashboard.SemanticModel"
            }
        }
    }
    with open(os.path.join(REPORT_DIR, "definition.pbir"), "w") as f:
        json.dump(pbir_content, f, indent=2)
        
    # 3. Write Report/item.config.json bypassed to prevent conflict with .platform
        
    # 4. Write SemanticModel/definition.pbism
    pbism_content = {
        "version": "1.0",
        "settings": {}
    }
    with open(os.path.join(MODEL_DIR, "definition.pbism"), "w") as f:
        json.dump(pbism_content, f, indent=2)
        
    # 5. Write SemanticModel/item.config.json bypassed to prevent conflict with .platform
        
    # 6. Write SemanticModel/model.bim containing tables, columns, and relationships
    model_bim = {
        "name": "bluestock_mf_dashboard",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-IN",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "fastCombine": True
            },
            "defaultPowerBIDataSourceVersion": "PowerBI_V3",
            "sourceQueryCulture": "en-IN",
            "relationships": [
                {
                    "name": "rel_fund_nav",
                    "fromTable": "fact_nav",
                    "fromColumn": "amfi_code",
                    "toTable": "dim_fund",
                    "toColumn": "amfi_code"
                },
                {
                    "name": "rel_fund_transactions",
                    "fromTable": "fact_transactions",
                    "fromColumn": "amfi_code",
                    "toTable": "dim_fund",
                    "toColumn": "amfi_code"
                },
                {
                    "name": "rel_fund_performance",
                    "fromTable": "fact_performance",
                    "fromColumn": "amfi_code",
                    "toTable": "dim_fund",
                    "toColumn": "amfi_code"
                },
                {
                    "name": "rel_fund_portfolio",
                    "fromTable": "fact_portfolio",
                    "fromColumn": "amfi_code",
                    "toTable": "dim_fund",
                    "toColumn": "amfi_code"
                },
                {
                    "name": "rel_date_nav",
                    "fromTable": "fact_nav",
                    "fromColumn": "date",
                    "toTable": "dim_date",
                    "toColumn": "date"
                },
                {
                    "name": "rel_date_transactions",
                    "fromTable": "fact_transactions",
                    "fromColumn": "date",
                    "toTable": "dim_date",
                    "toColumn": "date"
                },
                {
                    "name": "rel_date_aum",
                    "fromTable": "fact_aum",
                    "fromColumn": "date",
                    "toTable": "dim_date",
                    "toColumn": "date"
                }
            ],
            "tables": [
                {
                    "name": "dim_fund",
                    "columns": [
                        {"name": "amfi_code", "dataType": "int64", "sourceColumn": "amfi_code"},
                        {"name": "fund_house", "dataType": "string", "sourceColumn": "fund_house"},
                        {"name": "scheme_name", "dataType": "string", "sourceColumn": "scheme_name"},
                        {"name": "category", "dataType": "string", "sourceColumn": "category"},
                        {"name": "sub_category", "dataType": "string", "sourceColumn": "sub_category"},
                        {"name": "plan", "dataType": "string", "sourceColumn": "plan"},
                        {"name": "launch_date", "dataType": "string", "sourceColumn": "launch_date"},
                        {"name": "benchmark", "dataType": "string", "sourceColumn": "benchmark"},
                        {"name": "expense_ratio_pct", "dataType": "double", "sourceColumn": "expense_ratio_pct"},
                        {"name": "exit_load_pct", "dataType": "double", "sourceColumn": "exit_load_pct"},
                        {"name": "min_sip_amount", "dataType": "int64", "sourceColumn": "min_sip_amount"},
                        {"name": "min_lumpsum_amount", "dataType": "int64", "sourceColumn": "min_lumpsum_amount"},
                        {"name": "fund_manager", "dataType": "string", "sourceColumn": "fund_manager"},
                        {"name": "risk_category", "dataType": "string", "sourceColumn": "risk_category"},
                        {"name": "sebi_category_code", "dataType": "string", "sourceColumn": "sebi_category_code"}
                    ],
                    "partitions": [
                        {
                            "name": "dim_fund-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\01_fund_master.csv"),[Delimiter=",", Columns=15, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{{\"amfi_code\", Int64.Type}, {\"expense_ratio_pct\", type number}, {\"exit_load_pct\", type number}, {\"min_sip_amount\", Int64.Type}, {\"min_lumpsum_amount\", Int64.Type}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "dim_date",
                    "columns": [
                        {"name": "date", "dataType": "string", "sourceColumn": "date"},
                        {"name": "year", "dataType": "int64", "sourceColumn": "year"},
                        {"name": "month", "dataType": "int64", "sourceColumn": "month"},
                        {"name": "quarter", "dataType": "int64", "sourceColumn": "quarter"},
                        {"name": "is_weekday", "dataType": "int64", "sourceColumn": "is_weekday"}
                    ],
                    "partitions": [
                        {
                            "name": "dim_date-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\dim_date.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{{\"year\", Int64.Type}, {\"month\", Int64.Type}, {\"quarter\", Int64.Type}, {\"is_weekday\", Int64.Type}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "fact_nav",
                    "columns": [
                        {"name": "date", "dataType": "string", "sourceColumn": "date"},
                        {"name": "amfi_code", "dataType": "int64", "sourceColumn": "amfi_code"},
                        {"name": "nav", "dataType": "double", "sourceColumn": "nav"}
                    ],
                    "partitions": [
                        {
                            "name": "fact_nav-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\02_nav_history.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{{\"amfi_code\", Int64.Type}, {\"nav\", type number}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "fact_transactions",
                    "columns": [
                        {"name": "investor_id", "dataType": "string", "sourceColumn": "investor_id"},
                        {"name": "date", "dataType": "string", "sourceColumn": "date"},
                        {"name": "amfi_code", "dataType": "int64", "sourceColumn": "amfi_code"},
                        {"name": "transaction_type", "dataType": "string", "sourceColumn": "transaction_type"},
                        {"name": "amount_inr", "dataType": "int64", "sourceColumn": "amount_inr"},
                        {"name": "state", "dataType": "string", "sourceColumn": "state"},
                        {"name": "city", "dataType": "string", "sourceColumn": "city"},
                        {"name": "city_tier", "dataType": "string", "sourceColumn": "city_tier"},
                        {"name": "age_group", "dataType": "string", "sourceColumn": "age_group"},
                        {"name": "gender", "dataType": "string", "sourceColumn": "gender"},
                        {"name": "annual_income_lakh", "dataType": "double", "sourceColumn": "annual_income_lakh"},
                        {"name": "payment_mode", "dataType": "string", "sourceColumn": "payment_mode"},
                        {"name": "kyc_status", "dataType": "string", "sourceColumn": "kyc_status"}
                    ],
                    "partitions": [
                        {
                            "name": "fact_transactions-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\08_investor_transactions.csv"),[Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Renamed Columns\" = Table.RenameColumns(#\"Promoted Headers\",{{\"transaction_date\", \"date\"}}),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Renamed Columns\",{{\"amfi_code\", Int64.Type}, {\"amount_inr\", Int64.Type}, {\"annual_income_lakh\", type number}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "fact_performance",
                    "columns": [
                        {"name": "amfi_code", "dataType": "int64", "sourceColumn": "amfi_code"},
                        {"name": "scheme_name", "dataType": "string", "sourceColumn": "scheme_name"},
                        {"name": "fund_house", "dataType": "string", "sourceColumn": "fund_house"},
                        {"name": "category", "dataType": "string", "sourceColumn": "category"},
                        {"name": "plan", "dataType": "string", "sourceColumn": "plan"},
                        {"name": "return_1yr_pct", "dataType": "double", "sourceColumn": "return_1yr_pct"},
                        {"name": "return_3yr_pct", "dataType": "double", "sourceColumn": "return_3yr_pct"},
                        {"name": "return_5yr_pct", "dataType": "double", "sourceColumn": "return_5yr_pct"},
                        {"name": "benchmark_3yr_pct", "dataType": "double", "sourceColumn": "benchmark_3yr_pct"},
                        {"name": "alpha", "dataType": "double", "sourceColumn": "alpha"},
                        {"name": "beta", "dataType": "double", "sourceColumn": "beta"},
                        {"name": "sharpe_ratio", "dataType": "double", "sourceColumn": "sharpe_ratio"},
                        {"name": "sortino_ratio", "dataType": "double", "sourceColumn": "sortino_ratio"},
                        {"name": "std_dev_ann_pct", "dataType": "double", "sourceColumn": "std_dev_ann_pct"},
                        {"name": "max_drawdown_pct", "dataType": "double", "sourceColumn": "max_drawdown_pct"},
                        {"name": "aum_crore", "dataType": "int64", "sourceColumn": "aum_crore"},
                        {"name": "expense_ratio_pct", "dataType": "double", "sourceColumn": "expense_ratio_pct"},
                        {"name": "morningstar_rating", "dataType": "int64", "sourceColumn": "morningstar_rating"},
                        {"name": "risk_grade", "dataType": "string", "sourceColumn": "risk_grade"}
                    ],
                    "partitions": [
                        {
                            "name": "fact_performance-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\07_scheme_performance.csv"),[Delimiter=",", Columns=19, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{{\"amfi_code\", Int64.Type}, {\"return_1yr_pct\", type number}, {\"return_3yr_pct\", type number}, {\"return_5yr_pct\", type number}, {\"benchmark_3yr_pct\", type number}, {\"alpha\", type number}, {\"beta\", type number}, {\"sharpe_ratio\", type number}, {\"sortino_ratio\", type number}, {\"std_dev_ann_pct\", type number}, {\"max_drawdown_pct\", type number}, {\"aum_crore\", Int64.Type}, {\"expense_ratio_pct\", type number}, {\"morningstar_rating\", Int64.Type}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "fact_aum",
                    "columns": [
                        {"name": "date", "dataType": "string", "sourceColumn": "date"},
                        {"name": "fund_house", "dataType": "string", "sourceColumn": "fund_house"},
                        {"name": "aum_lakh_crore", "dataType": "double", "sourceColumn": "aum_lakh_crore"},
                        {"name": "aum_crore", "dataType": "int64", "sourceColumn": "aum_crore"},
                        {"name": "num_schemes", "dataType": "int64", "sourceColumn": "num_schemes"}
                    ],
                    "partitions": [
                        {
                            "name": "fact_aum-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\03_aum_by_fund_house.csv"),[Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{{\"aum_lakh_crore\", type number}, {\"aum_crore\", Int64.Type}, {\"num_schemes\", Int64.Type}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "fact_portfolio",
                    "columns": [
                        {"name": "amfi_code", "dataType": "int64", "sourceColumn": "amfi_code"},
                        {"name": "stock_symbol", "dataType": "string", "sourceColumn": "stock_symbol"},
                        {"name": "stock_name", "dataType": "string", "sourceColumn": "stock_name"},
                        {"name": "sector", "dataType": "string", "sourceColumn": "sector"},
                        {"name": "weight_pct", "dataType": "double", "sourceColumn": "weight_pct"},
                        {"name": "market_value_cr", "dataType": "double", "sourceColumn": "market_value_cr"},
                        {"name": "current_price_inr", "dataType": "double", "sourceColumn": "current_price_inr"},
                        {"name": "portfolio_date", "dataType": "string", "sourceColumn": "portfolio_date"}
                    ],
                    "partitions": [
                        {
                            "name": "fact_portfolio-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\09_portfolio_holdings.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{{\"amfi_code\", Int64.Type}, {\"weight_pct\", type number}, {\"market_value_cr\", type number}, {\"current_price_inr\", type number}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "fact_sip_industry",
                    "columns": [
                        {"name": "month", "dataType": "string", "sourceColumn": "month"},
                        {"name": "sip_inflow_crore", "dataType": "int64", "sourceColumn": "sip_inflow_crore"},
                        {"name": "active_sip_accounts_crore", "dataType": "double", "sourceColumn": "active_sip_accounts_crore"},
                        {"name": "new_sip_accounts_lakh", "dataType": "double", "sourceColumn": "new_sip_accounts_lakh"},
                        {"name": "sip_aum_lakh_crore", "dataType": "double", "sourceColumn": "sip_aum_lakh_crore"},
                        {"name": "yoy_growth_pct", "dataType": "double", "sourceColumn": "yoy_growth_pct"}
                    ],
                    "partitions": [
                        {
                            "name": "fact_sip_industry-Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\04_monthly_sip_inflows.csv"),[Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{{\"sip_inflow_crore\", Int64.Type}, {\"active_sip_accounts_crore\", type number}, {\"new_sip_accounts_lakh\", type number}, {\"sip_aum_lakh_crore\", type number}, {\"yoy_growth_pct\", type number}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    }
    
    with open(os.path.join(MODEL_DIR, "model.bim"), "w") as f:
        json.dump(model_bim, f, indent=2)
        
    print("Power BI Project (.pbip) folder structure successfully generated!")

if __name__ == "__main__":
    create_pbip_structure()
