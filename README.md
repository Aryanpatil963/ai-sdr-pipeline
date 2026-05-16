# AI SDR Pipeline - VideoSDK

Automated pipeline for finding prospects, researching them with AI, and generating hyper-personalized outreach.

## What it does
1. **Discovery:** Finds target companies and specific personas (CTOs, VPs of Eng) using Apollo.io.
2. **AI Research:** Uses GPT to analyze company descriptions and categorizes them into "SMB" vs "Enterprise" based on size, industry, and use case.
3. **Outreach Generation:** Writes distinct, personalized cold emails and LinkedIn DMs based on the persona and the company's specific video/audio API needs.
4. **Dashboard:** Provides a clean Streamlit interface to view pipeline value, account research, and generated copy.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your API keys to `.env`:
   ```env
   OPENAI_API_KEY=your_openai_key
   APOLLO_API_KEY=your_apollo_key
   ```
   *Note: If no keys are provided, the system falls back to mock data so you can test the UI.*

## Run
1. Run the data pipeline:
   ```bash
   python main.py
   ```
2. Start the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## Architecture
- `discovery.py`: Hits Apollo APIs (or uses mock data)
- `research.py`: GPT-4o classification and analysis
- `outreach.py`: GPT-4o drafting engine with persona-based prompting
- `main.py`: Orchestrates the flow and dumps to JSON
- `dashboard.py`: Streamlit visualization
