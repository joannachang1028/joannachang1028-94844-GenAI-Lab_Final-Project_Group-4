# Q2 Analysis Report: Customer Review Analysis with LLM

## 1. Overview

This report documents the LLM-based analysis of customer reviews for the Zyllion Shiatsu Back and Neck Massager (ZMA-13). The goal is to extract valuable information from textual reviews that can be used for image generation in Q3.

**Product**: Zyllion Shiatsu Back and Neck Massager with Heat (ZMA-13)\
**Product Link**: https://www.amazon.com/dp/B0FHPNJ7JR/ref=syn_sd_onsite_desktop_0?ie=UTF8&psc=1&pf_rd_p=4500617b-0cc7-45a9-8bde-f455bfff54d3&pf_rd_r=F4WMMGS0S46M02Q6DAAW&pd_rd_wg=eT3Q5&pd_rd_w=ehQdu&pd_rd_r=32e3055e-1053-405c-9346-d894368da3ee&aref=0gKUYwQWS6 \
**Data Source**: Amazon customer reviews  
**Total Reviews Analyzed**: 50 reviews  
**Model Used**: GPT-4o-mini (OpenAI API)

### Product Selection Rationale

Why I chose this product:

1. **High Visual Descriptiveness**: Reviews often mention specific design elements (silicone nodes, faux leather material, brown color, ergonomic shape)
2. **Popular Product**: 50+ purchases in the past month, ensuring sufficient review data
3. **Category Characteristics**: Health products typically have detailed visual descriptions
4. **Feature-Rich**: Multiple features (heating, 3D massage, straps) that users describe visually

## 2. Analysis Methodology

### 2.1 Prompt Engineering Strategy

I designed task-specific prompts for each analysis type. The key strategies used:

- **Role-based prompting**: Each prompt starts with a clear role definition (e.g., "You are an expert at extracting visual information from product reviews")
- **Structured output**: All prompts request JSON-formatted responses for consistent parsing
- **Low temperature (0.3-0.5)**: Used lower temperature settings for more consistent and factual extraction

### 2.2 Text Chunking Strategy

Given GPT-4o-mini's token limit, I implemented a chunking strategy:

- **Chunk size**: 3,000 characters per chunk
- **Overlap**: 200 characters between chunks to preserve context
- **Sentence boundary**: Chunks break at sentence endings (., !, ?) when possible

For this dataset (50 reviews), the total text was small enough to fit in a single chunk, so no chunking was needed in practice.

### 2.3 Analysis Pipeline

The analysis pipeline consists of 5 sequential steps:

1. Visual Feature Extraction → `visual_features.json`
2. Product Feature Extraction → `product_features.json`
3. Sentiment Analysis → `sentiment_analysis.json`
4. Topic Extraction → `extracted_topics.json`
5. Image Generation Summary → `image_generation_summary.json`

## 3. Analysis Results

### 3.1 Visual Feature Extraction

Extracted visual attributes from customer reviews:

| Category | Extracted Information |
|----------|----------------------|
| Colors | Black, Brown |
| Materials | Fabric, Nylon, Polyester, Faux Leather |
| Size | Compact, smaller than most pillows |
| Shape/Design | Pillow-like, Ergonomic |
| Textures | Soft, Smooth |
| Visual Features | Buttons, Replacement cover, Zipper, Velcro straps |

**Overall Appearance**: Customers describe the massager as sturdy and strong with a compact ergonomic design, featuring a soft fabric cover that is easy to replace.

### 3.2 Product Feature Extraction

| Feature Type | Details |
|-------------|---------|
| Functional | 3D deep tissue massage, Heat function, Multiple massage modes |
| Design | Ergonomic shape, Velcro straps for securing to chairs |
| Material | Soft silicone nodes, Durable exterior fabric |
| Portability | Compact and lightweight, easy to move |
| Usage Context | Office chair, Car headrests, Couch, Bed |

### 3.3 Sentiment Analysis

**Overall Sentiment Distribution:**
- Positive: 80%
- Neutral: 15%
- Negative: 5%

**Satisfaction Score: 9/10**

**Top Positive Themes:**
1. Effective pain relief
2. Strong and durable motor
3. Good customer service and warranty support
4. Compact and easy to use
5. Heat feature enhances relaxation

**Negative Themes:**
1. Wiring issues over time
2. Cover wears out with use
3. Automatic directional switch can be inconvenient
4. Pressure can be difficult to adjust

### 3.4 Topic Extraction

Identified 9 main topics from customer reviews:

| Topic | Visual Relevance | Description |
|-------|-----------------|-------------|
| Durability | High | Customers praise the sturdy build quality |
| Compact Design | High | Appreciated for portability and storage |
| Effectiveness | High | Strong relief for muscle tension |
| Heating Function | Medium | Popular feature for enhanced relaxation |
| User-Friendly Controls | Medium | Simple and intuitive operation |
| Versatility | Medium | Works on back, neck, legs, feet |
| Pressure Sensitivity | Medium | Some find intensity hard to adjust |
| Design Flaws | Medium | Wiring and auto-switch issues mentioned |
| Customer Service | Low | Good warranty support noted |

## 4. Output for Image Generation (Q3)

### 4.1 Key Visual Elements

Based on the analysis, the following visual elements should be emphasized in image generation:

1. **Brown fabric cover** (nylon/polyester material)
2. **Soft silicone massage nodes** on each side
3. **Ergonomic pillow-like shape**
4. **Velcro straps** for securing to chairs
5. **User-friendly control buttons**
6. **Compact size** (smaller than typical pillows)

### 4.2 Recommended Prompt for Image Generation

> "Create an image of a compact, pillow-like back and neck massager in rich brown fabric. The massager should feature soft silicone nodes on each side, an ergonomic design that fits body contours, and Velcro straps for securing it to a chair. Include user-friendly buttons and a zipper for a replacement cover. The overall look should convey a sturdy and modern aesthetic, suitable for therapeutic use in home or office settings."

## 5. Challenges and Lessons Learned

### Challenges Faced

1. **Amazon's Anti-Scraping**: Had to use Selenium with manual login to collect reviews
2. **Inconsistent Review Quality**: Some reviews lack visual descriptions
3. **Color Discrepancy**: Product is marketed as "Brown" but some reviews mention "Black" - this could be due to different variants

### What Worked Well

- Using JSON output format ensured consistent, parseable results
- Lower temperature (0.3) produced more reliable factual extractions
- Separating analyses into distinct prompts gave cleaner, more focused results

### What Could Be Improved

- Could implement RAG with vector database for larger review datasets
- Could experiment with few-shot prompting for better visual extraction
- Could add image analysis of review photos if available

## 6. Output Files Summary

| File | Description |
|------|-------------|
| `product_info.json` | Product selection rationale |
| `product_description.json` | Scraped product description |
| `customer_reviews.json` | 50 collected customer reviews |
| `visual_features.json` | Extracted visual attributes |
| `product_features.json` | Extracted product features |
| `sentiment_analysis.json` | Sentiment analysis results |
| `extracted_topics.json` | Topic modeling results |
| `image_generation_summary.json` | Final summary for Q3 |

---

*This analysis provides the foundation for Q3 image generation using diffusion models.*
