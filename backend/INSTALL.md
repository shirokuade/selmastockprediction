# Installation Guide

## Python Version Compatibility

| Python Version | Status | Recommendation |
|---------------|--------|----------------|
| 3.13.x | ⚠️ Partial | Some packages may need compilation |
| 3.12.x | ✅ Recommended | Fully supported, all packages work |
| 3.11.x | ✅ Recommended | Fully supported, all packages work |
| 3.10.x | ✅ Supported | Works well |
| 3.9.x | ✅ Supported | Works well |
| 3.8.x | ⚠️ End of life | Not recommended |

## Installation Instructions

### For Python 3.11 or 3.12 (Recommended)

```bash
cd backend

# Check your Python version
python3.12 --version  # or python3.11 --version

# Create virtual environment
python3.12 -m venv venv  # or python3.11

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### For Python 3.13 (Current Issue)

Python 3.13 is very new and some packages don't have pre-built wheels yet. You have two options:

#### Option A: Switch to Python 3.12 (Easiest)

```bash
# Install Python 3.12 via Homebrew (macOS)
brew install python@3.12

# Create virtual environment with 3.12
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Install Build Tools for Python 3.13

```bash
# Install build tools (macOS)
brew install gcc cmake

# Create virtual environment
cd backend
python3.13 -m venv venv
source venv/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Try alternative requirements
pip install -r requirements-py313.txt
```

#### Option C: Install packages one by one

```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install packages that work first
pip install fastapi uvicorn pydantic pydantic-settings
pip install yfinance requests pandas numpy
pip install python-dotenv loguru aiofiles

# Try ML packages (may take time to compile)
pip install lightgbm  # Usually works
pip install scikit-learn  # May need to compile
pip install xgboost  # May need to compile
```

## Verification

After installation, verify everything works:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify key packages
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import sklearn; print(f'scikit-learn: {sklearn.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python -c "import yfinance; print('yfinance: OK')"
```

## Running the Application

```bash
cd backend

# Make sure virtual environment is activated
source venv/bin/activate

# Copy environment file
cp .env.example .env

# Run the application
python main.py
```

The API will be available at: http://localhost:8000

## Troubleshooting

### Error: "No module named 'sklearn'"

```bash
pip install scikit-learn
```

### Error: "Cython compilation error"

This means a package needs to compile from source. Solutions:

1. Use Python 3.11 or 3.12 instead (recommended)
2. Install build tools:
   ```bash
   # macOS
   brew install gcc cmake
   xcode-select --install

   # Ubuntu/Debian
   sudo apt-get install build-essential python3-dev

   # Windows
   # Install Visual Studio Build Tools
   ```

### Error: "Could not find a version that satisfies"

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Try installing with no cache
pip install --no-cache-dir -r requirements.txt
```

### Packages install but import fails

```bash
# Reinstall in virtual environment
deactivate
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Alternative: Docker Installation

If you're having persistent issues, use Docker:

```bash
cd backend

# Build Docker image
docker build -t stock-predictor .

# Run container
docker run -p 8000:8000 stock-predictor
```

## Need Help?

If you continue to have issues:

1. **Check Python version**: `python --version` (use 3.11 or 3.12)
2. **Use virtual environment**: Always activate venv before installing
3. **Upgrade pip**: `pip install --upgrade pip`
4. **Check error messages**: Read the full error output
5. **Try Docker**: Use containerization to avoid dependency issues

## System Requirements

- **Python**: 3.9 - 3.12 (3.11/3.12 recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space for dependencies and data
- **OS**: macOS, Linux, or Windows 10+
- **Internet**: Required for downloading stock data
