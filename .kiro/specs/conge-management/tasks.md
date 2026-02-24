# Implementation Plan: Gestion des Congés Professionnelle

## Overview

Ce plan d'implémentation détaille les étapes pour construire un système complet de gestion des congés dans rhBackFast. Le système supportera les demi-journées, la gestion multi-pays des jours fériés, la validation hiérarchique multi-niveaux, et fournira une API REST complète avec traçabilité.

## Tasks

- [x] 1. Setup et Configuration Initiale
- [x] 1.1 Créer la structure du module conge_app
  - Créer les fichiers: __init__.py, models.py, schemas.py, routes.py, services.py, constants.py, utils.py
  - _Requirements: Infrastructure_

- [x] 1.2 Installer et configurer la bibliothèque holidays
  - Ajouter holidays au pyproject.toml
  - Tester le chargement des jours fériés pour CD, FR, BE
  - _Requirements: 2.1, 2.2_

- [x] 1.3 Créer les constantes et énumérations
  - Définir DemiJournee, StatutDemande, ActionHistorique
  - Définir PAYS_SUPPORTES, PERMISSIONS
  - _Requirements: 1.1, 4.1_

- [x] 2. Modèles de Données
- [x] 2.1 Créer le modèle TypeConge
  - Champs: nom, code, nb_jours_max_par_an, report_autorise, necessite_validation, niveaux_validation
  - Relations: demandes, soldes
  - Contrainte unique sur code
  - _Requirements: 3.1_

- [x] 2.2 Créer le modèle JourFerie
  - Champs: pays_code, nom, date_ferie, type_date, annee, est_personnalise
  - Contrainte unique sur (pays_code, nom, annee)
  - Index sur pays_code et date_ferie
  - _Requirements: 2.2, 2.3_

- [x] 2.3 Créer le modèle DemandeConge
  - Champs: employe_id, type_conge_id, date_debut, date_fin
  - Champs demi-journée: est_demi_journee, periode_demi_journee
  - Champs calculés: nb_jours_demandes, nb_jours_ouvrables
  - Champs validation: statut, niveau_validation_actuel
  - Relations: employe, type_conge, historique
  - _Requirements: 1.1, 4.1, 18.1_


- [x] 2.4 Créer le modèle SoldeConge
  - Champs: employe_id, type_conge_id, annee, alloue, utilise, restant, reporte
  - Contrainte unique sur (employe_id, type_conge_id, annee)
  - Relations: employe, type_conge
  - _Requirements: 5.1, 5.6_

- [x] 2.5 Créer le modèle HistoriqueConge
  - Champs: demande_conge_id, niveau_validation, valideur_id, action, date_action, commentaire
  - Champs délégation: delegue_a_id
  - Relations: demande_conge, valideur, delegue_a
  - _Requirements: 6.1, 18.6_

- [x] 3. Utilitaires et Helpers
- [x] 3.1 Implémenter les fonctions de calcul de dates
  - is_weekend(date) → bool
  - count_working_days(date_debut, date_fin, holidays) → int
  - dates_overlap(start1, end1, start2, end2) → bool
  - _Requirements: 13.2_

- [x] 3.2 Implémenter HolidayService
  - load_holidays_for_country(pays_code, annee, db) avec parsing des noms
  - get_holidays_between_dates(pays_code, date_debut, date_fin, db)
  - add_custom_holiday(pays_code, nom, date_ferie, type_date, db)
  - _parse_holiday_name(name) pour extraire le type de date
  - _Requirements: 2.2, 2.5, 2.6_

- [x] 3.3 Implémenter CongeCalculationService.calculate_working_days
  - Calculer nb_jours_demandes (0.5 si demi-journée, sinon jours calendaires)
  - Calculer nb_jours_ouvrables (exclure weekends et fériés)
  - _Requirements: 1.2, 2.5, 13.1, 13.3, 13.4_

- [x] 3.4 Implémenter CongeCalculationService.check_sufficient_balance
  - Récupérer le solde de l'employé pour le type de congé
  - Vérifier si solde_restant >= nb_jours_demandes
  - _Requirements: 4.8, 11.4_

