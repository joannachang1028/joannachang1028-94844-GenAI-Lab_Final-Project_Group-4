## Final Project – Generating Product Image from Customer Reviews

**Course**: 94‑844 Generative AI Lab (Fall 2025)  
**Group 4**: Yu Zhang, Yongqi Yu, Libin Chen, Joanna Chang  

This project builds an end‑to‑end pipeline that converts **customer reviews → structured text features → high‑fidelity image prompts → product images** using LLMs and diffusion models.

---

## Product Overview

We study three visually and semantically rich products from distinct categories:

| **Product** | **Category** | **Rating & Volume** |
| --- | --- | --- |
| **Zyllion Shiatsu Back and Neck Massager with Heat** | Health & Household | 4.4 ★ (50,884 reviews) |
| **8BitDo Retro Mechanical Keyboard** | PC Accessories | 4.8 ★ (2,183 reviews) |
| **Hario V60 Ceramic Pour Over Coffee Set** | Home & Kitchen | 4.6 ★ (1,921 reviews) |

- **Distinct categories**: health device, keyboard, coffee gear → diverse shapes and use contexts.  
- **Visually & semantically rich**: each product has strong visual identity and rich review language.  
- **Diverse review volumes**: from ~2k to 50k reviews, all highly rated (4.4–4.8), providing ample but noisy textual signal.

---

## Pipeline Overview

**Massager differs** mainly in **review numbers** and **chunking strategy**; all three share the same LLM.

|  | **Massager** | **Keyboard** | **Coffee Set** |
| --- | --- | --- | --- |
| **Text model** | `gpt-5.1` | `gpt-5.1` | `gpt-5.1` |
| **How reviews are obtained (top reviews)** | Web scraping (Selenium + Amazon) | Hard‑coded real top reviews | Hard‑coded real reviews |
| **# of reviews used in pipeline** | 50 reviews | 5 reviews | 5 reviews |
| **Chunking strategy** | `chunk_size = 3000`, `overlap = 200` (per‑chunk summarization) | None | None |

All three pipelines then feed into a shared **image generation** stage that uses:

- **OpenAI GPT‑Image‑1** (`gpt‑image‑1`)  
- **Stable Diffusion XL (SDXL)** (`stabilityai/stable-diffusion-xl-base-1.0`)

---

## Analytics Engine Components (Q2)

We implement a modular analytics engine over review + description text.

### Summarization

- **Massager**: per‑chunk summaries aggregated into a condensed review text.  
- **Keyboard**: no standalone global summary (tasks operate directly on full reviews).  
- **Coffee set**: overall summary + pros / cons + frequently mentioned keywords.

### Visual Feature Extraction

- **Massager** – rich schema:
  1. Colors mentioned  
  2. Materials described  
  3. Size / dimensions  
  4. Shape / design elements  
  5. Textures  
  6. Visual features (buttons, straps, etc.)  
  7. Overall appearance  

- **Keyboard**:
  1. colors  
  2. materials  
  3. shape_design  
  4. visual_features (e.g., knobs, LEDs, Super Buttons)  
  5. overall_aesthetic  

- **Coffee set**:
  1. materials  
  2. colors  
  3. shapes  
  4. textures  
  5. patterns  
  6. functional visual elements  
  7. usage scenes  

### Product Feature Extraction (functional / design)

- **Massager**:
  1. Functional features (what it does)  
  2. Design features (design elements)  
  3. Material features  
  4. Size / portability  
  5. Usage context (where / how used)  
  6. Key selling points  

- **Keyboard**:
  1. functional_features  
  2. design_features  
  3. connectivity  
  4. unique_selling_points  

- **Coffee set**:
  - No separate product‑feature JSON; functional aspects are merged into visual‑feature extraction.

### Sentiment Analysis

- **Massager**:
  1. Overall sentiment distribution  
  2. Sentiment themes  
  3. Visual sentiment  
  4. Satisfaction score  

- **Keyboard**:
  1. Overall sentiment  
  2. Sentiment themes  
  3. Visual sentiment  

- **Coffee set**:
  1. Overall sentiment  
  2. Sentiment distribution  
  3. Reasons for sentiment  
  4. One‑sentence summary  

### Topic Extraction

- **Massager**:
  - Topic name, description, keywords, visual relevance.  
- **Keyboard**:
  - No topic extraction (design choice to keep pipeline minimal).  
- **Coffee set**:
  - Topics + descriptions + representative keywords + representative comments.

### Image Generation Summary

- **Massager & Keyboard**:
  - JSON with:
    - `visual_description`  
    - `key_visual_elements`  
    - `recommended_prompt_for_image_generation`  

- **Coffee set**:
  - A curated list of recommended prompts used directly for image generation.

---

## Image Generation

We transform the structured text into images using two models:

### OpenAI GPT‑Image‑1

- Better at following structured prompts and instructions.  
- More accurate geometry and object layout.  
- Lower hallucination, simpler textures.  

### Stable Diffusion XL (SDXL)

- More photorealistic textures and lighting.  
- Highly aesthetic images, high diversity.  
- More frequent semantic drift and component errors.

### Prompt Versioning Strategy

For each product we test **three prompt styles**:

1. **Prompt v1 – Natural language**  
2. **Prompt v2 – Condensed attribute‑focused**  
3. **Prompt v3 – Structured photorealistic**  

Structured prompts (v3) consistently produce the most faithful and stable results.

---

## Key Findings

- **OpenAI GPT‑Image‑1** → higher semantic accuracy (correct parts and layout).  
- **SDXL** → more photorealistic but with more hallucinated or incorrect components.  
- For all three products, **customer reviews contain enough signal to approximate the product**, but fine geometric details and UI elements are still hard to match exactly.  
- **Massager** benefits from chunked, high‑volume reviews; **Keyboard** shows the effect of detailed but low‑N reviews; **Coffee set** demonstrates the simplest end‑to‑end baseline.

---

## Challenges & Future Work

**Challenges**
- Noisy, inconsistent review language.  
- Limited review subsets (5–50) may not fully represent the full customer population.  
- Lack of objective metrics for comparing generated vs. real product images.

**Future Enhancements**
- Improve chunking strategies to preserve context while controlling cost.  
- Experiment with different structured representations from Q2 to drive generation.  
- Explore fine‑tuning or reward‑based optimization with similarity metrics.  
- Build a more complete **multi‑agent workflow** (Researcher / Analyst / Creative / Visualizer) with feedback loops from generated images back into the pipeline.


