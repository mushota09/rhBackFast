# Guide de Lancement de l'Application rhBackFast

## ✅ État Actuel

L'application FastAPI est maintenant **prête à être lancée** ! Tous les problèmes ont été corrigés :

1. ✅ Audit system intégré dans les routes
2. ✅ Erreurs de syntaxe corrigées
3. ✅ Permissions corrigées (`require_permission` avec 2 arguments)
4. ✅ Dépréciation `regex` → `pattern` corrigée
5. ✅ Routes d'audit réparées

## 🚀 Lancement de l'Application

### Option 1 : Lancement Direct (Recommandé)

```bash
cd D:\PROJETS\PYTHON_3\rhBackFast
python main.py
```

L'application démarrera sur `http://localhost:8000`

### Option 2 : Lancement avec Uvicorn

```bash
cd D:\PROJETS\PYTHON_3\rhBackFast
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3 : Lancement en arrière-plan (PowerShell)

```powershell
cd D:\PROJETS\PYTHON_3\rhBackFast
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

## 📊 Vérification du Serveur

Une fois le serveur lancé, vous verrez :

```
✓ Configuration validation successful

🚀 Starting RH Management System v1.0.0...
✓ Application ready

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Test Rapide

Ouvrez votre navigateur et accédez à :

- **API Root** : http://localhost:8000/
- **Health Check** : http://localhost:8000/health
- **Documentation Interactive (Swagger)** : http://localhost:8000/docs
- **Documentation Alternative (ReDoc)** : http://localhost:8000/redoc

Ou utilisez le script de test :

```bash
python test_server.py
```

## 📚 Endpoints Disponibles

### Authentification (`/api/auth`)
- `POST /api/auth/login` - Connexion (avec audit LOGIN/LOGIN_FAILED)
- `POST /api/auth/logout` - Déconnexion (avec audit LOGOUT)
- `POST /api/auth/refresh` - Rafraîchir le token
- `GET /api/auth/protected` - Route protégée de test

### Employés (`/api/employees`)
- `GET /api/employees` - Liste des employés
- `POST /api/employees` - Créer un employé (avec audit CREATE)
- `GET /api/employees/{id}` - Détails d'un employé
- `PUT /api/employees/{id}` - Modifier un employé (avec audit UPDATE)
- `DELETE /api/employees/{id}` - Supprimer un employé (avec audit DELETE)
- `GET /api/employees/export` - Exporter les employés (avec audit EXPORT)

### Utilisateurs (`/api/users`)
- `GET /api/users` - Liste des utilisateurs
- `POST /api/users` - Créer un utilisateur (avec audit CREATE)
- `GET /api/users/{id}` - Détails d'un utilisateur
- `PUT /api/users/{id}` - Modifier un utilisateur (avec audit UPDATE)
- `DELETE /api/users/{id}` - Supprimer un utilisateur (avec audit DELETE)

### Services (`/api/services`)
- `GET /api/services` - Liste des services
- `POST /api/services` - Créer un service
- `GET /api/services/{id}` - Détails d'un service
- `PUT /api/services/{id}` - Modifier un service
- `DELETE /api/services/{id}` - Supprimer un service

### Groupes (`/api/groups`)
- `GET /api/groups` - Liste des groupes
- `POST /api/groups` - Créer un groupe
- `GET /api/groups/{id}` - Détails d'un groupe
- `PUT /api/groups/{id}` - Modifier un groupe
- `DELETE /api/groups/{id}` - Supprimer un groupe

### Permissions (`/api/permissions`)
- `GET /api/permissions` - Liste des permissions
- `GET /api/permissions/{id}` - Détails d'une permission

### Audit Logs (`/api/audit-logs`)
- `GET /api/audit-logs` - Liste des logs d'audit (avec filtres)
- `GET /api/audit-logs/{id}` - Détails d'un log
- `GET /api/audit-logs/stats` - Statistiques d'audit
- `GET /api/audit-logs/users/{user_id}` - Logs d'un utilisateur
- `GET /api/audit-logs/resources/{resource_type}` - Logs d'une ressource

### Paie (`/api/paie`)
- `GET /api/paie/alerts` - Liste des alertes
- `POST /api/paie/alerts` - Créer une alerte
- `GET /api/paie/payroll/export` - Exporter la paie (avec audit EXPORT)

## 🔐 Système d'Audit Intégré

Toutes les actions importantes sont maintenant auditées automatiquement :

### Actions Auditées

1. **CRUD Operations** (CREATE, UPDATE, DELETE)
   - Employés
   - Utilisateurs
   - Services
   - Groupes

2. **Authentification** (LOGIN, LOGIN_FAILED, LOGOUT)
   - Connexions réussies
   - Tentatives de connexion échouées
   - Déconnexions

3. **Exports** (EXPORT)
   - Export d'employés
   - Export de paie

### Informations Capturées

Pour chaque action, le système enregistre :
- ✅ Utilisateur (qui a fait l'action)
- ✅ Action (CREATE, UPDATE, DELETE, etc.)
- ✅ Type de ressource (employe, user, etc.)
- ✅ ID de la ressource
- ✅ Anciennes valeurs (pour UPDATE/DELETE)
- ✅ Nouvelles valeurs (pour CREATE/UPDATE)
- ✅ Adresse IP
- ✅ User-Agent (navigateur)
- ✅ Méthode HTTP
- ✅ Chemin de la requête
- ✅ Statut de la réponse
- ✅ Temps d'exécution
- ✅ Timestamp

### Données Sensibles Masquées

Les données sensibles sont automatiquement masquées dans les logs :
- Mots de passe → `***MASKED***`
- Tokens → `***MASKED***`
- Clés API → `***MASKED***`
- Numéros de carte bancaire → `***MASKED***`

## 🗄️ Base de Données

### Configuration

La base de données est configurée dans `.env` :

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_gZ4eYlSdwr3o@ep-tiny-sound-agslibpd-pooler.c-2.eu-central-1.aws.neon.tech/rh_db?sslmode=require
```

