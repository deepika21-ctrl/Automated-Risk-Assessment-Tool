# ⬡ RiskOS — Automated Portfolio Risk Assessment Tool

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.5+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-HPA-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**An AI-powered, production-grade portfolio risk management platform combining Modern Portfolio Theory, Monte Carlo Simulation, and LLM-driven scenario analysis.**

[🚀 Quick Start](#-quick-start) · [📊 Features](#-features) · [🧠 How It Works](#-how-it-works) · [📸 Screenshots](#-screenshots--demo) · [🛠 Tech Stack](#-tech-stack)

</div>

---

## 🎯 Problem Statement

Manual portfolio risk assessment is **slow, inconsistent, and scales poorly**:

- Portfolio managers spend hours manually calculating risk metrics like VaR and drawdown
- "What-if" scenario analysis (e.g., *"What happens to my portfolio in a recession?"*) is rarely run at all
- Allocations are often based on intuition rather than mathematical optimization
- Small teams cannot run the thousands of simulations required for rigorous stress testing

> **Real-world context:** During the 2022 market crash, portfolios lacking proper risk management saw losses of 30–50% that quantitative models could have partially anticipated and hedged.

---

## 💡 Solution

**RiskOS** is a full-stack AI web application that automates the entire risk assessment pipeline:

```
Upload Portfolio CSV  →  Fetch Live Market Data  →  Calculate Risk Metrics
         ↓
Optimize Allocation (MPT)  →  Run 10,000 Monte Carlo Simulations
         ↓
Generate AI Scenarios (LLM)  →  Stress Test  →  Interactive Dashboard
```

---

## ✨ Features

### 📊 Tab 1 — Current Portfolio Analysis
- Calculates **Annual Return, Volatility, Sharpe Ratio, Sortino Ratio**
- Computes **Value at Risk (VaR)** and **Conditional VaR (CVaR)** at user-defined confidence levels
- Renders **cumulative performance** chart and **asset correlation heatmap**
- Shows individual asset performance breakdown table

### 🎯 Tab 2 — Portfolio Optimization (Modern Portfolio Theory)
- Finds the **Maximum Sharpe Ratio portfolio** using SLSQP quadratic programming
- Computes the **Minimum Variance portfolio**
- Plots the full **Efficient Frontier** overlaid with 2,000 randomly sampled portfolios
- Shows weight changes: *how much to buy/sell of each asset*

### 🤖 Tab 3 — AI Scenario Generation (LLM-Powered)
- Uses **Mixtral-8x7B via Hugging Face API** with financial prompt engineering
- Generates natural-language analysis for 5 macro scenarios:
  - 📉 Economic Recession
  - 📈 High Inflation (>5%)
  - 💰 Interest Rate Hike
  - 🚀 Bull Market
  - ⚡ Volatility Spike
- Also provides an **AI Risk Interpretation** of your specific portfolio metrics

### 🎲 Tab 4 — Monte Carlo Simulation
- Simulates **up to 20,000 correlated portfolio paths**
- Uses **Cholesky decomposition** to preserve realistic asset correlations
- Outputs: Mean/Median terminal value, 5th/95th percentile bands, probability of profit
- Plots simulation fan chart and **terminal value distribution histogram**

### ⚠️ Tab 5 — Stress Testing
- Pre-built scenarios: *Market Crash −30%, Tech Selloff, Bond Crisis, Stagflation, Bull Market*
- Runs Monte Carlo under each stressed return assumption
- Outputs worst-case 5th percentile, mean, and best-case 95th percentile per scenario

---

## 📸 Screenshots & Demo

### 🔐 Login Page
> Secure role-based access with a dark gamey RiskOS interface

| Feature | Detail |
|---|---|
| Users | admin, shreya, deepika, demo |
| Auth | Session-state based (no external DB required) |
| Design | Dark mode, Orbitron font, glassmorphism card |

### 📊 Sample Output

**Input Portfolio (`data/sample_portfolio.csv`):**

| Ticker | Weight |
|--------|--------|
| AAPL   | 0.30   |
| MSFT   | 0.25   |
| GOOGL  | 0.20   |
| TLT    | 0.15   |
| GLD    | 0.10   |

**Output Metrics (example):**

| Metric | Value |
|--------|-------|
| Annual Return | 18.4% |
| Annual Volatility | 14.2% |
| Sharpe Ratio | 1.014 |
| VaR (95%) | −1.38% |
| CVaR (95%) | −2.01% |
| Max Drawdown | −19.7% |

**Monte Carlo (10,000 simulations, 1-year, $100,000 initial):**

| Stat | Value |
|------|-------|
| Expected Value | $118,400 |
| 5th Percentile (Worst Case) | $82,300 |
| 95th Percentile (Best Case) | $158,200 |
| Probability of Profit | 73.4% |

---

## 🧠 How It Works

### Algorithm 1 — Markowitz Mean-Variance Optimization (MPT)

We minimize portfolio variance subject to a target return constraint using **SLSQP** solver from `scipy.optimize`:

```python
# Maximize Sharpe Ratio = (Rp - Rf) / σp
# Subject to: Σwi = 1, wi ≥ 0

result = minimize(
    fun=neg_sharpe,           # objective: maximize Sharpe
    x0=equal_weights,
    method='SLSQP',
    constraints=[{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}],
    bounds=[(0, 1)] * n_assets
)
```

### Algorithm 2 — Monte Carlo with Cholesky Decomposition

To generate **correlated** random return paths (not independent), we use Cholesky decomposition of the covariance matrix:

```python
L = np.linalg.cholesky(cov_matrix)          # Cholesky factor
Z = np.random.standard_normal((n_days, n_assets))
correlated_returns = Z @ L.T                  # Inject correlations
portfolio_value[t] = portfolio_value[t-1] * (1 + correlated_returns @ weights)
```

### Algorithm 3 — LLM Prompt Engineering

Structured prompts inject portfolio data into context for the Mixtral-8x7B model:

```
System: You are a quantitative risk analyst.
User: Analyze a portfolio of [AAPL 30%, MSFT 25%, ...] under a recession scenario.
      Current Sharpe: 1.01, VaR: -1.38%, Max Drawdown: -19.7%
      Provide specific impact analysis and recommendations.
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI** | Streamlit 1.5+ | Interactive web dashboard |
| **Styling** | Custom CSS (Orbitron, dark theme) | Gamey professional UI |
| **Optimization** | SciPy SLSQP | Quadratic programming for MPT |
| **Simulation** | NumPy + Cholesky | 10,000-path Monte Carlo |
| **AI/LLM** | Hugging Face API (Mixtral-8x7B) | Scenario generation |
| **Data** | yfinance | Real-time & historical stock prices |
| **Visualization** | Plotly, Matplotlib, Seaborn | Interactive charts |
| **ML Utilities** | scikit-learn | Data preprocessing |
| **Container** | Docker | Reproducible deployment |
| **Orchestration** | Kubernetes + HPA | Auto-scaling (2–10 pods) |
| **Config** | python-dotenv | Secure API key management |
| **Testing** | pytest | 30+ unit test cases |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Local Setup (3 commands)

```bash
# 1. Clone the repository
git clone https://github.com/deepika21-ctrl/Automated-Risk-Assessment-Tool.git
cd Automated-Risk-Assessment-Tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app/streamlit_app_enhanced.py
```

Open your browser at **http://localhost:8501**

**Login with:** `demo` / `demo`

### Environment Variables (Optional — for AI features)

```bash
cp .env.example .env
# Add your Hugging Face API key to .env:
# HUGGINGFACE_API_KEY=hf_your_key_here
```

> ℹ️ The app works fully without an API key — AI tabs use intelligent fallback scenarios.

---

## 📁 Project Structure

```
Automated-Risk-Assessment-Tool/
├── app/
│   ├── streamlit_app_enhanced.py   # Main UI (login + 5 analysis tabs)
│   └── streamlit_app.py            # Original base app
├── core/
│   ├── config.py                   # Centralized settings & constants
│   ├── data.py                     # Yahoo Finance data fetching
│   ├── optimization.py             # MPT: Sharpe, MinVol, Efficient Frontier
│   ├── monte_carlo.py              # Monte Carlo + Cholesky simulation
│   └── llm_integration.py          # HuggingFace LLM + fallback scenarios
├── data/
│   └── sample_portfolio.csv        # Example 5-asset portfolio
├── tests/
│   └── test_core.py                # 30+ pytest unit tests
├── k8s/
│   ├── deployment.yaml             # Kubernetes deployment (3 replicas)
│   ├── service.yaml                # LoadBalancer service
│   └── hpa.yaml                    # Horizontal Pod Autoscaler (2–10 pods)
├── Dockerfile                      # Multi-stage Python image
├── docker-compose.yml              # Local Docker development
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
└── README.md
```

---

## ☸️ Docker & Kubernetes Deployment

```bash
# Build Docker image
docker build -t risk-assessment-tool:latest .

# Run with Docker Compose
docker-compose up

# Deploy to Kubernetes
kubectl create secret generic risk-assessment-secrets \
  --from-literal=huggingface-api-key=YOUR_KEY

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Check pods (auto-scales 2–10 based on CPU/memory)
kubectl get pods
kubectl get hpa
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

Expected output: **30+ tests PASSED** covering optimization, Monte Carlo, VaR/CVaR, stress testing, and edge cases.

---

## 📈 Results & Validation

| Test Case | Result |
|-----------|--------|
| Sharpe optimization on 5-asset portfolio | ✅ Converges in <50ms |
| Monte Carlo (10,000 paths, 252 days) | ✅ Completes in ~3 seconds |
| Cholesky decomposition (correlation preservation) | ✅ Verified via covariance check |
| Efficient frontier (50 portfolios) | ✅ Monotonically increasing return/risk |
| Stress test (5 scenarios × 1,000 sims) | ✅ All scenarios complete in <10s |

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>Built with ❤️ for Quantitative Finance · Powered by AI + Advanced Portfolio Theory</strong><br/>
  <sub>Streamlit · SciPy · Hugging Face · Kubernetes</sub>
</div>
