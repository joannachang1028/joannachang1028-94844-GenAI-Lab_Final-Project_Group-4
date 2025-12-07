# Final Project: Generating Product Image from Customer Reviews

## Project Overview

This project implements Q1 and Q2 of the Final Project:
- **Q1**: Product Selection and Customer Review Data Collection
- **Q2**: Analysis of Customer Reviews with LLM

For detailed analysis results, see `Q2_Analysis_Report.md`.

## Project Structure

```
Final Project/
├── main_Back and Neck Massager.py  # Main Python script for Back and Neck Massager (Q1 & Q2)
├── requirements.txt            # Python dependencies
├── .evn                        # OpenAI API key (not tracked in git)
├── README.md                   # This file
├── Analysis_Report_Back and Neck Massager.md    # Analysis report
├── SELENIUM_SETUP.md           # Selenium setup guide
└── data/                       # Output directory
    ├── product_info.json           # Product selection info
    ├── product_description.json    # Scraped product description
    ├── customer_reviews.json       # Collected reviews (50 reviews)
    ├── visual_features.json        # Extracted visual features
    ├── product_features.json       # Extracted product features
    ├── sentiment_analysis.json     # Sentiment analysis results
    ├── extracted_topics.json       # Topic extraction results
    └── image_generation_summary.json  # Summary for Q3
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.evn` file with your OpenAI API key:
```
OPENAI_API=your_api_key_here
```

### 3. Install ChromeDriver (for Selenium)

```bash
# macOS
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/downloads
```

## How to Run

### Option 1: Run Complete Script

```bash
python main.py
```

### Option 2: Run Step-by-Step (Recommended)

Open `main.py` in VS Code or Jupyter. Each `#%%` block can be executed independently:

1. **Step 0**: Setup and Configuration
2. **Q1-1**: Product Selection
3. **Q1-2**: Collect Product Description
4. **Q1-3**: Collect Customer Reviews (Selenium)
5. **Q2-1**: Load Data
6. **Q2-2**: Visual Feature Extraction
7. **Q2-3**: Product Feature Extraction
8. **Q2-4**: Sentiment Analysis
9. **Q2-5**: Topic Extraction
10. **Q2-6**: Image Generation Summary

## Configuration Options

In `main.py`, you can adjust these settings:

```python
USE_SELENIUM_SCRAPING = True   # True: scrape reviews, False: use existing data
MAX_PAGES = 5                  # Number of review pages to scrape
LOGIN_TIMEOUT = 60             # Seconds to wait for manual Amazon login
HEADLESS_MODE = False          # Must be False for manual login
```

## Notes

- **Amazon Login**: The browser will open for manual login (60 seconds timeout)
- **LLM Model**: Uses `gpt-5.1` for all review analysis and summarization steps
- **Data**: All outputs are saved in the `data/` directory
