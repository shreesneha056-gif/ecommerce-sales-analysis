import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Sales Dashboard", page_icon="🛒", layout="wide")

BG       = "#2B0808"
CARD_BG  = "#3E1818"
GRID_CLR = "#3D1919"
TEXT_CLR = "#EAE1E1"
ACCENT   = "#DE6A73"
CHART_COLORS = ["#DE6A73","#603131","#3E1D1D","#2F0808","#EAE1E1"]

st.markdown(f"""
<style>
  .stApp {{ background-color: {BG}; }}
  section[data-testid="stSidebar"] {{ background-color: {CARD_BG}; }}
  h1,h2,h3,h4,p {{ color: {TEXT_CLR} !important; }}
  .kpi-card {{ background:{CARD_BG};border:1px solid {GRID_CLR};border-radius:6px;padding:16px;text-align:center;margin-bottom:8px; }}
  .kpi-label {{ color:{ACCENT};font-size:12px;font-weight:600; }}
  .kpi-value {{ color:{TEXT_CLR};font-size:22px;font-weight:700; }}
  div[data-testid="stDataFrame"] {{ background:{CARD_BG}; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=['rating','totalunitssold'])
    df['Rating_Catagory'] = pd.cut(df['rating'], bins=[0,2,3,4,5],
                                    labels=['Low','Medium','Good','Excellent'])
    df['Discount_Stratorgy'] = pd.cut(df['averagediscount'].fillna(0),
                                       bins=[-1,10,25,50,101],
                                       labels=['Low Discount','Medium Discount','High Discount','Very High Discount'])
    df['Merchant_tiers'] = pd.cut(df['totalunitssold'],
                                   bins=[0,50,200,500,9999999],
                                   labels=['Bronze','Silver','Gold','Platinum'])
    df['Urgency_status']  = df['urgencytextrate'].apply(lambda x: 'Urgent' if pd.notna(x) and x > 50 else 'Normal')
    df['Total_Products']  = df['listedproducts'].fillna(0)
    df['total_sales']     = (df['totalunitssold'] * df['meanproductprices'].fillna(0)).round(2)
    df['Avg_Discount_pct']= df['averagediscount'].fillna(0)
    return df

df = load_data()

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=CARD_BG,
    font=dict(color=TEXT_CLR, family="Segoe UI"),
    margin=dict(l=10,r=10,t=30,b=10)
)

# ── Sidebar slicers ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h3 style='color:{ACCENT}'>🔽 Filters</h3>", unsafe_allow_html=True)
    disc_opts = sorted(df['Discount_Stratorgy'].dropna().unique().tolist())
    sel_disc  = st.selectbox("Discount Strategy", ["All"] + disc_opts)
    tier_opts = sorted(df['Merchant_tiers'].dropna().unique().tolist())
    sel_tiers = st.multiselect("Merchant Tiers", tier_opts, default=tier_opts)
    st.markdown("---")
    st.markdown(f"<small style='color:{TEXT_CLR}'>👩‍💻 Sneha Shree M U</small>", unsafe_allow_html=True)

# ── Filter ─────────────────────────────────────────────────────────────────────
f = df.copy()
if sel_disc != "All":
    f = f[f['Discount_Stratorgy'] == sel_disc]
if sel_tiers:
    f = f[f['Merchant_tiers'].isin(sel_tiers)]

# ── Title ──────────────────────────────────────────────────────────────────────
st.markdown(f"<h2 style='color:{TEXT_CLR};text-align:center'>🛒 E-Commerce Sales Dashboard</h2>", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
for col, label, val in [
    (k1,"Total Sales",        f"${f['total_sales'].sum():,.0f}"),
    (k2,"Total Products",     f"{f['Total_Products'].sum():,.0f}"),
    (k3,"Count of Merchants", f"{len(f):,}"),
    (k4,"Avg Rating",         f"{f['rating'].mean():.2f}"),
    (k5,"Avg Discount %",     f"{f['Avg_Discount_pct'].mean():.1f}%"),
]:
    col.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{val}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Bar + Area ──────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 1.6])

with c1:
    st.markdown(f"<h4 style='color:{TEXT_CLR}'>Rating Category vs Count of Merchants</h4>", unsafe_allow_html=True)
    bd = f.groupby('Rating_Catagory', observed=True)['merchantid'].count().reset_index()
    bd.columns = ['Rating_Catagory','Count']
    fig = go.Figure(go.Bar(x=bd['Count'], y=bd['Rating_Catagory'], orientation='h',
                           marker_color=ACCENT, text=bd['Count'],
                           textposition='outside', textfont=dict(color=TEXT_CLR)))
    fig.update_layout(**LAYOUT, height=280,
                      xaxis=dict(gridcolor=GRID_CLR, color=TEXT_CLR),
                      yaxis=dict(color=TEXT_CLR))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown(f"<h4 style='color:{TEXT_CLR}'>Merchant Tiers vs Total Sales (Area)</h4>", unsafe_allow_html=True)
    ad = f.groupby('Merchant_tiers', observed=True)['total_sales'].sum().reset_index()
    fig = go.Figure(go.Scatter(
        x=ad['Merchant_tiers'].astype(str), y=ad['total_sales'],
        fill='tozeroy', line=dict(color=ACCENT, width=2.5),
        fillcolor="rgba(222,106,115,0.25)",
        mode='lines+markers'))
    fig.update_layout(**LAYOUT, height=280,
                      xaxis=dict(gridcolor=GRID_CLR, color=TEXT_CLR),
                      yaxis=dict(gridcolor=GRID_CLR, color=TEXT_CLR))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Treemap + Pie + Clustered Column ────────────────────────────────────
c3, c4, c5 = st.columns(3)

with c3:
    st.markdown(f"<h4 style='color:{TEXT_CLR}'>Discount Strategy vs Merchants</h4>", unsafe_allow_html=True)
    td = f.groupby('Discount_Stratorgy', observed=True)['merchantid'].count().reset_index()
    td.columns = ['Discount_Stratorgy','Count']
    fig = px.treemap(td, path=['Discount_Stratorgy'], values='Count',
                     color='Count', color_continuous_scale=['#3E1818','#DE6A73'])
    fig.update_layout(**LAYOUT, height=300, coloraxis_showscale=False)
    fig.update_traces(textfont=dict(color=TEXT_CLR, size=12))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.markdown(f"<h4 style='color:{TEXT_CLR}'>Rating Category vs Total Sales</h4>", unsafe_allow_html=True)
    pd_df = f.groupby('Rating_Catagory', observed=True)['total_sales'].sum().reset_index()
    fig = px.pie(pd_df, names='Rating_Catagory', values='total_sales',
                 color_discrete_sequence=CHART_COLORS)
    fig.update_traces(textfont_color=TEXT_CLR, textposition='inside', textinfo='percent+label')
    fig.update_layout(**LAYOUT, height=300, legend=dict(font=dict(color=TEXT_CLR)))
    st.plotly_chart(fig, use_container_width=True)

with c5:
    st.markdown(f"<h4 style='color:{TEXT_CLR}'>Urgency Status vs Products & Merchants</h4>", unsafe_allow_html=True)
    ud = f.groupby('Urgency_status').agg(
        Total_Products=('Total_Products','sum'),
        Merchants=('merchantid','count')).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Total Products', x=ud['Urgency_status'],
                         y=ud['Total_Products'], marker_color=ACCENT))
    fig.add_trace(go.Bar(name='Count of Merchants', x=ud['Urgency_status'],
                         y=ud['Merchants'], marker_color='#603131'))
    fig.update_layout(**LAYOUT, height=300, barmode='group',
                      xaxis=dict(color=TEXT_CLR),
                      yaxis=dict(gridcolor=GRID_CLR, color=TEXT_CLR),
                      legend=dict(font=dict(color=TEXT_CLR)))
    st.plotly_chart(fig, use_container_width=True)

# ── Table ──────────────────────────────────────────────────────────────────────
st.markdown(f"<h4 style='color:{TEXT_CLR}'>Merchant Tiers Summary</h4>", unsafe_allow_html=True)
tbl = f.groupby('Merchant_tiers', observed=True).agg(
    total_sales=('total_sales','sum'),
    rating=('rating','mean'),
    Total_Products=('Total_Products','sum')
).reset_index()
tbl['total_sales']    = tbl['total_sales'].apply(lambda x: f"${x:,.0f}")
tbl['rating']         = tbl['rating'].apply(lambda x: f"{x:.2f}")
tbl['Total_Products'] = tbl['Total_Products'].apply(lambda x: f"{x:,.0f}")
tbl.columns = ['Merchant Tiers','Total Sales','Avg Rating','Total Products']
st.dataframe(tbl, use_container_width=True, hide_index=True)

st.caption("Built by Sneha Shree M U | Data Analyst & Data Scientist | Bangalore")
