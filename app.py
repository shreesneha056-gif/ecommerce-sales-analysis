import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Sales Intelligence", page_icon="⚡", layout="wide")

# ── Exact Power BI colors from pbix ──────────────────────────────────────────
BG       = "#0F1117"   # page background dark navy
CARD_BG  = "#161B27"   # card background
LINE_CLR = "#1E2435"   # subtle lines
TEXT_CLR = "#E2E8F0"   # main text
MUTED    = "#64748B"   # muted label text
GREEN    = "#10B981"   # Total Sales accent
RED      = "#EF4444"   # Total Profit accent / Smartphone bar
AMBER    = "#F59E0B"   # Avg Order Value accent / Mouse/Printer bar
YELLOW   = "#D9B300"   # Keyboard/Tablet bar
DKGREEN  = "#085d41"   # Camera/Monitor bar
# Category donut colors (Electronics=green, Accessories=amber, Office=red)
DONUT_COLORS = ["#10B981","#F59E0B","#EF4444"]
# Bar colors per product matching Power BI exactly
BAR_COLOR_MAP = {
    "Camera":     "#10B981",
    "Monitor":    "#10B981",
    "Mouse":      "#F59E0B",
    "Printer":    "#F59E0B",
    "Smartphone": "#EF4444",
    "Smartwatch": "#D9B300",
    "Keyboard":   "#D9B300",
    "Tablet":     "#D9B300",
    "Laptop":     "#085d41",
    "Headphones": "#085d41",
}

