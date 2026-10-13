from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b"

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
    "stroke symptoms"
]


def careai_response(message):
    message = message.lower().strip()

    # Immediate safety check before calling the AI.
    if any(term in message for term in EMERGENCY_KEYWORDS):
        return (
            "🚨 Your symptoms may indicate an emergency. "
            "Please contact your local emergency services immediately. "
            "Do not delay urgent care while chatting with CAREAI. "
            "If possible, ask someone nearby to help."
        )

    try:
        result = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 250
                }
            },
            timeout=(5, 90)
        )

        result.raise_for_status()
        data = result.json()

        answer = data.get("message", {}).get("content", "").strip()

        if answer:
            return answer

        raise ValueError("Ollama returned an empty answer")

    except (requests.RequestException, ValueError) as error:
        app.logger.warning("Ollama request failed: %s", error)

        # Basic fallback if the local AI is unavailable.
        if "burn" in message:
            return (
                "For a minor thermal burn, cool the area under "
                "cool running water for 20 minutes. Do not apply "
                "ice, butter, or creams. Seek urgent medical care "
                "for serious burns."
            )

        if "fever" in message:
            return (
                "Fever can have many causes. Rest, drink fluids, "
                "and monitor your symptoms. Seek medical advice "
                "if symptoms worsen, persist, or concern you."
            )

        if "headache" in message:
            return (
                "For a mild headache, rest and drink water. "
                "Seek urgent medical care for a sudden, extremely "
                "severe headache or one with new neurological symptoms."
            )

        return (
            "CAREAI's local AI is temporarily unavailable. "
            "Please make sure Ollama is running and the selected "
            "model is installed, then try again. For urgent health "
            "concerns, contact a healthcare professional."
        )


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def files(filename):
    return send_from_directory(".", filename)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    if not isinstance(user_message, str):
        return jsonify({"response": "Please enter a valid text question."}), 400

    user_message = user_message.strip()

    if not user_message:
        return jsonify({"response": "Please type a question for CAREAI."}), 400

    if len(user_message) > 2000:
        return jsonify({
            "response": "Please keep your question under 2000 characters."
        }), 400

    response = careai_response(user_message)

    # Preserve the JSON format expected by your existing script.js.
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
