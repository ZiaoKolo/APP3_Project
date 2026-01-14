import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clé API Google Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA7NyEgc7JZozf1IBbYmPbTGSP5V_A-waA")
    
    # Modèle Gemini à utiliser
    GEMINI_MODEL = "gemini-2.5-pro"  
    
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
        "pm25": {"normal": 12, "warning": 35, "danger": 55}
    }