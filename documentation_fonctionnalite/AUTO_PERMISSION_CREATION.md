# Création Automatique des Permissions au Démarrage

## Vue d'ensemble

Le système peut créer automatiquement toutes les permissions CRUD pour tous les modèles au démarrage de l'application. Cette fonctionnalité est contrôlée par la variable d'environnement `AUTO_CREATE_PERMISSIONS`.

## Configuration

### Activer la création automatique (Développement)

Dans votre fichier `.env`:
```bash
AUTO_CREATE_PERMISSIONS=True
```

### Désactiver la création automatique (Production)

Dans votre fichier `.env`:
```bash
AUTO_CREATE_PERMISSIONS=False
```

## Comment ça fonctionne

### 1. Au démarrage de l'application

Quand vous lancez l'application avec `uvicorn main:app` ou `python main.py`, le système:

1. Vérifie si `AUTO_CREATE_PERMISSIONS=True`
2. Si oui, inspecte tous les modèles SQLAlchemy
3. Pour chaque modèle, crée 4 permissions (CREATE, READ, UPDATE, DELETE)
4. Vérifie si la permission existe déjà (évite les doublons)
5. Crée uniquement les permissions manquantes
6. Affiche un résumé dans les logs

### 2. Exemple de sortie

```
🚀 Starting RH Management System v1.0.0...

🔐 Creating default permissions...
✅ Created 40 new permissions
⏭️  Skipped 0 existing permissions
✓ Permission initialization complete (40 total)

✓ Application ready
```

### 3. Lors des redémarrages suivants

```
🚀 Starting RH Management System v1.0.0...

🔐 Creating default permissions...
⏭️  Skipped 40 existing permissions
✓ Permission initialization complete (40 total)

✓ Application ready
```

## Avantages

### ✅ Pour le développement

1. **Pas d'étape manuelle** - Les permissions sont créées automatiquement
2. **Nouveau développeur** - Setup simplifié, pas besoin de lancer de script
3. **Nou
ndes (mais une seule fois)
2. **Logs verbeux** - Peut polluer les logs de production
3. **Pas de contrôle** - Les permissions sont créées automatiquement
4. **Migrations préférées** - En production, on préfère des migrations contrôlées

## Recommandations

### Développement Local
```bash
AUTO_CREATE_PERMISSIONS=True
```
✅ Activé - Facilite le développement

### Tests / CI/CD
```bash
AUTO_CREATE_PERMISSIONS=True
```
✅ Activé - Simplifie les tests

### Staging
```bash
AUTO_CREATE_PERMISSIONS=True
```
✅ Activé - Permet de tester la fonctionnalité

### Production
```bash
AUTO_CREATE_PERMISSIONS=False
```
❌ Désactivé - Utilisez des migrations contrôlées

## Alternative: Script Manuel

Si vous préférez créer les permissions manuellement, vous pouvez toujours utiliser le script:

```bash
# Créer toutes les permissions
python create_permissions.py create

# Lister les permissions
python create_permissions.py list

# Supprimer toutes les permissions (attention!)
python create_permissions.py delete
```

## Personnalisation

### Modifier les mappings de ressources

Éditez `app/core/startup.py`:

```python
MODEL_RESOURCE_MAPPING = {
    "Employe": "employe",
    "User": "user",
    "MonNouveauModele": "ma_ressource",  # Ajoutez ici
}
```

### Modifier les content types

Éditez `app/core/startup.py`:

```python
CONTENT_TYPE_MAPPING = {
    "employe": 1,
    "user": 2,
    "ma_ressource": 99,  # Ajoutez ici
}
```

### Ajouter d'autres tâches de démarrage

Éditez `app/core/startup.py`:

```python
async def run_startup_tasks():
    """Run all startup tasks"""
    await create_default_permissions()
    await create_default_groups()  # Ajoutez ici
    await create_default_users()   # Ajoutez ici
```

## Gestion des erreurs

### Si la création échoue

Le système n'empêche pas l'application de démarrer. Si une erreur se produit:

