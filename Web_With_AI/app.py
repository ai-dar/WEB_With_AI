from flask import Flask, render_template, request, jsonify
from g4f.client import Client

app = Flask(__name__)
client = Client()

# Словарь для хранения истории разговоров
conversation_history = {}

# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_id = request.remote_addr  # Используем IP адрес как идентификатор пользователя
    user_input = request.json.get('message')

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Инициализация истории пользователя, если ее нет
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Добавляем сообщение пользователя в историю
    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    try:
        # Отправка запроса к модели GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history[user_id],
        )
        chat_gpt_response = response.choices[0].message.content  # Ответ модели

        # Добавляем ответ бота в историю
        conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})

        return jsonify({"response": chat_gpt_response})
    except Exception as e:
        print(f"Error while processing GPT request: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
