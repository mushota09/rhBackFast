# Requirements Document - Gestion des Congés Professionnelle

## Introduction

Ce document définit les exigences pour un système complet de gestion des congés dans rhBackFast. Le système doit gérer les congés en demi-journées, supporter plusieurs pays avec leurs jours fériés respectifs (estimated et observed), et fournir une API REST complète avec pagination, recherche, expansion de relations et traçabilité via audit logs.

## Glossaire

- **System**: Le système de gestion des congés (conge_app) dans rhBackFast
- **API**: L'interface REST exposée par le système
- **Employe**: Un employé de l'entreprise pouvant demander des congés
- **TypeConge**: Un type de congé (congé payé, maladie, etc.)
- **DemandeConge**: Une demande de congé soumise par un employé
- **SoldeConge**: Le solde de jours de congé disponibles pour un employé
- **HistoriqueConge**: L'historique des validations/rejets d'une demande
- **Niveau_Validation**: Un niveau dans la chaîne de validation hiérarchique
- **Valideur**: Un utilisateur autorisé à valider une demande à un niveau donné
- **Chaine_Validation**: La séquence ordonnée des niveaux de validation requis
- **Demi_Journee**: Une unité de 0.5 jour (matin ou après-midi)
- **Jour_Ferie**: Un jour férié officiel d'un pays
- **Estimated_Holiday**: Date estimée d'un jour férié (avant confirmation officielle)
- **Observed_Holiday**: Date réelle observée d'un jour férié
- **Audit_Log**: Enregistrement de traçabilité des actions effectuées
- **Expand**: Paramètre permettant de charger les relations d'un objet
- **Pagination**: Mécanisme de division des résultats en pages

## Requirements

### Requirement 1: Gestion des Demi-Journées

**User Story:** En tant qu'employé, je veux pouvoir demander des congés de plusieurs jours complets OU une demi-journée isolée (matin ou après-midi), afin de mieux gérer mon temps de travail.

#### Acceptance Criteria

1. WHEN un employé crée une demande de congé pour plusieurs jours, THE System SHALL permettre de spécifier date_debut < date_fin avec debut_demi_journee = JOURNEE_COMPLETE et fin_demi_journee = JOURNEE_COMPLETE
2. WHEN un employé crée une demande de congé pour une demi-journée, THE System SHALL permettre de spécifier date_debut = date_fin avec debut_demi_journee = MATIN ou APRES_MIDI
3. WHEN une demande de congé est créée pour plusieurs jours avec debut_demi_journee ou fin_demi_journee différent de JOURNEE_COMPLETE, THE System SHALL rejeter la demande avec une erreur explicite
4. WHEN une demande de congé est créée pour une demi-journée, THE System SHALL calculer nb_jours_total = 0.5
5. WHEN une demande de congé est créée pour plusieurs jours complets, THE System SHALL calculer nb_jours_total = (date_fin - date_debut) + 1
6. WHEN le solde de congé est calculé, THE System SHALL supporter les valeurs décimales (ex: 2.5 jours)
7. THE System SHALL stocker le type de demi-journée (MATIN, APRES_MIDI, JOURNEE_COMPLETE) pour chaque demande

### Requirement 2: Gestion Multi-Pays des Jours Fériés

**User Story:** En tant qu'administrateur RH, je veux gérer les jours fériés de plusieurs pays avec leurs dates estimated et observed, afin de calculer correctement les jours ouvrables.

#### Acceptance Criteria

1. THE System SHALL utiliser une bibliothèque Python de gestion des jours fériés (holidays ou workalendar)
2. WHEN un pays est configuré, THE System SHALL charger automatiquement ses jours fériés officiels
3. THE System SHALL distinguer entre les dates "estimated" (prévues) et "observed" (réellement observées) des jours fériés
4. WHEN un jour férié tombe un weekend, THE System SHALL appliquer les règles de report selon le pays
5. WHEN le calcul des jours ouvrables est effectué, THE System SHALL exclure les jours fériés du pays de l'employé
6. THE System SHALL permettre d'ajouter des jours fériés personnalisés par pays
7. THE System SHALL stocker le code pays (ISO 3166-1 alpha-2) pour chaque employé

### Requirement 3: API REST Complète pour TypeConge

**User Story:** En tant que développeur frontend, je veux une API REST complète pour gérer les types de congés, afin de construire une interface utilisateur riche.

#### Acceptance Criteria

