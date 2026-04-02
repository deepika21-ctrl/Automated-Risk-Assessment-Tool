# 🎯 Automated Risk Assessment Tool for Portfolio Optimization

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Compatible-326CE5.svg)](https://kubernetes.io/)

**AI-Powered Portfolio Risk Assessment with LLM Scenario Generation & Monte Carlo Simulation**

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Kubernetes Deployment](#-kubernetes-deployment)
- [Project Structure](#-project-structure)

---

## 🎯 Problem Statement

Portfolio managers in quantitative finance face significant challenges:

1. **Manual Risk Assessment**: Error-prone and time-consuming
2. **Volatile Markets**: Difficulty predicting asset behavior across diverse portfolios (stocks, bonds, crypto)
3. **Scenario Analysis**: Limited ability to test "what-if" scenarios at scale
4. **Computational Limits**: Cannot run large-scale simulations quickly
5. **Suboptimal Allocations**: Leading to higher exposure to losses

**Real-World Impact**: The 2022 market crash demonstrated the critical need for automated, intelligent risk assessment tools.

---

## 💡 Solution Overview

This project delivers an **AI-powered web application** that:

1. **Generates Market Scenarios** using Large Language Models (LLMs)
2. **Optimizes Portfolios** using Modern Portfolio Theory (MPT)
3. **Runs Monte Carlo Simulations** (10,000+ iterations) for stress testing
4. **Scales with Kubernetes** for multi-user, compute-intensive workloads

---

## ✨ Key Features

### 🤖 AI-Powered Analysis
- LLM Scenario Generation using Hugging Face
- Natural Language Risk Interpretation
- Market condition forecasting

### 📊 Portfolio Optimization
- Modern Portfolio Theory (MPT) implementation
- Efficient Frontier calculation
- Maximum Sharpe Ratio portfolio
- Minimum Variance portfolio

### 🎲 Monte Carlo Simulation
- 10,000+ simulations for robust forecasting
- Value at Risk (VaR) & CVaR calculation
- Path visualization

### ⚠️ Stress Testing
- Multiple scenario analysis
- Custom stress tests
- Probability distributions

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.11+ |
| LLM | Hugging Face API |
| Optimization | SciPy |
| Data | NumPy, Pandas |
| Visualization | Plotly, Matplotlib |
| Market Data | yfinance |
| Container | Docker |
| Orchestration | Kubernetes + HPA |

---

## 📦 Installation

### Local Setup

```bash
# Clone repository
git clone https://github.com/deepika21-ctrl/Automated-Risk-Assessment-Tool.git
cd Automated-Risk-Assessment-Tool

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add HUGGINGFACE_API_KEY

# Run application
streamlit run app/streamlit_app_enhanced.py
```

---

## 🚀 Usage

1. **Upload Portfolio**: CSV with `ticker` and `weight` columns
2. **Adjust Parameters**: Risk-free rate, confidence levels
3. **Explore Tabs**: Analysis, Optimization, AI Scenarios, Simulations

---

## ☸️ Kubernetes Deployment

```bash
# Build image
docker build -t risk-assessment-tool:latest .

# Create secrets
kubectl create secret generic risk-assessment-secrets \
  --from-literal=huggingface-api-key=YOUR_KEY

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

---

## 📁 Project Structure

```
├── app/                    # Streamlit applications
├── core/                   # Core modules
│   ├── config.py          # Configuration
│   ├── optimization.py    # MPT optimization
│   ├── llm_integration.py # LLM scenarios
│   └── monte_carlo.py     # Simulations
├── k8s/                   # Kubernetes configs
├── Dockerfile             # Container definition
└── requirements.txt       # Dependencies
```

---

---

<div align="center">
  <strong>Built with ❤️ for Quant Finance</strong>
</div>
