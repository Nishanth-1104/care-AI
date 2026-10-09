from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)


def careai_response(message):
    message = message.lower().strip()

    if "hello" in message or "hi" in message:
        return "Hello! 👋 I'm CAREAI. How can I help you?"

    elif "fever" in message:
        return "Fever can happen for many reasons. Stay hydrated, rest, and monitor your symptoms. If symptoms are severe or persistent, seek medical care."

    elif "headache" in message:
        return "For a mild headache, try resting and drinking enough water. If the headache is sudden, severe, or unusual, seek medical attention."

    elif "burn" in message:
        return "For a minor burn, cool the area under clean running water for about 20 minutes. Do not apply ice directly. Serious burns need medical attention."

    elif "water" in message or "hydration" in message:
        return "💧 Staying hydrated is important. Drink water regularly, especially during hot weather or physical activity."

    elif "healthy" in message or "lifestyle" in message or "healthy habits" in message:
        return "🥗 Eat nutritious food, stay active, drink enough water, sleep well, and maintain good hygiene."

    elif "prevention" in message:
        return "🛡️ Regular handwashing, good hygiene, nutritious food, physical activity, and recommended preventive healthcare can help reduce health risks."
    elif "cold" in message:
        return "For a mild cold, get enough rest, drink fluids, and monitor your symptoms. Seek medical care if symptoms become severe or persistent."

    elif "cough" in message:
        return "For a mild cough, stay hydrated and rest. If you have difficulty breathing, chest pain, or a persistent severe cough, seek medical care."

    elif "stomach pain" in message or "stomach" in message:
        return "For mild stomach discomfort, stay hydrated and eat light foods. If the pain is severe or persistent, seek medical care."
    
    elif "emergency" in message or "unconscious" in message:
        return "🚨 This may be an emergency. Contact your local emergency services immediately and stay with the person if it is safe to do so."

    elif "bleeding" in message:
        return "🩹 Apply firm, steady pressure with clean cloth or gauze to control bleeding. If bleeding is heavy or does not stop, seek emergency medical help."

    elif "choking" in message:
        return "🚨 Choking can be life-threatening. If the person cannot breathe or speak, seek emergency help immediately."

    elif "nosebleed" in message:
        return "For a nosebleed, sit upright, lean slightly forward, and gently pinch the soft part of the nose for about 10–15 minutes. Seek medical care if bleeding continues."

    elif "sprain" in message:
        return "For a mild sprain, rest the area and use a wrapped cold pack for short periods. If there is severe pain, deformity, or inability to use the limb, seek medical care."
    else:
        return "I'm still learning! 🤖 Please ask me about fever, headache, burns, hydration, healthy habits, or prevention."


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def files(filename):
    return send_from_directory(".", filename)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "")

    response = careai_response(user_message)

    return jsonify({
        "response": response
    })


if __name__ == "__main__":
    app.run(debug=True)