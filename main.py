import requests
import pandas as pd
import json
from config import Config
from gtts import gTTS
import os

class RespirIAModel:
    """
    Modèle IA pour la prédiction des risques respiratoires
    Utilise Gemini 2.5 Pro via OpenRouter pour l'analyse contextuelle et prédictive
    """
    
    def __init__(self):
        # Configuration d'OpenRouter
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.GEMINI_MODEL
        self.training_context = ""
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY non configurée dans .env")
        
    def load_training_data(self):
        """
        Charge et prépare les données d'entraînement
        Ces données serviront de contexte pour Gemini
        """
        try:
            df = pd.read_csv(Config.TRAINING_DATA_PATH)
            print(f"✓ Données chargées : {len(df)} enregistrements")
            
            # Créer un contexte d'apprentissage pour Gemini
            self.training_context = self._create_context_from_data(df)
            return df
        except Exception as e:
            print(f"✗ Erreur lors du chargement des données : {e}")
            return None
    
    def _create_context_from_data(self, df):
        """
        Transforme les données CSV en contexte textuel pour Gemini
        """
        context = """
                Tu es RespirIA, un assistant médical spécialisé dans la prédiction des risques respiratoires.
                CONNAISSANCES MÉDICALES (basées sur les données d'entraînement) :
        """
        # Analyser les patterns dans les données
        if 'maladie' in df.columns and 'conditions' in df.columns:
            diseases = df['maladie'].unique()
            for disease in diseases:
                disease_data = df[df['maladie'] == disease]
                context += f"\n{disease.upper()} :\n"
                context += f"- Cas observés : {len(disease_data)}\n"
                
        # Ajouter des statistiques générales
        context += f"\n\nTOTAL DES CAS ANALYSÉS : {len(df)}\n"
        
        return context
    
    def analyze_environment(self, sensor_data):
        """
        Analyse les données des capteurs et prédit les risques
        
        Args:
            sensor_data (dict): Données JSON des capteurs
            
        Returns:
            dict: Analyse complète avec risques et recommandations
        """
        # Créer le prompt pour Gemini
        prompt = f"""
{self.training_context}

MISSION :
Analyse les données environnementales suivantes et prédit les risques pour les maladies respiratoires.

DONNÉES DES CAPTEURS :
{json.dumps(sensor_data, indent=2, ensure_ascii=False)}

ANALYSE REQUISE :
1. Niveau de risque global (FAIBLE / MODÉRÉ / ÉLEVÉ / CRITIQUE)
2. Maladies potentiellement concernées (asthme, bronchite, rhinite allergique, etc.)
3. Facteurs environnementaux problématiques
4. Recommandations personnalisées et concrètes
5. Prévisions pour les prochaines heures

FORMAT DE RÉPONSE (JSON) :
{{
    "niveau_risque": "MODÉRÉ",
    "score_risque": 65,
    "maladies_concernees": ["asthme", "rhinite"],
    "facteurs_risque": [
        {{"facteur": "CO2 élevé", "valeur": "1200 ppm", "impact": "élevé"}},
        {{"facteur": "Humidité faible", "valeur": "30%", "impact": "modéré"}}
    ],
    "recommandations": [
        "Évitez les activités physiques intenses",
        "Aérez votre intérieur tôt le matin",
        "Gardez votre inhalateur à portée de main"
    ],
    "message_vocal": "Attention, risque respiratoire modéré détecté. Le taux de CO2 est élevé et l'air est sec. Je vous conseille d'éviter les activités physiques intenses et de bien aérer votre logement.",
    "previsions": "Le risque devrait diminuer en soirée avec la baisse des températures."
}}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
"""
        
        try:
            # Appel à OpenRouter via l'API compatible OpenAI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://respiria.app",
                "X-Title": "RespirIA"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Tu es RespirIA, un assistant médical spécialisé dans la prédiction des risques respiratoires."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": Config.TEMPERATURE,
                "max_tokens": Config.MAX_OUTPUT_TOKENS
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"✗ Erreur OpenRouter : {response.status_code} - {response.text}")
                return self._get_fallback_response()
            
            # Parser la réponse JSON de OpenRouter
            response_data = response.json()
            result_text = response_data['choices'][0]['message']['content']
            
            # Parser la réponse JSON
            result = self._parse_gemini_response(result_text)
            
            return result
            
        except Exception as e:
            print(f"✗ Erreur lors de l'analyse : {e}")
            return self._get_fallback_response()
    
    def _parse_gemini_response(self, response_text):
        """
        Parse la réponse de Gemini et extrait le JSON
        """
        try:
            # Nettoyer la réponse (enlever les balises markdown si présentes)
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            result = json.loads(cleaned.strip())
            return result
        except:
            # Si le parsing échoue, retourner le texte brut
            return {
                "niveau_risque": "INDÉTERMINÉ",
                "message_vocal": response_text,
                "recommandations": ["Consultez les données manuellement"]
            }
    
    def _get_fallback_response(self):
        """
        Réponse de secours en cas d'erreur
        """
        return {
            "niveau_risque": "ERREUR",
            "score_risque": 0,
            "message_vocal": "Impossible d'analyser les données pour le moment. Veuillez réessayer.",
            "recommandations": ["Vérifiez votre connexion", "Contactez le support technique"]
        }
    
    def generate_audio(self, text, filename="alerte.mp3"):
        """
        Génère un fichier audio à partir du texte
        
        Args:
            text (str): Texte à convertir en audio
            filename (str): Nom du fichier de sortie
            
        Returns:
            str: Chemin du fichier audio généré
        """
        try:
            # Créer le dossier de sortie si nécessaire
            os.makedirs(Config.AUDIO_OUTPUT_DIR, exist_ok=True)
            
            # Générer l'audio
            tts = gTTS(text=text, lang=Config.AUDIO_LANGUAGE, slow=False)
            output_path = os.path.join(Config.AUDIO_OUTPUT_DIR, filename)
            tts.save(output_path)
            
            print(f"✓ Audio généré : {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Erreur lors de la génération audio : {e}")
            return None


# Fonction principale pour tester le modèle
def main():
    print("=== RespirIA - Système de Prédiction des Risques Respiratoires ===\n")
    
    # Initialiser le modèle
    model = RespirIAModel()
    
    # Charger les données d'entraînement
    print("1. Chargement des données d'entraînement...")
    model.load_training_data()
    
    # Charger un exemple de données capteurs
    print("\n2. Chargement des données capteurs...")
    with open(Config.SAMPLE_INPUT_PATH, 'r', encoding='utf-8') as f:
        sensor_data = json.load(f)
    print(f"✓ Données capteurs chargées : {json.dumps(sensor_data, indent=2, ensure_ascii=False)}")
    
    # Analyser l'environnement
    print("\n3. Analyse en cours avec Gemini...")
    result = model.analyze_environment(sensor_data)
    
    # Afficher les résultats
    print("\n" + "="*60)
    print("RÉSULTATS DE L'ANALYSE")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Générer l'audio
    if "message_vocal" in result:
        print("\n4. Génération du message audio...")
        audio_path = model.generate_audio(result["message_vocal"])
        if audio_path:
            print(f"✓ Vous pouvez écouter l'alerte : {audio_path}")
    
    print("\n✓ Analyse terminée avec succès !")


if __name__ == "__main__":
    main()