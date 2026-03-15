from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import os
from datetime import datetime

app = Flask(__name__)

genai.configure(api_key="AIzaSyCMQ1YiX7PlGVG5RHW9o7QImwyHD7bo8Os")
model = genai.GenerativeModel("gemini-2.5-flash")

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(load_history())

@app.route("/clear_session", methods=["POST"])
def clear_session():
    data = request.json
    session_id = data.get("session_id")
    history = load_history()
    history = [h for h in history if h.get("session_id") != session_id]
    save_history(history)
    return jsonify({"status": "cleared"})

@app.route("/clear_all", methods=["POST"])
def clear_all():
    save_history([])
    return jsonify({"status": "cleared"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").lower()
    session_id = data.get("session_id", "default")

    education_keywords = [
        "education", "school", "college", "university", "student", "teacher",
        "study", "learn", "exam", "test", "homework", "assignment", "class",
        "subject", "math", "science", "history", "geography", "english",
        "physics", "chemistry", "biology", "lesson", "syllabus", "degree",
        "course", "lecture", "textbook", "grade", "marks", "scholarship",
        "training", "knowledge", "skill", "reading", "writing", "arithmetic",
        "what is", "explain", "define", "how does", "why is", "who is",
        "formula", "theorem", "equation", "element", "atom", "cell",
        "grammar", "literature", "poem", "essay", "language", "culture"
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history = load_history()

    if not any(word in user_message for word in education_keywords):
        error_reply = "⚠️ Out of Domain: I am an Education chatbot. Please ask questions related to subjects like Mathematics, Science, History, Geography, English, or any academic topic."
        history.append({
            "session_id": session_id,
            "datetime": timestamp,
            "user": user_message,
            "bot": error_reply,
            "type": "error"
        })
        save_history(history)
        return jsonify({"reply": error_reply, "type": "error"})

    try:
        prompt = f"""You are EduBot, an expert education assistant. Answer the following question clearly and in a well-structured format.

Rules for your response:
- Use numbered points for steps or lists
- Use bullet points for details or explanations
- Use headings where needed
- Keep each point short and clear
- If there is a definition, state it first
- End with a simple summary if the answer is long

Question: {user_message}"""

        response = model.generate_content(prompt)
        bot_reply = response.text

        history.append({
            "session_id": session_id,
            "datetime": timestamp,
            "user": user_message,
            "bot": bot_reply,
            "type": "success"
        })
        save_history(history)
        return jsonify({"reply": bot_reply, "type": "success"})

    except Exception as e:
        app.logger.exception("Error generating response")
        return jsonify({"error": "Failed to generate response", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
