# Quant-Investment: Automated Quantitative Trading System

An end-to-end automated quantitative stock trading system that scrapes market data, engineers features, trains machine learning models, and automatically executes buy orders through Korea Investment API (KIS).

## 🎯 Features

- **Data Acquisition**: Web scrapes historical stock data from 11 market sectors (~787 stocks)
- **Feature Engineering**: Computes 13 technical indicators (moving averages, RSI, Bollinger Bands, MACD, etc.)
- **Machine Learning**: Random Forest classifier to predict stock price movements
- **Stock Recommendations**: Identifies top-N stocks most likely to rise above target threshold
- **Automated Trading**: Integrates with Korea Investment API for real-time order execution
- **Flexible Pipeline**: Step-by-step or end-to-end execution modes

## 📊 Project Overview

### Data Flow Architecture

```
stockanalysis.com (11 sectors)
         ↓
    scrap.py (Web Scraping)
         ↓
  stock_data/ (787 raw CSV files)
         ↓
  preprocess.py (Feature Engineering)
         ↓
processed_data/ (787 processed CSV files)
         ↓
 train_model.py (Random Forest Model)
         ↓
  [Top-N Stock Recommendations]
         ↓
auth.py + domestic.py (KIS OpenAPI)
         ↓
  Automated Buy Orders
```

## 📁 Project Structure

```
Quant-Investment/
├── main.py                      # CLI entry point for orchestration
├── scrap.py                     # Web scraping historical stock data
├── preprocess.py                # Feature engineering & technical indicators
├── train_model.py               # Model training & stock recommendations
├── auth.py                      # KIS OpenAPI authentication
├── domestic.py                  # KIS OpenAPI trading operations
├── data_organize.py             # Utility for data organization
├── config.yaml                  # API credentials & configuration
├── training_workflow.ipynb      # Jupyter notebook demonstration
├── chromedriver                 # Selenium WebDriver
├── stock_data/                  # Raw historical stock data (CSV)
├── processed_data/              # Feature-engineered data (CSV)
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Chrome browser (for web scraping)
- Korea Investment API credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Quant-Investment.git
cd Quant-Investment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- pandas
- numpy
- scikit-learn
- beautifulsoup4
- selenium
- requests
- pyyaml

### Configuration

⚠️ **IMPORTANT: Never commit credentials to GitHub!**

1. Copy the template configuration file:
```bash
cp config.example.yaml config.yaml
```

2. Edit `config.yaml` and add your KIS API credentials:
```yaml
my_app: "YOUR_APP_KEY_HERE"              # Get from https://apiportal.koreainvestment.com/
my_sec: "YOUR_APP_SECRET_HERE"           # Keep this secret!
my_acct: "YOUR_ACCOUNT_FIRST_8_DIGITS"   # e.g., "64428904"
my_prod: "01"                             # 01=real trading, 03=simulation
```

3. The `config.yaml` file is automatically ignored by Git (.gitignore). Never share your credentials!

4. Ensure `chromedriver` is in the project root and is executable.

## 💻 Usage

### Command Line Interface

Run the main orchestration script with various options:

```bash
# Scrape stock data only
python main.py --step scrap

# Preprocess data only
python main.py --step preprocess

# Train model with custom parameters
python main.py --step train --period 30 --threshold 0.1 --topn 5

# Execute full pipeline
python main.py --step all --period 30 --threshold 0.1 --topn 5

