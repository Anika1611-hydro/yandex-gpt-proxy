from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY')
YANDEX_FOLDER_ID = os.environ.get('YANDEX_FOLDER_ID')

@app.route('/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    question = data.get('question', '')
    
    response = requests.post(
        'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {YANDEX_API_KEY}',
            'x-folder-id': YANDEX_FOLDER_ID
        },
        json={
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {"temperature": 0.7, "maxTokens": 500},
            "messages": [{"role": "user", "text": question}]
        }
    )
    
    if response.status_code != 200:
        return jsonify({'error': f'Ошибка {response.status_code}'}), response.status_code
    
    result = response.json()
    answer = result['result']['alternatives'][0]['message']['text']
    
    # Возвращаем для сайта простой JSON с полем answer
    return jsonify({'answer': answer})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
