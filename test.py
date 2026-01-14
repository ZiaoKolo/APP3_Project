import requests
import json
from pprint import pprint

# Configuration
API_URL = "http://localhost:8000"

def test_health():
    """Test de l'état de santé de l'API"""
    print("\n" + "="*60)
    print("TEST 1 : Vérification de l'état de l'API")
    print("="*60)
    
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    pprint(response.json())
    
    assert response.status_code == 200, "L'API n'est pas accessible"
    print("✓ Test réussi")

def test_analyze_basic():
    """Test d'analyse basique"""
    print("\n" + "="*60)
    print("TEST 2 : Analyse de données capteurs basiques")
    print("="*60)
    
    # Données de test - Conditions normales
    sensor_data = {
        "temperature": 22.0,
        "humidity": 50.0,
        "co2": 700.0,
        "pm25": 10.0,
        "pollen": "faible",
        "location": "Abidjan",
        "user_id": "test_user_1"
    }
    
    print("Données envoyées :")
    pprint(sensor_data)
    
    response = requests.post(
        f"{API_URL}/analyze",
        json=sensor_data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print("\nRéponse reçue :")
    result = response.json()
    pprint(result)
    
    assert response.status_code == 200, "Erreur lors de l'analyse"
    assert result["success"] == True, "L'analyse a échoué"
    assert "niveau_risque" in result, "Niveau de risque manquant"
    
    print(f"\n✓ Test réussi - Niveau de risque : {result['niveau_risque']}")

def test_analyze_high_risk():
    """Test avec des conditions à haut risque"""
    print("\n" + "="*60)
    print("TEST 3 : Analyse avec conditions à HAUT RISQUE")
    print("="*60)
    
    # Données de test - Conditions dangereuses
    sensor_data = {
        "temperature": 35.0,
        "humidity": 25.0,
        "co2": 1500.0,
        "pm25": 75.0,
        "pollen": "très élevé",
        "location": "Abidjan",
        "user_id": "test_user_2"
    }
    
    print("Données envoyées (conditions dangereuses) :")
    pprint(sensor_data)
    
    response = requests.post(
        f"{API_URL}/analyze",
        json=sensor_data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print("\nRéponse reçue :")
    result = response.json()
    pprint(result)
    
    assert response.status_code == 200, "Erreur lors de l'analyse"
    assert result["success"] == True, "L'analyse a échoué"
    
    print(f"\n✓ Test réussi - Niveau de risque : {result['niveau_risque']}")
    print(f"Message vocal : {result.get('message_vocal', 'N/A')}")

def test_analyze_with_audio():
    """Test de génération d'audio"""
    print("\n" + "="*60)
    print("TEST 4 : Analyse avec génération d'audio")
    print("="*60)
    
    sensor_data = {
        "temperature": 30.0,
        "humidity": 35.0,
        "co2": 1200.0,
        "pm25": 45.0,
        "pollen": "élevé",
        "location": "Abidjan",
        "user_id": "test_user_audio"
    }
    
    print("Données envoyées :")
    pprint(sensor_data)
    
    response = requests.post(
        f"{API_URL}/analyze-with-audio",
        json=sensor_data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print("\nRéponse reçue :")
    result = response.json()
    pprint(result)
    
    assert response.status_code == 200, "Erreur lors de l'analyse avec audio"
    assert "audio_url" in result, "URL audio manquante"
    
    print(f"\n✓ Test réussi")
    print(f"Audio disponible à : {API_URL}{result['audio_url']}")

def test_batch_analyze():
    """Test d'analyse en batch"""
    print("\n" + "="*60)
    print("TEST 5 : Analyse en batch (plusieurs ensembles de données)")
    print("="*60)
    
    # Plusieurs ensembles de données
    batch_data = [
        {
            "temperature": 22.0,
            "humidity": 50.0,
            "co2": 700.0,
            "pm25": 10.0,
            "user_id": "batch_1"
        },
        {
            "temperature": 32.0,
            "humidity": 30.0,
            "co2": 1300.0,
            "pm25": 60.0,
            "user_id": "batch_2"
        },
        {
            "temperature": 18.0,
            "humidity": 65.0,
            "co2": 600.0,
            "pm25": 8.0,
            "user_id": "batch_3"
        }
    ]
    
    print(f"Envoi de {len(batch_data)} ensembles de données")
    
    response = requests.post(
        f"{API_URL}/batch-analyze",
        json=batch_data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    result = response.json()
    
    print(f"\nNombre de résultats : {result['total']}")
    for i, analysis in enumerate(result['results']):
        print(f"\nRésultat {i+1} - Niveau de risque : {analysis['niveau_risque']}")
    
    assert response.status_code == 200, "Erreur lors de l'analyse batch"
    assert result['total'] == len(batch_data), "Nombre de résultats incorrect"
    
    print("\n✓ Test réussi")

def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print("🧪 DÉMARRAGE DE LA SUITE DE TESTS")
    print("="*60)
    
    try:
        test_health()
        test_analyze_basic()
        test_analyze_high_risk()
        test_analyze_with_audio()
        test_batch_analyze()
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DU TEST : {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR : Impossible de se connecter à l'API")
        print("Assurez-vous que l'API est lancée avec : python api.py")
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE : {e}")

if __name__ == "__main__":
    run_all_tests()