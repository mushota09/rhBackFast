"""
Test pour la création complète d'employé avec fichiers
"""
import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_create_complete_employee_with_files(client: AsyncClient, auth_headers):
    """Test de création d'un employé complet avec fichiers"""
    
    # Préparer les données
    employee_data = {
        "prenom": "Jean",
        "nom": "Dupont",
        "email_personnel": "jean.dupont@test.com",
        "telephone_personnel": "+243123456789",
        "date_naissance": "1990-01-01",
        "sexe": "M",
        "statut_matrimonial": "S",
        "nationalite": "Congolaise",
        "niveau_etude": "Licence",
        "adresse_ligne1": "123 Rue Test",
        "date_embauche": "2024-01-01",
        "statut_emploi": "ACTIVE",
        "nombre_enfants": 0,
        "nom_contact_urgence": "Marie Dupont",
        "lien_contact_urgence": "Épouse",
        "telephone_contact_urgence": "+243987654321"
    }
    
    contract_data = {
        "type_contrat": "CDI",
        "date_debut": "2024-01-01",
        "type_salaire": "M",
        "salaire_base": 50000,
        "devise": "USD",
        "indemnite_logement": 10,
        "indemnite_deplacement": 5,
        "prime_fonction": 5,
        "autre_avantage": 0,
        "assurance_patronale": 3.5,
        "assurance_salariale": 1.5,
        "fpc_patronale": 1,
        "fpc_salariale": 0.5
    }

    
    documents_metadata = [
        {
            "type_document": "CONTRACT",
            "titre": "Contrat de travail",
            "description": "Contrat CDI signé"
        },
        {
            "type_document": "ID",
            "titre": "Carte d'identité",
            "expiry_date": "2030-12-31"
        }
    ]
    
    # Créer des fichiers de test
    contract_file = BytesIO(b"Contenu du contrat PDF")
    contract_file.name = "contrat.pdf"
    
    id_card_file = BytesIO(b"Image de la carte d'identité")
    id_card_file.name = "carte_identite.jpg"
    
    # Préparer le FormData
    import json
    files = {
        "employee": (None, json.dumps(employee_data)),
        "contract": (None, json.dumps(contract_data)),
        "documents_metadata": (None, json.dumps(documents_metadata)),
        "files": [
            ("files", ("contrat.pdf", contract_file, "application/pdf")),
            ("files", ("carte_identite.jpg", id_card_file, "image/jpeg"))
        ]
    }
    
    # Envoyer la requête
    response = await client.post(
        "/api/employees/create-complete",
        files=files,
        headers=auth_headers
    )
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "employee_id" in data["data"]
    assert "contract_id" in data["data"]
    assert "user_id" in data["data"]
    assert data["data"]["documents_count"] == 2


@pytest.mark.asyncio
async def test_create_complete_employee_without_files(client: AsyncClient, auth_headers):
    """Test de création d'un employé complet sans fichiers"""
    
    employee_data = {
        "prenom": "Marie",
        "nom": "Martin",
        "email_personnel": "marie.martin@test.com",
        "telephone_personnel": "+243123456790",
        "date_naissance": "1992-05-15",
        "sexe": "F",
        "statut_matrimonial": "M",
        "nationalite": "Congolaise",
        "niveau_etude": "Master",
        "adresse_ligne1": "456 Avenue Test",
        "date_embauche": "2024-02-01",
        "statut_emploi": "ACTIVE",
        "nombre_enfants": 2,
        "nom_contact_urgence": "Pierre Martin",
        "lien_contact_urgence": "Époux",
        "telephone_contact_urgence": "+243987654322"
    }
    
    contract_data = {
        "type_contrat": "CDI",
        "date_debut": "2024-02-01",
        "type_salaire": "M",
        "salaire_base": 60000,
        "devise": "USD",
        "indemnite_logement": 15,
        "indemnite_deplacement": 10,
        "prime_fonction": 10,
        "autre_avantage": 5000,
        "assurance_patronale": 3.5,
        "assurance_salariale": 1.5,
        "fpc_patronale": 1,
        "fpc_salariale": 0.5
    }
    
    # Pas de documents
    documents_metadata = []
    
    import json
    files = {
        "employee": (None, json.dumps(employee_data)),
        "contract": (None, json.dumps(contract_data)),
        "documents_metadata": (None, json.dumps(documents_metadata))
    }
    
    response = await client.post(
        "/api/employees/create-complete",
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["documents_count"] == 0
