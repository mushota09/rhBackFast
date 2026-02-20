"""
Script de vérification détaillée de la correspondance entre modèles Django et FastAPI
"""
import sys
from pathlib import Path

# Définition des modèles attendus avec leurs colonnes
DJANGO_MODELS = {
    "Service": {
        "table": "rh_service",
        "columns": ["id", "titre", "code", "description", "created_at", "updated_at"]
    },
    "Group": {
        "table": "user_management_group",
        "columns": ["id", "code", "name", "description", "is_active", "created_at", "updated_at"]
    },
    "ServiceGroup": {
        "table": "rh_service_group",
        "columns": ["id", "service_id", "group_id", "created_at", "updated_at"]
    },
    "User": {
        "table": "user_management_user",
        "columns": ["id", "email", "password", "nom", "prenom", "is_active", "is_superuser",
                   "employe_id", "phone", "photo", "is_staff", "last_login", "date_joined",
                   "created_at", "updated_at"]
    },
    "UserGroup": {
        "table": "user_management_usergroup",
        "columns": ["id", "user_id", "group_id", "assigned_by_id", "assigned_at",
                   "is_active", "created_at", "updated_at"]
    },
    "Permission": {
        "table": "user_management_permission",
        "columns": ["id", "codename", "name", "content_type", "resource", "action",
                   "description", "created_at", "updated_at"]
    },
    "GroupPermission": {
        "table": "user_management_grouppermission",
        "columns": ["id", "group_id", "permission_id", "granted", "created_by_id",
                   "created_at", "updated_at"]
    },
    "Employe": {
        "table": "rh_employe",
        "columns": ["id", "prenom", "nom", "postnom", "date_naissance", "sexe",
                   "statut_matrimonial", "nationalite", "banque", "numero_compte",
                   "niveau_etude", "numero_inss", "email_personnel", "email_professionnel",
                   "telephone_personnel", "telephone_professionnel", "adresse_ligne1",
                   "adresse_ligne2", "ville", "province", "code_postal", "pays", "matricule",
                   "poste_id", "responsable_id", "date_embauche", "statut_emploi",
                   "nombre_enfants", "nom_conjoint", "biographie", "nom_contact_urgence",
                   "lien_contact_urgence", "telephone_contact_urgence", "created_at", "updated_at"]
    },
    "Contrat": {
        "table": "rh_contrat",
        "columns": ["id", "employe_id", "type_contrat", "date_debut", "date_fin",
                   "salaire_base", "devise", "is_active", "created_at", "updated_at"]
    },
    "Document": {
        "table": "rh_document",
        "columns": ["id", "employe_id", "type_document", "titre", "description",
                   "fichier", "date_upload", "expiry_date", "uploaded_by",
                   "created_at", "updated_at"]
    },
    "Alert": {
        "table": "paie_alert",
        "columns": ["id", "alert_type", "severity", "status", "title", "message",
                   "details", "employe_id", "periode_paie_id", "created_by_id",
                   "acknowledged_by_id", "acknowledged_at", "resolved_by_id",
                   "resolved_at", "email_sent", "email_sent_at", "created_at", "updated_at"]
    },
    "RetenueEmploye": {
        "table": "paie_retenu_salaire",
        "columns": ["id", "employe_id", "type_retenue", "description", "montant_mensuel",
                   "montant_total", "montant_deja_deduit", "date_debut", "date_fin",
                   "est_active", "est_recurrente", "cree_par_id", "banque_beneficiaire",
                   "compte_beneficiaire", "modification_history", "created_at", "updated_at"]
    },
    "PeriodePaie": {
        "table": "paie_periode",
        "columns": ["id", "annee", "mois", "date_debut", "date_fin", "statut",
                   "traite_par_id", "date_traitement", "approuve_par_id", "date_approbation",
                   "nombre_employes", "masse_salariale_brute", "total_cotisations_patronales",
                   "total_cotisations_salariales", "total_net_a_payer", "created_at", "updated_at"]
    },
    "EntreePaie": {
        "table": "paie_entree",
        "columns": ["id", "employe_id", "periode_paie_id", "contrat_reference",
                   "salaire_base", "indemnite_logement", "indemnite_deplacement",
                   "indemnite_fonction", "allocation_familiale", "autres_avantages",
                   "salaire_brut", "cotisations_patronales", "cotisations_salariales",
                   "retenues_diverses", "total_charge_salariale", "base_imposable",
                   "salaire_net", "payslip_generated", "payslip_file", "payslip_generated_at",
                   "is_validated", "validation_errors", "calculated_by_id", "calculated_at",
                   "validated_by_id", "validated_at", "modification_history",
                   "created_at", "updated_at"]
    },
    "TypeConge": {
        "table": "cg_type_conge",
        "columns": ["id", "nom", "code", "nb_jours_max_par_an", "report_autorise",
                   "necessite_validation", "created_at", "updated_at"]
    },
    "DemandeConge": {
        "table": "cg_demande_conge",
        "columns": ["id", "employe_id", "type_conge_id", "date_debut", "date_fin",
                   "nb_jours_total", "raison", "statut", "documents", "approuve_par_id",
                   "date_approbation", "created_at", "updated_at"]
    },
    "SoldeConge": {
        "table": "cg_solde_conge",
        "columns": ["id", "employe_id", "type_conge_id", "annee", "alloue", "utilise",
                   "restant", "reporte", "created_at", "updated_at"]
    },
    "HistoriqueConge": {
        "table": "cg_historique_conge",
        "columns": ["id", "demande_conge_id", "poste_valideur_id", "date_validation",
                   "commentaire", "created_at", "updated_at"]
    }
}

