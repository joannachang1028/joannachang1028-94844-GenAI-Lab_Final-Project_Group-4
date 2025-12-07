import json
import os
from openai import OpenAI
import scraper

class Agent:
    def __init__(self, name, client):
        self.name = name
        self.client = client

class ResearcherAgent(Agent):
    """
    Role: Gathers data either from the local cache or by triggering the live web scraper.
    """
    def fetch_data(self, input_value, is_live_scraping=False):
        # MODE A: Live Scraping
        if is_live_scraping:
            asin = input_value
            print(f"[{self.name}]: Initiating live scrape for ASIN {asin}...")
            
            # Run the scraper module
            scraped_data = scraper.run_scraper(asin)
            
            if not scraped_data or not scraped_data['reviews']:
                return {"status": "error", "message": "Scraping failed or no reviews found."}
            
            # Save the fresh data to a cache folder for future use
            save_path = f"data/{asin}"
            os.makedirs(save_path, exist_ok=True)
            
            with open(f"{save_path}/product_description.json", 'w', encoding='utf-8') as f:
                json.dump({"title": scraped_data['title'], "features": scraped_data['features']}, f, indent=2)
            
            with open(f"{save_path}/customer_reviews.json", 'w', encoding='utf-8') as f:
                json.dump(scraped_data['reviews'], f, indent=2)
                
            return self._format_corpus(scraped_data['title'], scraped_data['features'], scraped_data['reviews'])

        # MODE B: Load Existing Data
        else:
            product_folder = input_value
            base_path = f"data/{product_folder}"
            try:
                with open(f"{base_path}/product_description.json", 'r', encoding='utf-8') as f:
                    desc = json.load(f)
                with open(f"{base_path}/customer_reviews.json", 'r', encoding='utf-8') as f:
                    reviews = json.load(f)
                
                return self._format_corpus(desc.get('title', ''), desc.get('features', []), reviews)
            except FileNotFoundError:
                return {"status": "error", "message": f"Data files not found in {base_path}"}

    def _format_corpus(self, title, features, reviews):
        """Helper to format the raw data into a text block for the LLM."""
        raw_text = f"PRODUCT TITLE: {title}\n"
        raw_text += f"KEY FEATURES: {json.dumps(features, indent=2)}\n"
        raw_text += "CUSTOMER REVIEWS:\n" + "\n".join([f"- {r.get('body', '')}" for r in reviews])
        return {"raw_text": raw_text, "status": "success", "count": len(reviews)}

class AnalystAgent(Agent):
    """
    Role: Analyzes raw text to extract visual cues and sentiment.
    """
    def analyze(self, raw_text):
        prompt = f"""
        You are a Senior Product Analyst. Analyze the following product data.
        
        Data:
        {raw_text[:15000]}
        
        Your Goal: Extract structured data for an image generation model.
        
        Return valid JSON with these specific keys:
        1. "visual_features": A list of physical attributes (colors, materials, shapes, lights, buttons).
        2. "aesthetic_style": A short string describing the vibe (e.g., "Retro 80s Electronics", "Modern Minimalist").
        3. "sentiment_score": An integer from 1-10.
        4. "sentiment_summary": A one-sentence summary of user opinion.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

class CreativeAgent(Agent):
    """
    Role: Converts analysis into a stable diffusion prompt.
    """
    def write_prompt(self, analysis):
        visuals = analysis.get('visual_features', [])
        style = analysis.get('aesthetic_style', '')
        
        prompt = f"""
        Act as an expert Prompt Engineer. Write a detailed prompt for DALL-E 3 to create a photorealistic product image.
        
        Context:
        The product aesthetic is: {style}
        Key visual features to include: {', '.join(visuals)}
        
        The prompt must be descriptive, specifying professional studio lighting, camera angle, and high-resolution texture details.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

class VisualizerAgent(Agent):
    """
    Role: Takes the text prompt and uses DALL-E 3 to generate the final image.
    """
    def generate_image(self, prompt):
        print(f"[{self.name}]: Sending prompt to DALL-E 3...")
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            return {"status": "success", "url": image_url}
        except Exception as e:
            return {"status": "error", "message": str(e)}