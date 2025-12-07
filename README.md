# Final Project Presentation

## GROUP 4

YU ZHANG
YONGQI YU
LIBIN CHEN
JOANNA CHANG

---

# Outline

* Product Overview
* Pipeline Selection
    * Model
    * Chunking strategy
* Analytics Engine Components
    * Summarization, Visual feature, Product feature, Sentiment analysis
    * Topic extraction, Image generation summary
* Image Generation
* AI Agentic Workflow
* Challenges and Limitations
* Future Enhancements

---

# Overview of Product Categories

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ZYLLION SHIATSU BACK AND NECK MASSAGER WITH HEAT</td>
<td>8BITDO RETRO MECHANICAL KEYBOARD</td>
<td>HARIO V60 CERAMIC POUR OVER COFFEE SET</td>
    </tr>
<tr>
      <td>Health & Household</td>
<td>PC Accessories</td>
<td>Home & Kitchen</td>
    </tr>
<tr>
      <td>4.4 ⭐ (50,884 reviews)</td>
<td>4.8 ⭐ (2,183 reviews)</td>
<td>4.6 ⭐ (1,921 reviews)</td>
    </tr>
  </tbody>
</table>



---

# Rationale for Selection

<table>
  <thead>
    <tr>
      <th>DISTINCT CATEGORIES</th>
      <th>VISUALLY & SEMANTICALLY RICH</th>
      <th>DIVERSE REVIEW VOLUMES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Three distinct product categories enhances the **diversity** of the evaluation and ensures **varied textual cues** for analysis</td>
<td>The selected products are **visually** and **semantically rich**, providing ample opportunities for exploring text-derived visual signals and enhancing model performance</td>
<td>Review counts range from 2,000 to 50,000, and all products have consistently high average ratings between 4.4 and 4.8</td>
    </tr>
  </tbody>
</table>



---

# Pipeline Overview

Massager differs in
* Review numbers
* Chunking strategy

<table>
    <thead>
    <tr>
        <th></th>
        <th>Massager</th>
        <th>Keyboard</th>
        <th>Coffee Set</th>
    </tr>
    </thead>
    <tr>
        <td>Model</td>
<td>gpt-5.1</td>
<td>gpt-5.1</td>
<td>gpt-5.1</td>
    </tr>
<tr>
        <td>How reviews
<br/>
are obtained
<br/>
(top reviews)</td>
<td>Web scraping
<br/>
(Selenium package)</td>
<td>Hard-coded</td>
<td>Hard-coded</td>
    </tr>
<tr>
        <td># of reviews</td>
<td>50 reviews</td>
<td>5 reviews</td>
<td>5 reviews</td>
    </tr>
<tr>
        <td>Chunking
<br/>
Strategy</td>
<td>chunk_size = 3000
<br/>
overlap = 200</td>
<td>None</td>
<td>None</td>
    </tr>
</table>



---

# Analytics Engine Components

## Keyboard
* No summarization
* Fewer feature extraction

## Coffee set
* No product feature extraction

<table>
  <thead>
    <tr>
      <th></th>
      <th>Massager</th>
      <th>Keyboard</th>
      <th>Coffee Set</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Summarization</td>
<td>per-chunk summaries</td>
<td><span style="color:red;">None</span></td>
<td>Overall summary, pros/cons, keywords</td>
    </tr>
<tr>
      <td>Visual feature extraction</td>
<td>
        <ol>
          <li>Colors mentioned</li>
          <li>Materials described</li>
          <li>Size/Dimensions</li>
          <li>Shape/Design elements</li>
          <li>Textures</li>
          <li>Visual features (buttons, straps, etc.)</li>
          <li>Overall appearance</li>
        </ol>
      </td>
<td>
        <ol>
          <li>colors</li>
          <li>materials</li>
          <li>shape design</li>
          <li>visual features</li>
          <li>overall aesthetic</li>
        </ol>
      </td>
<td>
        <ol>
          <li>materials</li>
          <li>colors</li>
          <li>shapes</li>
          <li>textures</li>
          <li>patterns</li>
          <li>functional visual element</li>
          <li>usage scenes</li>
        </ol>
      </td>
    </tr>
<tr>
      <td>Product feature extraction<br>(functional/ design)</td>
<td>
        <ol>
          <li>Functional Features (what it does)</li>
          <li>Design Features (design elements)</li>
          <li>Material Features</li>
          <li>Size/Portability</li>
          <li>Usage Context (where/how used)</li>
          <li>Key Selling Points</li>
        </ol>
      </td>