1. THE System SHALL exposer un endpoint GET /api/conge/types pour lister les types de congés
2. THE System SHALL exposer un endpoint POST /api/conge/types pour créer un type de congé
3. THE System SHALL exposer un endpoint GET /api/conge/types/{id} pour récupérer un type de congé
4. THE System SHALL exposer un endpoint PUT /api/conge/types/{id} pour modifier un type de congé
5. THE System SHALL exposer un endpoint DELETE /api/conge/types/{id} pour supprimer un type de congé
6. WHEN un type de congé est supprimé, THE System SHALL vérifier qu'aucune demande active n'y est liée

### Requirement 4: API REST Complète pour DemandeConge

**User Story:** En tant qu'employé, je veux pouvoir gérer mes demandes de congés via une API REST, afin d'utiliser différentes interfaces (web, mobile).

#### Acceptance Criteria

1. THE System SHALL exposer un endpoint GET /api/conge/demandes pour lister les demandes de congés
2. THE System SHALL exposer un endpoint POST /api/conge/demandes pour créer une demande de congé
3. THE System SHALL exposer un endpoint GET /api/conge/demandes/{id} pour récupérer une demande
4. THE System SHALL exposer un endpoint PUT /api/conge/demandes/{id} pour modifier une demande
5. THE System SHALL exposer un endpoint DELETE /api/conge/demandes/{id} pour annuler une demande
6. THE System SHALL exposer un endpoint POST /api/conge/demandes/{id}/approve pour approuver une demande au niveau actuel
7. THE System SHALL exposer un endpoint POST /api/conge/demandes/{id}/reject pour rejeter une demande
8. WHEN une demande est créée, THE System SHALL valider que l'employé a suffisamment de solde
9. WHEN une demande est approuvée à tous les niveaux, THE System SHALL déduire les jours du solde de l'employé
10. WHEN une demande est rejetée ou annulée, THE System SHALL restaurer les jours au solde si déjà déduits

### Requirement 5: API REST Complète pour SoldeConge

**User Story:** En tant qu'administrateur RH, je veux gérer les soldes de congés des employés via une API, afin d'automatiser les allocations annuelles.

#### Acceptance Criteria

1. THE System SHALL exposer un endpoint GET /api/conge/soldes pour lister les soldes de congés
2. THE System SHALL exposer un endpoint POST /api/conge/soldes pour créer un solde de congé
3. THE System SHALL exposer un endpoint GET /api/conge/soldes/{id} pour récupérer un solde
4. THE System SHALL exposer un endpoint PUT /api/conge/soldes/{id} pour modifier un solde
5. THE System SHALL exposer un endpoint DELETE /api/conge/soldes/{id} pour supprimer un solde
6. THE System SHALL calculer automatiquement le champ "restant" (alloue - utilise + reporte)
7. WHEN une nouvelle année commence, THE System SHALL permettre de créer les soldes pour tous les employés

### Requirement 6: API REST Complète pour HistoriqueConge

**User Story:** En tant que manager, je veux consulter l'historique des validations de congés, afin de suivre le processus d'approbation.

#### Acceptance Criteria

1. THE System SHALL exposer un endpoint GET /api/conge/historiques pour lister les historiques
2. THE System SHALL exposer un endpoint GET /api/conge/historiques/{id} pour récupérer un historique
3. WHEN une demande est approuvée ou rejetée, THE System SHALL créer automatiquement un enregistrement d'historique
4. THE System SHALL stocker l'utilisateur valideur, la date, et le commentaire dans l'historique

### Requirement 7: Pagination avec Option no_pagination

**User Story:** En tant que développeur frontend, je veux pouvoir paginer les résultats ou récupérer tous les résultats, afin d'optimiser les performances.

#### Acceptance Criteria

1. WHEN un endpoint de liste est appelé sans paramètres, THE System SHALL retourner les résultats paginés (skip=0, limit=100)
2. WHEN le paramètre no_pagination=true est fourni, THE System SHALL retourner tous les résultats sans pagination
3. WHEN les résultats sont paginés, THE System SHALL retourner les champs: results, total, skip, limit
4. WHEN les résultats ne sont pas paginés, THE System SHALL retourner les champs: results, total
5. THE System SHALL permettre de personnaliser skip et limit via les paramètres de requête

### Requirement 8: Expansion des Relations (Expand)

**User Story:** En tant que développeur frontend, je veux pouvoir charger les relations d'un objet en une seule requête, afin d'éviter les requêtes N+1.

#### Acceptance Criteria