### Migrations

La migration de la table `audit_log` est déjà appliquée :

```bash
alembic current
# Output: 893871e59f44 (head)
```

Pour voir l'historique des migrations :

```bash
alembic history
```

Pour appliquer de nouvelles migrations :

```bash
alembic upgrade head
```

## 🔧 Configuration

### Variables d'Environnement (`.env`)

```env
# Application
APP_NAME="RH Management System"
APP_VERSION="1.0.0"
DEBUG=True

# Database
DATABASE_URL=postgresql+asyncpg://...

# Security
SECRET_KEY=dev-secret-key-for-development-only-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Permissions
AUTO_CREATE_PERMISSIONS=True
```

### Middleware Activé

- ✅ **CORS Middleware** - Permet les requêtes cross-origin
- ✅ **Audit Middleware** - Enregistre automatiquement toutes les requêtes

## 📝 Prochaines Étapes

### Phase 8 : Permissions (À faire)
- [ ] Créer les permissions d'audit (`audit.view`, `audit.export`, `audit.delete`)
- [ ] Exécuter `python create_permissions.py`
ur les statistiques
- [ ] Archivage automatique des logs anciens
- [ ] Suppression automatique après rétention

## 🐛 Dépannage

### Le serveur ne démarre pas

1. Vérifiez que le port 8000 n'est pas déjà utilisé :
   ```bash
   netstat -ano | findstr :8000
   ```

2. Vérifiez la connexion à la base de données :
   ```bash
   python -c "from app.core.database import engine; print('DB OK')"
   ```

3. Vérifiez les logs d'erreur dans la console

### Erreur de connexion à la base de données

Si vous voyez `TypeError: connect() got an unexpected keyword argument 'sslmode'` :

1. Vérifiez que `asyncpg` est installé :
   ```bash
   pip install asyncpg
   ```

2. Vérifiez l'URL de la base de données dans `.env`

### Les routes d'audit ne fonctionnent pas

1. Vérifiez que la migration est appliquée :
   ```bash
   alembic current
   ```

2. Vérifiez que la table `audit_log` existe :
   ```sql
   SELECT * FROM audit_log LIMIT 1;
   ```

## 📞 Support

Pour toute question ou problème :

1. Consultez la documentation interactive : http://localhost:8000/docs
2. Vérifiez les logs de l'application
3. Consultez les fichiers de spécification dans `.kiro/specs/audit-system/`

---

**Créé** : 2024-02-17
**Version** : 1.0.0
**Status** : ✅ PRÊT POUR UTILISATION
