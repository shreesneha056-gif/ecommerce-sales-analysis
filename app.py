import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Active Seller Performance", page_icon="🛒", layout="wide")

# ── Exact Power BI colors from dashboard ──────────────────────────────────────
BG         = "#2B0808"   # dark maroon background
CARD_BG    = "#3E1818"   # slightly lighter maroon for cards
GRID_CLR   = "#3D1919"   # grid lines
TEXT_CLR   = "#EAE1E1"   # light pinkish white text
ACCENT1    = "#DE6A73"   # main pink/rose accent
ACCENT2    = "#C94B55"   # darker rose
ACCENT3    = "#F0A0A8"   # lighter pink
ACCENT4    = "#A83040"   # deep rose
PIE_COLORS = ["#DE6A73", "#C94B55", "#F0A0A8", "#A83040"]  # rose tones like Power BI
AREA_COLOR = "#DE6A73"

st.markdown(f"""
<style>
  /* Page background */
  .stApp, .stApp > div, [data-testid="stAppViewContainer"] {{
    background-color: {BG} !important;
  }}
  /* Sidebar */
  section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {{
    background-color: {CARD_BG} !important;
  }}
  /* All text */
  h1,h2,h3,h4,h5,h6,p,span,label,div,li {{
    color: {TEXT_CLR} !important;
  }}
  /* KPI Cards */
  .kpi-box {{
    background-color: {CARD_BG};
    border: 1px solid {GRID_CLR};
    border-radius: 4px;
    padding: 10px 14px;
    text-align: center;
    min-height: 70px;
  }}
  .kpi-label {{
    color: {ACCENT1} !important;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .kpi-value {{
    color: {TEXT_CLR} !important;
    font-size: 26px;
    font-weight: 700;
    margin-top: 4px;
  }}
  /* Title bar */
  .title-bar {{
    background-color: {CARD_BG};
    border-left: 5px solid {ACCENT1};
    padding: 14px 20px;
    border-radius: 4px;
    margin-bottom: 16px;
  }}
  /* Tile slicer style */
  .tile-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-bottom: 10px;
  }}
  .tile-btn {{
    background-color: {ACCENT1};
    color: white !important;
    border: none;
    border-radius: 4px;
    padding: 10px;
    text-align: center;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }}
  /* Dataframe */
  [data-testid="stDataFrame"] {{
    background-color: {CARD_BG} !important;
  }}
  /* selectbox, multiselect */
  [data-baseweb="select"] > div {{
    background-color: {CARD_BG} !important;
    border-color: {ACCENT1} !important;
    color: {TEXT_CLR} !important;
  }}
  [data-baseweb="select"] span {{ color: {TEXT_CLR} !important; }}
  /* Remove default streamlit backgrounds */
  [data-testid="block-container"] {{
    background-color: {BG} !important;
  }}
  .stMarkdown, .element-container {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

# ── Load & process data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=['rating', 'totalunitssold'])

    # Recreate Power BI calculated columns
    df['Rating_Catagory'] = pd.cut(
        df['rating'], bins=[0, 2, 3, 4, 5],
        labels=['Poor', 'Average', 'Good', 'Excellent'])

    df['Discount_Stratorgy'] = df['averagediscount'].fillna(0).apply(lambda x:
        'No Discount'    if x == 0    else
        'Low'            if x <= 10   else
        'Medium'         if x <= 25   else
        'High'           if x <= 50   else 'Very High')

    df['Merchant_tiers'] = pd.cut(
        df['totalunitssold'],
        bins=[0, 50, 200, 500, 9999999],
        labels=['Bronze', 'Silver', 'Gold', 'Platinum'])

    # Urgency_status from Power BI — "Has Banner" vs "No Banner" based on urgency
    df['Urgency_status'] = df['urgencytextrate'].apply(
        lambda x: 'Has Banner' if pd.notna(x) and x > 0 else 'No Banner')

    df['Total_Products'] = df['listedproducts'].fillna(0).astype(int)
    df['total_sales']    = (df['totalunitssold'] * df['meanproductprices'].fillna(0)).round(0)
    df['Sum_of_rating']  = df['rating']
    return df

df = load_data()

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=CARD_BG,
    font=dict(color=TEXT_CLR, family="Segoe UI", size=12),
    margin=dict(l=8, r=8, t=28, b=8),
)

# ── Sidebar — Filters (matching Power BI layout) ──────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='background:{ACCENT1};padding:10px;border-radius:4px;'><b style='color:white;font-size:15px;'>Filters</b></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Merchant_tiers — tile style (multiselect as closest match)
    st.markdown(f"<p style='color:{TEXT_CLR};font-weight:600;margin-bottom:4px;'>Merchant_tiers</p>", unsafe_allow_html=True)
    # Render tiles visually
    tier_opts = ['Bronze', 'Gold', 'Platinum', 'Silver']
    sel_tiers = st.multiselect("", tier_opts, default=tier_opts, label_visibility="collapsed",
                                key="tiers")

    st.markdown("<br>", unsafe_allow_html=True)

    # Discount_Stratorgy — dropdown
    st.markdown(f"<p style='color:{TEXT_CLR};font-weight:600;margin-bottom:4px;'>Discount_Stratorgy</p>", unsafe_allow_html=True)
    disc_opts = ['All'] + sorted(df['Discount_Stratorgy'].dropna().unique().tolist())
    sel_disc  = st.selectbox("", disc_opts, label_visibility="collapsed", key="disc")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧹 Clear_Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown(f"<small style='color:{TEXT_CLR}'>👩‍💻 Sneha Shree M U<br><a href='https://www.linkedin.com/in/sneha-shree-mu/' style='color:{ACCENT1}'>LinkedIn</a></small>", unsafe_allow_html=True)

# ── Apply filters ──────────────────────────────────────────────────────────────
f = df.copy()
if sel_tiers:
    f = f[f['Merchant_tiers'].isin(sel_tiers)]
if sel_disc != 'All':
    f = f[f['Discount_Stratorgy'] == sel_disc]

# ── Title bar (matching Power BI) ─────────────────────────────────────────────
st.markdown(f"""
<div class='title-bar'>
  <span style='color:{ACCENT1};font-size:18px;font-weight:700;'>
    🟥 E-Commerce Active Seller Performance
  </span>
</div>""", unsafe_allow_html=True)

# ── KPI Cards row (Avg_Rating | count_of_merchant | Total_Products | total_sales) ──
k1, k2, k3, k4 = st.columns(4)
for col, label, val in [
    (k1, "Avg_Rating",         f"{f['rating'].mean():.2f}"),
    (k2, "count_of_merchant",  f"{len(f):,}"),
    (k3, "Total_Products",     f"{f['Total_Products'].sum()//1000:.0f}K"),
    (k4, "total_sales",        f"{f['total_sales'].sum()/1e6:.0f}M"),
]:
    col.markdown(f"""
    <div class='kpi-box'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{val}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Area Chart (left) + Pie Chart (right) ──────────────────────────────
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown(f"<p style='color:{TEXT_CLR};font-size:13px;font-weight:600'>Total_sales by Merchant_tiers</p>", unsafe_allow_html=True)
    area_df = f.groupby('Merchant_tiers', observed=True)['total_sales'].sum().reset_index()
    area_df.columns = ['Merchant_tiers', 'total_sales']
    # Sort to match Power BI (Platinum → Gold → Silver → Bronze)
    tier_order = ['Platinum', 'Gold', 'Silver', 'Bronze']
    area_df['Merchant_tiers'] = pd.Categorical(area_df['Merchant_tiers'], categories=tier_order, ordered=True)
    area_df = area_df.sort_values('Merchant_tiers')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=area_df['Merchant_tiers'].astype(str),
        y=area_df['total_sales'],
        fill='tozeroy',
        line=dict(color=ACCENT1, width=2),
        fillcolor=f"rgba(222,106,115,0.35)",
        mode='lines+markers+text',
        text=area_df['total_sales'].apply(lambda x: f"{x/1e6:.1f}M"),
        textposition='top center',
        textfont=dict(color=TEXT_CLR, size=11),
        marker=dict(color=ACCENT1, size=6)
    ))
    fig.update_layout(**LAYOUT, height=300,
                      xaxis=dict(title='Merchant_tiers', color=TEXT_CLR,
                                 gridcolor=GRID_CLR, linecolor=GRID_CLR),
                      yaxis=dict(title='total_sales', color=TEXT_CLR,
                                 gridcolor=GRID_CLR, tickformat=',.0s'))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown(f"<p style='color:{TEXT_CLR};font-size:13px;font-weight:600'>Total_sales by Rating_Catagory</p>", unsafe_allow_html=True)
    pie_df = f.groupby('Rating_Catagory', observed=True)['total_sales'].sum().reset_index()
    fig = px.pie(pie_df, names='Rating_Catagory', values='total_sales',
                 color_discrete_sequence=PIE_COLORS)
    fig.update_traces(
        textposition='outside',
        textinfo='label+value',
        textfont=dict(color=TEXT_CLR, size=11),
        pull=[0.03]*len(pie_df)
    )
    fig.update_layout(**LAYOUT, height=300,
                      legend=dict(font=dict(color=TEXT_CLR, size=11),
                                  bgcolor='rgba(0,0,0,0)',
                                  orientation='v', x=1.02, y=0.5))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Treemap + Clustered Column ─────────────────────────────────────────
