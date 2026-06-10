import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Set page config
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Bluestock Branding (Royal Blue #414BEA, Flamingo #F05537, Midnight Blue #012970)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Title and Header Styles */
    .main-title {
        color: #012970;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .subtitle {
        color: #6c757d;
        font-size: 16px;
        margin-bottom: 25px;
    }
    
    /* KPI Card Container */
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        flex: 1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #414BEA;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
    }
    .kpi-card-flamingo {
        border-left: 5px solid #F05537;
    }
    .kpi-card-midnight {
        border-left: 5px solid #012970;
    }
    .kpi-label {
        font-size: 13px;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #012970;
    }
</style>
""", unsafe_allow_html=True)

# Helper to load data
DATA_DIR = r"c:\Users\jibum\OneDrive\Desktop\Bluestock Internship\day 2\data\processed"

@st.cache_data
def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

# Load all datasets
fund_master = load_csv("01_fund_master.csv")
nav_history = load_csv("02_nav_history.csv")
aum_by_fund_house = load_csv("03_aum_by_fund_house.csv")
monthly_sip_inflows = load_csv("04_monthly_sip_inflows.csv")
category_inflows = load_csv("05_category_inflows.csv")
industry_folio_count = load_csv("06_industry_folio_count.csv")
scheme_performance = load_csv("07_scheme_performance.csv")
investor_transactions = load_csv("08_investor_transactions.csv")
portfolio_holdings = load_csv("09_portfolio_holdings.csv")
benchmark_indices = load_csv("10_benchmark_indices.csv")
dim_date = load_csv("dim_date.csv")

# Inject Bluestock Sidebar Branding
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #414BEA; font-weight: 700; margin: 0;'>BLUESTOCK</h2>
        <p style='color: #F05537; font-weight: 500; font-size: 12px; margin: 0;'>MUTUAL FUND ANALYTICS</p>
    </div>
    <hr style='margin-top: 10px; margin-bottom: 20px;' />
    """, 
    unsafe_allow_html=True
)

# Sidebar Navigation
pages = [
    "🏢 Industry Overview", 
    "📈 Fund Performance", 
    "👥 Investor Analytics", 
    "🔥 SIP & Market Trends",
    "🔍 Fund Deep-Dive (Drill-Through)"
]
selected_page = st.sidebar.radio("Navigation", pages)

