import os
from dotenv import load_dotenv
from google import generativeai as genai

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise Exception("❌ GOOGLE_API_KEY missing")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


def summarize_domain(content: str, url: str, page_count: int):
    prompt = f"""
You are an expert technical writer. Summarize the overall website in a medium, clean, professional format.
Generate ONLY Markdown.

## 🌐 Domain Summary  
(Write 6–8 lines clearly describing the website's purpose, target audience, content, and strengths.)

### ⭐ Key Features of the Domain
- Extract 4–6 important key features from the content.
- Features must be short and meaningful.

Here is the website content:
\"\"\"
{content}
\"\"\"
"""

    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Domain summary failed: {str(e)}"


def summarize_page(page_text: str, page_url: str):
    prompt = f"""
You are an AI documentation writer. Summarize the page in a medium-sized, clean structure.
Generate ONLY Markdown.

### 📝 Summary  
(Write 6–8 lines explaining the page contents and purpose.)

### ⭐ Key Features  
- Extract 3–5 important features from this page.

Page URL: {page_url}

Page Content:
\"\"\"
{page_text}
\"\"\"
"""

    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Page summary failed: {str(e)}"
