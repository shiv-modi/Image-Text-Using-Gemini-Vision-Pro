from pathlib import Path
import google.generativeai as genai
from flask import Flask, request, render_template

app = Flask(__name__)

genai.configure(api_key="API_KEY")

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(model_name="gemini-pro-vision",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_image = request.files.get('image')
        
        if uploaded_image:
            try:
                image_path = Path("uploads") / uploaded_image.filename
                uploaded_image.save(image_path)
            except Exception as e:
                return render_template('index.html', error=f"Error saving image: {e}")

            # Validate that an image is present
            if not image_path.exists():
                return render_template('index.html', error=f"Could not find image: {image_path}")

            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": image_path.read_bytes()
                },
            ]

            user_input = request.form['content']
            
            try:
                prompt_parts = [image_parts[0], user_input]
                response = model.generate_content(prompt_parts)
                return render_template('index.html', generate=response.text ,user_input = user_input)
            except Exception as e:
                return render_template('index.html', error=f"Error generating content: {e}")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5007)
