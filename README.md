RespirIA - Système Intelligent de Prédiction des Risques Respiratoires

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

##  Description

RespirIA est un système intelligent basé sur l'IA (Google Gemini) qui analyse en temps réel les données environnementales pour prédire les risques de maladies respiratoires (asthme, bronchite, rhinite allergique, etc.).

Le système utilise des capteurs IoT pour collecter des données (température, humidité, CO₂, particules fines, pollen) et génère des alertes personnalisées avec recommandations vocales.

##  Fonctionnalités

- ✅ **Analyse prédictive** avec IA Gemini
- ✅ **Prédiction en temps réel** des risques respiratoires
- ✅ **Recommandations personnalisées** basées sur les conditions environnementales
- ✅ **Alertes vocales** (Text-to-Speech en français)
- ✅ **API REST** pour intégration facile
- ✅ **Support multi-utilisateurs**
- ✅ **Analyse en batch** pour traitement de masse

##  Architecture

```
┌─────────────────┐
│ Capteurs IoT    │
│ (Temp, CO₂...)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API REST       │
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gemini AI      │
│  (Analyse)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Application    │
│  Mobile/Web     │
└─────────────────┘
```

##  Installation Rapide

### 1. Cloner le projet
```bash
git clone https://github.com/votre-repo/respiria.git
cd respiria/IA_ENGINE
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer l'API Gemini
```bash
# Copier le template de configuration
cp .env.example .env

# Éditer .env et ajouter votre clé API Gemini
# GEMINI_API_KEY=votre_cle_ici
```

### (Alternative) Créer ou modifier le fichier `.env`
Si vous n'avez pas de `.env.example`, créez un fichier `.env` à la racine du projet et ajoutez votre clé :

```bash
# Fichier .env
GEMINI_API_KEY=VOTRE_CLE_GEMINI_ICI
GEMINI_MODEL=gemini-2.5-pro
API_PORT=8000
AUDIO_LANGUAGE=fr
```

Remplacez `VOTRE_CLE_GEMINI_ICI` par votre clé réelle. Le projet utilise `python-dotenv` et `config.py` charge automatiquement ce fichier.

### 5. Lancer l'API
```bash
python api.py
```

✅ L'API est accessible sur : **http://localhost:8000**  
 Documentation interactive : **http://localhost:8000/docs**

## 📁 Structure du Projet

```
IA_ENGINE/
├── data/
│   ├── training_data.csv      # Données d'entraînement
│   └── sample_input.json      # Exemple de données capteurs
├── output_audio/              # Fichiers audio générés
├── venv/                      # Environnement virtuel
├── api.py                     # API REST FastAPI
├── config.py                  # Configuration
├── main.py                    # Script principal
├── test.py                    # Tests automatiques
├── requirements.txt           # Dépendances Python
├── .env.example              # Template de configuration
└── README.md                 # Ce fichier
```

## 🔧 Configuration

### Variables d'environnement (.env)

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `GEMINI_API_KEY` | Clé API Google Gemini | (obligatoire) |
| `GEMINI_MODEL` | Modèle à utiliser | `gemini-1.5-flash` |
| `API_PORT` | Port du serveur API | `8000` |
| `AUDIO_LANGUAGE` | Langue audio | `fr` |
| `TEMPERATURE` | Créativité du modèle | `0.7` |

##  Format des Données

### Données d'entrée (JSON)

```json
{
  "temperature": 32.0,
  "humidity": 35.0,
  "co2": 1200.0,
  "pm25": 45.0,
  "pollen": "élevé",
  "location": "Abidjan",
  "user_id": "user123"
}
```

### Réponse de l'API

```json
{
  "success": true,
  "niveau_risque": "ÉLEVÉ",
  "score_risque": 75,
  "maladies_concernees": ["asthme", "rhinite allergique"],
  "facteurs_risque": [
    {
      "facteur": "CO2 élevé",
      "valeur": "1200 ppm",
      "impact": "élevé"
    }
  ],
  "recommandations": [
    "Évitez les activités extérieures",
    "Portez un masque filtrant"
  ],
  "message_vocal": "Attention, risque respiratoire élevé détecté...",
  "audio_url": "/audio/alerte_user123_20251021.mp3"
}
```

## 🔌 Utilisation de l'API

### Analyse simple

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 32.0,
    "humidity": 35.0,
    "co2": 1200.0,
    "pm25": 45.0,
    "pollen": "élevé"
  }'
```

### Analyse avec audio

```bash
curl -X POST "http://localhost:8000/analyze-with-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 32.0,
    "humidity": 35.0,
    "co2": 1200.0,
    "user_id": "user123"
  }'
```

### Exemple Python

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "temperature": 32.0,
        "humidity": 35.0,
        "co2": 1200.0,
        "pm25": 45.0
    }
)

result = response.json()
print(f"Risque: {result['niveau_risque']}")
print(f"Recommandations: {result['recommandations']}")
```

##  Tests

```bash
# Lancer tous les tests
python test.py

# Tester le modèle seul
python main.py
```

##  Intégration avec Applications

### Flutter
```dart
Future<Map<String, dynamic>> analyzeAir(Map data) async {
  final response = await http.post(
    Uri.parse('http://votre-api.com/analyze'),
    body: json.encode(data),
  );
  return json.decode(response.body);
}
```

### React/JavaScript
```javascript
const analyzeAir = async (data) => {
  const response = await fetch('http://votre-api.com/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  return await response.json();
};
```

##  Déploiement

### Google Cloud Run
```bash
gcloud run deploy respiria-api \
  --source . \
  --platform managed \
  --region europe-west1
```

### Docker
```bash
docker build -t respiria-api .
docker run -p 8000:8000 respiria-api
```

## Amélioration Continue

Le modèle s'améliore avec les données :
1. Collecter plus de données réelles
2. Ajouter des feedbacks utilisateurs
3. Réentraîner régulièrement le contexte
4. Ajuster les seuils d'alerte

##  Contribution

Les contributions sont les bienvenues ! Pour contribuer :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Équipe

Projet E-Santé 4.0 - Prévention des maladies respiratoires  
Développé avec ❤️ en Côte d'Ivoire


**Note** : Ce projet utilise Google Gemini pour l'analyse prédictive. Une clé API valide est requise pour utiliser le système.