c3, c4 = st.columns([1, 1])

with c3:
    st.markdown(f"<p style='color:{TEXT_CLR};font-size:13px;font-weight:600'>Count_of_merchant by Discount_Stratorgy</p>", unsafe_allow_html=True)
    tree_df = f.groupby('Discount_Stratorgy', observed=True)['merchantid'].count().reset_index()
    tree_df.columns = ['Discount_Stratorgy', 'count']
    # Use red/maroon tones matching Power BI treemap
    fig = px.treemap(tree_df, path=['Discount_Stratorgy'], values='count',
                     color='count',
                     color_continuous_scale=[[0,'#A83040'],[0.5,'#C94B55'],[1,'#DE6A73']])
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value}",
        textfont=dict(color='white', size=13)
    )
    fig.update_layout(**LAYOUT, height=300, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.markdown(f"<p style='color:{TEXT_CLR};font-size:13px;font-weight:600'>Total_Products and Count_of_merchant by Urgency_status</p>", unsafe_allow_html=True)
    urg_df = f.groupby('Urgency_status').agg(
        Total_Products=('Total_Products', 'sum'),
        count_of_merchant=('merchantid', 'count')
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Total_Products', x=urg_df['Urgency_status'],
        y=urg_df['Total_Products'],
        marker_color=ACCENT3,
        text=urg_df['Total_Products'],
        textposition='outside',
        textfont=dict(color=TEXT_CLR, size=11)
    ))
    fig.add_trace(go.Bar(
        name='count_of_merchant', x=urg_df['Urgency_status'],
        y=urg_df['count_of_merchant'],
        marker_color=ACCENT2,
        text=urg_df['count_of_merchant'],
        textposition='outside',
        textfont=dict(color=TEXT_CLR, size=11)
    ))
    fig.update_layout(**LAYOUT, height=300, barmode='group',
                      xaxis=dict(color=TEXT_CLR, gridcolor=GRID_CLR),
                      yaxis=dict(color=TEXT_CLR, gridcolor=GRID_CLR),
                      legend=dict(font=dict(color=TEXT_CLR), bgcolor='rgba(0,0,0,0)',
                                  orientation='h', x=0, y=1.1))
    st.plotly_chart(fig, use_container_width=True)

