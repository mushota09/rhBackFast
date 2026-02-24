# Permissions Extraites du Projet rhBackFast

Ce document liste toutes les permissions spécifiques utilisées dans les appels `require_permission()` à travers le projet rhBackFast.

Date d'extraction: ${new Date().toISOString()}

---

## CONGE_APP

**Fichier**: `rhBackFast/app/conge_app/routes.py`

### Permissions identifiées:

- **conge.view** - Consultation des données de congés
  - Liste des types de congés
  - Détails d'un type de congé
  - Liste des demandes de congés
  - Détails d'une demande de congé
  - Liste des soldes de congés
  - Détails d'un solde de congé
  - Liste des historiques de congés
  - Détails d'un historique de congé
  - Statistiques globales de congés
  - Statistiques par employé
  - Statistiques par service

- **conge.manage_types** - Gestion des types de congés
  - Création d'un type de congé
  - Modification d'un type de congé
  - Suppression d'un type de congé

- **conge.export** - Export des données de congés
  - Export des demandes de congés (JSON, CSV, Excel)

- **conge.create** - Création de demandes de congés
  - Création d'une nouvelle demande de congé

- **conge.update** - Modification de demandes de congés
  - Modification d'une demande de congé (statut PENDING uniquement)

- **conge.delete** - Suppression/Annulation de demandes de congés
  - Annulation d'une demande de congé

- **conge.approve** - Approbation/Rejet de demandes de congés
  - Approbation d'une demande de congé
  - Rejet d'une demande de congé
  - Délégation de validation d'une demande de congé

- **conge.manage_soldes** - Gestion des soldes de congés
  - Création d'un solde de congé
  - Modification d'un solde de congé
  - Suppression d'un solde de congé
  - Création en masse de soldes de congés

---

## AUDIT_APP

**Fichier**: `rhBackFast/app/audit_app/routes.py`

### Permissions identifiées:

- **audit.view** - Consultation des logs d'audit
  - Liste des logs d'audit avec filtres
  - Statistiques d'audit
  - Logs d'audit par utilisateur
  - Logs d'audit par type de ressource
  - Détails d'un log d'audit spécifique

---

## PAIE_APP

**Fichier**: `rhBackFast/app/paie_app/routes.py`

### Permissions identifiées:

- **alert.view** - Consultation des alertes
  - Liste des alertes
  - Détails d'une alerte
  - Résumé des alertes

- **alert.create** - Création d'alertes
  - Création d'une nouvelle alerte

- **alert.update** - Modification d'alertes
  - Envoi manuel de notification pour une alerte

- **retenue.view** - Consultation des retenues
  - Liste des retenues employés
  - Résumé des retenues
  - Historique de modification d'une retenue

- **retenue.create** - Création de retenues
iste des entrées de paie
  - Génération de bulletin de paie pour une entrée
  - Téléchargement de bulletin de paie

- **entree.update** - Modification d'entrées de paie
  - Recalcul d'une entrée de paie

- **payroll.view** - Consultation et export de la paie
  - Export d'une période de paie (Excel, CSV)
  - Export de toutes les périodes de paie
  - Export des retenues
  - Export général de la paie (déprécié)
  - Résumé d'une période de paie
  - Résumé annuel
  - Historique de paie d'un employé
  - Top des salaires
  - Résumé du tableau de bord
  - Analyse comparative

---

## USER_APP

**Fichier**: `rhBackFast/app/user_app/routes.py`

### Statut:
❌ **Fichi
. payroll.view

### USER_APP (0 permission)
- Aucune permission trouvée

---

## TOTAL: 20 permissions uniques

---

## NOTES

1. **Format des permissions**: Toutes les permissions suivent le format `app.action`
2. **Cohérence**: Les permissions sont cohérentes avec le modèle CRUD (Create, Read, Update, Delete)
3. **Permissions spéciales**:
   - `conge.manage_types`: Gestion administrative des types de congés
   - `conge.manage_soldes`: Gestion administrative des soldes de congés
   - `conge.approve`: Permission spéciale pour le workflow de validation
   - `conge.export`: Permission spéciale pour l'export de données
   - `payroll.view`: Permission globale pour la consultation de la paie

4. **Sécurité**: Chaque endpoint est protégé par une permission spécifique via le décorateur `require_permission()`

---

## RECOMMANDATIONS

1. **user_app**: Considérer l'ajout de permissions pour user_app si des routes existent
2. **Documentation**: Maintenir ce document à jour lors de l'ajout de nouvelles routes
3. **Tests**: Vérifier que toutes les permissions sont correctement configurées dans la base de données
4. **Rôles**: Mapper ces permissions aux rôles utilisateurs appropriés