- [x] 3.5 Implémenter CongeCalculationService.check_date_conflicts
  - Rechercher demandes approuvées qui chevauchent les dates
  - Retourner liste des conflits
  - _Requirements: 14.1, 14.2_

- [x] 4. Schémas Pydantic
- [x] 4.1 Créer les schémas TypeConge
  - TypeCongeBase, TypeCongeCreate, TypeCongeUpdate, TypeCongeResponse
  - _Requirements: 3.1_

- [x] 4.2 Créer les schémas DemandeConge
  - DemandeCongeBase avec validateurs Pydantic
  - Valider: est_demi_journee → periode_demi_journee requis
  - Valider: est_demi_journee → date_debut = date_fin
  - DemandeCongeCreate, DemandeCongeUpdate, DemandeCongeResponse
  - ApproveRejectRequest
  - _Requirements: 1.1, 4.1, 11.1_

- [x] 4.3 Créer les schémas SoldeConge
  - SoldeCongeBase, SoldeCongeCreate, SoldeCongeUpdate, SoldeCongeResponse
  - _Requirements: 5.1_

- [x] 4.4 Créer les schémas HistoriqueConge
  - HistoriqueCongeResponse
  - _Requirements: 6.1_

- [x] 4.5 Créer les schémas JourFerie
  - JourFerieBase, JourFerieCreate, JourFerieResponse
  - _Requirements: 2.2_

- [-] 5. Services Métier - ValidationService
- [x] 5.1 Implémenter get_required_validators
  - Déterminer les valideurs pour chaque niveau selon hiérarchie
  - Niveau 1: Manager direct, Niveau 2: Directeur, Niveau 3: RH
  - _Requirements: 18.1, 18.2_

- [x] 5.2 Implémenter can_user_validate
  - Vérifier si l'utilisateur peut valider au niveau actuel
  - _Requirements: 18.2_

- [x] 5.3 Implémenter approve_at_level
  - Créer HistoriqueConge avec action=APPROVED
  - Incrémenter niveau_validation_actuel
  - Si dernier niveau: statut=APPROVED, déduire du solde
  - Sinon: statut=IN_PROGRESS
  - _Requirements: 18.4, 18.7, 4.9_

- [x] 5.4 Implémenter reject_at_level
  - Créer HistoriqueConge avec action=REJECTED
  - Statut=REJECTED
  - Restaurer solde si déjà déduit
  - _Requirements: 18.5, 4.10_

- [x] 5.5 Implémenter delegate_validation
  - Créer HistoriqueConge avec action=DELEGATED
  - Enregistrer delegue_a_id
  - _Requirements: 18.10_

- [x] 6. Services Métier - DemandeCongeService
- [x] 6.1 Implémenter create_demande
  - Valider employé existe
  - Valider type de congé existe
  - Valider date_debut <= date_fin
  - Calculer nb_jours_demandes et nb_jours_ouvrables
  - Vérifier solde suffisant
  - Vérifier pas de conflit de dates
  - Créer la demande avec statut=PENDING
  - _Requirements: 4.1, 4.8, 11.1, 11.2, 11.3, 11.4, 14.1_

- [x] 6.2 Implémenter update_demande
  - Vérifier statut=PENDING (seulement modifiable si en attente)
  - Recalculer jours si dates changent
  - _Requirements: 4.4_

- [x] 6.3 Implémenter cancel_demande
  - Statut=CANCELLED
  - Restaurer solde si déjà déduit
  - _Requirements: 4.5, 4.10_

- [x] 6.4 Implémenter list_demandes
  - Supporter filtres: employe_id, type_conge_id, statut, date_debut, date_fin
  - Supporter search sur raison
  - Supporter expand: employe, type_conge, historique
  - Supporter pagination et no_pagination
  - _Requirements: 4.1, 7.1, 8.1, 9.1_

- [x] 7. Routes API - TypeConge
- [x] 7.1 Implémenter GET /api/conge/types
  - Liste avec pagination et expand
  - Permission: conge.view
  - _Requirements: 3.1, 7.1, 8.1, 12.1_

- [x] 7.2 Implémenter POST /api/conge/types
  - Créer type de congé
  - Permission: conge.manage_types
  - Audit log: CREATE
  - _Requirements: 3.2, 10.1, 12.2_

