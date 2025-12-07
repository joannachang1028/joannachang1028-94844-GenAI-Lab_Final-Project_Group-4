# Q1 & Q2 Analysis: 8BitDo Retro Mechanical Keyboard
**94-844 Generative AI Lab (Fall 2025) - Final Project**

## Project Overview
This repository contains the Product Selection (Q1) and Customer Review Analysis (Q2) for the third group product: the 8BitDo Retro Mechanical Keyboard.

The goal of this module is to extract high-fidelity visual descriptions from text-based customer reviews using LLMs (GPT-4o-mini). These outputs are structured specifically to support the Image Generation phase (Q3).

## Product Details
* **Product Name:** 8BitDo Retro Mechanical Keyboard
* **Category:** Electronics > Computers & Accessories
* **ASIN:** B0CCP8KYGG
* **Rationale:** Selected for its distinct "Nintendo NES" retro aesthetic (boxy shape, creamy grey/red colors, large buttons), which provides a unique challenge for diffusion models compared to organic or kitchen products.

## File Structure

Final_Project_8BitDo_Keyboard.ipynb   # Main analysis notebook (Q1 & Q2 code)
README.md                             # This documentation
data/                                 # Generated output files
    product_info.json                 # Rationale and metadata
    product_description.json          # Raw product specs
    customer_reviews.json             # Raw customer review text
    visual_features.json              # LLM-extracted visual attributes (colors, shapes)
    product_features.json             # Functional & design feature extraction
    sentiment_analysis.json           # User sentiment breakdown
    image_generation_summary.json     # CRITICAL: Final input for Q3

## Setup & Usage

### 1. Prerequisites
Ensure you have the following installed:
* Python 3.8+
* Jupyter Notebook
* Dependencies: openai, python-dotenv

### 2. Environment Variables
Create a .env file in the root directory containing your OpenAI API key:
OPENAI_API=your_api_key_here

### 3. Running the Analysis
Open Final_Project_8BitDo_Keyboard.ipynb and run all cells.
* Note: The notebook is configured to use the pre-collected data in the data/ folder to ensure reproducibility without re-scraping Amazon.

## Instructions for Q3

Your main input file is: data/image_generation_summary.json

Please use the following data points for your Stable Diffusion / Midjourney prompts:

1.  **Recommended Prompt:** Use the "recommended_prompt_for_image_generation" field directly. It has been optimized to include key visual triggers like "retro 1980s style," "creamy grey plastic," and "Super Buttons."
2.  **Key Visual Elements:** Refer to the "key_visual_elements" list (e.g., "Retro red power LED," "Concave keys") to refine or iterate on your prompts if the initial generation misses details.
3.  **Aesthetic Context:** The visual_features.json file contains specific color palettes ("creamy grey," "bold red") if you need to adjust color grading.

## Analysis Highlights
* **Visual Style:** Retro, Boxy, NES-Themed.
* **Sentiment:** Highly positive (80%), with users praising the aesthetic and build quality but noting the "loud" clicky switches.
* **Unique Features:** Two large programmable "Super Buttons" and a physical volume knob are defining visual characteristics.
