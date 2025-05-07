import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from together import Together
from retrying import retry

app = Flask(__name__)
CORS(app)

# Configurer l'API Together AI
api_key = "50c2ff4f3f7c67049d390f5fe9f179663bba09fe9ca629221b95276658b78d70"
client = Together(api_key=api_key)

@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000,
    stop_max_attempt_number=5
)
def call_together_with_retry(prompt):
    # Combiner les prompts
    system_prompt = prompt[0]["content"]
    user_prompt = prompt[1]["content"]
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": combined_prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=2048
    )
    return response

@app.route('/')
def home():
    return render_template('pageweb.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Le champ "prompt" est requis dans le JSON'}), 400
        prompt = data['prompt']
        print(f"Prompt reçu : {prompt}")

        system_prompt = """You are an expert Frontend HTML developer who use tailwind CSS with the CDN to style his html. You generate concise, valid HTML5 (HTML, CSS, JavaScript on the same page, no separate files) code, on the same page, based on user descriptions, just focus on giving the code. Always include basic HTML structure (<!DOCTYPE html>, <html>, <head>, <body>). Always give CSS styles that make smooth and attractive UI, basic CSS styles that can make modern interface, and ensure proper nesting of elements. Prioritize functionality and responsiveness. And if you have to give a response, give it in French. Don't put backticks at the top or end of the code. Always style buttons with some colors and border-radius."""
        user_prompt = f"Create a HTML web app based on this description: {prompt}"

        print("Appel de l'API Together...")
        completion = call_together_with_retry(
            prompt=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        print(f"Réponse API : {completion}")

        generated_code = completion.choices[0].message.content
        return jsonify({'code': generated_code})
    except Exception as e:
        print(f"Erreur : {str(e)}")
        return jsonify({'error': f"Erreur lors de la génération du code : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)