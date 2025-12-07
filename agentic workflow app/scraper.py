import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Configures Chrome to look like a real user to avoid immediate blocking."""
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--start-maximized')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    return webdriver.Chrome(options=options)

def run_scraper(asin, review_limit=10):
    """
    Orchestrates the entire scraping process for a single ASIN.
    Returns a dictionary containing product metadata and reviews.
    """
    driver = setup_driver()
    product_data = {
        "title": "Unknown Product",
        "features": [],
        "reviews": []
    }
    
    try:
        # Step 1: Manual Login (Critical for Amazon)
        print("[Scraper]: Opening Amazon Login Page...")
        driver.get("https://www.amazon.com/ap/signin")
        
        # We allow 45 seconds for the user to manually log in if prompted.
        # If already logged in or no captcha, this wait ensures the session is stable.
        print("[Scraper]: Waiting 45 seconds for manual login/verification...")
        time.sleep(45) 
        
        # Step 2: Scrape Product Details (Title & Features)
        print(f"[Scraper]: Navigating to Product Page {asin}...")
        driver.get(f"https://www.amazon.com/dp/{asin}")
        time.sleep(3)
        
        # Extract Title
        try:
            product_data["title"] = driver.find_element(By.ID, "productTitle").text.strip()
        except:
            print("[Scraper Warning]: Could not find product title.")

        # Extract Feature Bullets
        try:
            feature_element = driver.find_element(By.ID, "feature-bullets")
            items = feature_element.find_elements(By.TAG_NAME, "li")
            product_data["features"] = [item.text.strip() for item in items if item.text.strip()]
        except:
            print("[Scraper Warning]: Could not find feature bullets.")

        # Step 3: Scrape Reviews
        print("[Scraper]: Navigating to Reviews Page...")
        driver.get(f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=1")
        time.sleep(3)
        
        review_elements = driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")
        
        for element in review_elements[:review_limit]:
            try:
                # Extract Body
                body = element.find_element(By.CSS_SELECTOR, "[data-hook='review-body']").text.strip()
                
                # Extract Title (optional but good for context)
                try:
                    title = element.find_element(By.CSS_SELECTOR, "[data-hook='review-title']").text.split('\n')[-1]
                except:
                    title = ""
                    
                if body:
                    product_data["reviews"].append({
                        "title": title,
                        "body": body
                    })
            except:
                continue
                
        print(f"[Scraper]: Successfully scraped {len(product_data['reviews'])} reviews.")

    except Exception as e:
        print(f"[Scraper Error]: {e}")
        return None
    finally:
        driver.quit()
        
    return product_data