- [x] 7.3 Implémenter GET /api/conge/types/{id}
  - Détail avec expand
  - Permission: conge.view
  - _Requirements: 3.3, 8.1, 12.1_

- [x] 7.4 Implémenter PUT /api/conge/types/{id}
  - Modifier type de congé
  - Permission: conge.manage_types
  - Audit log: UPDATE
  - _Requirements: 3.4, 10.2, 12.3_

- [x] 7.5 Implémenter DELETE /api/conge/types/{id}
  - Vérifier aucune demande active liée
  - Permission: conge.manage_types
  - Audit log: DELETE
  - _Requirements: 3.5, 3.6, 10.3, 12.4_

- [x] 8. Routes API - DemandeConge
- [-] 8.1 Implémenter GET /api/conge/demandes
  - Liste avec filtres, search, pagination, expand
  - Permission: conge.view
  - _Requirements: 4.1, 7.1, 8.1, 9.1, 12.1_

- [x] 8.2 Implémenter POST /api/conge/demandes
  - Créer demande via DemandeCongeService.create_demande
  - Permission: conge.create
  - Audit log: CREATE
  - _Requirements: 4.2, 10.1, 12.2_

- [x] 8.3 Implémenter GET /api/conge/demandes/{id}
  - Détail avec expand
  - Permission: conge.view
  - _Requirements: 4.3, 8.1, 12.1_

- [x] 8.4 Implémenter PUT /api/conge/demandes/{id}
  - Modifier via DemandeCongeService.update_demande
  - Permission: conge.update
  - Audit log: UPDATE
  - _Requirements: 4.4, 10.2, 12.3_

- [x] 8.5 Implémenter DELETE /api/conge/demandes/{id}
  - Annuler via DemandeCongeService.cancel_demande
  - Permission: conge.delete
  - Audit log: DELETE
  - _Requirements: 4.5, 10.3, 12.4_

- [x] 8.6 Implémenter POST /api/conge/demandes/{id}/approve
  - Approuver via ValidationService.approve_at_level
  - Permission: conge.approve
  - Audit log: APPROVE
  - _Requirements: 4.6, 10.4, 12.5_

- [x] 8.7 Implémenter POST /api/conge/demandes/{id}/reject
  - Rejeter via ValidationService.reject_at_level
  - Permission: conge.approve
  - Audit log: REJECT
  - _Requirements: 4.7, 10.5, 12.5_

- [x] 8.8 Implémenter POST /api/conge/demandes/{id}/delegate
  - Déléguer via ValidationService.delegate_validation
  - Permission: conge.approve
  - Audit log: DELEGATE
  - _Requirements: 18.10_

- [x] 8.9 Implémenter GET /api/conge/demandes/export
  - Exporter en JSON/CSV/Excel
  - Permission: conge.export
  - Audit log: EXPORT
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [x] 9. Routes API - SoldeConge
- [x] 9.1 Implémenter GET /api/conge/soldes
  - Liste avec filtres, pagination, expand
  - Permission: conge.view
  - _Requirements: 5.1, 7.1, 8.1, 12.1_

- [x] 9.2 Implémenter POST /api/conge/soldes
  - Créer solde
  - Calculer automatiquement restant
  - Permission: conge.manage_soldes
  - Audit log: CREATE
  - _Requirements: 5.2, 5.6, 10.1, 12.2_

- [x] 9.3 Implémenter GET /api/conge/soldes/{id}
  - Détail avec expand
  - Permission: conge.view
  - _Requirements: 5.3, 8.1, 12.1_

- [x] 9.4 Implémenter PUT /api/conge/soldes/{id}
  - Modifier solde
  - Recalculer automatiquement restant
  - Permission: conge.manage_soldes
  - Audit log: UPDATE
  - _Requirements: 5.4, 5.6, 10.2, 12.3_

- [x] 9.5 Implémenter DELETE /api/conge/soldes/{id}
  - Supprimer solde
  - Permission: conge.manage_soldes
  - Audit log: DELETE
  - _Requirements: 5.5, 10.3, 12.4_

- [x] 9.6 Implémenter POST /api/conge/soldes/bulk-create
  - Créer soldes pour tous les employés d'une année
  - Permission: conge.manage_soldes
  - _Requirements: 5.7_

