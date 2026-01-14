import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuration OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Modèle Gemini via OpenRouter
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "google/gemini-2.5-pro")  
    
    # Chemins des fichiers
    TRAINING_DATA_PATH = "data/training_data.csv"
    SAMPLE_INPUT_PATH = "data/sample_input.json"
    
    # Paramètres du modèle
    TEMPERATURE = 0.7
    MAX_OUTPUT_TOKENS = 2048
    
    # Paramètres audio
    AUDIO_LANGUAGE = "fr"  
    AUDIO_OUTPUT_DIR = "output_audio/"
    
    # Seuils d'alerte
    THRESHOLDS = {
        "co2": {"normal": 800, "warning": 1000, "danger": 1500},
        "humidity": {"min_normal": 40, "max_normal": 60},
        "temperature": {"min_normal": 18, "max_normal": 26},
        "pm25": {"normal": 12, "warning": 35, "danger": 55},
        "no2": {"normal": 40, "warning": 100, "danger": 200},
        "pressure": {"min_normal": 1000, "max_normal": 1030}
    }