from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from monsterapi import client  # Assuming the Monster API client is imported

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to store the API keys and models
api_key = None
model = None
monster_api_key = None
monster_client = None


@app.route('/api/set-api-key', methods=['POST'])
def set_api_key():
    global api_key, model, monster_api_key, monster_client
    data = request.json
    api_key = data.get('api_key', '').strip()
    monster_api_key = data.get('monster_api_key', '').strip()  # Get Monster API key

    if not api_key or not monster_api_key:
        return jsonify({'error': 'Both API keys are required.'}), 400

    try:
        # Set up Gemini API (text generation model)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Set up Monster API client
        monster_client = client(monster_api_key)

        return jsonify({'message': 'API keys set successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/chat', methods=['POST'])
def chat():
    global model, monster_client
    if not model or not monster_client:
        return jsonify({'error': 'API keys not set. Please set the API keys first using /api/set-api-key.'}), 400

    data = request.json
    input_prompt = data.get('prompt', '').strip()

    if not input_prompt:
        return jsonify({'error': 'Please enter a valid prompt.'}), 400

    try:
        # Check if the prompt is for image generation
        if input_prompt.lower().startswith("generate image of"):
            # Use the Monster API to generate the image
            model_name = 'txt2img'
            input_data = {
                'prompt': input_prompt,
                'samples': 1,
                'steps': 50,
                'aspect_ratio': 'square',
                'guidance_scale': 7.5,
                'seed': 2414,
            }
            # Generate the image and get the URL
            result = monster_client.generate(model_name, input_data)
            image_url = result['output'][0]  # Assuming the result returns a list of images
            return jsonify({'image_url': image_url}), 200
        else:
            # Otherwise, use the Gemini model for text generation
            response = model.generate_content(input_prompt)
            return jsonify({'response': response.text}), 200
    except Exception as e:
        return jsonify({'error': f"Error generating content: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