<td>
        <ol>
          <li>functional_feature</li>
          <li>design_features</li>
          <li>connectivity</li>
          <li>unique_selling_points</li>
        </ol>
      </td>
<td><span style="color:red;">None</span><br>(combined with visual feature extraction)</td>
    </tr>
  </tbody>
</table>



---

# Visual feature & Product feature (conti.)

```python
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
```

```python
visual_prompt = f"""
Analyze the following reviews for the 8BitDo Retro Mechanical Keyboard.
Extract ONLY visual/physical attributes.
Reviews:
{all_review_text[:15000]}
Return JSON with keys:
colors, materials, shape_design, visual_features (specific parts like knobs, LEDs), overall_aesthetic.
"""
```

```python
def build_visual_feature_prompt(text):
    return f"""
You are an expert in extracting visual and physical product characteristics from text.
From the following product reviews, extract ONLY concrete visual or physical features of the product.
Include attributes such as: shape, color, material, texture, size, special patterns, and usage environment.
Return the output in JSON with this structure:
{{
    "materials": [],
    "colors": [],
    "shapes": [],
    "textures": [],
    "distinctive_patterns": [],
    "functional_visual_elements": [],
    "common_usage_scenes": []
}}
"""
```

```python
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
```

```python
feature_prompt = f"""
Extract key functional and design features from these reviews.
Reviews:
{all_review_text[:15000]}
Return JSON with keys:
functional_features, design_features, connectivity, unique_selling_points.
"""
```

---

# Analytics Engine Components

*   No topic extraction for keyboard
*   Recommended prompts are used directly to generate images

<table>
  <thead>
    <tr>
      <th></th>
      <th>Massager</th>
      <th>Keyboard</th>
      <th>Coffee Set</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Sentiment analysis</td>
<td>
        <p>1.Overall sentiment</p>
        <p>2.Sentiment themes</p>
        <p>3.Visual sentiment</p>
        <p>4.Satisfaction score</p>
      </td>
<td>
        <p>1.Overall sentiment</p>
        <p>2.Sentiment themes</p>
        <p>3.Visual sentiment</p>
      </td>
<td>
        <p>1.Overall sentiment</p>
        <p>2.Sentiment distribution</p>
        <p>3.Reasoning</p>
        <p>4.Summary</p>
      </td>
    </tr>
<tr>
      <td>Topic extraction</td>
<td>
        <p>1.Topic name</p>
        <p>2.Description</p>
        <p>3.Keywords</p>
        <p>4.Visual relevance</p>
      </td>
<td>None</td>
<td>
        <p>1.Topic</p>
        <p>2.Description</p>
        <p>3.Representative keywords</p>
        <p>4.Representative comments</p>
      </td>
    </tr>
<tr>
      <td>Image generation summary</td>
<td>
        <p>1.Visual description</p>
        <p>2.Key visual elements</p>
        <p>3.Recommended prompts for image generation</p>
      </td>
<td>
        <p>1.Visual description</p>
        <p>2.Key visual elements</p>
        <p>3.Recommended prompts for image generation</p>
      </td>
<td>Recommended prompts for image generation</td>
    </tr>
  </tbody>
</table>



---

# Image Generation

Transform textual product attributes extracted from customer reviews into realistic product images using image generation models.

We evaluate:
1. How well models convert text to visual appearance
2. How different prompts affect fidelity & realism
3. Model differences between OpenAI and SDXL

---

# Models Used

## OpenAI GPT-Image-1

Introducing our latest image generation model in the API

*   Better at following instructions
*   More accurate geometry
*   Lower hallucination
*   Slightly simpler textures

Try in Playground
Listen to article 4:25

## Stable Diffusion XL (SDXL)

*   Better at texture realism & lighting
*   Very aesthetic images
*   Higher variability
*   Occasional shape/component errors

Source:
https://stablediffusionxl.com/
https://platform.openai.com/docs/models/gpt-image-1

---

# Our Prompt Versioning Strategy

For each of 3 products:
3 prompt versions

*   **Prompt 1: Natural Language Prompt**
    *   Reads like a normal description, minimal structure
*   **Prompt 2: Condensed Attribute-Focused Prompt**
    *   Removes storytelling language
    *   Focuses on essential product features
    *   More consistent than prompt 1
*   **Prompt 3: Structured Photorealistic Prompt**
    *   Most structured and detailed
    *   Includes materials, geometry, textures
    *   Includes lighting, background, photography style

