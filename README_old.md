# 📊 Automated Risk Assessment Tool for Portfolio Optimization

An AI-powered portfolio risk analysis and optimization system built using Python, Streamlit, and financial market data APIs.

This project aims to automate portfolio stress testing, risk forecasting, and allocation optimization for diverse asset classes such as stocks, bonds, and cryptocurrencies.

---

## 🚀 Problem Statement

Portfolio managers in quantitative finance struggle to assess risk in volatile markets, especially when dealing with diversified portfolios across multiple asset classes.

Manual risk calculations:
- Are time-consuming  
- Are error-prone  
- Do not scale for large portfolios  
- Cannot efficiently simulate multiple market scenarios  

This project solves that by building an automated risk analysis and scenario simulation tool.

---

## 🎯 Project Objectives

- Automate portfolio risk analysis
- Enable scenario-based stress testing
- Optimize portfolio allocation
- Integrate LLMs for intelligent scenario interpretation (Upcoming)
- Design for scalable deployment using Docker & Kubernetes (Upcoming)

---

## 🏗 Current Progress (Week 1 MVP)

✔ Streamlit-based user interface  
✔ Portfolio CSV upload  
✔ Sample portfolio support  
✔ Input validation  
✔ Clean project architecture  
✔ GitHub version control integration  

---

## 📂 Project Structure

```
Risk-Assessment-Tool/
│
├── app/                     # Streamlit UI application
│   └── streamlit_app.py
│
├── core/                    # Risk & optimization logic (Upcoming)
│
├── data/                    # Sample portfolio CSV
│   └── sample_portfolio.csv
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📥 Portfolio CSV Format

The uploaded portfolio must follow this structure:

```csv
ticker,weight
AAPL,0.25
MSFT,0.25
GOOGL,0.20
TLT,0.20
BTC-USD,0.10
```

Rules:
- Must contain columns: `ticker` and `weight`
- Weights should sum to 1.0

---

## 🛠 Tech Stack

### Core Technologies
- Python
- Streamlit
- Pandas
- NumPy
- yFinance (Yahoo Finance API)

### Dev & Deployment
- Git & GitHub
- Virtual Environments (.venv)
- (Upcoming) Docker
- (Upcoming) Kubernetes

### AI Integration (Upcoming)
- Hugging Face LLMs
- Prompt engineering for scenario simulation

---

## ▶️ How to Run Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/deepika21-ctrl/Automated-Risk-Assessment-Tool.git
cd Automated-Risk-Assessment-Tool
```

### 2️⃣ Create Virtual Environment

Windows:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Mac/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
streamlit run app/streamlit_app.py
```

Open in browser:
```
http://localhost:8501
```

---

## 🔮 Upcoming Features

- Historical price data fetching
- Portfolio return computation
- Volatility calculation
- Value at Risk (VaR)
- Conditional VaR (CVaR)
- Sharpe Ratio computation
- Scenario-based stress testing
- Portfolio optimization engine
- LLM-driven market scenario generation
- Multi-container Docker deployment
- Kubernetes orchestration with autoscaling

---

## 🌍 Real-World Impact

This system can be used by:

- Investment analysts
- Quantitative researchers
- FinTech startups
- Portfolio managers
- Banking institutions

It helps reduce portfolio exposure during extreme events such as market crashes or interest rate shocks.

---

## 👩‍💻 Author

**Deepika Yadav**  
B.Tech Computer Science Engineering  
Focused on AI, Quant Finance & Scalable Systems  

---

## ⭐ Future Vision

Transform this tool into a full-scale AI-powered portfolio intelligence platform with:

- Real-time risk monitoring
- Cloud-native scaling
- Automated strategy optimization
- Interactive financial analytics dashboard

---

If you find this project interesting, feel free to ⭐ star the repository.