- [x] 10. Routes API - HistoriqueConge et Statistiques
- [x] 10.1 Implémenter GET /api/conge/historiques
  - Liste avec filtres, pagination, expand
  - Permission: conge.view
  - _Requirements: 6.1, 7.1, 8.1, 12.1_

- [x] 10.2 Implémenter GET /api/conge/historiques/{id}
  - Détail avec expand
  - Permission: conge.view
  - _Requirements: 6.2, 8.1, 12.1_

- [x] 10.3 Implémenter GET /api/conge/stats
  - Statistiques globales avec filtres
  - Permission: conge.view
  - _Requirements: 19.1, 19.2, 19.3_

- [x] 10.4 Implémenter GET /api/conge/stats/employe/{id}
  - Statistiques d'un employé
  - Permission: conge.view
  - _Requirements: 19.4_

- [x] 10.5 Implémenter GET /api/conge/stats/service/{id}
  - Statistiques d'un service
  - Permission: conge.view
  - _Requirements: 19.5_

- [x] 11. Migration de Base de Données
- [x] 11.1 Créer la migration Alembic(sans ecraser les migrations(les donnees se trouvant dans la base) des autres tables existants dans la base de donnees)
  - Créer tables: cg_type_conge, cg_jour_ferie, cg_demande_conge, cg_solde_conge, cg_historique_conge
  - Créer index de performance
  - Créer contraintes uniques
  - _Requirements: Infrastructure_

- [x] 11.2 Tester la migration
  - Tester si la migration est bien faite
  - Vérifier index créés
  - _Requirements: Infrastructure_

- [x] 12. Données Initiales
- [x] 12.1 Créer les permissions lors du lancement du projet ,il existe deja un script qui fait ca
  - conge.view, conge.create, conge.update, conge.delete
  - conge.approve, conge.manage_types, conge.manage_soldes, conge.export
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 12.2 Créer script de chargement des types de congés
  - Types par défaut: Congé Payé, RTT, Maladie, Maternité, etc.
  - _Requirements: 3.1_

- [x] 12.3 Créer script de chargement des jours fériés
  - Charger jours fériés pour CD, FR, BE pour 2024-2026
  - _Requirements: 2.2_

- [x] 13. Intégration et Configuration
- [x] 13.1 Intégrer les routes dans main.py
  - Ajouter router conge_app
  - _Requirements: Infrastructure_

- [x] 13.2 Ajouter variables d'environnement
  - DEFAULT_COUNTRY_CODE, HOLIDAYS_AUTO_LOAD, MAX_VALIDATION_LEVELS
  - MAX_DOCUMENT_SIZE_MB, ALLOWED_DOCUMENT_TYPES
  - _Requirements: Infrastructure_

- [x] 13.3 Mettre à jour la documentation API
  - Ajouter exemples dans docstrings
  - Vérifier OpenAPI/Swagger
  - _Requirements: Infrastructure_

- [ ] 14. Tests Unitaires
- [ ]* 14.1 Tests pour utils.py
  - Test is_weekend, count_working_days, dates_overlap
  - _Requirements: 13.2_

- [ ]* 14.2 Tests pour HolidayService
  - Test load_holidays_for_country, get_holidays_between_dates
  - _Requirements: 2.2, 2.5_

- [ ]* 14.3 Tests pour CongeCalculationService
  - Test calculate_working_days, check_sufficient_balance, check_date_conflicts
  - _Requirements: 1.2, 4.8, 14.1_

- [ ]* 14.4 Tests pour ValidationService
  - Test approve_at_level, reject_at_level, delegate_validation
  - _Requirements: 18.4, 18.5, 18.10_

- [ ]* 14.5 Tests pour DemandeCongeService
  - Test create_demande, update_demande, cancel_demande
  - _Requirements: 4.2, 4.4, 4.5_

- [ ]* 14.6 Tests pour les routes TypeConge
  - Test CRUD complet
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 14.7 Tests pour les routes DemandeConge
  - Test CRUD, approve, reject, delegate, export
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ]* 14.8 Tests pour les routes SoldeConge
  - Test CRUD, bulk-create
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.7_

