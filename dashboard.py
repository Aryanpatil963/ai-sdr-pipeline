import streamlit as st
import json, pandas as pd

# Must be the first Streamlit command
st.set_page_config(page_title="AI SDR Pipeline", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    /* Styling to make the UI look more premium and less default */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .badge-smb {
        background-color: #2e7d32;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8em;
    }
    .badge-enterprise {
        background-color: #1565c0;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8em;
    }
    .company-card {
        background: #1E2127;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
    .main-title {
        background: -webkit-linear-gradient(#eee, #333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        text-align: center;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Outbound SDR Pipeline — VideoSDK")
st.markdown("<p style='text-align: center; color: #888;'>Automated Discovery, AI Research & Personalized Outreach Generation</p>", unsafe_allow_html=True)

try:
    with open("pipeline_output.json") as f:
        data = json.load(f)
except FileNotFoundError:
    st.warning("No pipeline output found. Run `python main.py` first to generate data.")
    st.stop()

# Summary table
st.subheader("📊 Pipeline Overview")

# Calculate some metrics
total_companies = len(data)
total_contacts = sum(len(item.get("contacts", [])) for item in data)
enterprise_count = sum(1 for item in data if item.get("research", {}).get("segment") == "Enterprise")
smb_count = total_companies - enterprise_count

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Companies", total_companies)
col2.metric("Total Contacts", total_contacts)
col3.metric("SMB Opportunities", smb_count)
col4.metric("Enterprise Opportunities", enterprise_count)

st.divider()

rows = []
for item in data:
    r = item.get("research", {})
    rows.append({
        "Company": item["company"]["name"],
        "Segment": r.get("segment", "-"),
        "Use Case": r.get("use_case", "-"),
        "Pipeline Value": r.get("pipeline_value", "-"),
        "Contacts": len(item["contacts"])
    })

df = pd.DataFrame(rows)

# Clean and visually pleasing dataframe
def highlight_segment(s):
    if s == "Enterprise":
        return "background-color: rgba(21, 101, 192, 0.2); color: #90caf9;"
    return "background-color: rgba(46, 125, 50, 0.2); color: #a5d6a7;"

st.dataframe(
    df.style.map(highlight_segment, subset=["Segment"]), 
    use_container_width=True,
    hide_index=True
)

st.divider()
st.subheader("🎯 Target Accounts Drill-down")

# Drill-down per company
for item in data:
    co = item["company"]
    r = item.get("research", {})
    seg = r.get("segment", "SMB")
    
    badge_html = f"<span class='badge-smb'>SMB</span>" if seg == "SMB" else f"<span class='badge-enterprise'>Enterprise</span>"
    
    with st.expander(f"{co['name']} | {r.get('pipeline_value', 'Unknown Value')} | {seg}"):
        st.markdown(f"### {co['name']} {badge_html}", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**What they do:** {r.get('summary', 'No summary generated')}")
            st.markdown(f"**VideoSDK use case:** {r.get('use_case', 'Unknown')}")
            st.info(f"**AI Reasoning:** {r.get('reasoning', 'No reasoning provided')}")
        with col2:
            st.markdown(f"**Domain:** [{co.get('domain', '#')}](https://{co.get('domain', '')})")
            st.markdown(f"**Employees:** {co.get('employee_count', 'Unknown')}")
            st.markdown(f"**Industry:** {co.get('industry', 'Unknown')}")

        st.markdown("#### 👥 Contacts + Outreach")
        outreach_data = item.get("outreach_per_contact", [])
        if not outreach_data:
            st.warning("No outreach generated for this company.")
            
        for idx, item2 in enumerate(outreach_data):
            contact = item2.get("contact", {})
            outreach = item2.get("outreach", {})
            st.markdown(f"##### {contact.get('name', 'Unknown')} — {contact.get('title', 'Unknown Title')}")
            st.caption(f"Email: {contact.get('email', 'N/A')} | LinkedIn: {contact.get('linkedin', 'N/A')}")
            
            tab1, tab2 = st.tabs(["✉️ Cold Email", "💬 LinkedIn DM"])
            with tab1:
                st.code(outreach.get("cold_email", "No email generated"), language="text")
            with tab2:
                st.code(outreach.get("linkedin_dm", "No DM generated"), language="text")
            st.markdown("---")