1. WHEN le paramètre expand est fourni, THE System SHALL charger les relations spécifiées
2. THE System SHALL supporter l'expansion simple (ex: expand=employe)
3. THE System SHALL supporter l'expansion multiple (ex: expand=employe,type_conge)
4. THE System SHALL supporter l'expansion imbriquée (ex: expand=employe.poste)
5. WHEN une relation n'existe pas, THE System SHALL ignorer l'expansion sans erreur
6. THE System SHALL documenter les relations expandables pour chaque endpoint

### Requirement 9: Recherche et Filtrage

**User Story:** En tant qu'utilisateur, je veux pouvoir rechercher et filtrer les congés, afin de trouver rapidement l'information dont j'ai besoin.

#### Acceptance Criteria

1. WHEN le paramètre search est fourni sur /api/conge/demandes, THE System SHALL rechercher dans les champs: raison, statut
2. WHEN des filtres sont fournis (employe_id, type_conge_id, statut, date_debut, date_fin), THE System SHALL filtrer les résultats
3. THE System SHALL supporter le tri via le paramètre ordering (ex: ordering=-date_debut)
4. THE System SHALL supporter le tri ascendant (ordering=field) et descendant (ordering=-field)
5. WHEN plusieurs filtres sont combinés, THE System SHALL appliquer un ET logique

### Requirement 10: Traçabilité via Audit Logs

**User Story:** En tant qu'administrateur, je veux tracer toutes les actions effectuées sur les congés, afin d'assurer la conformité et la sécurité.

#### Acceptance Criteria

1. WHEN une demande de congé est créée, THE System SHALL enregistrer un audit log avec action=CREATE
2. WHEN une demande de congé est modifiée, THE System SHALL enregistrer un audit log avec action=UPDATE et les anciennes/nouvelles valeurs
3. WHEN une demande de congé est supprimée, THE System SHALL enregistrer un audit log avec action=DELETE
4. WHEN une demande est approuvée, THE System SHALL enregistrer un audit log avec action=APPROVE
5. WHEN une demande est rejetée, THE System SHALL enregistrer un audit log avec action=REJECT
6. THE System SHALL enregistrer l'utilisateur, l'IP, le user-agent, et le timestamp pour chaque action
7. THE System SHALL utiliser le service AuditService existant pour la traçabilité

### Requirement 11: Validation des Données

**User Story:** En tant que système, je veux valider toutes les données entrantes, afin de garantir l'intégrité des données.

#### Acceptance Criteria

1. WHEN une demande de congé est créée, THE System SHALL valider que date_debut <= date_fin
2. WHEN une demande de congé est créée, THE System SHALL valider que l'employé existe
3. WHEN une demande de congé est créée, THE System SHALL valider que le type de congé existe
4. WHEN une demande de congé est créée, THE System SHALL valider que le solde est suffisant
5. WHEN un solde est créé, THE System SHALL valider que l'année est valide (entre 2000 et 2100)
6. WHEN un type de congé est créé, THE System SHALL valider que le code est unique
7. IF une validation échoue, THEN THE System SHALL retourner une erreur HTTP 400 avec un message explicite

### Requirement 12: Gestion des Permissions

**User Story:** En tant qu'administrateur, je veux contrôler qui peut effectuer quelles actions sur les congés, afin de sécuriser le système.

#### Acceptance Criteria

1. THE System SHALL vérifier la permission "conge.view" pour les endpoints GET
2. THE System SHALL vérifier la permission "conge.create" pour les endpoints POST
3. THE System SHALL vérifier la permission "conge.update" pour les endpoints PUT
4. THE System SHALL vérifier la permission "conge.delete" pour les endpoints DELETE
5. THE System SHALL vérifier la permission "conge.approve" pour l'approbation des demandes
6. IF un utilisateur n'a pas la permission requise, THEN THE System SHALL retourner une erreur HTTP 403

### Requirement 13: Calcul Intelligent des Jours Ouvrables

**User Story:** En tant que système, je veux calculer automatiquement le nombre de jours ouvrables, afin d'exclure les weekends et jours fériés.

#### Acceptance Criteria

1. WHEN une demande de congé est créée, THE System SHALL calculer automatiquement nb_jours_total
2. THE System SHALL exclure les samedis et dimanches du calcul
3. THE System SHALL exclure les jours fériés du pays de l'employé
4. THE System SHALL supporter les demi-journées dans le calcul (0.5 jour)
5. WHEN le pays de l'employé change, THE System SHALL recalculer les jours ouvrables des demandes futures

