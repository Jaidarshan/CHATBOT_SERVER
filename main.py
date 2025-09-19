import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import base64

app = Flask(__name__)
CORS(app)

api_key = None
model = None
hf_api_token = None 

@app.route('/api/set-api-key', methods=['POST'])
def set_api_key():
    global api_key, model, hf_api_token 
    data = request.json
    
    api_key = data.get('api_key', '').strip()
    hf_api_token = data.get('hf_token', '').strip() 

    if not api_key or not hf_api_token:
        return jsonify({'error': 'Both Gemini API Key and Hugging Face Token are required.'}), 400

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return jsonify({'message': 'API keys set successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/chat', methods=['POST'])
def chat():
    global model, hf_api_token 
    
    if not model or not hf_api_token: 
        return jsonify({'error': 'API keys not set. Please set the API keys first.'}), 400

    data = request.json
    input_prompt = data.get('prompt', '').strip()
    # Get the history from the request, default to an empty list
    history_data = data.get('history', [])

    if not input_prompt:
        return jsonify({'error': 'Please enter a valid prompt.'}), 400

    try:
        # Image generation logic remains the same (it doesn't need history)
        if input_prompt.lower().startswith("generate image of"):
            image_prompt = input_prompt[len("generate image of"):].strip()
            
            if not hf_api_token:
                return jsonify({'error': 'Hugging Face Token not set. Please set it via the API key modal.'}), 400

            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {hf_api_token}"} 
            payload = {"inputs": image_prompt}

            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()

            image_bytes = response.content
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{base64_image}"
            
            return jsonify({'image_url': image_data_url}), 200
        
        else:
            formatted_history = []
            for entry in history_data:
                role = 'user' if entry['type'] == 'user' else 'model'
                if 'text' in entry:
                    formatted_history.append({'role': role, 'parts': [entry['text']]})

            chat_session = model.start_chat(history=formatted_history)

            gemini_response = chat_session.send_message(input_prompt)
            
            return jsonify({'response': gemini_response.text}), 200

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 503:
            return jsonify({'error': 'The image model is currently loading, please try again in 20-30 seconds.'}), 503
        elif e.response.status_code == 401:
            return jsonify({'error': 'Authentication failed. Please check your Hugging Face token.'}), 401
        return jsonify({'error': f"Error calling Image API: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)