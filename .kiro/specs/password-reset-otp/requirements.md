# Requirements Document - Password Reset OTP

## Introduction

Ce document définit les exigences pour l'implémentation d'un système de réinitialisation de mot de passe par OTP (One-Time Password) dans l'application rhBackFast. Le système permettra aux utilisateurs de réinitialiser leur mot de passe de manière sécurisée via un code à usage unique envoyé par email.

## Glossary

- **System**: Le système de réinitialisation de mot de passe par OTP dans rhBackFast
- **User**: Un utilisateur enregistré dans la table user_management_user
- **OTP**: Code à usage unique de 6 chiffres envoyé par email
- **Reset_Token**: Jeton unique généré pour sécuriser le processus de réinitialisation
- **Email_Service**: Service d'envoi d'emails configuré dans l'application
- **Database**: Base de données PostgreSQL de l'application

## Requirements

### Requirement 1: Demande de réinitialisation de mot de passe

**User Story:** En tant qu'utilisateur ayant oublié mon mot de passe, je veux demander une réinitialisation par email, afin de recevoir un code OTP pour réinitialiser mon mot de passe.

#### Acceptance Criteria

1. WHEN un utilisateur soumet une adresse email valide, THESystem SHALL valider que l'email existe dans la base de données
2. WHEN l'email est validé, THE System SHALL invalider tous les OTP non utilisés existants pour cet utilisateur
3. WHEN les anciens OTP sont invalidés, THE System SHALL générer un nouveau code OTP de 6 chiffres
4. WHEN l'OTP est généré, THE System SHALL créer un enregistrement PasswordResetOTP avec un reset_token unique
5. WHEN l'enregistrement est créé, THE System SHALL définir une expiration de 15 minutes
6. WHEN l'OTP est enregistré, THE System SHALL envoyer un email contenant le code OTP
7. IF l'envoi d'email échoue, THEN THE System SHALL supprimer l'enregistrement OTP et retourner une erreur
8. WHEN l'email est envoyé avec succès, THE System SHALL retourner un message de confirmation

### Requirement 2: Vérification du code OTP

**User Story:** En tant qu'utilisateur ayant reçu un code OTP, je veux vérifier ce code, afin de pouvoir procéder à la réinitialisation de mon mot de passe.

#### Acceptance Criteria

1. WHEN un utilisateur soumet un email et un code OTP, THE System SHALL valider le format du code OTP (6 chiffres)
2. WHEN le format est valide, THE System SHALL rechercher un enregistrement OTP correspondant non utilisé et non vérifié
3. IF aucun enregistrement n'est trouvé, THEN THE System SHALL retourner une erreur "Code OTP invalide ou expiré"
4. WHEN un enregistrement est trouvé, THE System SHALL vérifier si l'OTP est expiré
5. IF l'OTP est expiré, THEN THE System SHALL retourner une erreur "Code OTP expiré"
6. WHEN l'OTP est valide et non expiré, THE System SHALL marquer l'enregistrement comme vérifié
7. WHEN l'enregistrement est marqué vérifié, THE System SHALL enregistrer la date de vérification
8. WHEN la vérification est complète, THE System SHALL retourner le reset_token pour l'étape suivante

### Requirement 3: Renvoi du code OTP

**User Story:** En tant qu'utilisateur n'ayant pas reçu ou ayant perdu mon code OTP, je veux demander un nouveau code, afin de pouvoir continuer le processus de réinitialisation.

#### Acceptance Criteria

1. WHEN un utilisateur demande un nouveau code OTP, THE System SHALL vérifier qu'aucun OTP n'a été créé dans la dernière minute
2. IF un OTP récent existe, THEN THE System SHALL retourner une erreur avec code HTTP 429 (Too Many Requests)
3. WHEN la limite de temps est respectée, THE System SHALL invalider tous les OTP non utilisés existants
4. WHEN les anciens OTP sont invalidés, THE System SHALL générer un nouveau code OTP
5. WHEN le nouveau code est généré, THE System SHALL créer un nouvel enregistrement PasswordResetOTP
6. WHEN l'enregistrement est créé, THE System SHALL envoyer un email avec le nouveau code
7. IF l'envoi échoue, THEN THE System SHALL supprimer l'enregistrement et retourner une erreur
8. WHEN l'email est envoyé, THE System SHALL retourner un message de confirmation

### Requirement 4: Réinitialisation du mot de passe

**User Story:** En tant qu'utilisateur ayant vérifié mon code OTP, je veux définir un nouveau mot de passe, afin de retrouver l'accès à mon compte.

#### Acceptance Criteria

1. WHEN un utilisateur soumet email, OTP, reset_token et nouveau mot de passe, THE System SHALL valider le format du mot de passe
2. WHEN le format est validé, THE System SHALL vérifier que le mot de passe contient au moins 8 caractères
3. WHEN la longueur est validée, THE System SHALL vérifier la présence d'au moins une lettre
4. WHEN la présence de lettre est validée, THE System SHALL vérifier la présence d'au moins unchiffre
5. WHEN le mot de passe est validé, THE System SHALL rechercher un enregistrement OTP vérifié et non utilisé
6. IF aucun enregistrement n'est trouvé, THEN THE System SHALL retourner une erreur "Token invalide"
7. WHEN l'enregistrement est trouvé, THE System SHALL vérifier que l'OTP n'est pas expiré
8. IF l'OTP est expiré, THEN THE System SHALL retourner une erreur "Session expirée"
9. WHEN toutes les validations passent, THE System SHALL hasher le nouveau mot de passe
10. WHEN le mot de passe est hashé, THE System SHALL mettre à jour le mot de passe de l'utilisateur dans une transaction
11. WHEN le mot de passe est mis à jour, THE System SHALL marquer l'OTP comme utilisé
12. WHEN l'OTP est marqué utilisé, THE System SHALL invalider tous les autres OTP de l'utilisateur
13. WHEN la transaction est complète, THE System SHALL retourner un message de succès

