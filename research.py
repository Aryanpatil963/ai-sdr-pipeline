import openai, os, json
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a GTM analyst for an API platform for developers.
Given a company's info, you must:
1. Summarize what the company does (1-2 sentences)
2. Identify their likely use case for a video API based on their segment:
   - SMB: telehealth app, startup collaboration tool, internal meeting app
   - Enterprise: online education platform, banking communication system, enterprise customer support platform
3. Segment them strictly based on employee count:
   - "SMB": < 100 employees
   - "Enterprise": >= 200 employees
4. Generate a logical reasoning string for why they are in that segment.
   - Example Enterprise: "This company is classified as Enterprise due to large employee count, global operations, and complex infrastructure requirements."
5. Estimate pipeline value:
   - SMB: $500-$2000/yr
   - Enterprise: $20,000-$100,000/yr

Return ONLY valid JSON with keys:
{
  "summary": "...",
  "use_case": "...",
  "segment": "SMB" or "Enterprise",
  "reasoning": "...",
  "pipeline_value": "$X,XXX"
}
"""

def research_company(company: dict) -> dict:
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_key_here":
        # Return mock AI response if no key is provided
        emp_count = company.get('employee_count', 0) or 0
        is_enterprise = emp_count >= 200
        return {
            "summary": f"Company operating in {company.get('industry', 'tech')} space.",
            "use_case": "enterprise customer support platform" if is_enterprise else "startup collaboration tool",
            "segment": "Enterprise" if is_enterprise else "SMB",
            "reasoning": "This company is classified as Enterprise due to large employee count, global operations, and complex infrastructure requirements." if is_enterprise else "Classified as SMB due to small team size and likely self-serve approach.",
            "pipeline_value": "$50,000/yr" if is_enterprise else "$1,200/yr"
        }

    prompt = f"""
Company: {company['name']}
Industry: {company['industry']}
Employees: {company['employee_count']}
Description: {company['description']}
Domain: {company['domain']}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cheap + fast
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        raw = response.choices[0].message.content
        # Remove markdown JSON codeblocks if present
        if raw.startswith("```json"):
            raw = raw.replace("```json", "", 1)
        if raw.endswith("```"):
            raw = raw[::-1].replace("```", "", 1)[::-1]
        raw = raw.strip()
        
        return json.loads(raw)
    except Exception as e:
        print(f"Error researching {company['name']}: {e}")
        return {"summary": "Error during AI generation", "segment": "SMB", "use_case": "unknown", 
                "reasoning": str(e), "pipeline_value": "$1,000/yr"}

def research_all(companies_data):
    """Add AI research to each company"""
    for item in companies_data:
        print(f"Researching {item['company']['name']}...")
        item["research"] = research_company(item["company"])
    return companies_data