# Auto-trade: Execute full pipeline and buy top stocks at specified price
python main.py --step all --period 30 --threshold 0.1 --topn 5 --buy_price 65000
```

### Arguments

- `--step`: Pipeline stage to execute
  - `scrap`: Download historical stock data
  - `preprocess`: Compute technical indicators
  - `train`: Train model and generate recommendations
  - `all`: Execute entire pipeline

- `--period`: Forecast horizon in days (default: 30)
- `--threshold`: Target return threshold as decimal (default: 0.1 = 10%)
- `--topn`: Number of top stocks to recommend (default: 5)
- `--buy_price`: If specified, automatically execute buy orders at this price

### Interactive Notebook

Explore the trading workflow step-by-step:
```bash
jupyter notebook training_workflow.ipynb
```

The notebook demonstrates:
- Single stock analysis
- Target creation (forward return prediction)
- Train/test split
- Random Forest model training
- Model evaluation and performance metrics

## 🔧 Components

### 1. Data Scraping (scrap.py)
- **Source**: stockanalysis.com
- **Method**: Selenium WebDriver with headless Chrome
- **Coverage**: 11 market sectors including:
  - Financials, Healthcare, Technology, Industrials
  - Consumer Discretionary, Materials, Real Estate
  - Communication Services, Energy, Consumer Staples, Utilities
- **Output**: OHLCV (Open, High, Low, Close, Volume) CSV files

### 2. Data Preprocessing (preprocess.py)
Computes 13 technical indicators for each stock:

**Momentum Indicators:**
- Daily Return
- MACD (EMA12 - EMA26)

**Moving Averages:**
- MA5, MA20, MA50
- EMA12, EMA26

**Volatility:**
- 20-day rolling volatility

**Oscillators:**
- RSI14 (14-period Relative Strength Index)

**Bollinger Bands:**
- Upper, Middle, Lower bands

### 3. Model Training (train_model.py)
- **Algorithm**: Random Forest Classifier
- **Configuration**: 200 trees, max_depth=10
- **Target Variable**: Binary classification
  - 1 = Stock rises ≥ threshold% within N days
  - 0 = Stock rises < threshold%
- **Data**: All 787 preprocessed stock files
- **Validation**: 80% training, 20% testing (temporal split)
- **Output**: Probability predictions and top-N stock recommendations

### 4. KIS OpenAPI Integration

**Authentication (auth.py):**
- OAuth2 token generation with 24-hour expiration
- Token caching to minimize re-authentication
- Automatic refresh within 6-hour window
- Error handling for API failures

**Trading Operations (domestic.py):**
- Place cash buy/sell orders
- Modify/cancel existing orders
- Query available buying power
- Account balance and portfolio management

### 5. Orchestration (main.py)
Central CLI interface that:
- Manages workflow execution
- Handles parameter validation
- Coordinates module interactions
- Provides flexible execution modes

## 📈 Model Performance

Example performance on AAPL stock (1981-2024 data, 10,965+ rows):
- **Accuracy**: 73.4%
- **Precision (Rise prediction)**: 38%
- **Recall (Rise prediction)**: 1%

*Note: Current model has class imbalance bias (predicts no-rise more frequently). Consider rebalancing techniques (SMOTE, class weights) for production use.*

## 📊 Data Characteristics

- **Stock Universe**: ~787 stocks across 11 sectors
- **Time Span**: Historical data spanning decades (e.g., AAPL: 1981-2024)
- **Raw Data Size**: ~319 MB (787 CSV files)
- **Processed Data Size**: ~1.4 GB (with 13 computed features)
- **Data Format**: CSV with OHLCV and computed indicators

## ⚠️ Important Notes

### Real Trading Disclaimer
- This system executes **real trades** with actual money via KIS OpenAPI
- The model performance (73% accuracy on historical data) does not guarantee future profitability
- Past performance is not indicative of future results
- **Use with caution** and proper risk management
- Consider paper trading first in simulation mode

### Production Considerations
- **Class Imbalance**: Consider SMOTE or class weight adjustments
- **Hyperparameter Tuning**: Test different thresholds, periods, and model configurations
- **Market Regime Changes**: Model may underperform during market shocks
- **Slippage & Commissions**: Account for trading costs not included in backtests
- **Risk Management**: Implement position sizing and stop-loss logic

## 🔄 Trading Workflow

1. **Data Collection**: Scrape latest historical data from web
2. **Feature Extraction**: Compute technical indicators
3. **Model Inference**: Generate stock rise probability for each stock
4. **Ranking**: Sort by prediction probability and select top-N
5. **Order Execution**: Place buy orders through KIS API at specified price
6. **Monitoring**: Track portfolio performance and model predictions

## 📝 Configuration Example

```yaml
# config.yaml
kis:
  app_key: "ps0000001234567890123456789012"
  app_secret: "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
  account_number: "50083401"
  product_code: "01"  # 01=real trading, 00=simulation

trading:
  sector: "all"
  max_stocks: 5
  order_type: "buy"
```

## 🛠️ Development

### Running Tests
```bash
# Single module execution
python scrap.py
python preprocess.py
python train_model.py
```

### Debugging
Enable verbose logging by modifying the respective Python files:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 References

- [Korea Investment OpenAPI Documentation](https://apiportal.koreainvestment.com/)
- [stockanalysis.com](https://stockanalysis.com)
- [scikit-learn Random Forest](https://scikit-learn.org/stable/modules/ensemble.html#random-forests)
- [Technical Analysis Indicators](https://en.wikipedia.org/wiki/Technical_analysis)

## 🔒 Security

- **Never commit `config.yaml` to GitHub** - It's automatically ignored by `.gitignore`
- **Never share API keys or account numbers** in issues, PRs, or discussions
- If credentials are accidentally exposed:
  1. Immediately regenerate your KIS API keys
  2. Change your account settings
  3. Contact Korea Investment customer support
- Use `config.example.yaml` as a template for setup instructions

## 📄 License

[Add your license information here]

## 👤 Author

[Your Name]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚡ Troubleshooting

### ChromeDriver Issues
```bash
# Make sure chromedriver is executable
chmod +x chromedriver

# Or update to match your Chrome version
# Download from: https://chromedriver.chromium.org/
```

### API Authentication Errors
- Verify credentials in `config.yaml`
- Check KIS API key expiration
- Ensure account has sufficient buying power

### Data Missing or Corrupted
```bash
# Re-scrape data
python main.py --step scrap

# Re-preprocess
python main.py --step preprocess
```

### Model Performance Issues
- Try different `--threshold` and `--period` values
- Adjust Random Forest hyperparameters in `train_model.py`
- Check for missing or NaN values in processed data

---

**Last Updated**: October 2025

For issues or questions, please open a GitHub issue or contact the maintainers.