### Requirement 5: Modèle de données PasswordResetOTP

**User Story:** En tant que système, je veux stocker les informations d'OTP de manière sécurisée, afin de gérer le processus de réinitialisation.

#### Acceptance Criteria

1. THE System SHALL créer une table password_reset_otp avec les champs suivants
2. THE System SHALL définir un champ id comme clé primaire auto-incrémentée
3. THE System SHALL définir un champ user_id comme clé étrangère vers user_management_user
4. THE System SHALL définir un champ email de type string
5. THE System SHALL définir un champ otp de type string (6 caractères)
6. THE System SHALL définir un champ reset_token de type string unique
7. THE System SHALL définir un champ is_verified de type boolean (défaut: False)
8. THE System SHALL définir un champ is_used de type boolean (défaut: False)
9. THE System SHALL définir un champ created_at de type datetime avec valeur automatique
10. THE System SHALL définir un champ verified_at de type datetime nullable
11. THE System SHALL définir un champ expires_at de type datetime
12. WHENun nouvel enregistrement est créé sans reset_token, THE System SHALL générer un token unique de 32 caractères
13. WHEN un nouvel enregistrement est créé sans expires_at, THE System SHALL définir l'expiration à 15 minutes après la création

### Requirement 6: Services découpés

**User Story:** En tant que développeur, je veux organiser le code en services séparés, afin de maintenir une architecture propre et testable.

#### Acceptance Criteria

1. THE System SHALL créer un service OTPGenerationService pour la génération d'OTP
2. THE System SHALL créer un service EmailService pour l'envoi d'emails
3. THE System SHALL créer un service OTPValidationService pour la validation d'OTP
4. THE System SHALL créer un service PasswordResetService pour la réinitialisation de mot de passe
5. WHEN les services sont créés, THE System SHALL exporter tous les services depuis __init__.py
6. WHEN les services sont utilisés, THE System SHALL injecter les dépendances via le constructeur

### Requirement 7: Endpoints API

**User Story:** En tant que client API, je veux accéder aux fonctionnalités de réinitialisation via des endpoints REST, afin d'intégrer le système dans l'application frontend.

#### Acceptance Criteria

1. THE System SHALL créer un endpoint POST /api/password-reset/request pour demander un OTP
2. THE System SHALL créer un endpoint POST /api/password-reset/verify pour vérifier un OTP
3. THE System SHALL créer un endpoint POST /api/password-reset/resend pour renvoyer un OTP
4. THE System SHALL créer un endpoint POST /api/password-reset/reset pour réinitialiser le mot de passe
5. WHEN les endpoints sont créés, THE System SHALL permettre l'accès sans authentification
6. WHEN les endpoints reçoivent des requêtes, THE System SHALL valider les données avec Pydantic schemas
7. WHEN les endpoints traitent des erreurs, THE System SHALL retourner des messages d'erreur appropriés en français

### Requirement 8: Gestion des erreurs et sécurité

**User Story:** En tant qu'administrateur système, je veux que le système gère les erreurs de manière sécurisée, afin de protéger les données des utilisateurs.

#### Acceptance Criteria

1. WHEN une erreur de validation survient, THE System SHALL retourner un code HTTP 400
2. WHEN un utilisateur n'est pas trouvé, THE System SHALL retourner un message générique pour éviter l'énumération d'emails
3. WHEN un OTP est expiré, THE System SHALL retourner un code HTTP 400 avec un message clair
4. WHEN trop de tentatives sont effectuées, THE System SHALL retourner un code HTTP 429
5. WHEN une erreur serveur survient, THE System SHALL retourner un code HTTP 500 avec un message générique
6. WHEN des transactions échouent, THE System SHALL effectuer un rollback automatique
7. WHEN des logs sont générés, THE System SHALL ne jamais logger les mots de passe ou OTP en clair

### Requirement 9: Template d'email

**User Story:** En tant qu'utilisateur recevant un email d'OTP, je veux un email bien formaté et professionnel, afin de comprendre facilement les instructions.

#### Acceptance Criteria

1. THE System SHALL créer un template HTML pour l'email d'OTP
2. WHEN l'email est généré, THE System SHALL inclure le nom de l'utilisateur si disponible
3. WHEN l'email est généré, THE System SHALL afficher le code OTP de manière visible
4. WHEN l'email est généré, THE System SHALL indiquer la durée de validité (15 minutes)
5. WHEN l'email est généré, THE System SHALL inclure un avertissement de sécurité
6. WHEN l'email est généré, THESystem SHALL utiliser les couleurs et le branding de l'application
7. THE System SHALL créer une version texte brut de l'email pour compatibilité

### Requirement 10: Migration de base de données

**User Story:** En tant que développeur, je veux créer une migration Alembic, afin d'ajouter la table password_reset_otp à la base de données.

#### Acceptance Criteria

1. THE System SHALL créer une migration Alembic pour la table password_reset_otp
2. WHEN la migration est exécutée, THE System SHALL créer la table avec tous les champs requis
3. WHEN la migration est exécutée, THE System SHALL créer les index appropriés
4. WHEN la migration est exécutée, THE System SHALL créer les contraintes de clé étrangère
5. WHEN la migration est inversée, THE System SHALL supprimer la table proprement

