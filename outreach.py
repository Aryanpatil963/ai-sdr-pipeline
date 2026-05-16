import openai, os
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SMB_EMAIL_PROMPT = """
Write a SHORT cold email (under 100 words) for a startup founder or CTO.
Tone: casual, direct, peer-to-peer. No fluff.
Goal: get them to try VideoSDK.live for free (self-serve).
Mention their specific use case. End with a CTA to sign up free.
Do NOT use generic phrases like "I hope this finds you well".
"""

ENTERPRISE_EMAIL_PROMPT = """
Write a cold email (120-150 words) for a VP/CTO at a mid-market/enterprise company.
Tone: professional, value-focused, ROI-driven.
Goal: book a 20-minute demo call.
Mention their company context, the pain point, and how VideoSDK solves it at scale.
Include a specific CTA to schedule a call.
"""

SMB_DM_PROMPT = """
Write a LinkedIn DM under 50 words for a startup founder.
Casual, genuine, no pitching. Just start a conversation around their use case.
"""

ENTERPRISE_DM_PROMPT = """
Write a LinkedIn DM (60-80 words) for a senior enterprise contact.
Professional, specific to their company, opens with an insight or question.
Goal: get a reply that leads to a call.
"""

def generate_outreach(contact: dict, company: dict, research: dict) -> dict:
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_key_here":
        # Fallback to mock data
        return {
            "cold_email": f"Hi {contact['name']},\n\nMock email body targeting {research.get('use_case', 'video')} for {company['name']}.\n\nBest,\nSDR",
            "linkedin_dm": f"Hey {contact['name']}, noticed you at {company['name']}. Let's chat about {research.get('use_case', 'video')}."
        }

    segment = research.get("segment", "SMB")
    use_case = research.get("use_case", "video communication")
    summary = research.get("summary", "")

    context = f"""
Contact: {contact['name']}, {contact['title']} at {company['name']}
Company summary: {summary}
Use case for VideoSDK: {use_case}
Segment: {segment}
"""

    email_prompt = SMB_EMAIL_PROMPT if segment == "SMB" else ENTERPRISE_EMAIL_PROMPT
    dm_prompt = SMB_DM_PROMPT if segment == "SMB" else ENTERPRISE_DM_PROMPT

    def call_gpt(system, user):
        try:
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.7
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating outreach: {e}")
            return f"Error: {str(e)}"

    return {
        "cold_email": call_gpt(email_prompt, context),
        "linkedin_dm": call_gpt(dm_prompt, context)
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
