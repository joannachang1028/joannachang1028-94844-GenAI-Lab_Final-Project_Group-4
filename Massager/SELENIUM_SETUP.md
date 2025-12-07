# Selenium Web Scraping Setup Guide

## Install ChromeDriver

Selenium requires ChromeDriver to control the Chrome browser. Please install it according to your system:

### macOS

```bash
# Install using Homebrew
brew install chromedriver

# Or download manually
# 1. Visit https://chromedriver.chromium.org/downloads
# 2. Download ChromeDriver matching your Chrome version
# 3. Extract and move to PATH directory, or place in project directory
```

### Windows

1. Visit https://chromedriver.chromium.org/downloads
2. Download ChromeDriver matching your Chrome browser version
3. Extract `chromedriver.exe` to system PATH or project directory

### Linux

```bash
sudo apt-get install chromium-chromedriver
# or
sudo yum install chromium-chromedriver
```

## Verify Installation

After installation, run the following command to verify:

```bash
chromedriver --version
```

## Using the Scraping Feature

### 1. Install Python Packages

```bash
pip install -r requirements.txt
```

This will install `selenium` and other dependencies.

### 2. Configure Scraping Settings

Find the following block in `main.py` and adjust the settings:

```python
USE_SELENIUM_SCRAPING = True   # True = Execute scraping
MAX_PAGES = 5                   # Number of pages to scrape (approximately 10 reviews per page)
HEADLESS_MODE = False          # False = Display browser, True = Background execution
DELAY_BETWEEN_PAGES = 4.0      # Delay between pages (seconds)
```

### 3. Execute Scraping

Run the main program:

```bash
python main.py
```

Or use interactive mode to execute the scraping block (blocks marked with `#%%`).

## Important Notes

### ⚠️ Important Reminders

1. **Comply with Terms of Service**: Please ensure your usage complies with Amazon's terms of service
2. **Rate Limiting**: Set appropriate delays (recommended 3-5 seconds) to avoid being blocked
3. **CAPTCHA**: If you encounter CAPTCHA, manual handling is required
4. **IP Blocking**: Frequent requests may result in IP blocking

### Recommended Settings

- **First-time Testing**: Set `HEADLESS_MODE = False` to observe browser behavior
- **Large-scale Scraping**: Set `HEADLESS_MODE = True` and increase `DELAY_BETWEEN_PAGES`
- **When Blocked**: Increase delay time or pause scraping

### Troubleshooting

**Issue: ChromeDriver Not Found**
- Verify ChromeDriver is installed and in PATH
- Or specify ChromeDriver path:
  ```python
  from selenium.webdriver.chrome.service import Service
  service = Service('/path/to/chromedriver')
  driver = webdriver.Chrome(service=service, options=chrome_options)
  ```

**Issue: Browser Version Mismatch**
- Ensure ChromeDriver version matches your Chrome browser version
- Update Chrome or download the corresponding ChromeDriver version

**Issue: Blocked by Amazon**
- Increase delay time
- Use a realistic User-Agent
- Consider using a proxy server
- Manually handle CAPTCHA and continue

## Alternative Solutions

If Selenium scraping cannot be used, consider:

1. **Manual Collection**: Manually copy reviews from Amazon pages
2. **Amazon API**: Apply for Amazon Product Advertising API
3. **Third-party Services**: Use specialized review collection services