# ── Table (matching Power BI tableEx exactly) ──────────────────────────────────
st.markdown(f"<p style='color:{TEXT_CLR};font-size:13px;font-weight:600;margin-top:8px'>Merchant Tiers Summary</p>", unsafe_allow_html=True)
tbl = f.groupby('Merchant_tiers', observed=True).agg(
    total_sales   =('total_sales',   'sum'),
    Sum_of_rating =('Sum_of_rating', 'sum'),
    Total_Products=('Total_Products','sum')
).reset_index()

# Add Total row
total_row = pd.DataFrame([{
    'Merchant_tiers': 'Total',
    'total_sales':    tbl['total_sales'].sum(),
    'Sum_of_rating':  tbl['Sum_of_rating'].sum(),
    'Total_Products': tbl['Total_Products'].sum()
}])
tbl = pd.concat([tbl, total_row], ignore_index=True)
tbl['total_sales']    = tbl['total_sales'].apply(lambda x: f"{x:,.0f}")
tbl['Sum_of_rating']  = tbl['Sum_of_rating'].apply(lambda x: f"{x:,.2f}")
tbl['Total_Products'] = tbl['Total_Products'].apply(lambda x: f"{x:,.0f}")
tbl.columns = ['Merchant_tiers','total_sales','Sum of rating','Total_Products']

st.dataframe(tbl, use_container_width=True, hide_index=True)
st.caption("Built by Sneha Shree M U | Data Analyst & Data Scientist | Bangalore")
