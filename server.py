from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Your keys here
OPENROUTER_API_KEY = "your OPENROUTER_API_KEY"
HUGGINGFACE_API_KEY = "your HUGGINGFACE_API_KEY "

# Language name mapping to English-readable form (from detection)
LANG_CODE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Marathi": "mr"
}

# Supported translation models (src → tgt)
TRANSLATION_MODEL_MAP = {
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
    ("fr", "en"): "Helsinki-NLP/opus-mt-ROMANCE-en",
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
    ("es", "en"): "Helsinki-NLP/opus-mt-ROMANCE-en",
    ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
    ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
    ("en", "mr"): "Helsinki-NLP/opus-mt-en-mr",
    ("mr", "en"): "Helsinki-NLP/opus-mt-mr-en"
}


# Detect language using OpenRouter (Mistral)
def detect_language(text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Language Translator"
    }
    prompt = f"Detect the language of the following text:\n\"{text}\""
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    lang = response.json()["choices"][0]["message"]["content"]
    return lang.strip().split()[0]  # Just "English", "Hindi", etc.

# Translate using Hugging Face Helsinki-NLP
def translate(text, src_lang, tgt_lang):
    model_id = TRANSLATION_MODEL_MAP.get((src_lang, tgt_lang))
    if not model_id:
        return f"❌ Translation from {src_lang} to {tgt_lang} not supported."

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = { "inputs": text }

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=15
        )

        # Fail early on bad response
        if not response.ok:
            return f"❌ Hugging Face Error: {response.status_code} {response.reason}"

        try:
            result = response.json()
        except Exception as e:
            return f"❌ JSON decode error: {str(e)}"

        if isinstance(result, list) and "translation_text" in result[0]:
            return result[0]["translation_text"]
        elif "error" in result:
            return f"❌ Model error: {result['error']}"
        else:
            return "❌ Unexpected response format."

    except Exception as e:
        return f"❌ Translation request failed: {str(e)}"


@app.route("/translate", methods=["POST"])
def translate_route():
    try:
        data = request.get_json()
        text = data["text"]
        target = data.get("target_lang", "hi")

        # Use passed source_lang if available
        source_lang = data.get("source_lang")
        if not source_lang:
            detected_lang_name = detect_language(text)
            source_lang = LANG_CODE_MAP.get(detected_lang_name, "en")

        translated = translate(text, source_lang, target)

        return jsonify({ "translation": translated })

    except Exception as e:
        return jsonify({ "translation": f"❌ Server error: {str(e)}" }), 500


if __name__ == "__main__":
    app.run(debug=True)
