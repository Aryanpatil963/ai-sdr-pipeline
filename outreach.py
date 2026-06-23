import openai, os, json
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MASTER_OUTREACH_PROMPT = """
You are an expert AI SDR (Sales Development Representative).

Your task is to generate:
1. A personalized cold email
2. A personalized LinkedIn DM

The messages MUST feel human, personalized, and relevant to the prospect's business.

Follow these rules carefully:

### PRIORITY RULES
- Do NOT sound generic or like a mass template.
- Mention the company context naturally (use the provided company summary).
- Show that you understand the company's industry and use case.
- Keep SMB outreach short and casual.
- Keep Enterprise outreach professional and detailed.
- Use natural language, not marketing buzzwords.
- Include one clear CTA only.

### CTA RULES
For SMB:
- "Worth trying our free version?"
- "Happy to share a quick setup link."

For Enterprise:
- "Open to a quick 20-minute demo next week?"
- "Would it make sense to explore this further?"

### OUTPUT FORMAT
Return ONLY a valid JSON object with exactly two keys: "cold_email" and "linkedin_dm". Do not use markdown blocks around the JSON.
{
  "cold_email": "Subject: ...\\n\\nHi Name,\\n...",
  "linkedin_dm": "Hey Name, ..."
}
"""

def generate_outreach(contact: dict, company: dict, research: dict) -> dict:
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_key_here":
        # Fallback to mock data if no OpenAI key
        is_smb = research.get("segment") == "SMB"
        cta = "Worth trying our free version?" if is_smb else "Open to a quick 20-minute demo next week?"
        first_name = contact['name'].split()[0] if 'name' in contact else 'there'
        
        return {
            "cold_email": f"Subject: {company['name']} + Our Platform\n\nHi {first_name},\n\nI noticed {company['name']} is building interesting things in the {company.get('industry', 'tech')} space. Since you are the {contact.get('title', 'leader')}, I thought you might be dealing with {research.get('use_case', 'API')} challenges.\n\nOur platform helps teams solve exactly this at scale.\n\n{cta}\n\nBest,\nSDR",
            "linkedin_dm": f"Hey {first_name}, loved what {company['name']} is doing. Wondering how you're handling {research.get('use_case', 'video')}? {cta}"
        }

    segment = research.get("segment", "SMB")
    use_case = research.get("use_case", "video communication")
    summary = research.get("summary", "")

    user_context = f"""
Prospect Name: {contact.get('name', 'Unknown')}
Role: {contact.get('title', 'Unknown')}
Company: {company.get('name', 'Unknown')}
Industry: {company.get('industry', 'Technology')}
Company Size: {segment}
Company Summary: {summary}
Product/Service Being Sold: Our API Platform
Pain Point Solved/Use Case: {use_case}
"""

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": MASTER_OUTREACH_PROMPT},
                {"role": "user", "content": user_context}
            ],
            temperature=0.7
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```json"):
            raw = raw.replace("```json", "", 1)
        if raw.endswith("```"):
            raw = raw[::-1].replace("```", "", 1)[::-1]
        
        return json.loads(raw.strip())
    except Exception as e:
        print(f"Error generating outreach for {contact.get('name')}: {e}")
        return {
            "cold_email": f"Error generating email: {e}",
            "linkedin_dm": f"Error generating DM: {e}"
        }

def generate_all_outreach(companies_data):
    for item in companies_data:
        item["outreach_per_contact"] = []
        for contact in item["contacts"]:
            print(f"  Writing outreach for {contact.get('name', 'Unknown')}...")
            outreach = generate_outreach(contact, item["company"], item["research"])
            item["outreach_per_contact"].append({
                "contact": contact,
                "outreach": outreach
            })
    return companies_data
