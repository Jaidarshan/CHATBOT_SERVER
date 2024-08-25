from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store the API key
api_key = None
model = None

@app.route('/api/set-api-key', methods=['POST'])
def set_api_key():
    global api_key, model
    data = request.json
    api_key = data.get('api_key', '').strip()

    if not api_key:
        return jsonify({'error': 'API key is required.'}), 400

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return jsonify({'message': 'API key set successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    global model
    if not model:
        return jsonify({'error': 'API key not set. Please set the API key first using /api/set-api-key.'}), 400

    data = request.json
    input_prompt = data.get('prompt', '').strip()

    if not input_prompt:
        return jsonify({'error': 'Please enter a valid prompt.'}), 400

    try:
        response = model.generate_content(input_prompt)
        return jsonify({'response': response.text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
