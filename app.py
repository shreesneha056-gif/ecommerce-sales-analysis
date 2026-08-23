import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Sales Dashboard", page_icon="🛒", layout="wide")

st.markdown("""
<style>
.metric-card {background:#f0f4ff;border-radius:10px;padding:16px;text-align:center;border-left:4px solid #2E75B6;}
.title-bar {background:linear-gradient(90deg,#1F4E79,#2E75B6);padding:18px;border-radius:10px;margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df = df[['Order_Date','Product_Name','Category','Region','Quantity','Sales','Profit']].dropna(subset=['Sales'])
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Month'] = df['Order_Date'].dt.to_period('M').astype(str)
    df['Year'] = df['Order_Date'].dt.year
    df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
    df['AOV'] = df['Sales'] / df['Quantity']
    return df

df = load_data()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="title-bar"><h2 style="color:white;margin:0;">🛒 E-Commerce Sales Performance Dashboard</h2><p style="color:#cce4ff;margin:0;">Interactive analytics by Sneha Shree M U</p></div>', unsafe_allow_html=True)

# ── Sidebar Filters ─────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/shopping-cart.png", width=80)
st.sidebar.title("🔽 Filters")

years = sorted(df['Year'].unique())
sel_year = st.sidebar.multiselect("📅 Year", years, default=years)

categories = sorted(df['Category'].dropna().unique())
sel_cat = st.sidebar.multiselect("📦 Category", categories, default=categories)

regions = sorted(df['Region'].dropna().unique())
sel_region = st.sidebar.multiselect("🗺️ Region", regions, default=regions)

products = sorted(df['Product_Name'].dropna().unique())
sel_product = st.sidebar.multiselect("🏷️ Product", products, default=products)

st.sidebar.markdown("---")
st.sidebar.markdown("**👩‍💻 Built by Sneha Shree M U**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/sneha-shree-mu/) | [GitHub](https://github.com/shreesneha056-gif)")

# ── Filter Data ─────────────────────────────────────────────────────────────────
filtered = df[
    df['Year'].isin(sel_year) &
    df['Category'].isin(sel_cat) &
    df['Region'].isin(sel_region) &
    df['Product_Name'].isin(sel_product)
]

# ── KPI Cards ──────────────────────────────────────────────────────────────────
st.markdown("### 📌 Key Performance Indicators")
k1, k2, k3, k4, k5 = st.columns(5)

total_sales   = filtered['Sales'].sum()
total_profit  = filtered['Profit'].sum()
total_orders  = len(filtered)
avg_margin    = filtered['Profit_Margin'].mean()
avg_order_val = filtered['AOV'].mean()

k1.metric("💰 Total Sales",   f"${total_sales:,.0f}")
k2.metric("📈 Total Profit",  f"${total_profit:,.0f}")
k3.metric("🛒 Total Orders",  f"{total_orders:,}")
k4.metric("📊 Profit Margin", f"{avg_margin:.1f}%")
k5.metric("🧾 Avg Order Value", f"${avg_order_val:,.0f}")

st.markdown("---")

# ── Row 1: Sales by Category + Region ─────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 📦 Sales by Category")
    cat_df = filtered.groupby('Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=True)
    fig = px.bar(cat_df, x='Sales', y='Category', orientation='h',
                 color='Sales', color_continuous_scale='Blues',
                 text=cat_df['Sales'].apply(lambda x: f"${x:,.0f}"))
    fig.update_traces(textposition='outside')
    fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("#### 🗺️ Sales by Region")
    reg_df = filtered.groupby('Region')['Sales'].sum().reset_index()
    fig = px.pie(reg_df, names='Region', values='Sales', hole=0.45,
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Monthly Sales Trend + Profit by Category ───────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.markdown("#### 📅 Monthly Sales Trend")
    month_df = filtered.groupby('Month')[['Sales','Profit']].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=month_df['Month'], y=month_df['Sales'], name='Sales',
                             line=dict(color='#2E75B6', width=2.5), fill='tozeroy', fillcolor='rgba(46,117,182,0.1)'))
    fig.add_trace(go.Scatter(x=month_df['Month'], y=month_df['Profit'], name='Profit',
                             line=dict(color='#70AD47', width=2)))
    fig.update_layout(height=350, xaxis_tickangle=45, margin=dict(l=0,r=0,t=10,b=0), legend=dict(x=0,y=1))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.markdown("#### 💹 Profit Margin by Category")
    margin_df = filtered.groupby('Category').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    margin_df['Margin%'] = (margin_df['Profit'] / margin_df['Sales'] * 100).round(1)
    fig = px.bar(margin_df, x='Category', y='Margin%',
                 color='Margin%', color_continuous_scale='RdYlGn',
                 text=margin_df['Margin%'].apply(lambda x: f"{x:.1f}%"))
    fig.update_traces(textposition='outside')
    fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Top Products + Sales vs Profit scatter ─────────────────────────────
c5, c6 = st.columns(2)

with c5:
    st.markdown("#### 🏆 Top 10 Products by Sales")
    top_prod = filtered.groupby('Product_Name')['Sales'].sum().nlargest(10).reset_index()
    fig = px.bar(top_prod, x='Sales', y='Product_Name', orientation='h',
                 color='Sales', color_continuous_scale='Blues',
                 text=top_prod['Sales'].apply(lambda x: f"${x:,.0f}"))
    fig.update_traces(textposition='outside')
    fig.update_layout(height=380, showlegend=False, coloraxis_showscale=False,
                      yaxis={'categoryorder':'total ascending'}, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

with c6:
    st.markdown("#### 🔵 Sales vs Profit by Region")
    sp_df = filtered.groupby(['Region','Category']).agg(Sales=('Sales','sum'), Profit=('Profit','sum'), Orders=('Quantity','sum')).reset_index()
    fig = px.scatter(sp_df, x='Sales', y='Profit', color='Region', size='Orders',
                     hover_data=['Category'], color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# ── Raw Data Table ─────────────────────────────────────────────────────────────
with st.expander("📋 View Raw Data"):
    st.dataframe(filtered[['Order_Date','Product_Name','Category','Region','Quantity','Sales','Profit','Profit_Margin']].sort_values('Sales', ascending=False), use_container_width=True)

st.caption("🎓 Built by Sneha Shree M U | Data Analyst & Data Scientist | Bangalore")