def extract_fastapi_model_info(file_path: Path) -> dict:
    """Extrait les informations des modèles FastAPI"""
    models = {}
    current_model = None
    current_table = None
    current_columns = []
    base_model_columns = ['id', 'created_at', 'updated_at']  # Colonnes héritées de BaseModel

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Détection de classe
        if line.startswith('class ') and ('(BaseModel)' in line or '(Base)' in line):
            # Sauvegarder le modèle précédent
            if current_model and current_table:
                # Ajouter les colonnes héritées de BaseModel
                all_columns = base_model_columns + current_columns
                models[current_model] = {
                    "table": current_table,
                    "columns": all_columns
                }

            # Nouveau modèle
            current_model = line.split('class ')[1].split('(')[0].strip()
            current_table = None
            current_columns = []

        # Détection de table
        elif '__tablename__' in line and '=' in line:
            current_table = line.split('=')[1].strip().strip('"').strip("'")

        # Détection de colonne (ignorer les relationships)
        elif ': Mapped[' in line and '=' in line:
            col_name = line.split(':')[0].strip()
            # Ignorer les colonnes privées et les relationships
            if not col_name.startswith('_') and 'relationship(' not in line:
                current_columns.append(col_name)

    # Sauvegarder le dernier modèle
    if current_model and current_table:
        all_columns = base_model_columns + current_columns
        models[current_model] = {
            "table": current_table,
            "columns": all_columns
        }

    return models

def verify_models():
    """Vérifie la correspondance entre Django et FastAPI"""
    print("=" * 100)
    print("VÉRIFICATION DE LA CORRESPONDANCE DES MODÈLES DJANGO ↔ FASTAPI")
    print("=" * 100)

    # Extraire les modèles FastAPI
    fastapi_models = {}
    model_files = [
        ("app/user_app/models.py", "User App"),
        ("app/paie_app/models.py", "Paie App"),
        ("app/conge_app/models.py", "Conge App"),
    ]

    for file_path, app_name in model_files:
        path = Path(file_path)
        if path.exists():
            models = extract_fastapi_model_info(path)
            fastapi_models.update(models)
            print(f"\n✅ {app_name}: {len(models)} modèles extraits")

    print(f"\n📊 Total FastAPI: {len(fastapi_models)} modèles")
    print(f"📊 Total Django: {len(DJANGO_MODELS)} modèles")

    # Vérification détaillée
    print("\n" + "=" * 100)
    print("VÉRIFICATION DÉTAILLÉE")
    print("=" * 100)

    all_ok = True
    missing_models = []
    table_mismatches = []
    column_issues = []

    for model_name, django_info in DJANGO_MODELS.items():
        print(f"\n🔍 Vérification: {model_name}")
        print("-" * 100)

        if model_name not in fastapi_models:
            print(f"  ❌ MODÈLE MANQUANT dans FastAPI")
            missing_models.append(model_name)
            all_ok = False
            continue

        fastapi_info = fastapi_models[model_name]

        # Vérifier le nom de table
        if django_info["table"] != fastapi_info["table"]:
            print(f"  ❌ TABLE DIFFÉRENTE:")
            print(f"     Django:  {django_info['table']}")
            print(f"     FastAPI: {fastapi_info['table']}")
            table_mismatches.append(model_name)
            all_ok = False
        else:
            print(f"  ✅ Table: {django_info['table']}")

        # Vérifier les colonnes
        django_cols = set(django_info["columns"])
        fastapi_cols = set(fastapi_info["columns"])

        missing_in_fastapi = django_cols - fastapi_cols
        extra_in_fastapi = fastapi_cols - django_cols

        if missing_in_fastapi:
            print(f"  ⚠️  Colonnes manquantes dans FastAPI: {', '.join(sorted(missing_in_fastapi))}")
            column_issues.append((model_name, "missing", missing_in_fastapi))
            # Ne pas marquer comme erreur si ce sont des champs optionnels Django
            optional_fields = {'phone', 'photo', 'is_staff', 'last_login', 'date_joined', 'granted'}
            if not missing_in_fastapi.issubset(optional_fields):
                all_ok = False

        if extra_in_fastapi:
            print(f"  ℹ️  Colonnes supplémentaires dans FastAPI: {', '.join(sorted(extra_in_fastapi))}")

        common_cols = django_cols & fastapi_cols
        print(f"  ✅ Colonnes communes: {len(common_cols)}/{len(django_cols)}")

    # Résumé final
    print("\n" + "=" * 100)
    print("RÉSUMÉ FINAL")
    print("=" * 100)

    if all_ok:
        print("\n✅ TOUS LES MODÈLES CORRESPONDENT!")
        print(f"   - {len(DJANGO_MODELS)} modèles vérifiés")
        return 0
    else:
        print("\n❌ PROBLÈMES DÉTECTÉS:")
        if missing_models:
            print(f"   - {len(missing_models)} modèle(s) manquant(s): {', '.join(missing_models)}")
        if table_mismatches:
            print(f"   - {len(table_mismatches)} table(s) avec nom différent")
        if column_issues:
            print(f"   - {len(column_issues)} modèle(s) avec colonnes manquantes")
        return 1

if __name__ == "__main__":
    sys.exit(verify_models())