1. L'erreur est affichée dans les logs
2. L'application continue de démarrer
3. Vous pouvez créer les permissions manuellement plus tard

Exemple:
```
🔐 Creating default permissions...
❌ Error creating permissions: connection refused

✓ Application ready
```

### Vérifier que les permissions sont créées

```bash
# Via l'API
curl http://localhost:8000/api/permissions

# Via le script
python create_permissions.py list

# Via la base de données
psql -d rh_db -c "SELECT COUNT(*) FROM user_management_permission;"
```

## Débogage

### Activer les logs détaillés

Dans `app/core/startup.py`, changez `echo=False` en `echo=True`:

```python
engine = create_async_engine(settings.DATABASE_URL, echo=True)
```

Cela affichera toutes les requêtes SQL exécutées.

### Vérifier la configuration

```python
from app.core.config import settings
print(settings.AUTO_CREATE_PERMISSIONS)  # Devrait afficher True ou False
```

## Migration depuis le script manuel

Si vous utilisiez `create_permissions.py` avant:

1. **Rien à faire!** Les permissions existantes ne seront pas recréées
2. Activez `AUTO_CREATE_PERMISSIONS=True`
3. Redémarrez l'application
4. Les nouvelles permissions seront créées automatiquement

## FAQ

### Q: Est-ce que ça ralentit l'application?
**R:** Seulement au démarrage, et seulement de 1-2 secondes. Une fois l'application démarrée, il n'y a aucun impact.

### Q: Est-ce que ça crée des doublons?
**R:** Non, le système vérifie si chaque permission existe avant de la créer.

### Q: Que se passe-t-il si j'ajoute un nouveau modèle?
**R:** Au prochain redémarrage, les permissions pour ce modèle seront créées automatiquement.

### Q: Puis-je désactiver temporairement?
**R:** Oui, mettez `AUTO_CREATE_PERMISSIONS=False` dans votre `.env` et redémarrez.

### Q: Est-ce que ça fonctionne avec Docker?
**R:** Oui, ajoutez la variable d'environnement dans votre `docker-compose.yml`:
```yaml
environment:
  - AUTO_CREATE_PERMISSIONS=True
```

### Q: Est-ce que ça fonctionne avec plusieurs instances?
**R:** Oui, chaque instance vérifie si les permissions existent. La première instance les crée, les autres les ignorent.

### Q: Puis-je utiliser les deux méthodes?
**R:** Oui! Vous pouvez avoir `AUTO_CREATE_PERMISSIONS=True` ET utiliser le script `create_permissions.py` manuellement. Ils sont compatibles.

## Exemples d'utilisation

### Développement local

```bash
# 1. Activer dans .env
echo "AUTO_CREATE_PERMISSIONS=True" >> .env

# 2. Démarrer l'application
python main.py

# 3. Les permissions sont créées automatiquement!
```

### Docker

```yaml
# docker-compose.yml
services:
  api:
    build: .
    environment:
      - AUTO_CREATE_PERMISSIONS=True
      - DATABASE_URL=postgresql+asyncpg://...
    ports:
      - "8000:8000"
```

### Tests

```python
# conftest.py
import pytest
from app.core.startup import create_default_permissions

@pytest.fixture(scope="session")
async def setup_permissions():
    """Create permissions before running tests"""
    await create_default_permissions()
```

## Conclusion

La création automatique des permissions au démarrage est une fonctionnalité pratique pour le développement et les tests. Elle simplifie le setup et garantit que les permissions sont toujours à jour.

Pour la production, il est recommandé de désactiver cette fonctionnalité et d'utiliser des migrations contrôlées à la place.

## Voir aussi

- [PERMISSION_QUICK_START.md](./PERMISSION_QUICK_START.md) - Guide de démarrage rapide
- [create_permissions.py](./create_permissions.py) - Script manuel
- [app/core/startup.py](./app/core/startup.py) - Code source
- [app/core/config.py](./app/core/config.py) - Configuration
