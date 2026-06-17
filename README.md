# 📊 NASDAQ Listed Securities — Data Visualization Dashboard

**Course:** Exploratory Data Analysis  
**Instructor:** Ali Hassan Sherazi  
**Submission Date:** 05-June-2026

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Dashboard
```bash
streamlit run app.py
```

The dashboard opens in your browser at `http://localhost:8501`

---

## 📁 Project Structure
```
nasdaq_dashboard/
├── data/
│   └── 1780492838799_nasdaq-listed__1_.csv   ← EXACT original filename
├── app.py              ← Main Streamlit dashboard
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 📊 Charts Included (All 10 Required)

| # | Chart | Insight |
|---|-------|---------|
| 1 | Pie Chart | Security type proportional distribution |
| 2 | Histogram | Ticker symbol length frequency |
| 3 | Line Chart | Listings per year trend |
| 4 | Bar Chart | Entity suffix comparison |
| 5 | Scatter Plot | Symbol length vs name word count |
| 6 | Box Plot | Name word count spread by security type |
| 7 | Heatmap | Numerical feature correlation matrix |
| 8 | Area Chart | Cumulative listings over time |
| 9 | Count Plot | SPAC vs Non-SPAC frequency by type |
| 10 | Violin Plot | Symbol length distribution by type |
| 🎁 | Pair Plot | Bonus: multi-feature relationships |

---

## 🔍 Filters (All Linked to All Charts)
- **Search** — keyword filter on Symbol or Security Name
- **Security Type** — multi-select dropdown
- **Share Class** — multi-select dropdown
- **SPAC / Non-SPAC** — category dropdown
- **Entity Suffix** — multi-select dropdown
- **Symbol Length** — range slider
- **Listing Year** — range slider (simulated)
- **Reset Button** — restores all defaults

---

## 💡 Key Insights
- **Common Stock** dominates NASDAQ listings (~43%)
- **ETFs** are the second largest category (~21%)
- Most tickers are **4 characters** long (standard NASDAQ format)
- **Warrants, Units, and Rights** are primarily SPAC-related instruments
- Security names for ETFs and Funds tend to have more words

---

## ⚙️ Feature Engineering
Since the raw dataset only has Symbol + Security Name, the following features were extracted:
- `Security_Type` — parsed from name keywords
- `Share_Class` — Class A/B/C, Series A/B/C/D
- `Entity_Suffix` — Inc., Corp., Ltd., LLC, etc.
- `Is_SPAC` — detected via acquisition/blank check keywords
- `Symbol_Length` — character count of ticker
- `Name_Word_Count` — word count of security name
- `Listing_Year` — simulated (reproducible random seed)
- `Sim_Market_Cap_B` — simulated for scatter/correlation demos
