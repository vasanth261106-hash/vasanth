import json, os
from .recommendation_service import home_fallback, party_fallback, jewelry_fallback

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None; types = None

class GeminiService:
    def __init__(self):
        self.api_key=os.getenv("GEMINI_API_KEY","").strip()
        self.model=os.getenv("GEMINI_MODEL","gemini-1.5-flash")
        self.client = genai.Client(api_key=self.api_key) if genai and self.api_key else None

    def _call(self, prompt, image_bytes=None, mime="image/jpeg"):
        if not self.client: return None
        contents=[prompt]
        if image_bytes and types:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime))
        response=self.client.models.generate_content(model=self.model, contents=contents)
        text=getattr(response,"text","") or ""
        text=text.strip().replace("```json","").replace("```","").strip()
        try: return json.loads(text)
        except Exception: return None

    def home(self,data):
        prompt=f"Return ONLY valid JSON for a home budget recommendation. Budget: {data}. Include title,total_budget,allocated,remaining,groups (array with category,item,description,price,quantity,platforms),additional_suggestions. Keep total within budget."
        return self._call(prompt) or home_fallback(data)
    def party(self,data):
        prompt=f"Return ONLY valid JSON for a party budget recommendation. Input: {data}. Include title,budget,allocated,remaining,groups (category,item,description,price,platforms),venue_suggestions,additional_suggestions. Keep total within budget."
        return self._call(prompt) or party_fallback(data)
    def jewelry(self,data,image_bytes=None,mime="image/jpeg"):
        prompt=f"Return ONLY valid JSON for jewelry recommendations. Input: {data}. Include title,total_budget,remaining,outfit_analysis,items (item,description,price,style,platforms),styling_tips."
        return self._call(prompt,image_bytes,mime) or jewelry_fallback(data)