st.markdown(f"""
<style>
  .stApp, [data-testid="stAppViewContainer"],
  [data-testid="block-container"] {{
    background-color: {BG} !important;
  }}
  section[data-testid="stSidebar"] {{
    display: none !important;
  }}
  h1,h2,h3,h4,p,span,label,div {{
    color: {TEXT_CLR} !important;
  }}
  /* KPI cards */
  .kpi-card {{
    background:{CARD_BG};
    border-radius:8px;
    padding:16px 20px;
    border:1px solid {LINE_CLR};
  }}
  .kpi-label {{
    color:{MUTED} !important;
    font-size:12px;
    font-weight:500;
    margin-bottom:6px;
  }}
  .kpi-value {{
    font-size:28px;
    font-weight:700;
    margin-top:2px;
  }}
  /* Category button row */
  .cat-row {{
    display:flex;
    gap:8px;
    margin-bottom:14px;
  }}
  .stButton>button {{
    background:{CARD_BG};
    color:{TEXT_CLR};
    border:1px solid {LINE_CLR};
    border-radius:6px;
    padding:6px 20px;
    font-size:13px;
  }}
  .stButton>button:hover {{
    border-color:{GREEN};
    color:{GREEN};
  }}
  [data-baseweb="select"]>div {{
    background:{CARD_BG} !important;
    border-color:{LINE_CLR} !important;
    color:{TEXT_CLR} !important;
  }}
  [data-testid="stSlider"] {{
    color:{TEXT_CLR};
  }}
  .chart-card {{
    background:{CARD_BG};
    border:1px solid {LINE_CLR};
    border-radius:8px;
    padding:14px;
    margin-bottom:10px;
  }}
  .clear-btn>button {{
    background:{CARD_BG};
    border:1px solid {LINE_CLR};
    color:{TEXT_CLR};
    border-radius:6px;
    width:100%;
  }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Year']  = df['Order_Date'].dt.year
    df['Month'] = df['Order_Date'].dt.strftime('%b')
    df['MonthNum'] = df['Order_Date'].dt.month
    df['Total_Profit']    = df['Profit']
    df['Profit_Margin_%'] = (df['Profit'] / df['Sales']).round(4)
    df['Avg_Order_Value'] = (df['Sales'] / df['Quantity']).round(2)
    df['Total_Sales']     = df['Sales']
    df['Total_Quantity']  = df['Quantity']
    return df

df = load_data()

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=CARD_BG,
    font=dict(color=TEXT_CLR, family="Segoe UI", size=12),
    margin=dict(l=8, r=8, t=30, b=8),
)

# ── Top bar: Title + Category buttons ─────────────────────────────────────────
top1, top2 = st.columns([2, 3])
with top1:
    st.markdown(f"<h3 style='color:{TEXT_CLR};margin:0;'>⚡ Sales Intelligence</h3>", unsafe_allow_html=True)
with top2:
    bc1, bc2, bc3, bc4 = st.columns(4)
    if 'cat_filter' not in st.session_state:
        st.session_state.cat_filter = 'All'
    for col, cat in [(bc1,'All'),(bc2,'Electronics'),(bc3,'Accessories'),(bc4,'Office')]:
        with col:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True):
                st.session_state.cat_filter = cat
                st.rerun()

st.markdown("<hr style='border-color:#1E2435;margin:6px 0 14px 0;'>", unsafe_allow_html=True)

# ── Main layout: left filters + right content ──────────────────────────────────
left, right = st.columns([1, 6])

with left:
    # Clear all slicers
    if st.button("Clear all slicers", use_container_width=True, key="clear"):
        st.session_state.cat_filter = 'All'
        st.session_state.year_range = (2022, 2024)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Category dropdown
    st.markdown(f"<p style='color:{TEXT_CLR};font-size:12px;font-weight:600;margin-bottom:2px;'>Category</p>", unsafe_allow_html=True)
    cat_opts = ['All'] + sorted(df['Category'].unique().tolist())
    sel_cat_dd = st.selectbox("", cat_opts,
                               index=cat_opts.index(st.session_state.cat_filter),
                               label_visibility="collapsed", key="cat_dd")
    if sel_cat_dd != st.session_state.cat_filter:
        st.session_state.cat_filter = sel_cat_dd
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Year slicer
    st.markdown(f"<p style='color:{TEXT_CLR};font-size:12px;font-weight:600;margin-bottom:2px;'>Year</p>", unsafe_allow_html=True)
    years = sorted(df['Year'].unique().astype(int).tolist())
    if 'year_range' not in st.session_state:
        st.session_state.year_range = (min(years), max(years))
    y1 = st.selectbox("From", years, index=years.index(st.session_state.year_range[0]),
                       label_visibility="visible", key="y1")
    y2 = st.selectbox("To", years, index=years.index(st.session_state.year_range[1]),
                       label_visibility="visible", key="y2")
    st.session_state.year_range = (y1, y2)

with right:
    # ── Apply filters ──────────────────────────────────────────────────────────
    f = df[df['Year'].between(y1, y2)]
    if st.session_state.cat_filter != 'All':
        f = f[f['Category'] == st.session_state.cat_filter]

    # ── KPI Cards ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    total_sales  = f['Sales'].sum()
    total_profit = f['Profit'].sum()
    profit_margin = total_profit / total_sales if total_sales else 0
    avg_order    = f['Sales'].mean()

    for col, label, val, color in [
        (k1, "Total Sales",      f"{total_sales/1e6:.2f}M",  GREEN),
        (k2, "Total_Profit",     f"{total_profit/1e6:.2f}M", RED),
        (k3, "Profit_Margin_%",  f"{profit_margin:.2f}",     TEXT_CLR),
        (k4, "Avg_Order_Value",  f"{avg_order/1e3:.2f}K",    AMBER),
    ]:
        col.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value' style='color:{color};'>{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Area Chart: Total Sales by Month ───────────────────────────────────────
    st.markdown(f"<div class='chart-card'>", unsafe_allow_html=True)
    month_df = f.groupby(['MonthNum','Month'])['Sales'].sum().reset_index()
    month_df = month_df.sort_values('Sales', ascending=False)  # sorted by value desc like Power BI

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=month_df['Month'], y=month_df['Sales'],
        fill='tozeroy',
        line=dict(color="#6366F1", width=2),
        fillcolor="rgba(99,102,241,0.35)",
        mode='lines+text',
        text=month_df['Sales'].apply(lambda x: f"{x/1e6:.2f}M"),
        textposition='top center',
        textfont=dict(color=TEXT_CLR, size=10),
    ))
    fig.update_layout(**LAYOUT, height=300,
        title=dict(text="Total Sales by Month", font=dict(color=TEXT_CLR, size=13), x=0.5),
        xaxis=dict(title='Month', color=TEXT_CLR, gridcolor=LINE_CLR,
                   showgrid=True, gridwidth=1),
        yaxis=dict(title='Total Sales_Rising, Falling', color=TEXT_CLR,
                   gridcolor=LINE_CLR, tickformat=',.1s'))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Bottom row: Bar Chart + Donut ──────────────────────────────────────────
    b1, b2 = st.columns([1.3, 1])

    with b1:
        st.markdown(f"<div class='chart-card'>", unsafe_allow_html=True)
        prod_df = f.groupby('Product_Name')['Sales'].sum().reset_index()
        prod_df = prod_df.sort_values('Sales', ascending=True)
        prod_df['color'] = prod_df['Product_Name'].map(BAR_COLOR_MAP)

        fig = go.Figure(go.Bar(
            x=prod_df['Sales'],
            y=prod_df['Product_Name'],
            orientation='h',
            marker_color=prod_df['color'].tolist(),
            text=prod_df['Sales'].apply(lambda x: f"{x/1e6:.2f}M"),
            textposition='outside',
            textfont=dict(color=TEXT_CLR, size=11),
        ))
        fig.update_layout(**LAYOUT, height=320,
            title=dict(text="Total Sales by Product_Name",
                       font=dict(color=TEXT_CLR, size=13), x=0),
            xaxis=dict(title='Total Sales', color=TEXT_CLR, gridcolor=LINE_CLR),
            yaxis=dict(title='Product_Name', color=TEXT_CLR, gridcolor=LINE_CLR,
                       showgrid=False))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with b2:
        st.markdown(f"<div class='chart-card'>", unsafe_allow_html=True)
        cat_df = f.groupby('Category')['Sales'].sum().reset_index()
        cat_df['pct'] = (cat_df['Sales'] / cat_df['Sales'].sum() * 100).round(2)
        cat_df['label'] = cat_df.apply(
            lambda r: f"{r['Sales']/1e6:.0f}M ({r['pct']}%)", axis=1)

        fig = px.pie(cat_df, names='Category', values='Sales', hole=0.55,
                     color='Category',
                     color_discrete_map={
                         'Electronics': GREEN,
                         'Accessories': AMBER,
                         'Office': RED
                     })
        fig.update_traces(
            textposition='outside',
            texttemplate='%{customdata}',
            customdata=cat_df['label'],
            textfont=dict(color=TEXT_CLR, size=11),
            pull=[0.02, 0.02, 0.02]
        )
        fig.update_layout(**LAYOUT, height=320,
            title=dict(text="Total Sales by Category",
                       font=dict(color=TEXT_CLR, size=13), x=0),
            legend=dict(title='Category',
                        font=dict(color=TEXT_CLR, size=11),
                        bgcolor='rgba(0,0,0,0)',
                        orientation='v', x=1.0, y=0.5))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.caption("Built by Sneha Shree M U | Data Analyst & Data Scientist | Bangalore")
