# 🚗 AutoZoeker - Car Search Website

A web application that scrapes and displays car listings from Dutch car websites.

## 📸 Screenshot

![AutoZoeker Main Interface](screenshot.png)

## 🚀 Features

- **Web Scraping**: Automatically scrapes car data from Gaspedaal.nl
- **Data Enrichment**: Adds price estimates from ANWB and details from Finnik
- **AI Analysis**: Uses deepseek to analyze car value and condition
- **Web Interface**: Beautiful React frontend with sorting

## 🛠️ Development Setup

### Backend
```bash
cd backend
npm install
npm run dev
```

### Frontend  
```bash
cd frontend
npm install
npm run dev
```

### Scraper
```bash
cd scraper
pip install -r requirements.txt
python main.py scrape normalize
```

## 📊 How It Works

1. **Scraper** fetches car listings from Gaspedaal.nl
2. **Normalizer** enriches data with ANWB prices and Finnik details
3. **AI Analyzer** evaluates each car's value proposition
4. **Backend API** serves the processed data
5. **Frontend** displays cars with sorting options

## 🔧 Configuration

- Update cookies in `scraper/main.py` monthly for Gaspedaal access
- Set OpenAI API key in `.env` for AI analysis features
- Modify search URL in `main.py` to change car criteria
