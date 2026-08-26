# 💼 Sales Intelligence Dashboard

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat-square&logo=mysql&logoColor=white)

> Interactive Streamlit dashboard replicating a Power BI report — analyzing e-commerce sales performance across products, categories, months, and years with full filter capability.

## 🌐 Live Demo
**👉 [Open Dashboard](https://ecommerce-sales-analysis-dashboard1.streamlit.app/)**

---

## 🎯 Dashboard Overview

| KPI | Value |
|-----|-------|
| Total Sales | 11M |
| Total Profit | 1.84M |
| Profit Margin % | 0.17 |
| Avg Order Value | 3.05K |

## 📊 Charts (exact Power BI replica)
- **Area Chart** — Total Sales by Month (sorted by value, purple fill)
- **Horizontal Bar Chart** — Total Sales by Product Name (color-coded by category)
- **Donut Chart** — Total Sales by Category (Electronics / Accessories / Office)

## 🔽 Filters
- Category buttons — All / Electronics / Accessories / Office
- Category dropdown + Year slicer (2022 / 2023 / 2024)
- Clear all slicers button

## 🛠️ Tech Stack
- **Dashboard:** Streamlit, Plotly
- **Data:** Python, Pandas, SQL (MS SQL Server)
- **BI Tool:** Power BI (original design)
- **Deployment:** Streamlit Community Cloud

## 📂 Project Structure
```
ecommerce-sales-analysis/
├── app.py              # Streamlit dashboard app
├── data.xlsx           # E-commerce sales dataset
├── requirements.txt
├── ecommerce_sales_project/
│   ├── Data/           # Raw data
│   ├── sql/            # SQL queries
│   └── DashBoard/      # Power BI screenshots
└── README.md
```

## 🚀 How to Run Locally
```bash
git clone https://github.com/shreesneha056-gif/ecommerce-sales-analysis.git
cd ecommerce-sales-analysis
pip install -r requirements.txt
streamlit run app.py
```

---
📫 [LinkedIn](https://www.linkedin.com/in/sneha-shree-mu/) | [Portfolio](https://shreesneha056-gif.github.io/portfolio_website/) | [GitHub](https://github.com/shreesneha056-gif)
