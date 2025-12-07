"""
Final Project: Generating Product Image from Customer Reviews
Q1: Product Selection and Customer Review Data Collection
Q2: Analysis of Customer Reviews with LLM
"""

#%%
# ============================================================================
# Step 0: Imports and Configuration
# ============================================================================

import os
import json
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load environment variables
# Uses standard .env file at project root, as documented in README
load_dotenv('.env')
openai_api_key = os.getenv('OPENAI_API')
if not openai_api_key:
    raise ValueError("OpenAI API key not found in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Configuration
PRODUCT_URL = "https://www.amazon.com/gp/product/B0BYTNTGLY/ref=ewc_pr_img_1?smid=A2XRWKFPKCTI0V&th=1"
PRODUCT_ASIN = "B0BYTNTGLY"
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Headers for web scraping
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

print("✅ Setup complete!")
print(f"   Product ASIN: {PRODUCT_ASIN}")

#%%
# ============================================================================
# Step 1: Helper Functions
# ============================================================================

def extract_product_description(url: str) -> Dict:
    """Extract product description from Amazon product page."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product title
        title_elem = soup.find('span', {'id': 'productTitle'})
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        
        # Extract features from "About this item" section
        features = []
        about_section = soup.find('div', {'id': 'feature-bullets'})
        if about_section:
            feature_list = about_section.find_all('li', class_='a-spacing-mini')
            features = [li.get_text(strip=True) for li in feature_list if li.get_text(strip=True)]
        
        # Extract product details table
        product_details = {}
        details_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
        if details_table:
            for row in details_table.find_all('tr'):
                th, td = row.find('th'), row.find('td')
                if th and td:
                    product_details[th.get_text(strip=True)] = td.get_text(strip=True)
        
        # Extract price
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        price = price_elem.get_text(strip=True) if price_elem else "N/A"
        
        return {
            "title": title,
            "features": features,
            "product_details": product_details,
            "price": price,
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error extracting product description: {e}")
        # Fallback data
        return {
            "title": "Zyllion Shiatsu Back and Neck Massager with Heat - 3D Electric Kneading Deep Tissue Massage Pillow for Muscle Pain Relief, Brown, ZMA-13",
            "features": [
                "Advanced 3D Deep Tissue Massage: Ease sore and stiff muscles with two soft silicone nodes on each side",
                "Recommended by Doctors of Physical Therapy",
                "Ergonomic & Versatile: Fits your body's contours: arms, hands, legs and even feet",
                "Tested & Certified: Built with safety in mind, heat function has overheat protection",
                "Warranty Coverage: Includes an automatic 1-year warranty"
            ],
            "product_details": {
                "Use for": "Back, Feet, Legs, Neck, Whole Body",
                "Power Source": "Corded Electric",
                "Material": "Faux Leather",
                "Item Weight": "3.9 Pounds",
                "Brand": "Zyllion"
            },
            "price": "N/A",
            "scraped_at": datetime.now().isoformat(),
            "note": "Fallback data used due to scraping limitations"
        }


def setup_selenium_driver(headless: bool = False) -> webdriver.Chrome:
    """Setup Selenium Chrome driver with anti-detection settings."""
    chrome_options = Options()
    
    # Anti-detection settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
        })
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        print("   Install ChromeDriver: brew install chromedriver (macOS)")
        raise


def extract_rating_from_review(review_element) -> Optional[int]:
    """Extract star rating from review element."""
    try:
        rating_elem = review_element.find_element(
            By.CSS_SELECTOR, '[data-hook="review-star-rating"], .a-icon-alt, span.a-icon-alt'
        )
        rating_text = rating_elem.get_attribute('textContent') or rating_elem.text
        rating_match = re.search(r'(\d+)', rating_text)
        if rating_match:
            return int(rating_match.group(1))
    except NoSuchElementException:
        pass
    return None


def extract_review_data(review_element, review_index: int) -> Optional[Dict]:
    """Extract all data from a single review element."""
    try:
        review_id = review_element.get_attribute('id') or f"review_{review_index}"
        rating = extract_rating_from_review(review_element)
        
        # Review title
        try:
            title_elem = review_element.find_element(By.CSS_SELECTOR, '[data-hook="review-title"] span:not(.a-icon-alt)')
            review_title = title_elem.text.strip()
        except NoSuchElementException:
            review_title = ""
        
        # Review body
        try:
            body_elem = review_element.find_element(By.CSS_SELECTOR, '[data-hook="review-body"] span')
            review_body = body_elem.text.strip()
        except NoSuchElementException:
            review_body = ""
        
        # Reviewer name
        try:
            name_elem = review_element.find_element(By.CSS_SELECTOR, '.a-profile-name, [data-hook="review-author"]')
            reviewer_name = name_elem.text.strip()
        except NoSuchElementException:
            reviewer_name = "Anonymous"
        
        # Review date
        try:
            date_elem = review_element.find_element(By.CSS_SELECTOR, '[data-hook="review-date"]')
            review_date = date_elem.text.strip()
            date_match = re.search(r'(\w+\s+\d+,\s+\d{4})', review_date)
            if date_match:
                review_date = date_match.group(1)
        except NoSuchElementException:
            review_date = ""
        
        # Verified purchase
        verified_purchase = False
        try:
            review_element.find_element(By.CSS_SELECTOR, '[data-hook="avp-badge"]')
            verified_purchase = True
        except NoSuchElementException:
            pass
        
        # Helpful count
        helpful_count = 0
        try:
            helpful_elem = review_element.find_element(By.CSS_SELECTOR, '[data-hook="helpful-vote-statement"]')
            helpful_match = re.search(r'(\d+)', helpful_elem.text)
            if helpful_match:
                helpful_count = int(helpful_match.group(1))
        except NoSuchElementException:
            pass
        
        if review_body or review_title:
            return {
                "review_id": review_id,
                "rating": rating,
                "review_title": review_title,
                "review_body": review_body,
                "reviewer_name": reviewer_name,
                "review_date": review_date,
                "verified_purchase": verified_purchase,
                "helpful_count": helpful_count
            }
    except Exception as e:
        print(f"   ⚠️  Error extracting review data: {e}")
    return None


def collect_amazon_reviews(asin: str, max_pages: int = 5, headless: bool = False, 
                          delay: float = 3.0, login_timeout: int = 60) -> List[Dict]:
    """
    Collect customer reviews from Amazon using Selenium.
    Opens browser for manual login, then scrapes reviews.
    """
    print(f"\n📝 Collecting reviews for ASIN: {asin}")
    print(f"   Max pages: {max_pages} | Login timeout: {login_timeout}s")
    
    reviews = []
    driver = None
    
    try:
        print("\n🔧 Setting up Selenium Chrome driver...")
        driver = setup_selenium_driver(headless=headless)
        
        # Navigate to Amazon login page
        print("\n" + "="*60)
        print("🔐 AMAZON LOGIN")
        print(f"   You have {login_timeout} seconds to login manually.")
        print("="*60)
        
        driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
        
        # Wait for user to login
        print(f"\n⏳ Waiting {login_timeout} seconds for login...")
        for remaining in range(login_timeout, 0, -10):
            print(f"   ⏰ {remaining} seconds remaining...")
            time.sleep(10)
        
        print("\n✅ Continuing with scraping...")
        
        # URL formats to try
        url_formats = [
            lambda a, p: f"https://www.amazon.com/product-reviews/{a}/" if p == 1 else f"https://www.amazon.com/product-reviews/{a}/?pageNumber={p}",
            lambda a, p: f"https://www.amazon.com/product-reviews/{a}/?ie=UTF8&reviewerType=all_reviews" if p == 1 else f"https://www.amazon.com/product-reviews/{a}/?ie=UTF8&reviewerType=all_reviews&pageNumber={p}",
            lambda a, p: f"https://www.amazon.com/product-reviews/{a}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews" if p == 1 else f"https://www.amazon.com/product-reviews/{a}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&pageNumber={p}",
        ]
        
        # Find working URL format
        print(f"\n🔍 Finding working review page URL format...")
        working_url_format = None
        
        for idx, url_func in enumerate(url_formats, 1):
            test_url = url_func(asin, 1)
            print(f"   Testing format {idx}...")
            
            try:
                driver.get(test_url)
                time.sleep(5)
                
                current_url = driver.current_url.lower()
                if 'signin' in current_url or 'ap/signin' in current_url:
                    continue
                
                driver.execute_script("window.scrollTo(0, 300);")
                time.sleep(2)
                review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review"]')
                
                if review_elements:
                    print(f"   ✅ Format {idx} works! Found {len(review_elements)} reviews.")
                    working_url_format = url_func
                    break
            except Exception:
                continue
        
        if not working_url_format:
            print(f"\n❌ Could not find working URL format. Login may have failed.")
            return []
        
        # Scrape all pages
        for page in range(1, max_pages + 1):
            print(f"\n📄 Scraping page {page}/{max_pages}...")
            review_url = working_url_format(asin, page)
            
            try:
                driver.get(review_url)
                time.sleep(5)
                
                if 'signin' in driver.current_url.lower():
                    print(f"   ⚠️  Redirected to login. Stopping.")
                    break
                
                # Scroll to load content
                for scroll_y in [500, 1000, 0]:
                    driver.execute_script(f"window.scrollTo(0, {scroll_y});")
                    time.sleep(2)
                
                # Find reviews
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="review"]'))
                    )
                except TimeoutException:
                    pass
                
                review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review"]')
                
                if not review_elements:
                    for selector in ['div[data-hook="review"]', '[id*="customer_review"]', '.review']:
                        review_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if review_elements:
                            break
                
                if review_elements:
                    print(f"   ✅ Found {len(review_elements)} reviews")
                    page_reviews = []
                    for i, elem in enumerate(review_elements):
                        data = extract_review_data(elem, len(reviews) + i + 1)
                        if data:
                            page_reviews.append(data)
                    
                    if page_reviews:
                        reviews.extend(page_reviews)
                        print(f"   ✅ Extracted {len(page_reviews)} reviews")
                    elif page == 1:
                        break
                else:
                    if page == 1:
                        break
                
                if page < max_pages:
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)[:80]}")
                if page == 1:
                    break
        
        print(f"\n✅ Total reviews collected: {len(reviews)}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        print(traceback.format_exc())
        
    finally:
        if driver:
            print("🔒 Closing browser...")
            driver.quit()
    
    return reviews


def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> List[str]:
    """Split text into chunks with overlap to preserve context."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end < len(text):
            sentence_end = max(
                text.rfind('.', start, end),
                text.rfind('!', start, end),
                text.rfind('?', start, end)
            )
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def summarize_text_in_chunks(
    text: str,
    chunk_size: int = 3000,
    overlap: int = 200,
    model: str = "gpt-5.1",
) -> str:
    """
    Use chunk_text + LLM to summarize long review text into a shorter,
    consolidated version for downstream analysis.
    """
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    if len(chunks) == 1:
        return text

    print(f"\n🧩 Chunking reviews into {len(chunks)} chunks for summarization...")
    summaries: List[str] = []

    for idx, chunk in enumerate(chunks, start=1):
        print(f"   ✏️ Summarizing chunk {idx}/{len(chunks)}...")
        summary_prompt = f"""
You are an expert at summarizing customer reviews for downstream analytics.

Summarize the following review chunk into a concise paragraph.
Focus on:
- Key opinions
- Visual descriptions of the product
- Any notable pros/cons

Reviews (chunk {idx}/{len(chunks)}):
{chunk}
"""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You create concise, information-dense summaries of customer reviews.",
                    },
                    {"role": "user", "content": summary_prompt},
                ],
                temperature=0.3,
            )
            summaries.append(response.choices[0].message.content.strip())
        except Exception as e:
            # Preserve information even if the LLM call fails for this chunk
            print(f"   ⚠️ Error summarizing chunk {idx}: {e}")
            summaries.append(chunk.strip())

    if not summaries:
        print("⚠️ Chunk summarization failed, falling back to original text.")
        return text

    if len(summaries) != len(chunks):
        print(
            f\"⚠️ Only {len(summaries)}/{len(chunks)} chunks were summarized successfully; "
            "using raw text for failed chunks.\"
        )

    return "\n\n".join(summaries)


