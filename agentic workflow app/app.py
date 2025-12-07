import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
# Import the new VisualizerAgent
from agents import ResearcherAgent, AnalystAgent, CreativeAgent, VisualizerAgent

# 1. Configuration
st.set_page_config(page_title="Universal Product Agent", layout="wide")
load_dotenv('.evn')

if not os.getenv("OPENAI_API"):
    st.error("Error: OPENAI_API key not found in .evn file")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API"))

# 2. Sidebar Controls
st.sidebar.title("🎛️ Agent Controls")
mode = st.sidebar.radio("Input Source", ["📂 Load Existing Data", "🌐 Live Web Scraping"])

target_input = ""
if mode == "📂 Load Existing Data":
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    folders = [f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f))]
    target_input = st.sidebar.selectbox("Select Cached Product", folders) if folders else None
else:
    target_input = st.sidebar.text_input("Enter Amazon ASIN", value="B0CCP8KYGG")
    st.sidebar.info("Note: A browser window will open. Please login manually if prompted.")

# 3. Main Interface
st.title("🤖 Universal Product Reconstructor")
st.markdown("### Autonomous Workflow: From Raw Data to Final Image")

if st.button("🚀 Start Full Pipeline", type="primary"):
    if not target_input:
        st.error("Please provide a valid input.")
        st.stop()

    # --- Step 1: Research ---
    st.subheader("1. Research Phase")
    researcher = ResearcherAgent("Researcher", client)
    
    with st.spinner("Agent is gathering data..."):
        is_live = (mode == "🌐 Live Web Scraping")
        result = researcher.fetch_data(target_input, is_live_scraping=is_live)
        
        if result['status'] == 'error':
            st.error(result['message'])
            st.stop()
            
        st.success(f"Data Acquisition Complete. Analyzed {result['count']} reviews.")
        with st.expander("Inspect Raw Data"):
            st.text(result['raw_text'][:800] + "...")

    # --- Step 2: Analysis ---
    st.subheader("2. Analysis Phase")
    analyst = AnalystAgent("Analyst", client)
    
    with st.spinner("Agent is analyzing visuals and sentiment..."):
        analysis = analyst.analyze(result['raw_text'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sentiment Score", f"{analysis.get('sentiment_score')}/10")
        with col2:
            st.info(f"**Aesthetic:** {analysis.get('aesthetic_style')}")
        with col3:
            st.write(f"**Summary:** {analysis.get('sentiment_summary')}")
            
        st.write("**Extracted Visual Features:**")
        st.json(analysis.get('visual_features'))

    # --- Step 3: Creation ---
    st.subheader("3. Creative Phase")
    creative = CreativeAgent("Creative", client)
    
    with st.spinner("Agent is drafting image prompts..."):
        prompt = creative.write_prompt(analysis)
        st.success("Image Generation Prompt Created")
        with st.expander("View Prompt"):
            st.code(prompt, language="text")

    # --- Step 4: Visualization (NEW) ---
    st.subheader("4. Visualization Phase (DALL-E 3)")
    visualizer = VisualizerAgent("Visualizer", client)

    with st.spinner("Generating high-fidelity image (this takes about 15 seconds)..."):
        image_result = visualizer.generate_image(prompt)
        
        if image_result['status'] == 'success':
            st.success("Image Generated Successfully!")
            # Display the image centrally with a caption
            st.image(image_result['url'], caption="AI Reconstructed Product Prototype", use_column_width=True)
        else:
            st.error(f"Image Generation Failed: {image_result['message']}")