from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY')
YANDEX_FOLDER_ID = os.environ.get('YANDEX_FOLDER_ID')

@app.route('/ask', methods=['POST'])
def ask_yandex():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Вопрос не может быть пустым'}), 400
        
        request_body = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 500
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты эколог-эксперт по ООПТ, гидрологии и качеству воды в Ленинградской области. Отвечай на русском языке кратко, понятно и полезно."
                },
                {
                    "role": "user",
                    "text": question
                }
            ]
        }
        
        # ========== ЛОГИРОВАНИЕ ОТПРАВКИ ==========
        print("=" * 50)
        print("🚀 Отправляю в Yandex:")
        print("  URL:", 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion')
        print("  API Key (первые 10 символов):", YANDEX_API_KEY[:10] + "..." if YANDEX_API_KEY else "None")
        print("  Folder ID:", YANDEX_FOLDER_ID)
        print("  Body:", request_body)
        print("=" * 50)
        
        response = requests.post(
            'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Api-Key {YANDEX_API_KEY}',
                'x-folder-id': YANDEX_FOLDER_ID
            },
            json=request_body,
            timeout=30
        )
        
        # ========== ЛОГИРОВАНИЕ ОТВЕТА ==========
        print("=" * 30)
        print(f"📡 СТАТУС ОТВЕТА: {response.status_code}")
        print(f"📄 ТЕЛО ОТВЕТА: {response.text[:500]}")
        print("=" * 30)
        
        if response.status_code != 200:
            return jsonify({'error': f'YandexGPT ошибка: {response.status_code}'}), response.status_code
        
        result = response.json()
        answer = result.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', 'Не удалось получить ответ')
        
        # ========== ЛОГИРОВАНИЕ УСПЕШНОГО ОТВЕТА ==========
        print("✅ Yandex ответил:", answer[:200])
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        print("🔥 КРИТИЧЕСКАЯ ОШИБКА:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