```json
"product1_massager": {
  "v1": """Create an image of a compact, pillow-like back and neck massager in rich brown fabric.
   The massager should feature soft silicone nodes on each side, an ergonomic design that fits body
   contours, and Velcro straps for securing it to a chair. Include user-friendly buttons and a
   zipper for a replacement cover. The overall look should convey a sturdy and modern aesthetic,
   suitable for therapeutic use in home or office settings.""",
  "v2": """Ultra-realistic photo of an ergonomic shiatsu massage pillow.
   Brown faux leather + fabric material, curved compact shape, four rounded massage nodes,
   simple control buttons, velcro straps. Bright studio lighting, sharp detail.""",
  "v3": """Realistic studio product photo of a compact, pillow-shaped shiatsu back and neck massager.
   Key visual features:
   - rich brown fabric cover made of nylon/polyester
   - four raised soft silicone massage nodes forming smooth rounded bumps
   - ergonomic curved design that fits body contours
   - Velcro straps on the back for attaching to a chair
   - user-friendly side control buttons and a visible zipper for a replaceable cover
   Style: clean white seamless background, soft diffused lighting, crisp detail and accurate textures."""
}
```

---

# Product 1 (Massager)

## OpenAI

## SDXL

### Key Findings:

*   OpenAI generated images closely match the real massager's shape and color.
*   The pillow-like outline and four glowing massage nodes are accurately captured.
*   Button placement is generally correct, though design differs slightly.
*   Models did not reproduce the blue rotation arrows seen in the real product.
*   SDXL outputs show higher realism but lower accuracy, often drifting into neck pillows.

---

# Product 2 (Keyboard)
## Prompts

### Initial prompt (v1):

*Create a image of a retro-style **audio device** with a boxy shape made of thick plastic. The device has a creamy grey body adorned with bold red accents. It features large 'Super Buttons' on the front, a prominent central volume knob, and a soft glowing power LED indicator. The overall design exudes a nostalgic aesthetic reminiscent of classic electronics, highlighting concave keys and a user-friendly layout.*

### Updated prompt (v2):

*Ultra-realistic retro-style **mechanical keyboard** modeled after classic 8-bit consoles. Matte creamy grey ABS plastic housing, bold red accent buttons, oversized Super Buttons, concave retro keycaps, a metallic central volume knob, and an illuminated LED indicator. Bright studio lighting, sharp detail.*

---

# Product 2 (Keyboard)

## OpenAI

## SDXL

Key Findings:
* OpenAI captures the color scheme (cream gray + red) but often misinterprets the product as a retro console or button box rather than a full keyboard.
* Layout accuracy is low: OpenAI struggles with accurate key arrangement, legends, and overall keyboard proportions.
* SDXL outputs show stronger realism but frequently hallucinate incorrect forms (e.g., audio equipment, multi-piece boards, random knob placement).
* Both models capture the retro aesthetic, but neither achieves true product-level accuracy in geometry or layout.

---

# Product 3 (Hario Pour Over Coffee Set)

## OpenAI

## SDXL

### Key Findings:

*   OpenAI accurately generated all core components (ceramic dripper, glass server, paper filters, scoop) with correct overall arrangement.
*   The dripper shape (V60 cone + spiral ribs) is captured reasonably well.
*   The glass carafe shape matches the real product, but measurement markings are inconsistent, and may missing.
*   Paper filters are recognized correctly as stacked fan shapes, but thickness and orientation vary.
*   SDXL outputs show high realism but significant semantic drift, like introducing wood bases, metal stands, or unrelated brewing accessories.

---

# Image Generation Summary

*   OpenAI → **higher accuracy**, better at capturing correct shape, layout, and components.
*   SDXL → **more photorealistic**, but often hallucinates unrelated product forms.
*   **Structured prompts** produce the most consistent and faithful results.
*   Both models struggle with **fine details**, UI icons, and precise component geometry.
*   Customer reviews provide enough signal for **approximate product reconstruction**, but not exact replication.

---

# AI Agentic Workflow

**Researcher Agent**
* Function: Data ingestion
* Live Mode: Selenium-based scraping of Amazon product pages (descriptions, reviews)

**Analyst Agent**
* Function: Use LLMs (GPT-4o) to parse unstructured text
* Output: Extracts objective visual features and computes sentiment analysis

**Creative Agent**
* Function: Convert analyst output into a high-fidelity image-generation prompt optimized for diffusion models

