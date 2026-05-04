from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    question = data.get('question', '')
    
    # Получаем ключи из переменных окружения
    api_key = os.environ.get('YANDEX_API_KEY')
    folder_id = os.environ.get('YANDEX_FOLDER_ID')
    
    print(f"🔑 API Key (первые 10): {api_key[:10] if api_key else 'None'}")
    print(f"📁 Folder ID: {folder_id}")
    print(f"❓ Вопрос: {question}")
    
    # Запрос к Yandex
    response = requests.post(
        'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {api_key}',
            'x-folder-id': folder_id
        },
        json={
            "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
            "completionOptions": {"temperature": 0.7, "maxTokens": 500},
            "messages": [{"role": "user", "text": question}]
        }
    )
    
    print(f"📡 Статус ответа: {response.status_code}")
    print(f"📄 Тело ответа: {response.text[:300]}")
    
    return jsonify(response.json()), response.status_code

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
