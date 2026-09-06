import os, json

CATEGORIES=["Electronics","ID/Documents","Keys","Clothing","Bags","Books","Accessories","Wallet/Money","Other"]

def _fallback(title, description):
    text=f"{title} {description}".lower()
    mapping={
        "Electronics":["laptop","phone","mobile","earphone","headphone","charger","watch"],
        "ID/Documents":["id","card","aadhaar","passport","document","certificate"],
        "Keys":["key","keys"],
        "Clothing":["shirt","jacket","shoe","shoes","hoodie"],
        "Bags":["bag","backpack","purse"],
        "Books":["book","notebook"],
        "Accessories":["glasses","spectacles","umbrella"],
        "Wallet/Money":["wallet","cash","money"]
    }
    category="Other"
    for c,words in mapping.items():
        if any(w in text for w in words): category=c; break
    words=[w.strip(".,!?;:()").lower() for w in text.split() if len(w)>3]
    return {"category":category,"summary":f"{title}: {description}","keywords":list(dict.fromkeys(words))[:15]}

def analyze_item(title,description,location):
    key=os.getenv("GEMINI_API_KEY")
    if not key: return _fallback(title,description)
    try:
        from google import genai
        client=genai.Client(api_key=key)
        prompt=f"""Analyze this lost/found item. Return ONLY JSON:
{{"category":"one of {CATEGORIES}","summary":"one sentence","keywords":["up to 12 important keywords"]}}
Title: {title}
Description: {description}
Location: {location}"""
        r=client.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"), contents=prompt)
        text=r.text.strip().replace("```json","").replace("```","").strip()
        data=json.loads(text)
        if data.get("category") not in CATEGORIES: data["category"]="Other"
        return data
    except Exception:
        return _fallback(title,description)

def explain_match(lost,found,score):
    key=os.getenv("GEMINI_API_KEY")
    if not key:
        return f"Possible match at {score:.0%}. Similar item details/category/location were detected. Verify unique identifiers before claiming."
    try:
        from google import genai
        client=genai.Client(api_key=key)
        prompt=f"""Explain why these lost/found reports may match in 2 concise sentences.
Do not claim certainty. Match score: {score:.0%}
LOST: {lost}
FOUND: {found}"""
        return client.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"), contents=prompt).text.strip()
    except Exception:
        return f"Possible match at {score:.0%}. Verify unique details."

def image_hint(filename):
    return "Image uploaded. Use it as supporting evidence; do not treat visual similarity as proof of ownership."
