# Résumé Complet des Permissions - RH Management System

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Liste complète des permissions](#liste-complète-des-permissions)
3. [Configuration du startup.py](#configuration-du-startuppy)
4. [Variables d'environnement](#variables-denvironnement)
5. [Messages de log au démarrage](#messages-de-log-au-démarrage)
6. [Instructions de vérification](#instructions-de-vérification)

---

## Vue d'ensemble

Le système RH Management utilise un système de permissions granulaire basé sur des ressources et des actions. Au total, **20 permissions** sont définies et créées automatiquement au démarrage de l'application.

### Architecture des permissions

- **Format**: `resource.action` (ex: `conge.view`, `alert.create`)
- **Stockage**: Table `Permission` dans la base de données
- **Attribution**: Via des groupes (`Group` → `GroupPermission` → `UserGroup`)
- **Vérification**: Fonction `require_permission(resource, action)` dans les routes

---

## Liste complète des permissions

### 📊 Total: 20 permissions

#### 1. Module CONGE (8 permissions)

Gestion des congés et absences.

| Codename | Description | Usage |
|----------|-------------|-------|
| `conge.view` | Consulter les congés | Voir les demandes de congés |
| `conge.create` | Créer des demandes de congés | Soumettre une nouvelle demande |
| `conge.update` | Modifier des demandes de congés | Éditer une demande existante |
| `conge.delete` | Supprimer des demandes de congés | Annuler/supprimer une demande |
| `conge.approve` | Approuver des demandes de congés | Valider ou rejeter une demande |
| `conge.manage_types` | Gérer les types de congés | Créer/modifier les types de congés |
| `conge.manage_soldes` | Gérer les soldes de congés | Ajuster les soldes des employés |
| `conge.export` | Exporter les données de congés | Générer des rapports Excel/PDF |

**Fichier source**: `app/conge_app/constants.py`

#### 2. Module PAIE (11 permissions)

Gestion de la paie et des salaires.

| Codename | Description | Usage |
|----------|-------------|-------|
| `alert.view` | Consulter les alertes | Voir les alertes de paie |
| `alert.create` | Créer des alertes | Créer de nouvelles alertes |
| `alert.update` | Modifier des alertes | Mettre à jour les alertes |
| `retenue.view` | Consulter les retenues | Voir les retenues salariales |
| `retenue.create` | Créer des retenues | Ajouter des retenues |
| `periode.view` | Consulter les périodes de paie | Voir les périodes |
| `periode.create` | Créer des périodes de paie | Créer une nouvelle période |
| `periode.update` | Modifier des périodes de paie | Traiter/finaliser/approuver |
| `entree.view` | Consulter les entrées de paie | Voir les fiches de paie |
| `entree.update` | Modifier les entrées de paie | Calculer les salaires |
| `payroll.view` | Consulter et exporter la paie | Exporter les données de paie |

**Fichier source**: `app/core/startup.py` (constante `PAIE_PERMISSIONS`)

#### 3. Module AUDIT (1 permission)

Gestion des logs d'audit.

| Codename | Description | Usage |
|----------|-------------|-------|
| `audit.view` | Consulter les logs d'audit | Voir l'historique des actions |

**Fichier source**: `app/core/startup.py` (constante `AUDIT_PERMISSIONS`)

---

## Configuration du startup.py

### Fonctionnement du système de création automatique

Le fichier `app/core/startup.py` contient deux fonctions principales exécutées au démarrage:

#### 1. `create_default_permissions()`

**Objectif**: Créer automatiquement toutes les permissions au démarrage.

**Processus**:

1. Vérifie si `AUTO_CREATE_PERMISSIONS=True`
2. Se connecte à la base de données
3. Crée les permissions CRUD pour tous les modèles (employe, user, group, etc.)
4. Crée les permissions spécifiques CONGE (8 permissions)
5. Crée les permissions spécifiques AUDIT (1 permission)
6. Crée les permissions spécifiques PAIE (11 permissions)
7. Évite les doublons (vérifie si la permission existe déjà)
8. Commit en base de données

**Code simplifié**:

```python
async def create_default_permissions():
    if not settings.AUTO_CREATE_PERMISSIONS:
        print("⏭️  Auto-create permissions disabled")
        return

    # Créer les permissions CONGE
    for codename, description in CONGE_PERMISSIONS.items():
        # Vérifier si existe déjà
        # Créer si n'existe pas
        permission = Permission(
            codename=codename,
            name=description,
            resource=re
 `HolidayService.load_holidays_for_country()`
6. Évite les doublons (vérifie si le jour férié existe déjà)
7. Affiche le nombre de jours fériés chargés

**Pays supportés**:
- **CD**: République Démocratique du Congo
- **FR**: France
- **BE**: Belgique
- **BI**: Burundi

**Années chargées**: 2024, 2025, 2026

**Code simplifié**:

```python
async def load_default_holidays():
    if not settings.CONGE__HOLIDAYS_AUTO_LOAD:
        print("⏭️  Auto-load holidays disabled")
        return

    COUNTRIES = ["CD", "FR", "BE", "BI"]
    YEARS = [2024, 2025, 2026]

    for country in COUNTRIES:
        for year in YEARS:
            await HolidayService.load_holidays_for_country(
                country, year, session
            )
```

#### 3. `run_startup_tasks()`

**Objectif**: Orchestrer toutes les tâches de démarrage.

```python
async def run_startup_tasks():
    await create_default_permissions()
    await load_default_holidays()
    # Ajouter d'autres tâches ici
```

#### 4. `startup_event_handler()`

**Objectif**: Wrapper synchrone appelé par FastAPI.

```python
def startup_event_handler():
    asyncio.run(run_startup_tasks())
```

**Appelé dans**: `main.py` via `@app.on_event("startup")`

---

## Variables d'environnement

### Configuration des permissions

#### `AUTO_CREATE_PERMISSIONS`

**Type**: Boolean
**Défaut**: `True`
**Description**: Active/désactive la création automatique des permissions au démarrage.

**Valeurs**:
- `True`: Les permissions sont créées automatiquement (recommandé pour développement)
- `False`: Les permissions doivent être créées manuellement (recommandé pour production)

**Exemple**:
```env
AUTO_CREATE_PERMISSIONS=True
```

**Impact**:
- Si `True`: Au démarrage, toutes les 20 permissions sont créées automatiquement
- Si `False`: Message "⏭️  Auto-create permissions disabled" affiché

### Configuration des congés

#### `CONGE__HOLIDAYS_AUTO_LOAD`

**Type**: Boolean
**Défaut**: `True`
**Description**: Active/désactive le chargement automatique des jours fériés au démarrage.

**Valeurs**:
- `True`: Les jours fériés sont chargés automatiquement pour CD, FR, BE, BI (2024-2026)
- `False`: Les jours fériés doivent être chargés manuellement

**Exemple**:
```env
CONGE__HOLIDAYS_AUTO_LOAD=True
```

**Impact**:
- Si `True`: Charge automatiquement ~100-150 jours fériés au démarrage
- Si `False`: Message "⏭️  Auto-load holidays disabled" affiché

#### `CONGE__DEFAULT_COUNTRY_CODE`

**Type**: String
**Défaut**: `CD`
**Description**: Code pays par défaut pour les calculs de congés (ISO 3166-1 alpha-2).

**Valeurs possibles**: `CD`, `FR`, `BE`, `BI`, `CA`, `US`, `GB`, `DE`, `ES`, `IT`, `NL`, `CH`, `LU`

**Exemple**:
```env
CONGE__DEFAULT_COUNTRY_CODE=CD
```

#### `CONGE__MAX_VALIDATION_LEVELS`

**Type**: Integer
**Défaut**: `3`
**Description**: Nombre maximum de niveaux de validation pour les demandes de congés.

**Exemple**:
```env
CONGE__MAX_VALIDATION_LEVELS=3
```

#### `CONGE__MAX_DOCUMENT_SIZE_MB`

**Type**: Integer
**Défaut**: `5`
**Description**: Taille maximale des documents joints aux demandes de congés (en MB).

**Exemple**:
```env
CONGE__MAX_DOCUMENT_SIZE_MB=5
```

#### `CONGE__ALLOWED_DOCUMENT_TYPES`

**Type**: String (comma-separated)
**Défaut**: `pdf,jpg,jpeg,png`
**Description**: Types de documents autorisés pour les pièces jointes.

**Exemple**:
```env
CONGE__ALLOWED_DOCUMENT_TYPES=pdf,jpg,jpeg,png
```

### Configuration de la sécurité

#### `AUTHENTICATION_ENABLED`

**Type**: Boolean
**Défaut**: `True`
**Description**: Active/désactive l'authentification JWT.

**Exemple**:
```env
AUTHENTICATION_ENABLED=True
```

#### `PERMISSION_CHECK_ENABLED`

**Type**: Boolean
**Défaut**: `True`
**Description**: Active/désactive la vérification des permissions.

**Exemple**:
```env
PERMISSION_CHECK_ENABLED=True
```

**Note**: Si `False`, tous les utilisateurs authentifiés ont accès à toutes les routes.

### Fichier .env complet

```env
# Permissions
AUTO_CREATE_PERMISSIONS=True

# Leave Management Configuration
CONGE__DEFAULT_COUNTRY_CODE=CD
CONGE__HOLIDAYS_AUTO_LOAD=True
CONGE__MAX_VALIDATION_LEVELS=3
CONGE__MAX_DOCUMENT_SIZE_MB=5
CONGE__ALLOWED_DOCUMENT_TYPES=pdf,jpg,jpeg,png

# Security
AUTHENTICATION_ENABLED=True
PERMISSION_CHECK_ENABLED=True
```

---

## Messages de log au démarrage

### Scénario 1: Première exécution (base de données vide)

```
🔐 Creating default permissions...
✅ Created 20 new permissions
   - Conge app: 8 permissions
   - Audit app: 1 permissions
   - Paie app: 11 permissions
✓ Permission initialization complete (20 total)

🎉 Loading default holidays...
  ✅ CD 2024: 12 new holidays
  ✅ CD 2025: 12 new holidays
  ✅ CD 2026: 12 new holidays
  ✅ FR 2024: 11 new holidays
  ✅ FR 2025: 11 new holidays
  ✅ FR 2026: 11 new holidays
  ✅ BE 2024: 10 new holidays
  ✅ BE 2025: 10 new holidays
  ✅ BE 2026: 10 new holidays
  ✅ BI 2024: 13 new holidays
  ✅ BI 2025: 13 new holidays
  ✅ BI 2026: 13 new holidays
✅ Loaded 138 new holidays
✓ Holiday initialization complete
```

### Scénario 2: Exécution suivante (données déjà présentes)

```
🔐 Creating default permissions...
⏭️  Skipped 20 existing permissions
✓ Permission initialization complete (20 total)

🎉 Loading default holidays...
⏭️  All holidays already loaded
✓ Holiday initialization complete
```

### Scénario 3: AUTO_CREATE_PERMISSIONS=False

```
⏭️  Auto-create permissions disabled (set AUTO_CREATE_PERMISSIONS=true to enable)

🎉 Loading default holidays...
  ✅ CD 2024: 12 new holidays
  ...
✓ Holiday initialization complete
```

### Scénario 4: CONGE__HOLIDAYS_AUTO_LOAD=False

```
🔐 Creating default permissions...
✅ Created 20 new permissions
✓ Permission initialization complete (20 total)

⏭️  Auto-load holidays disabled
```

### Scénario 5: Erreur de connexion à la base de données

```
🔐 Creating default permissions...
❌ Error creating permissions: could not connect to server

⏭️  Auto-load holidays disabled
```

**Note**: L'application démarre quand même, même si les tâches de startup échouent.

---

## Instructions de vérification

### 1. Vérifier que les permissions sont créées

#### Via l'API

```bash
# Lister toutes les permissions
curl -X GET "http://localhost:8000/permissions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Réponse attendue**: 20 permissions (ou plus si vous avez créé des permissions CRUD)

```json
{
  "items": [
    {
      "id": 1,
      "codename": "conge.view",
      "name": "Consulter les congés",
      "resource": "conge",
      "action": "VIEW",
      "description": "Consulter les congés"
    },
    {
      "id": 2,
      "codename": "conge.create",
      "name": "Créer des demandes de congés",
      "resource": "conge",
      "action": "CREATE",
      "description": "Créer des demandes de congés"
    },
    ...
  ],
  "total": 20
}
```

#### Via la base de données

```sql
-- Compter les permissions
SELECT COUNT(*) FROM permission;
-- Résultat attendu: 20 (ou plus)

-- Lister les permissions par app
SELECT resource, COUNT(*) as count
FROM permission
GROUP BY resource
ORDER BY resource;

-- Résultat attendu:
-- conge: 8
-- alert: 3
-- retenue: 2
-- periode: 3
-- entree: 2
-- payroll: 1
-- audit: 1
```

### 2. Vérifier que les jours fériés sont chargés

#### Via l'API

```bash
# Lister les jours fériés pour CD 2024
curl -X GET "http://localhost:8000/conge/jours-feries?pays_code=CD&annee=2024" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Réponse attendue**: ~12 jours fériés pour CD 2024

```json
{
  "items": [
    {
      "id": 1,
      "date": "2024-01-01",
      "nom": "Jour de l'An",
      "pays_code": "CD",
      "annee": 2024,
      "type_date": "NORMAL"
    },
    {
      "id": 2,
      "date": "2024-01-04",
      "nom": "Journée des Martyrs",
      "pays_code": "CD",
      "annee": 2024,
      "type_date": "NORMAL"
    },
    ...
  ],
  "total": 12
}
```

#### Via la base de données

```sql
-- Compter les jours fériés
SELECT COUNT(*) FROM jour_ferie;
-- Résultat attendu: ~138 (12*3 + 11*3 + 10*3 + 13*3)

-- Compter par pays et année
SELECT pays_code, annee, COUNT(*) as count
FROM jour_ferie
GROUP BY pays_code, annee
ORDER BY pays_code, annee;

-- Résultat attendu:
-- CD 2024: 12
-- CD 2025: 12
-- CD 2026: 12
-- FR 2024: 11
-- FR 2025: 11
-- FR 2026: 11
-- BE 2024: 10
-- BE 2025: 10
-- BE 2026: 10
-- BI 2024: 13
-- BI 2025: 13
-- BI 2026: 13
```

### 3. Vérifier les logs de démarrage

#### Démarrer l'application

```bash
cd rhBackFast
uvicorn main:app --reload
```

#### Vérifier la sortie console

Vous devriez voir:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.

🔐 Creating default permissions...
✅ Created 20 new permissions
   - Conge app: 8 permissions
   - Audit app: 1 permissions
   - Paie app: 11 permissions
✓ Permission initialization complete (20 total)

🎉 Loading default holidays...
  ✅ CD 2024: 12 new holidays
  ...
✅ Loaded 138 new holidays
✓ Holiday initialization complete

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 4. Tester une route protégée

#### Sans permission (doit échouer)

```bash
# Créer un utilisateur sans permissions
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "nom": "Test",
    "prenom": "User"
  }'

# Se connecter
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Essayer d'accéder à une route protégée
curl -X GET "http://localhost:8000/conge/demandes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Réponse attendue**: `403 Forbidden`

```json
{
  "detail": "Permission denied: conge.view"
}
```

#### Avec permission (doit réussir)

```bash
# 1. Créer un groupe
curl -X POST "http://localhost:8000/groups" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "EMPLOYEE",
    "nom": "Employé"
  }'

# 2. Attribuer la permission au groupe
curl -X POST "http://localhost:8000/group-permissions" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "permission_id": 1,
    "granted": true
  }'

# 3. Ajouter l'utilisateur au groupe
curl -X POST "http://localhost:8000/user-groups" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "group_id": 1
  }'

# 4. Réessayer d'accéder à la route
curl -X GET "http://localhost:8000/conge/demandes" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Réponse attendue**: `200 OK` avec la liste des demandes

### 5. Vérifier la configuration

#### Vérifier les variables d'environnement

```bash
# Afficher les variables
cat .env | grep -E "(AUTO_CREATE_PERMISSIONS|CONGE__)"
```

**Résultat attendu**:

```
AUTO_CREATE_PERMISSIONS=True
CONGE__DEFAULT_COUNTRY_CODE=CD
CONGE__HOLIDAYS_AUTO_LOAD=True
CONGE__MAX_VALIDATION_LEVELS=3
CONGE__MAX_DOCUMENT_SIZE_MB=5
CONGE__ALLOWED_DOCUMENT_TYPES=pdf,jpg,jpeg,png
```

#### Vérifier que la configuration est chargée

```python
# Dans un shell Python
from app.core.config import settings

print(settings.AUTO_CREATE_PERMISSIONS)  # True
print(settings.CONGE__HOLIDAYS_AUTO_LOAD)  # True
print(settings.CONGE__DEFAULT_COUNTRY_CODE)  # CD
```

### 6. Dépannage

#### Problème: Les permissions ne sont pas créées

**Causes possibles**:
1. `AUTO_CREATE_PERMISSIONS=False` dans `.env`
2. Erreur de connexion à la base de données
3. Les permissions existent déjà

**Solution**:
```bash
# Vérifier la variable
grep AUTO_CREATE_PERMISSIONS .env

# Vérifier les logs au démarrage
# Chercher "Creating default permissions"

# Supprimer les permissions existantes (si nécessaire)
# ATTENTION: Cela supprimera toutes les permissions!
psql -d rh_db -c "DELETE FROM permission;"
```

#### Problème: Les jours fériés ne sont pas chargés

**Causes possibles**:
1. `CONGE__HOLIDAYS_AUTO_LOAD=False` dans `.env`
2. Erreur de connexion à la base de données
3. Les jours fériés existent déjà

**Solution**:
```bash
# Vérifier la variable
grep CONGE__HOLIDAYS_AUTO_LOAD .env

# Vérifier les logs au démarrage
# Chercher "Loading default holidays"

# Supprimer les jours fériés existants (si nécessaire)
psql -d rh_db -c "DELETE FROM jour_ferie;"
```

#### Problème: 403 Forbidden sur toutes les routes

**Causes possibles**:
1. L'utilisateur n'a pas de permissions
2. L'utilisateur n'est pas dans un groupe
3. Le groupe n'a pas de permissions

**Solution**:
```bash
# Vérifier les permissions de l'utilisateur
curl -X GET "http://localhost:8000/group-permissions/users/{user_id}/permissions" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Créer un superuser (bypass toutes les permissions)
curl -X POST "http://localhost:8000/users" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure_password",
    "is_superuser": true
  }'
```

#### Problème: Désactiver temporairement les permissions

**Solution**:
```env
# Dans .env
PERMISSION_CHECK_ENABLED=False
```

**Note**: Tous les utilisateurs authentifiés auront accès à toutes les routes.

---

## Résumé

### Checklist de vérification

- [ ] `AUTO_CREATE_PERMISSIONS=True` dans `.env`
- [ ] `CONGE__HOLIDAYS_AUTO_LOAD=True` dans `.env`
- [ ] 20 permissions créées en base de données
- [ ] ~138 jours fériés chargés (CD, FR, BE, BI pour 2024-2026)
- [ ] Logs de démarrage affichent "✅ Created X new permissions"
- [ ] Logs de démarrage affichent "✅ Loaded X new holidays"
- [ ] Routes protégées retournent 403 sans permission
- [ ] Routes protégées retournent 200 avec permission

### Commandes rapides

```bash
# Démarrer l'application
uvicorn main:app --reload

# Compter les permissions
psql -d rh_db -c "SELECT COUNT(*) FROM permission;"

# Compter les jours fériés
psql -d rh_db -c "SELECT COUNT(*) FROM jour_ferie;"

# Lister les permissions via API
curl -X GET "http://localhost:8000/permissions"

# Lister les jours fériés via API
curl -X GET "http://localhost:8000/conge/jours-feries?pays_code=CD&annee=2024"
```

---

## Ressources complémentaires

- **Guide de référence des permissions**: `PERMISSIONS_REFERENCE.md`
- **Configuration de sécurité**: `SECURITY_CONFIG_GUIDE.md`
- **Code source startup**: `app/core/startup.py`
- **Code source permissions**: `app/core/permissions.py`
- **Constantes conge_app**: `app/conge_app/constants.py`
