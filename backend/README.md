# Indonesian Stock Prediction Backend

AI-powered stock prediction system for Indonesian stocks (IDX) using machine learning. This backend provides REST APIs for stock data fetching, model training, and price predictions. Built with quantitative analysis techniques inspired by Microsoft Qlib.

## Features

- **Stock Data Fetching**: Real-time and historical data for Indonesian stocks
- **AI Predictions**: Machine learning models using Qlib and Gradient Boosting
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, etc.
- **User Settings**: Save and manage user preferences
- **RESTful API**: FastAPI-based endpoints for easy integration
- **Indonesian Market**: Support for IDX stocks (BBCA, BMRI, TLKM, etc.)

## Tech Stack

- **Python 3.9+**
- **FastAPI**: Web framework
- **scikit-learn**: Machine learning models (Gradient Boosting)
- **LightGBM & XGBoost**: Advanced ML algorithms
- **yfinance**: Stock data fetching
- **Pandas/NumPy**: Data processing
- **Quantitative Analysis**: Techniques inspired by Microsoft Qlib

## Project Structure

```
backend/
├── api/
│   ├── routes/
│   │   ├── stock.py          # Stock-related endpoints
│   │   ├── prediction.py     # Prediction endpoints
│   │   └── settings.py       # Settings endpoints
│   └── models.py             # Pydantic models
├── services/
│   ├── stock_data_fetcher.py # Fetch stock data from Yahoo Finance
│   ├── qlib_handler.py       # Qlib integration
│   ├── predictor.py          # ML prediction service
│   └── settings_manager.py   # User settings management
├── config.py                 # Configuration settings
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd backend
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Create directories

```bash
mkdir -p data qlib_data models logs user_settings
```

## Configuration

Edit `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# CORS (Update with your frontend URL)
ALLOWED_ORIGINS=http://localhost:3000,https://your-netlify-app.netlify.app

# Data directories
DATA_DIR=./data
QLIB_DATA_DIR=./qlib_data
MODEL_DIR=./models

# Stock Market
DEFAULT_MARKET=IDX
STOCK_SUFFIX=.JK
```

## Running the Application

### Quick Start (Using run.sh)

```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root & Health

```http
GET /                  # API info
GET /health           # Health check
```

### Stock Endpoints

```http
GET  /api/stock/available              # List available stocks
POST /api/stock/info                   # Get stock information
POST /api/stock/history                # Get historical data
GET  /api/stock/validate/{symbol}      # Validate stock symbol
```

### Prediction Endpoints

```http
POST /api/prediction/predict           # Predict stock prices
POST /api/prediction/train             # Train model for stock
GET  /api/prediction/model-status/{symbol}  # Get model status
```

### Settings Endpoints

```http
POST /api/settings/save                # Save user settings
GET  /api/settings/get                 # Get user settings
PUT  /api/settings/update              # Update settings
DELETE /api/settings/delete            # Delete settings
```

## Usage Examples

### Get Stock Information

```bash
curl -X POST "http://localhost:8000/api/stock/info" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BBCA"}'
```

Response:
```json
{
  "symbol": "BBCA",
  "name": "Bank Central Asia",
  "current_price": 8525.0,
  "change": 75.0,
  "change_percent": 0.89,
  "volume": 12500000
}
```

### Predict Stock Price

```bash
curl -X POST "http://localhost:8000/api/prediction/predict" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BBCA", "days": 5}'
```

Response:
```json
{
  "symbol": "BBCA",
  "current_price": 8525.0,
  "predictions": [
    {"date": "2024-01-15", "price": 8575.25, "confidence": 0.85},
    {"date": "2024-01-16", "price": 8620.50, "confidence": 0.80}
  ],
  "trend": "up",
  "confidence": 0.82,
  "generated_at": "2024-01-14T10:30:00"
}
```

### Save User Settings

```bash
curl -X POST "http://localhost:8000/api/settings/save" \
  -H "Content-Type: application/json" \
  -d '{
    "default_stock": "BBCA",
    "prediction_days": 5,
    "notification_enabled": false
  }'
```

## Training Models

### Train Single Stock

```bash
curl -X POST "http://localhost:8000/api/prediction/train?symbol=BBCA"
```

### Train All Stocks (Batch)

```bash
python train_all.py
```

This will train models for all supported Indonesian stocks. Takes approximately 1-2 hours.

## Testing

Run the test script:

```bash
python test_api.py
```

This will test all API endpoints and display results.

## Supported Indonesian Stocks

The system supports 20+ major Indonesian stocks including:

- **BBCA**: Bank Central Asia
- **BMRI**: Bank Mandiri
- **BBRI**: Bank BRI
- **TLKM**: Telkom Indonesia
- **ASII**: Astra International
- **UNVR**: Unilever Indonesia
- And more...

See `config.py` for the complete list.

## Model Details

### Features Used

The prediction model uses the following technical indicators:

- **Returns**: Daily and log returns
- **Moving Averages**: MA5, MA10, MA20, MA60
- **Volatility**: 20-day rolling standard deviation
- **Volume Indicators**: Volume MA5, MA20
- **Momentum**: 5-day price momentum
- **RSI**: Relative Strength Index (14-day)
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Upper, middle, lower bands

### Algorithm

- **Primary Model**: Gradient Boosting Regressor
- **Training Period**: 5 years of historical data
- **Prediction Horizon**: 1-30 days
- **Confidence Score**: Decreases with longer horizons

## Deployment

### Docker (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t stock-predictor-backend .
docker run -p 8000:8000 stock-predictor-backend
```

### Cloud Deployment

#### AWS EC2
1. Launch EC2 instance (t2.medium or larger)
2. Install Python and dependencies
3. Run the application
4. Setup nginx as reverse proxy
5. Use PM2 or systemd for process management

#### Google Cloud Run
1. Build Docker image
2. Push to Container Registry
3. Deploy to Cloud Run
4. Configure environment variables

#### DigitalOcean App Platform
1. Connect GitHub repository
2. Configure build settings
3. Deploy automatically

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| API_HOST | Server host | 0.0.0.0 |
| API_PORT | Server port | 8000 |
| ENVIRONMENT | Environment mode | development |
| ALLOWED_ORIGINS | CORS origins | localhost:3000 |
| MODEL_TYPE | Model algorithm | lightgbm |
| TRAINING_PERIOD | Training data period (days) | 1825 |
| PREDICTION_HORIZON | Max prediction days | 5 |

## Troubleshooting

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Dependencies installation fails

```bash
# Upgrade pip
pip install --upgrade pip
# Install with verbose
pip install -r requirements.txt -v
```

### No data for stock

- Check if stock symbol is correct (use Yahoo Finance format: BBCA.JK)
- Verify internet connection
- Try different stock symbol

### Model training fails

- Ensure sufficient historical data is available
- Check if data directory has write permissions
- Verify enough disk space for model files

## Performance Tips

1. **Cache**: Models and scalers are cached in memory
2. **Batch Processing**: Train multiple stocks using `train_all.py`
3. **Concurrent Requests**: FastAPI handles async requests efficiently
4. **Model Updates**: Retrain models weekly for best accuracy

## Security

- Configure CORS properly for production
- Use HTTPS in production
- Implement API authentication (JWT recommended)
- Rate limiting for API endpoints
- Validate all user inputs

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

MIT License - see LICENSE file

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` folder

## Acknowledgments

- Microsoft Qlib team
- Yahoo Finance API
- FastAPI community
- Indonesian Stock Exchange (IDX)

---

Built with ❤️ for Indonesian stock market analysis