# ----------------- PAGE 1: INDUSTRY OVERVIEW -----------------
if selected_page == "🏢 Industry Overview":
    st.markdown("<h1 class='main-title'>🏢 Mutual Fund Industry Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Executive summary of the Indian mutual fund industry metrics, growth, and market share.</p>", unsafe_allow_html=True)
    
    # KPI Cards (AUM, SIP Inflows, Folios, Schemes)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>Total AUM</div>
            <div class='kpi-value'>₹81L Cr</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='kpi-card kpi-card-flamingo'>
            <div class='kpi-label'>SIP Inflows (Dec 25)</div>
            <div class='kpi-value'>₹31,002 Cr</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='kpi-card kpi-card-midnight'>
            <div class='kpi-label'>Total Folios</div>
            <div class='kpi-value'>26.12 Cr</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>Active Schemes</div>
            <div class='kpi-value'>1,908</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Visual Layout
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Industry AUM Growth Trend (2022-2025)")
        if not aum_by_fund_house.empty:
            # Aggregate AUM over time
            aum_trend = aum_by_fund_house.groupby('date')['aum_lakh_crore'].sum().reset_index()
            # Sort date
            aum_trend['date_parsed'] = pd.to_datetime(aum_trend['date'], format='%Y-%m-%d', errors='coerce')
            aum_trend = aum_trend.dropna().sort_values('date_parsed')
            
            fig = px.line(
                aum_trend, 
                x='date', 
                y='aum_lakh_crore',
                labels={'aum_lakh_crore': 'Total AUM (Lakh Cr)', 'date': 'Quarter'},
                markers=True
            )
            fig.update_traces(line_color='#414BEA', line_width=3, marker=dict(size=8, color='#F05537'))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#eaeaea'),
                yaxis=dict(showgrid=True, gridcolor='#eaeaea'),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("AUM by fund house data is not loaded.")
            
    with chart_col2:
        st.subheader("AUM Distribution by Asset Management Company (AMC)")
        if not scheme_performance.empty:
            amc_aum = scheme_performance.groupby('fund_house')['aum_crore'].sum().reset_index()
            amc_aum = amc_aum.sort_values('aum_crore', ascending=False)
            
            fig = px.bar(
                amc_aum,
                x='aum_crore',
                y='fund_house',
                orientation='h',
                labels={'aum_crore': 'AUM (₹ Crore)', 'fund_house': 'AMC'},
                color_discrete_sequence=['#012970']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#eaeaea'),
                yaxis=dict(categoryorder='total ascending'),
                hovermode='y unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Scheme performance data is not loaded.")

# ----------------- PAGE 2: FUND PERFORMANCE -----------------
elif selected_page == "📈 Fund Performance":
    st.markdown("<h1 class='main-title'>📈 Mutual Fund Performance & Risk Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Compare returns vs risk, view dynamic scorecard statistics, and benchmark NAV performance.</p>", unsafe_allow_html=True)
    
    if not scheme_performance.empty:
        # Dynamic Slicers
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            amc_list = ["All"] + list(scheme_performance['fund_house'].unique())
            sel_amc = st.selectbox("Fund House (AMC)", amc_list)
        with col_s2:
            cat_list = ["All"] + list(scheme_performance['category'].unique())
            sel_cat = st.selectbox("Category", cat_list)
        with col_s3:
            plan_list = ["All"] + list(scheme_performance['plan'].unique())
            sel_plan = st.selectbox("Plan Type", plan_list)
            
        # Filter data
        filtered_perf = scheme_performance.copy()
        if sel_amc != "All":
            filtered_perf = filtered_perf[filtered_perf['fund_house'] == sel_amc]
        if sel_cat != "All":
            filtered_perf = filtered_perf[filtered_perf['category'] == sel_cat]
        if sel_plan != "All":
            filtered_perf = filtered_perf[filtered_perf['plan'] == sel_plan]
            
        # Risk-Return Scatter Plot
        st.subheader("Risk-Return Trade-Off (Sharpe-Bubble Scatter)")
        fig_scatter = px.scatter(
            filtered_perf,
            x='return_3yr_pct',
            y='std_dev_ann_pct',
            size='aum_crore',
            color='risk_grade',
            hover_name='scheme_name',
            custom_data=['sharpe_ratio', 'sortino_ratio'],
            labels={'return_3yr_pct': '3 Year Return (%)', 'std_dev_ann_pct': 'Annualized Risk / Std Dev (%)', 'risk_grade': 'Risk Grade'},
            color_discrete_map={'High': '#F05537', 'Moderate': '#414BEA', 'Low': '#012970', 'Below Average': '#6c757d', 'Above Average': '#e0a800'}
        )
        fig_scatter.update_traces(
            hovertemplate="<b>%{hovertext}</b><br/>3Yr Return: %{x:.2f}%<br/>Std Dev: %{y:.2f}%<br/>Sharpe: %{customdata[0]:.2f}<br/>Sortino: %{customdata[1]:.2f}<br/>AUM: %{marker.size} Cr"
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#eaeaea'),
            yaxis=dict(showgrid=True, gridcolor='#eaeaea')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Sortable Scorecard Table
        st.subheader("Fund Scorecard Table")
        display_cols = [
            'amfi_code', 'scheme_name', 'fund_house', 'category', 'plan', 
            'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 
            'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct', 'alpha', 'beta', 'aum_crore'
        ]
        scorecard_df = filtered_perf[display_cols].copy()
        scorecard_df.columns = [
            'Code', 'Scheme Name', 'Fund House', 'Category', 'Plan', 
            'Return 1Yr (%)', 'Return 3Yr (%)', 'Return 5Yr (%)', 
            'Sharpe', 'Sortino', 'Std Dev (%)', 'Alpha (%)', 'Beta', 'AUM (₹ Cr)'
        ]
        st.dataframe(scorecard_df.style.format({
            'Return 1Yr (%)': '{:.2f}%',
            'Return 3Yr (%)': '{:.2f}%',
            'Return 5Yr (%)': '{:.2f}%',
            'Sharpe': '{:.2f}',
            'Sortino': '{:.2f}',
            'Std Dev (%)': '{:.2f}%',
            'Alpha (%)': '{:.2f}%',
            'Beta': '{:.2f}',
            'AUM (₹ Cr)': '{:,.0f}'
        }), use_container_width=True, hide_index=True)
        
        # Slicer to select a single fund for drill-through
        st.subheader("Select Fund for Drill-Through Detail Analysis")
        selected_scheme = st.selectbox("Choose a fund to drill down:", filtered_perf['scheme_name'].unique())
        if st.button("🔍 Go to Fund Deep-Dive Details"):
            st.session_state['drilled_scheme'] = selected_scheme
            # Simulate page switch by updating query params/session state
            st.info(f"Navigating to Fund Deep-Dive details for: {selected_scheme}. Please click the '🔍 Fund Deep-Dive (Drill-Through)' tab in the sidebar navigation.")
            
    else:
        st.info("Scheme performance data is not loaded.")

# ----------------- PAGE 3: INVESTOR ANALYTICS -----------------
elif selected_page == "👥 Investor Analytics":
    st.markdown("<h1 class='main-title'>👥 Investor Demographic & Behavioural Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Analyse transaction distributions, geo-demographic concentrations, and ticketing habits.</p>", unsafe_allow_html=True)
    
    if not investor_transactions.empty:
        # Dynamic Slicers
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            state_list = ["All"] + sorted(list(investor_transactions['state'].dropna().unique()))
            sel_state = st.selectbox("State", state_list)
        with col_s2:
            age_list = ["All"] + sorted(list(investor_transactions['age_group'].dropna().unique()))
            sel_age = st.selectbox("Age Group", age_list)
        with col_s3:
            tier_list = ["All"] + sorted(list(investor_transactions['city_tier'].dropna().unique()))
            sel_tier = st.selectbox("City Tier", tier_list)
            
        # Filter transactions
        filtered_tx = investor_transactions.copy()
        if sel_state != "All":
            filtered_tx = filtered_tx[filtered_tx['state'] == sel_state]
        if sel_age != "All":
            filtered_tx = filtered_tx[filtered_tx['age_group'] == sel_age]
        if sel_tier != "All":
            filtered_tx = filtered_tx[filtered_tx['city_tier'] == sel_tier]
            
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Transaction Volume by Indian State")
            state_vol = filtered_tx.groupby('state')['amount_inr'].sum().reset_index()
            state_vol = state_vol.sort_values('amount_inr', ascending=False).head(10)
            
            fig = px.bar(
                state_vol,
                x='amount_inr',
                y='state',
                orientation='h',
                labels={'amount_inr': 'Total Vol (₹)', 'state': 'State'},
                color_discrete_sequence=['#414BEA']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#eaeaea'),
                yaxis=dict(categoryorder='total ascending')
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with chart_col2:
            st.subheader("Transaction Type Distribution (Volume)")
            type_vol = filtered_tx.groupby('transaction_type')['amount_inr'].sum().reset_index()
            
            fig = px.pie(
                type_vol,
                values='amount_inr',
                names='transaction_type',
                hole=0.4,
                color_discrete_sequence=['#414BEA', '#F05537', '#012970']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            st.subheader("Age Group vs Average SIP Ticket Size")
            sip_tx = filtered_tx[filtered_tx['transaction_type'] == 'SIP']
            if not sip_tx.empty:
                age_sip = sip_tx.groupby('age_group')['amount_inr'].mean().reset_index()
                
                fig = px.bar(
                    age_sip,
                    x='age_group',
                    y='amount_inr',
                    labels={'amount_inr': 'Avg SIP Amount (₹)', 'age_group': 'Age Group'},
                    color_discrete_sequence=['#F05537']
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(showgrid=True, gridcolor='#eaeaea')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No SIP transaction records matched the filters.")
                
        with chart_col4:
            st.subheader("Monthly Transaction Volume Trend")
            # Group by month
            filtered_tx['date_parsed'] = pd.to_datetime(filtered_tx['transaction_date'], errors='coerce')
            filtered_tx = filtered_tx.dropna(subset=['date_parsed'])
            filtered_tx['month_period'] = filtered_tx['date_parsed'].dt.to_period('M').astype(str)
            
            monthly_vol = filtered_tx.groupby('month_period')['amount_inr'].sum().reset_index()
            monthly_vol = monthly_vol.sort_values('month_period')
            
            fig = px.line(
                monthly_vol,
                x='month_period',
                y='amount_inr',
                labels={'amount_inr': 'Transaction Amount (₹)', 'month_period': 'Month'},
                markers=True
            )
            fig.update_traces(line_color='#012970', line_width=3, marker=dict(size=8, color='#F05537'))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#eaeaea'),
                yaxis=dict(showgrid=True, gridcolor='#eaeaea'),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Investor transactions data is not loaded.")

# ----------------- PAGE 4: SIP & MARKET TRENDS -----------------
elif selected_page == "🔥 SIP & Market Trends":
    st.markdown("<h1 class='main-title'>🔥 SIP & General Market Trends</h1>", unsafe_allow_html=True)
    # KPI Cards (Active Accounts, New Registrations, YoY Growth, SIP AUM)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>Active SIP Accounts</div>
            <div class='kpi-value'>9.35 Cr</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='kpi-card kpi-card-flamingo'>
            <div class='kpi-label'>New SIP Registrations</div>
            <div class='kpi-value'>9.80 Lakh</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='kpi-card kpi-card-midnight'>
            <div class='kpi-label'>SIP Accounts YoY Growth</div>
            <div class='kpi-value'>17.17%</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='kpi-card'>
            <div class='kpi-label'>SIP Industry AUM</div>
            <div class='kpi-value'>₹15.90L Cr</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("SIP Inflow (Bar) vs Nifty 50 Close (Line)")
        if not monthly_sip_inflows.empty and not benchmark_indices.empty:
            # Prepare SIP
            sip_df = monthly_sip_inflows.copy()
            sip_df['date_parsed'] = pd.to_datetime(sip_df['month'], format='%Y-%m', errors='coerce')
            sip_df = sip_df.dropna().sort_values('date_parsed')
            
            # Prepare Nifty
            nifty = benchmark_indices[benchmark_indices['index_name'] == 'NIFTY50'].copy()
            nifty['date_parsed'] = pd.to_datetime(nifty['date'], format='%Y-%m-%d', errors='coerce')
            nifty = nifty.dropna()
            
            # Monthly Nifty Average Close
            nifty['month_str'] = nifty['date_parsed'].dt.strftime('%Y-%m')
            nifty_monthly = nifty.groupby('month_str')['close_value'].mean().reset_index()
            
            # Merge
            merged_trends = pd.merge(sip_df, nifty_monthly, left_on='month', right_on='month_str', how='inner')
            merged_trends = merged_trends.sort_values('date_parsed')
            
            # Dual Axis Chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(
                    x=merged_trends['month'],
                    y=merged_trends['sip_inflow_crore'],
                    name="SIP Inflow (₹ Cr)",
                    marker_color='#414BEA',
                    opacity=0.8
                ),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(
                    x=merged_trends['month'],
                    y=merged_trends['close_value'],
                    name="Nifty 50 Average Close",
                    line=dict(color='#F05537', width=3),
                    marker=dict(size=6)
                ),
                secondary_y=True
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5),
                hovermode='x unified'
            )
            fig.update_xaxes(title_text="Month", showgrid=True, gridcolor='#eaeaea')
            fig.update_yaxes(title_text="SIP Inflow (₹ Crore)", secondary_y=False, showgrid=True, gridcolor='#eaeaea')
            fig.update_yaxes(title_text="Nifty 50 Close Price", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Required SIP or Nifty 50 dataset missing.")
            
    with chart_col2:
        st.subheader("Monthly Category Inflow Distribution (Heatmap)")
        if not category_inflows.empty:
            cat_pivot = category_inflows.pivot(index='category', columns='month', values='net_inflow_crore').fillna(0)
            
            fig = px.imshow(
                cat_pivot,
                labels=dict(x="Month", y="Category", color="Net Inflow (Cr)"),
                x=cat_pivot.columns,
                y=cat_pivot.index,
                color_continuous_scale=[[0, '#012970'], [0.5, '#414BEA'], [1, '#F05537']]
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category inflows data is not loaded.")
            
    st.subheader("Top 5 Categories by Net Inflow FY25")
    if not category_inflows.empty:
        # Sum by category
        top_cats = category_inflows.groupby('category')['net_inflow_crore'].sum().reset_index()
        top_cats = top_cats.sort_values('net_inflow_crore', ascending=False).head(5)
        
        fig = px.bar(
            top_cats,
            x='category',
            y='net_inflow_crore',
            labels={'net_inflow_crore': 'Net Inflow (₹ Crore)', 'category': 'Category'},
            color_discrete_sequence=['#012970']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='#eaeaea')
        )
        st.plotly_chart(fig, use_container_width=True)

# ----------------- PAGE 5: DRILL-THROUGH DETAILS -----------------
elif selected_page == "🔍 Fund Deep-Dive (Drill-Through)":
    # Check if a scheme was selected via session state
    drilled_scheme = st.session_state.get('drilled_scheme', None)
    
    st.markdown("<h1 class='main-title'>🔍 Fund Deep-Dive Detail View</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Detailed historical performance, normalized NAV trend compared with benchmark indices, and sector weightings.</p>", unsafe_allow_html=True)
    
    # Fallback to selection list if none was selected
    if not drilled_scheme and not scheme_performance.empty:
        drilled_scheme = st.selectbox("Please select a scheme to analyze:", scheme_performance['scheme_name'].unique())
        
    if drilled_scheme:
        st.info(f"Active Deep-Dive Target: **{drilled_scheme}**")
        
        # Get scheme metadata
        scheme_info = scheme_performance[scheme_performance['scheme_name'] == drilled_scheme].iloc[0]
        amfi_code = scheme_info['amfi_code']
        
        # KPI Blocks specific to the fund
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Annualized 3Y Return</div>
                <div class='kpi-value'>{scheme_info['return_3yr_pct']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='kpi-card kpi-card-flamingo'>
                <div class='kpi-label'>Fund Sharpe Ratio</div>
                <div class='kpi-value'>{scheme_info['sharpe_ratio']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='kpi-card kpi-card-midnight'>
                <div class='kpi-label'>Fund Size (AUM)</div>
                <div class='kpi-value'>₹{scheme_info['aum_crore']:,} Cr</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Expense Ratio</div>
                <div class='kpi-value'>{scheme_info['expense_ratio_pct']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Detailed Stats and Chart
        col_c1, col_c2 = st.columns([2, 1])
        
        with col_c1:
            st.subheader("Normalized Fund NAV vs Benchmark Index (Base 100)")
            if not nav_history.empty and not benchmark_indices.empty:
                # Filter NAV history
                fund_nav = nav_history[nav_history['amfi_code'] == amfi_code].copy()
                fund_nav['date_parsed'] = pd.to_datetime(fund_nav['date'], format='%Y-%m-%d', errors='coerce')
                fund_nav = fund_nav.dropna().sort_values('date_parsed')
                
                # Filter Benchmark Nifty 50
                benchmark = benchmark_indices[benchmark_indices['index_name'] == 'NIFTY50'].copy()
                benchmark['date_parsed'] = pd.to_datetime(benchmark['date'], format='%Y-%m-%d', errors='coerce')
                benchmark = benchmark.dropna().sort_values('date_parsed')
                
                # Merge NAV and Benchmark
                merged_nav = pd.merge(fund_nav, benchmark, on='date_parsed', suffixes=('_fund', '_bench'), how='inner')
                merged_nav = merged_nav.sort_values('date_parsed')
                
                if not merged_nav.empty:
                    # Normalize
                    fund_start = merged_nav['nav'].iloc[0]
                    bench_start = merged_nav['close_value'].iloc[0]
                    merged_nav['Normalized Fund NAV'] = (merged_nav['nav'] / fund_start) * 100
                    merged_nav['Normalized Benchmark Price'] = (merged_nav['close_value'] / bench_start) * 100
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=merged_nav['date_parsed'],
                        y=merged_nav['Normalized Fund NAV'],
                        name=f"Fund: {drilled_scheme}",
                        line=dict(color='#414BEA', width=3)
                    ))
                    fig.add_trace(go.Scatter(
                        x=merged_nav['date_parsed'],
                        y=merged_nav['Normalized Benchmark Price'],
                        name="Benchmark: Nifty 50",
                        line=dict(color='#F05537', width=2, dash='dash')
                    ))
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=True, gridcolor='#eaeaea', title="Date"),
                        yaxis=dict(showgrid=True, gridcolor='#eaeaea', title="Normalized Price (Base 100)"),
                        hovermode='x unified',
                        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Could not align historical date records between NAV and Nifty 50 benchmark.")
            else:
                st.info("NAV history or benchmark index dataset is missing.")
                
        with col_c2:
            st.subheader("Top Sector Weights (%)")
            if not portfolio_holdings.empty:
                fund_port = portfolio_holdings[portfolio_holdings['amfi_code'] == amfi_code].copy()
                if not fund_port.empty:
                    sector_weights = fund_port.groupby('sector')['weight_pct'].sum().reset_index()
                    sector_weights = sector_weights.sort_values('weight_pct', ascending=False)
                    
                    fig = px.bar(
                        sector_weights,
                        x='weight_pct',
                        y='sector',
                        orientation='h',
                        labels={'weight_pct': 'Weight (%)', 'sector': 'Sector'},
                        color_discrete_sequence=['#012970']
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=True, gridcolor='#eaeaea'),
                        yaxis=dict(categoryorder='total ascending')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No sector details found in portfolio holdings for this fund.")
            else:
                st.info("Portfolio holdings dataset is not loaded.")
    else:
        st.info("No fund deep-dive target selected. Go to the 'Fund Performance' tab to choose a fund.")