def load_collected_data() -> tuple:
    """Load product description and reviews from data files."""
    # Load product description
    try:
        with open(f"{OUTPUT_DIR}/product_description.json", "r", encoding="utf-8") as f:
            product_desc = json.load(f)
    except FileNotFoundError:
        print("⚠️  Product description not found. Extracting...")
        product_desc = extract_product_description(PRODUCT_URL)
    
    # Load reviews
    try:
        with open(f"{OUTPUT_DIR}/customer_reviews.json", "r", encoding="utf-8") as f:
            reviews = json.load(f)
        if reviews:
            return product_desc, reviews
    except FileNotFoundError:
        pass
    
    # Fallback to example reviews
    print("⚠️  Customer reviews not found. Using example data for testing.")
    reviews = [
        {
            "review_id": "R1", "rating": 5,
            "review_title": "Amazing massager!",
            "review_body": "This massager is perfect. The brown faux leather looks elegant and the silicone nodes provide great pressure. Perfect size for my back.",
            "reviewer_name": "Customer1", "review_date": "2024-11-15",
            "verified_purchase": True, "helpful_count": 10
        },
        {
            "review_id": "R2", "rating": 4,
            "review_title": "Good but heats up",
            "review_body": "The massager works well and the heat feature is nice. The brown color matches my office chair. The straps are sturdy.",
            "reviewer_name": "Customer2", "review_date": "2024-11-10",
            "verified_purchase": True, "helpful_count": 5
        }
    ]
    return product_desc, reviews

