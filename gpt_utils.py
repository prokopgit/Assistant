import openai
import google.generativeai as genai
import os
import re

openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def clean_html(text: str) -> str:
    return re.sub(r'<[^>]*?>', '', text)

async def get_smart_reply(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-pro")
            r = model.generate_content(prompt)
            return r.text
        except Exception:
            return "🥔 Та шось пішло не так із тими нейромережами..."