import os
import openai
import google.generativeai as genai

openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def get_smart_reply(user_message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-pro")
            resp = model.generate_content(user_message)
            return resp.text
        except Exception:
            return "🥔 Та шось пішло не так із тими нейромережами..."