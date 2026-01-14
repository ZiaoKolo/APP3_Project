from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
from main import RespirIAModel
from config import Config
import os

# Initialisation de l'API
app = FastAPI(
    title="RespirIA API",
    description="API de prédiction des risques respiratoires avec IA",
    version="1.0.0"
)

# Configuration CORS pour permettre les appels depuis une application web/mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le modèle IA (chargé une seule fois au démarrage)
model = RespirIAModel()
model.load_training_data()

# Modèles de données Pydantic
class SensorData(BaseModel):
    """
    Format des données des capteurs
    """
    temperature: Optional[float] = None  # Temp. en °C
    humidity: Optional[float] = None  # Humidité en %
    co2: Optional[float] = None  # CO2 en ppm
    pm25: Optional[float] = None  # PM2.5 en µg/m³
    no2: Optional[float] = None  # NO2 en µg/m³
    pressure: Optional[float] = None  # Pression en hPa
    pollen: Optional[str] = None
    timestamp: Optional[str] = None
    location: Optional[str] = None
    user_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "temperature": 22.0,
                "humidity": 65.0,
                "co2": 420.0,
                "pm25": 38.0,
                "no2": 45.0,
                "pressure": 1015.0,
                "pollen": "modéré",
                "timestamp": "2026-01-14T14:30:00",
                "location": "Abidjan",
                "user_id": "user123"
            }
        }

class AnalysisResponse(BaseModel):
    """
    Format de la réponse d'analyse
    """
    success: bool
    # Données des capteurs
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2: Optional[float] = None
    pm25: Optional[float] = None
    no2: Optional[float] = None
    pressure: Optional[float] = None
    # Qualité de l'air
    air_quality_score: Optional[int] = None  # Score 0-100
    air_quality_level: Optional[str] = None  # "Bon", "Modéré", "Air mal sein", etc.
    # Analyse des risques
    niveau_risque: str
    score_risque: Optional[int] = None
    maladies_concernees: Optional[List[str]] = []
    risques_sante: Optional[List[dict]] = []  # Health risks with descriptions
    facteurs_risque: Optional[List[dict]] = []
    recommandations: Optional[List[str]] = []
    message_vocal: str
    previsions: Optional[str] = None
    audio_url: Optional[str] = None


# Routes de l'API

@app.get("/")
async def root():
    """
    Page d'accueil de l'API
    """
    return {
        "message": "Bienvenue sur RespirIA API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Analyser les données des capteurs",
            "POST /analyze-with-audio": "Analyser et générer l'audio",
            "GET /health": "Vérifier l'état de l'API",
            "GET /docs": "Documentation interactive"
        }
    }

@app.get("/health")
async def health_check():
    """
    Vérification de l'état de santé de l'API
    """
    return {
        "status": "healthy",
        "model_loaded": model.training_context != "",
        "gemini_configured": Config.GEMINI_API_KEY != "votre_cle_api_ici"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_environment(sensor_data: SensorData):
    """
    Analyse les données des capteurs et retourne une prédiction
    
    Args:
        sensor_data: Données des capteurs au format JSON
        
    Returns:
        Analyse complète avec niveau de risque et recommandations
    """
    try:
        # Convertir les données Pydantic en dictionnaire
        data_dict = sensor_data.dict(exclude_none=True)
        
        # Analyser avec le modèle IA
        result = model.analyze_environment(data_dict)
        
        # Ajouter le statut de succès
        result["success"] = True
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse : {str(e)}"
        )

@app.post("/analyze-with-audio", response_model=AnalysisResponse)
async def analyze_with_audio(sensor_data: SensorData):
    """
    Analyse les données ET génère un fichier audio
    
    Args:
        sensor_data: Données des capteurs au format JSON
        
    Returns:
        Analyse complète + URL du fichier audio
    """
    try:
        # Convertir les données
        data_dict = sensor_data.dict(exclude_none=True)
        
        # Analyser avec le modèle IA
        result = model.analyze_environment(data_dict)
        
        # Générer l'audio si un message vocal existe
        if "message_vocal" in result and result["message_vocal"]:
            user_id = data_dict.get("user_id", "unknown")
            filename = f"alerte_{user_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            audio_path = model.generate_audio(result["message_vocal"], filename)
            
            if audio_path:
                # Retourner l'URL relative du fichier audio
                result["audio_url"] = f"/audio/{filename}"
        
        result["success"] = True
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse avec audio : {str(e)}"
        )

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    Récupère un fichier audio généré
    
    Args:
        filename: Nom du fichier audio
        
    Returns:
        Fichier audio MP3
    """
    file_path = os.path.join(Config.AUDIO_OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier audio non trouvé")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )

@app.post("/batch-analyze")
async def batch_analyze(sensor_data_list: List[SensorData]):
    """
    Analyse plusieurs ensembles de données en batch
    
    Args:
        sensor_data_list: Liste de données capteurs
        
    Returns:
        Liste des analyses
    """
    try:
        results = []
        
        for sensor_data in sensor_data_list:
            data_dict = sensor_data.dict(exclude_none=True)
            result = model.analyze_environment(data_dict)
            result["success"] = True
            results.append(result)
        
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse batch : {str(e)}"
        )

# Import pandas pour timestamp (si nécessaire)
import pandas as pd

# Lancer l'API
if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("Démarrage de RespirIA API")
    print("="*60)
    print(f"URL locale : http://localhost:8000")
    print(f"Documentation : http://localhost:8000/docs")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)