**Visualizer Agent**
* Function: Use DALL·E 3 to generate a visual prototype from the creative prompt

---

# AI Agentic Workflow

## Overview
A scalable, autonomous AI agentic workflow that discovers, analyzes, and visually reconstructs products from web data. Built with Streamlit for the frontend and OpenAI models (GPT-4o for language understanding and DALL·E 3 for image synthesis).

Key capabilities:
- Multi-agent pipeline for data ingestion, analysis, prompt synthesis, and visualization
- Live scraping mode and cached-data mode for reproducible demos
- Generates structured visual features, sentiment scores, image prompts, and visual prototypes

## System Architecture
Four sequential agents:

1. Researcher Agent
    - Function: Data ingestion
    - Live Mode: Selenium-based scraping of Amazon product pages (descriptions, reviews)
    - Cached Mode: Loads pre-verified JSON datasets from disk

2. Analyst Agent
    - Function: Use LLMs (GPT-4o) to parse unstructured text
    - Output: Extracts objective visual features and computes sentiment analysis

3. Creative Agent
    - Function: Convert analyst output into a high-fidelity image-generation prompt optimized for diffusion models

4. Visualizer Agent
    - Function: Use DALL·E 3 to generate a visual prototype from the creative prompt

## Tech Stack
- Frontend: Streamlit
- LLMs / Images: OpenAI GPT-4o, DALL·E 3
- Scraping: Selenium (ChromeDriver)
- Language: Python

## Project Structure
```text
universal_product_agent/
├── app.py                 # Streamlit dashboard (frontend)
├── agents.py              # Agent definitions and orchestration
├── scraper.py             # Selenium scraper
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys) — DO NOT COMMIT
├── README.md              # Project documentation
└── data/                  # Cached product datasets
     └── product_name/
          ├── product_description.json
          └── customer_reviews.json
```

## Setup

1. Create a virtual environment and install dependencies:
    - python -m venv .venv
    - source .venv/bin/activate  (or .venv\Scripts\activate on Windows)
    - pip install -r requirements.txt

2. Configure API keys
    - Create a file named .env in the project root with the following (example):
      OPENAI_API_KEY=sk-REPLACE_WITH_YOUR_KEY
    - Never commit .env to version control

3. ChromeDriver (for live scraping)
    - Install Chrome and the matching ChromeDriver version accessible in PATH

## Launch the Application
Run:
streamlit run app.py

The app will open at http://localhost:8501 by default.

## Usage

Mode A — Live Web Scraping
- Select "Live Web Scraping" in the sidebar
- Enter an Amazon ASIN (e.g., B0CCP8KYGG)
- Click "Start Full Pipeline"
- Note: A Chrome window will open; the pipeline waits ~45s to allow manual login when required

Mode B — Load Existing Data
- Place JSON files under data/{product_name}/
- Select "Load Existing Data" in the sidebar
- Choose a product folder and click "Start Full Pipeline"

## Outputs
- Sentiment Score: 1–10 rating derived from review analysis
- Visual Features: Structured list of objective physical attributes extracted from text
- Image Prompt: Optimized prompt for diffusion-based generators
- Final Image: Visual prototype generated by DALL·E 3


---

# Challenges and Limitations

**NOISY REVIEWS**

User reviews often contain **inconsistent language** and irrelevant information, making it difficult to extract reliable insights for image generation.

**DATASET GENERALIZABILITY**

Relying on a **small subset** of customer reviews (5-50), the extracted visual features may not fully represent the product, limiting the generalizability and accuracy of the generated images.

**METRIC FOR GENERATED IMAGE**

There is no fixed or standardized metric to **evaluate** the quality of the generated images or to objectively compare them with real product images, making assessment largely subjective.

---

# Future Enhancements

## CHUNKING
Implementing more effective **chunking** strategies will preserve full contextual meaning across reviews, allowing the LLM to extract richer and more accurate visual features. This enhancement would reduce information loss and ultimately lead to more faithful, higher-quality product image generation.

## GENERATION IMPROVEMENT
Different **structure** of extracted information could be tested to achieve higher quality.
**Fine-tuning** the generation model using a selected similarity metric would help the model produce images that more closely match the real product's appearance.

## PIPELINE ENHANCEMENT
Iteratively **feeding** both the generated images and the original image back into the agent can progressively improve image quality.
Try a **multiple agent** workflow with each agent assigned specific task with high performance.

---


0

Thank You for Your
Attention
