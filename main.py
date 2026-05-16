import json
from discovery import discover_all
from research import research_all
from outreach import generate_all_outreach

def run_pipeline():
    print("=== AI SDR Pipeline Starting ===\n")

    print("Step 1: Discovering accounts and contacts...")
    data = discover_all()
    print(f"Found {len(data)} companies\n")

    print("Step 2+3: AI research and segmentation...")
    data = research_all(data)

    print("\nStep 4: Generating personalized outreach...")
    data = generate_all_outreach(data)

    # Save to JSON
    with open("pipeline_output.json", "w") as f:
        json.dump(data, f, indent=2)

    print("\n=== Done! Output saved to pipeline_output.json ===")
    print("Run: streamlit run dashboard.py")
    return data

if __name__ == "__main__":
    run_pipeline()
