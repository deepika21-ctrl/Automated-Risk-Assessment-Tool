# ⚡ Quick Start Guide

Get the Automated Risk Assessment Tool running in 5 minutes!

---

## 🚀 Fastest Way (Local Python)

```bash
# 1. Navigate to project
cd Automated-Risk-Assessment-Tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the enhanced app
streamlit run app/streamlit_app_enhanced.py
```

✅ **Done!** Access at `http://localhost:8501`

---

## 🐳 Docker Way (Recommended for Teachers)

```bash
# 1. Build image
docker build -t risk-tool .

# 2. Run container
docker run -p 8501:8501 risk-tool
```

✅ **Done!** Access at `http://localhost:8501`

---

## 📊 Test the App

### Step 1: Upload Sample Portfolio

Use the included `data/sample_portfolio.csv` or create your own:

```csv
ticker,weight
AAPL,0.30
MSFT,0.25
GOOGL,0.20
TLT,0.15
GLD,0.10
```

### Step 2: Explore Features

1. **📊 Current Portfolio Analysis**
   - View real-time metrics
   - See cumulative performance
   - Check correlation matrix

2. **🎯 Portfolio Optimization**
   - Find maximum Sharpe ratio portfolio
   - Identify minimum volatility allocation
   - Visualize efficient frontier

3. **🤖 AI Scenario Generation**
   - Generate recession scenarios
   - Analyze inflation impacts
   - Get AI risk assessments

4. **🎲 Monte Carlo Simulation**
   - Run 10,000 simulations
   - View probability distributions
   - Calculate VaR & CVaR

5. **⚠️ Stress Testing**
   - Test market crash scenarios
   - Compare worst/best cases
   - Assess probability of loss

---

## 🔑 Optional: Enable AI Features

For LLM scenario generation:

1. Get a free Hugging Face API key from: https://huggingface.co/settings/tokens

2. Create `.env` file:
```bash
echo "HUGGINGFACE_API_KEY=your_key_here" > .env
```

3. Restart the app

**Note**: App works without API key using fallback scenarios!

---

## 🧪 Run Tests

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/ -v

# Expected: 30+ tests pass
```

---

## 📸 Expected Screenshots

### Dashboard
![Dashboard](docs/images/dashboard.png)

### Efficient Frontier
![Frontier](docs/images/efficient_frontier.png)

### Monte Carlo
![Simulation](docs/images/monte_carlo.png)

---

## 🎓 Show Your Teacher

### Demo Script

**1. Introduction (2 min)**
```
"This tool helps portfolio managers assess risk using AI and advanced simulations.
It solves the problem of manual, error-prone risk calculations."
```

**2. Features Demo (5 min)**

**a) Upload Portfolio**
```
"I'll upload a portfolio with tech stocks and bonds..."
[Show data/sample_portfolio.csv]
```

**b) Current Analysis**
```
"The app fetches 2 years of historical data from Yahoo Finance
and calculates key metrics: Sharpe ratio, VaR, CVaR..."
[Show Tab 1: Metrics]
```

**c) Optimization**
```
"Using Modern Portfolio Theory, we find the optimal allocation
that maximizes risk-adjusted returns..."
[Show Tab 2: Efficient Frontier]
```

**d) AI Scenarios**
```
"The LLM generates market scenarios. Let me ask: 
'What happens in a recession?'"
[Show Tab 3: AI Generation]
```

**e) Monte Carlo**
```
"Running 10,000 simulations shows us the probability distribution
of future portfolio values..."
[Show Tab 4: Simulation paths]
```

**f) Stress Testing**
```
"Finally, we test extreme scenarios: market crash, tech selloff, etc."
[Show Tab 5: Stress results]
```

**3. Technical Architecture (3 min)**

```
"Backend: Python with scipy for optimization, NumPy for calculations
Frontend: Streamlit for rapid prototyping
LLM: Hugging Face API (Mixtral model)
Deployment: Dockerized, ready for Kubernetes scaling
```

[Show `k8s/` folder and explain HPA]

**4. Real-World Impact**
```
"This tool could have helped investors during the 2022 crash
by identifying overexposure to tech stocks..."
```

---

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install --upgrade -r requirements.txt
```

### "No data returned from Yahoo Finance"
```bash
# Check internet connection
# Or use sample data in data/ folder
```

### "Port 8501 already in use"
```bash
streamlit run app/streamlit_app_enhanced.py --server.port 8502
```

### Docker build fails
```bash
# Clear cache
docker system prune -a
docker build --no-cache -t risk-tool .
```

---

## 📚 Next Steps

1. ✅ Read `README.md` for full documentation
2. ✅ Check `DEPLOYMENT.md` for Kubernetes setup
3. ✅ Review `GIT_COMMIT_GUIDE.md` for commit strategy
4. ✅ Explore `tests/test_core.py` for code quality

---

## 🎯 Success Criteria Checklist

For your teacher's evaluation:

- [ ] App runs locally without errors
- [ ] Sample portfolio loads and displays metrics
- [ ] Optimization generates efficient frontier
- [ ] Monte Carlo runs 10,000 simulations successfully
- [ ] Stress testing shows results for multiple scenarios
- [ ] Docker image builds and runs
- [ ] Kubernetes manifests are present (deployment, service, HPA)
- [ ] Tests pass (pytest)
- [ ] Git history shows frequent, meaningful commits
- [ ] README explains problem, solution, and architecture

---

## 💡 Pro Tips for Demo

1. **Prepare Backup**: Take screenshots in case of live demo issues
2. **Test Beforehand**: Run through the entire demo 2-3 times
3. **Explain Simply**: "It's like having a financial advisor powered by AI"
4. **Show Code Quality**: Briefly show `core/optimization.py` structure
5. **Highlight Scalability**: Emphasize Kubernetes autoscaling (2-10 pods)

---

## 🎉 You're Ready!

Your project demonstrates:
- ✅ Advanced Python programming
- ✅ LLM integration (Hugging Face)
- ✅ Financial mathematics (MPT, Monte Carlo)
- ✅ Modern deployment (Docker, Kubernetes)
- ✅ Production-ready practices (tests, documentation)

**Good luck with your presentation!** 🚀