#%%
# ============================================================================
# Q1-1: Product Selection and Rationale
# ============================================================================

product_info = {
    "name": "Zyllion Shiatsu Back and Neck Massager with Heat",
    "model": "ZMA-13",
    "category": "Health & Household > Massage Tools & Equipment",
    "asin": PRODUCT_ASIN,
    "url": PRODUCT_URL,
    "selection_rationale": """
    1. Visual Descriptiveness: Reviews mention specific design elements (silicone nodes, faux leather, brown color, ergonomic shape)
    2. Popularity: 50+ bought in past month ensures sufficient review data
    3. Category Characteristics: Health products often have detailed visual descriptions
    4. Feature-Rich: Multiple features (heat, 3D massage, straps) that users describe visually
    """
}

print("\n📦 Product Selected:")
print(f"   Name: {product_info['name']}")
print(f"   ASIN: {product_info['asin']}")

with open(f"{OUTPUT_DIR}/product_info.json", "w", encoding="utf-8") as f:
    json.dump(product_info, f, indent=2, ensure_ascii=False)

#%%
# ============================================================================
# Q1-2: Collect Product Description
# ============================================================================

print("\n🔍 Collecting product description...")
product_description = extract_product_description(PRODUCT_URL)

print(f"✅ Product Description Collected:")
print(f"   Title: {product_description['title'][:60]}...")
print(f"   Features: {len(product_description['features'])} items")

