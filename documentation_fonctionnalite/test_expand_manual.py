"""
Script de test manuel pour valider les expansions

Usage:
    python test_expand_manual.py

Prérequis:
    - Le serveur doit être lancé sur http://localhost:8000
    - Un utilisateur doit exister avec email: mushota09@gmail.com
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
EMAIL = "mushota09@gmail.com"
PASSWORD = "rapha12345678"


def login() -> str:
    """Authentification et récupération du token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access"]
        print("✅ Authentification réussie")
        return token
    else:
        print(f"❌ Échec de l'authentification: {response.status_code}")
        print(response.text)
        exit(1)


def test_expand(token: str, endpoint: str, expand: str, description: str):
    """Teste une expansion spécifique"""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"Expand: {expand}")
    print(f"{'='*60}")

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}?expand={expand}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Afficher le premier résultat
            if "results" in data and len(data["results"]) > 0:
                first_result = data["results"][0]
                print(f"✅ Succès - {data['total']} résultat(s)")
                print(f"\nPremier résultat (structure):")
                print(json.dumps(first_result, indent=2, default=str)[:500] + "...")
            else:
                print(f"✅ Succès mais aucun résultat")
        else:
            print(f"❌ Erreur {response.status_code}")
            print(response.text[:200])

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def main():
    """Exécute tous les tests"""
    print("🚀 Démarrage des tests d'expansion")
    print(f"URL de base: {BASE_URL}")

    # Authentification
    token = login()

    # Tests d'expansion
    tests = [
        # Expansions simples
        {
            "endpoint": "/api/employees/",
            "expand": "poste",
            "description": "Expansion simple - poste"
        },
        {
            "endpoint": "/api/user-groups/",
            "expand": "user",
            "description": "Expansion simple - user"
        },

        # Expansions multiples
        {
            "endpoint": "/api/employees/",
            "expand": "poste,user_account",
            "description": "Expansion multiple - poste et user_account"
        },
        {
            "endpoint": "/api/user-groups/",
            "expand": "user,group",
            "description": "Expansion multiple - user et group"
        },

        # Expansions imbriquées simples
        {
            "endpoint": "/api/user-groups/",
            "expand": "user.employe",
            "description": "Expansion imbriquée - user.employe"
        },
        {
            "endpoint": "/api/employees/",
            "expand": "poste.service",
            "description": "Expansion imbriquée - poste.service"
        },

        # Expansions imbriquées multiples (le cas qui causait l'erreur)
        {
            "endpoint": "/api/employees/",
            "expand": "poste.service,poste.group",
            "description": "Expansion imbriquée multiple - poste.service et poste.group"
        },

        # Expansions profondes
        {
            "endpoint": "/api/user-groups/",
            "expand": "user.employe.poste",
            "description": "Expansion profonde (3 niveaux) - user.employe.poste"
        },

        # Expansions mixtes
        {
            "endpoint": "/api/employees/",
            "expand": "responsable,poste.service",
            "description": "Expansion mixte - simple et imbriquée"
        },
    ]

    # Exécuter tous les tests
    for test in tests:
        test_expand(
            token=token,
            endpoint=test["endpoint"],
            expand=test["expand"],
            description=test["description"]
        )

    print(f"\n{'='*60}")
    print("✅ Tous les tests sont terminés")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