- [ ] 15. Tests de Propriétés (Property-Based Tests)
- [ ]* 15.1 Property test: Half-Day Calculation Consistency
  - **Property 1: Half-Day Calculation Consistency**
  - **Validates: Requirements 1.1, 1.2, 1.5**
  - Générer demandes aléatoires avec demi-journées
  - Vérifier calcul correct (0.5 pour demi-journée, jours calendaires sinon)

- [ ]* 15.2 Property test: CRUD Round-Trip for TypeConge
  - **Property 3: CRUD Round-Trip for TypeConge**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
  - Générer TypeConge aléatoires
  - Tester create → read → update → read → delete

- [ ]* 15.3 Property test: Working Days Calculation Accuracy
  - **Property 6: Working Days Calculation Accuracy**
  - **Validates: Requirements 2.5, 13.1, 13.2, 13.3, 13.4**
  - Générer périodes aléatoires
  - Vérifier exclusion weekends et fériés

- [ ]* 15.4 Property test: Sufficient Balance Validation
  - **Property 7: Sufficient Balance Validation**
  - **Validates: Requirements 4.8, 11.4**
  - Générer demandes avec soldes insuffisants
  - Vérifier rejet avec erreur appropriée

- [ ]* 15.5 Property test: Balance Deduction on Approval
  - **Property 8: Balance Deduction on Approval**
  - **Validates: Requirements 4.9**
  - Générer demandes approuvées
  - Vérifier déduction exacte du solde

- [ ]* 15.6 Property test: Balance Restoration on Rejection
  - **Property 9: Balance Restoration on Rejection/Cancellation**
  - **Validates: Requirements 4.10**
  - Générer demandes approuvées puis rejetées
  - Vérifier restauration du solde

- [ ]* 15.7 Property test: Automatic Balance Calculation
  - **Property 10: Automatic Balance Calculation**
  - **Validates: Requirements 5.6**
  - Générer soldes aléatoires
  - Vérifier restant = alloue - utilise + reporte

- [ ]* 15.8 Property test: Automatic History Creation
  - **Property 11: Automatic History Creation**
  - **Validates: Requirements 6.3, 6.4**
  - Générer changements de statut
  - Vérifier création automatique d'historique

- [ ]* 15.9 Property test: Pagination Consistency
  - **Property 12: Pagination Consistency**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
  - Tester pagination vs no_pagination
  - Vérifier cohérence des résultats

- [ ]* 15.10 Property test: Expand Relation Loading
  - **Property 13: Expand Relation Loading**
  - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
  - Tester expand simple, multiple, imbriqué
  - Vérifier chargement correct des relations

- [ ]* 15.11 Property test: Audit Log Completeness
  - **Property 15: Audit Log Completeness**
  - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7**
  - Générer actions aléatoires
  - Vérifier création audit logs avec tous les champs

- [ ]* 15.12 Property test: Date Conflict Detection
  - **Property 19: Date Conflict Detection**
  - **Validates: Requirements 14.1, 14.2, 14.3, 14.4**
  - Générer demandes chevauchantes
  - Vérifier détection et rejet des conflits

- [ ]* 15.13 Property test: Hierarchical Validation Flow
  - **Property 22: Hierarchical Validation Flow**
  - **Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.7, 18.8, 18.9**
  - Générer demandes multi-niveaux
  - Vérifier progression correcte des niveaux

- [ ] 16. Checkpoint Final
- [ ] 16.1 Vérifier tous les tests passent
  - Exécuter pytest avec coverage
  - Vérifier coverage >= 90%
  - _Requirements: All_

- [ ] 16.2 Vérifier la documentation
  - OpenAPI/Swagger complet
  - Exemples fonctionnels
  - _Requirements: Infrastructure_

- [ ] 16.3 Demander feedback utilisateur
  - Tester les endpoints principaux
  - Vérifier les cas d'usage métier
  - _Requirements: All_

## Notes

- Les tâches marquées avec `*` sont optionnelles et peuvent être sautées pour un MVP plus rapide
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les checkpoints assurent une validation incrémentale
- Les tests de propriétés valident la correction universelle
- Les tests unitaires valident des exemples spécifiques et cas limites