with open(f"{OUTPUT_DIR}/product_description.json", "w", encoding="utf-8") as f:
    json.dump(product_description, f, indent=2, ensure_ascii=False)

#%%
# ============================================================================
# Q1-3: Collect Customer Reviews (Selenium Scraping)
# ============================================================================

# Scraping Settings
USE_SELENIUM_SCRAPING = True   # Set False to skip scraping and use existing data
MAX_PAGES = 5                  # Number of pages to scrape (~10 reviews/page)
HEADLESS_MODE = False          # Must be False for manual login
DELAY_BETWEEN_PAGES = 4.0      # Delay between pages (seconds)
LOGIN_TIMEOUT = 60             # Seconds to wait for manual login

if USE_SELENIUM_SCRAPING:
    print("\n🚀 Starting Selenium review scraping...")
    print(f"   Browser will open. You have {LOGIN_TIMEOUT}s to login.")
    
    try:
        collected_reviews = collect_amazon_reviews(
            asin=PRODUCT_ASIN,
            max_pages=MAX_PAGES,
            headless=HEADLESS_MODE,
            delay=DELAY_BETWEEN_PAGES,
            login_timeout=LOGIN_TIMEOUT
        )
        
        if collected_reviews:
            print(f"\n💾 Saving {len(collected_reviews)} reviews...")
            with open(f"{OUTPUT_DIR}/customer_reviews.json", "w", encoding="utf-8") as f:
                json.dump(collected_reviews, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved to: {OUTPUT_DIR}/customer_reviews.json")
        else:
            print("\n⚠️  No reviews collected. Will use existing data if available.")
            
    except Exception as e:
        print(f"\n❌ Scraping error: {e}")
else:
    print("\n⏭️  Skipping scraping. Using existing data.")

#%%
# ============================================================================
# Q2-1: Load Data for Analysis
# ============================================================================

print("\n📂 Loading collected data...")
product_description, customer_reviews = load_collected_data()

if len(customer_reviews) <= 2:
    print(f"⚠️  Only {len(customer_reviews)} reviews (example data).")
    print("   Run scraping to collect real reviews.")
else:
    print(f"✅ Loaded {len(customer_reviews)} reviews")

# Prepare review text for analysis
all_review_text = "\n\n".join([
    f"Rating: {r.get('rating', 'N/A')}/5\nTitle: {r.get('review_title', '')}\n{r.get('review_body', '')}"
    for r in customer_reviews
])

print(f"   Total text: {len(all_review_text)} characters")

# Create a condensed, chunk-aware summary of all reviews for downstream prompts
print("\n🧩 Creating condensed review summary using chunking...")
condensed_review_text = summarize_text_in_chunks(all_review_text)
print(f"   Condensed text length: {len(condensed_review_text)} characters")

#%%
# ============================================================================
# Q2-2: Extract Visual Features using LLM
# ============================================================================

print("\n🎨 Extracting visual features...")

visual_prompt = f"""
Analyze the following customer reviews and extract ALL visual information about the product.

Product: Zyllion Shiatsu Back and Neck Massager with Heat (Model: ZMA-13)

{condensed_review_text}

Extract:
1. Colors mentioned
2. Materials described
3. Size/Dimensions
4. Shape/Design elements
5. Textures
6. Visual features (buttons, straps, etc.)
7. Overall appearance

Format as JSON:
{{
    "colors": ["color1", "color2"],
    "materials": ["material1", "material2"],
    "size_dimensions": ["mention1", "mention2"],
    "shape_design": ["feature1", "feature2"],
    "textures": ["texture1", "texture2"],
    "visual_features": ["feature1", "feature2"],
    "overall_appearance": "summary description"
}}
"""

try:
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are an expert at extracting visual information from product reviews. Always respond with valid JSON."},
            {"role": "user", "content": visual_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    visual_features = json.loads(response.choices[0].message.content)
    print(f"✅ Visual features extracted!")
    print(f"   Colors: {visual_features.get('colors', [])}")
    print(f"   Materials: {visual_features.get('materials', [])}")
    
    with open(f"{OUTPUT_DIR}/visual_features.json", "w", encoding="utf-8") as f:
        json.dump(visual_features, f, indent=2, ensure_ascii=False)
        
except Exception as e:
    print(f"❌ Error: {e}")
    visual_features = {}

#%%
# ============================================================================
# Q2-3: Extract Product Features using LLM
# ============================================================================

print("\n🔍 Extracting product features...")

features_text = "\n".join([f"- {f}" for f in product_description.get('features', [])])

features_prompt = f"""
Analyze the product description and customer reviews to extract key product features.

PRODUCT DESCRIPTION:
Title: {product_description.get('title', 'N/A')}

Key Features:
{features_text}

CUSTOMER REVIEWS:
{condensed_review_text}

Extract:
1. Functional Features (what it does)
2. Design Features (design elements)
3. Material Features
4. Size/Portability
5. Usage Context (where/how used)
6. Key Selling Points

Format as JSON:
{{
    "functional_features": ["feature1", "feature2"],
    "design_features": ["feature1", "feature2"],
    "material_features": ["feature1", "feature2"],
    "size_portability": "description",
    "usage_context": ["context1", "context2"],
    "key_selling_points": ["point1", "point2"]
}}
"""

try:
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are an expert at analyzing products. Always respond with valid JSON."},
            {"role": "user", "content": features_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    product_features = json.loads(response.choices[0].message.content)
    print("✅ Product features extracted!")
    
    with open(f"{OUTPUT_DIR}/product_features.json", "w", encoding="utf-8") as f:
        json.dump(product_features, f, indent=2, ensure_ascii=False)
        
except Exception as e:
    print(f"❌ Error: {e}")
    product_features = {}

#%%
# ============================================================================
# Q2-4: Sentiment Analysis using LLM
# ============================================================================

print("\n😊 Analyzing sentiment...")

reviews_summary = "\n\n".join([
    f"Review {i+1} (Rating: {r.get('rating', 'N/A')}/5):\n{r.get('review_body', '')}"
    for i, r in enumerate(customer_reviews[:20])
])

sentiment_prompt = f"""
Analyze the sentiment of these customer reviews for a massager product.

{reviews_summary}

Provide:
1. Overall sentiment distribution (positive/neutral/negative percentages)
2. Common positive themes
3. Common negative themes
4. Sentiment towards visual aspects
5. Overall satisfaction score (1-10)

Format as JSON:
{{
    "overall_sentiment": {{
        "positive": percentage,
        "neutral": percentage,
        "negative": percentage
    }},
    "positive_themes": ["theme1", "theme2"],
    "negative_themes": ["theme1", "theme2"],
    "visual_sentiment": "description",
    "satisfaction_score": number
}}
"""

try:
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are an expert at sentiment analysis. Always respond with valid JSON."},
            {"role": "user", "content": sentiment_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    sentiment_analysis = json.loads(response.choices[0].message.content)
    print(f"✅ Sentiment analysis completed!")
    print(f"   Satisfaction Score: {sentiment_analysis.get('satisfaction_score', 'N/A')}/10")
    
    with open(f"{OUTPUT_DIR}/sentiment_analysis.json", "w", encoding="utf-8") as f:
        json.dump(sentiment_analysis, f, indent=2, ensure_ascii=False)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sentiment_analysis = {}

#%%
# ============================================================================
# Q2-5: Topic Extraction using LLM
# ============================================================================

print("\n📚 Extracting topics...")

topics_prompt = f"""
Analyze these customer reviews and extract main discussion topics.

{condensed_review_text}

Identify 5-10 main topics with:
- Topic name
- Brief description
- Key keywords
- Relevance to visual appearance (High/Medium/Low)

Format as JSON:
{{
    "topics": [
        {{
            "topic_name": "name",
            "description": "description",
            "keywords": ["keyword1", "keyword2"],
            "visual_relevance": "High/Medium/Low"
        }}
    ]
}}
"""

try:
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are an expert at topic extraction. Always respond with valid JSON."},
            {"role": "user", "content": topics_prompt}
        ],
        temperature=0.5,
        response_format={"type": "json_object"}
    )
    
    response_content = json.loads(response.choices[0].message.content)
    topics = response_content.get('topics', []) if isinstance(response_content, dict) else response_content
    
    print(f"✅ Extracted {len(topics)} topics")
    
    with open(f"{OUTPUT_DIR}/extracted_topics.json", "w", encoding="utf-8") as f:
        json.dump({"topics": topics}, f, indent=2, ensure_ascii=False)
        
except Exception as e:
    print(f"❌ Error: {e}")
    topics = []

#%%
# ============================================================================
# Q2-6: Create Image Generation Summary
# ============================================================================

print("\n🎨 Creating image generation summary...")

summary_prompt = f"""
Based on the following extracted information, create a comprehensive visual description for image generation.

PRODUCT DESCRIPTION:
{json.dumps(product_description, indent=2)}

VISUAL FEATURES:
{json.dumps(visual_features, indent=2)}

PRODUCT FEATURES:
{json.dumps(product_features, indent=2)}

Create a detailed visual description including:
1. Physical appearance (colors, materials, textures)
2. Size and proportions
3. Design elements and shape
4. Key visual features
5. Overall aesthetic

Output format:
{{
    "visual_description": "detailed description text",
    "key_visual_elements": ["element1", "element2"],
    "recommended_prompt_for_image_generation": "full prompt for image generation"
}}
"""

try:
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are an expert at creating visual descriptions for image generation. Always respond with valid JSON."},
            {"role": "user", "content": summary_prompt}
        ],
        temperature=0.4,
        response_format={"type": "json_object"}
    )
    
    image_generation_summary = json.loads(response.choices[0].message.content)
    
    print("✅ Image generation summary created!")
    print(f"\n📝 Recommended Prompt:")
    print(f"   {image_generation_summary.get('recommended_prompt_for_image_generation', 'N/A')[:150]}...")
    
    with open(f"{OUTPUT_DIR}/image_generation_summary.json", "w", encoding="utf-8") as f:
        json.dump(image_generation_summary, f, indent=2, ensure_ascii=False)
        
except Exception as e:
    print(f"❌ Error: {e}")
    image_generation_summary = {}

#%%
# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*60)
print("🎉 Q1 AND Q2 COMPLETE!")
print("="*60)
print(f"✅ Product Description: Collected")
print(f"✅ Customer Reviews: {len(customer_reviews)} reviews")
print(f"✅ Visual Features: Extracted")
print(f"✅ Product Features: Extracted")
print(f"✅ Sentiment Analysis: Completed")
print(f"✅ Topic Extraction: Completed")
print(f"✅ Image Generation Summary: Created")
print(f"\n📁 All outputs saved in: {OUTPUT_DIR}/")
print("="*60)
