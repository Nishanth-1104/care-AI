from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are CAREAI, an AI companion for general health awareness,
basic first-aid education, healthy habits, and illness prevention.

Rules:
1. Use simple, friendly English and clear, practical explanations.
2. Understand natural questions, even when phrased differently.
3. Do not claim to diagnose a disease or replace a healthcare professional.
4. Do not prescribe medicines or invent medicine dosages.
5. If information is insufficient, ask a brief clarifying question.
6. For severe or sudden symptoms, recommend urgent medical evaluation.
7. For signs of a life-threatening emergency, tell the user to contact
   local emergency services immediately.
8. For burns, explain basic first aid and when emergency care is needed.
9. Be calm, respectful, concise, and avoid frightening the user.
10. Never claim that you have examined or diagnosed the user.
11. If unsure, say so instead of making up medical facts.
12. Give general educational information, not a definitive diagnosis.
"""

EMERGENCY_KEYWORDS = [
    "unconscious",
    "not breathing",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "chest pain",
    "heavy bleeding",
    "severe bleeding",
    "overdose",
    "suicide attempt",
    "seizure",
    "stroke symptoms",
]


def careai_response(message):
    message = message.lower().strip()

    # Emergency check
    if any(term in message for term in EMERGENCY_KEYWORDS):
        return (
            "🚨 Your symptoms may indicate an emergency. "
            "Please contact your local emergency services immediately. "
            "Do not delay urgent care while chatting with CAREAI. "
            "If possible, ask someone nearby to help."
        )

    if client is None:
        app.logger.error("GROQ_API_KEY is not configured")
        return "CAREAI is not configured yet. Please set GROQ_API_KEY and restart the server."

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.3,
            max_tokens=250,
        )

        answer = response.choices[0].message.content.strip()
        return answer if answer else "CAREAI could not generate a response."

    except Exception as error:
        app.logger.exception("Groq request failed: %s", error)

        # Fallback responses
        if "burn" in message:
            return "Cool burn under running water for 20 minutes. Seek urgent care for serious burns."
        if "fever" in message:
            return "Rest, drink fluids, and monitor. Seek medical advice if fever persists or worsens."
        if "headache" in message:
            return "Rest and hydrate. Seek urgent care for sudden severe headache or new neurological symptoms."
        return "CAREAI is temporarily unavailable. Please try again later."


@app.post("/chat")
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object."), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="A non-empty message is required."), 400

    return jsonify(response=careai_response(message))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