### Requirement 14: Gestion des Conflits de Dates

**User Story:** En tant que système, je veux détecter les conflits de dates, afin d'éviter les demandes de congés qui se chevauchent.

#### Acceptance Criteria

1. WHEN une demande de congé est créée, THE System SHALL vérifier qu'il n'existe pas de demande approuvée qui chevauche les dates
2. IF un conflit est détecté, THEN THE System SHALL retourner une erreur HTTP 400 avec les détails du conflit
3. THE System SHALL permettre plusieurs demandes en attente pour les mêmes dates
4. WHEN une demande est approuvée, THE System SHALL rejeter automatiquement les autres demandes en conflit

### Requirement 15: Export et Reporting

**User Story:** En tant qu'administrateur RH, je veux exporter les données de congés, afin de générer des rapports.

#### Acceptance Criteria

1. THE System SHALL exposer un endpoint GET /api/conge/demandes/export pour exporter les demandes
2. THE System SHALL supporter les formats d'export: JSON, CSV, Excel
3. WHEN un export est effectué, THE System SHALL enregistrer un audit log
4. THE System SHALL permettre de filtrer les données à exporter (dates, employés, statuts)
5. THE System SHALL inclure toutes les relations expandées dans l'export

### Requirement 16: Notifications (Préparation Future)

**User Story:** En tant qu'employé, je veux être notifié des changements de statut de mes demandes, afin de rester informé.

#### Acceptance Criteria

1. THE System SHALL définir des hooks pour les événements: demande_created, demande_approved, demande_rejected
2. THE System SHALL permettre l'intégration future d'un système de notifications (email, push)
3. WHEN une demande change de statut, THE System SHALL déclencher l'événement correspondant
4. THE System SHALL stocker les préférences de notification de l'employé (pour implémentation future)

### Requirement 17: Gestion des Documents Justificatifs

**User Story:** En tant qu'employé, je veux pouvoir joindre des documents justificatifs à mes demandes, afin de fournir les preuves nécessaires.

#### Acceptance Criteria

1. THE System SHALL permettre d'attacher plusieurs documents à une demande de congé
2. THE System SHALL stocker les métadonnées des documents (nom, type, taille, date_upload)
3. THE System SHALL valider le type de fichier (PDF, JPG, PNG uniquement)
4. THE System SHALL valider la taille maximale (5 MB par fichier)
5. WHEN une demande est supprimée, THE System SHALL supprimer les documents associés

### Requirement 18: Validation Hiérarchique Multi-Niveaux

**User Story:** En tant que manager, je veux que les demandes de congés soient validées à différents niveaux hiérarchiques, afin de respecter le processus d'approbation de l'entreprise.

#### Acceptance Criteria

1. THE System SHALL définir une chaîne de validation hiérarchique pour chaque demande de congé
2. WHEN une demande de congé est créée, THE System SHALL déterminer automatiquement les valideurs requis selon la hiérarchie
3. THE System SHALL supporter plusieurs niveaux de validation (ex: Manager direct → Directeur → RH)
4. WHEN un valideur approuve une demande, THE System SHALL passer automatiquement au niveau suivant
5. WHEN un valideur rejette une demande, THE System SHALL arrêter le processus et notifier l'employé
6. THE System SHALL enregistrer chaque étape de validation dans l'historique avec: valideur, niveau, date, décision, commentaire
7. WHEN tous les niveaux ont approuvé, THE System SHALL marquer la demande comme APPROVED et déduire du solde
8. THE System SHALL permettre de configurer les niveaux de validation par type de congé ou par service
9. THE System SHALL afficher le statut actuel de validation (ex: "En attente validation niveau 2/3")
10. THE System SHALL permettre à un valideur de déléguer sa validation à un autre utilisateur

### Requirement 19: Statistiques et Tableaux de Bord

**User Story:** En tant que manager, je veux consulter des statistiques sur les congés de mon équipe, afin de mieux planifier.

#### Acceptance Criteria

1. THE System SHALL exposer un endpoint GET /api/conge/stats pour les statistiques globales
2. THE System SHALL calculer: total demandes, demandes par statut, jours moyens par employé
3. THE System SHALL permettre de filtrer les statistiques par période, service, type de congé
4. THE System SHALL calculer le taux d'utilisation des congés par employé
5. THE System SHALL identifier les employés avec des soldes négatifs ou expirant bientôt


