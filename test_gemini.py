from config import Config
import google.generativeai as genai
import traceback
import os

# Prefer model from environment if provided in .env
model_name = os.getenv('GEMINI_MODEL') or Config.GEMINI_MODEL
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(model_name)
print('Using model:', model_name)
try:
    resp = model.generate_content('Bonjour')
    print('RESPONSE_OK')
    text = getattr(resp, 'text', None)
    if text:
        print('TEXT_PREFIX:', text[:400])
    else:
        print('NO_TEXT_FIELD - full repr:')
        print(repr(resp))
except Exception as e:
    print('EXCEPTION')
    traceback.print_exc()
