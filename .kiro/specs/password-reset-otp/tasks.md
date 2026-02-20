# Implementation Plan: Password Reset OTP

## Overview

Ce plan d'implémentation détaille les étapes pour intégrer le système de réinitialisation de mot de passe par OTP dans rhBackFast. L'implémentation suivra une approche incrémentale en commençant par les fondations (modèle, schémas) puis en construisant les services et enfin les routes API.

## Tasks

- [x] 1. Créer le modèle de données PasswordResetOTP
  - Créer le fichier `app/reset_password_app/models.py`
  - Définir la classe PasswordResetOTP avec tous les champs requis
  - Ajouter la relation avec le modèle User
  - Implémenter la méthode `is_expired()`
  - Ajouter les contraintes de table appropriées
  - _Requirements: 5.1-5.13_

- [ ]* 1.1 Écrire les tests unitaires pour le modèle PasswordResetOTP
  - Tester la création d'enregistrement
  - Tester la méthode `is_expired()`
  - Tester les valeurs par défaut
  - _Requirements: 5.1-5.13_

- [x] 2. Créer la migration Alembic pour la table password_reset_otp
  - Générer la migration avec `alembic revision --autogenerate`
  - Vérifier que tous les champs sont présents
  - Vérifier les index et contraintes
  - Tester la migration (upgrade et downgrade)
  - _Requirements: 10.1-10.5_

- [x] 3. Créer les schémas Pydantic de validation
  - Créer le fichier `app/reset_password_app/schemas.py`
  - Défin
  - Définir ResendOTPRequest et ResendOTPResponse
  - Définir ResetPasswordRequest avec validateur de mot de passe
  - Définir ResetPasswordResponse
  - _Requirements: 7.6, 4.1-4.4_

- [ ]* 3.1 Écrire les tests de propriété pour la validation des schémas
  - **Property 13: Password validation enforces minimum length**
  - **Validates: Requirements 4.2**

- [ ]* 3.2 Éc
rire les tests de propriété pour la validation des lettres
  - **Property 14: Password validation requires letters**
  - **Validates: Requirements 4.3**

- [ ]* 3.3 Écrire les tests de propriété pour la validation des chiffres
  - **Property 15: Password validation requires digits**
  - **Validates: Requirements 4.4**

- [ ]* 3.4 Écrire les tests de propriété pour la validation du format OTP
  - **Property 7: OTP format validation rejects invalid codes**
  - **Validates: Requirements 2.1**

- [x] 4. Créer le service de génération d'OTP
  - Créer le dossier `app/reset_password_app/services/`
  - Créer le fichier `otp_generation_service.py`
  - Implémenter la méthode `generate_otp()` (6 chiffres)
  - Implémenter la méthode `generate_reset_token()` (32 caractères)
  - Implémenter la méthode `calculate_expiry()` (15 minutes)
  - _Requirements: 1.3, 1.4, 1.5, 6.1_

- [ ]* 4.1 Écrire les tests de propriété pour la génération d'OTP
  - **Property 3: OTP format is always 6 digits**
  - **Validates: Requirements 1.3, 3.4**

- [ ]* 4.2 Écrire les tests de propriété pour l'unicité des tokens
  - **Property 4: Reset tokens are unique**
  - **Validates: Requirements 1.4, 3.5**

- [ ]* 4.3 Écrire les tests de propriété pour l'expiration
  - **Property 5: Expiration time is always 15 minutes**
  - **Validates: Requirements 1.5**

- [x] 5. Créer le template d'email HTML
  - Créer le dossier `app/reset_password_app/templates/`
  - Créer le fichier `otp_email.html`
  - Implémenter le template HTML avec le code OTP visible
  - Inclure le nom de l'utilisateur, durée de validité, avertissement de sécurité
  - Utiliser les couleurs et le branding de l'application
  - _Requirements: 9.1-9.7_

- [ ]* 5.1 Écrire les tests de propriété pour le template d'email
  - **Property 20: Email template contains required elements**
  - **Validates: Requirements 9.1, 9.3, 9.4, 9.5**

- [x] 6. Créer le service d'envoi d'email
  - Créer le fichier `services/email_service.py`
  - Implémenter la classe EmailService avec configuration SMTP
  - Implémenter la méthode `send_otp_email()` (HTML + texte brut)
  - Implémenter `_render_otp_template()` pour charger le template
  - Implémenter `_render_plain_text()` pour la version texte
  - Gérer les erreurs d'envoi avec logging approprié
  - _Requirements: 1.6, 6.2, 9.1-9.7_

- [ ]* 6.1 Écrire les tests unitaires pour le service d'email
  - Tester l'envoi réussi (avec mock SMTP)
  - Tester l'échec d'envoi
  - Tester le rendu du template
  - _Requirements: 1.6, 1.7_

- [x] 7. Créer le service de validation d'OTP
  - Créer le fichier `services/otp_validation_service.py`
  - Implémenter la classe OTPValidationService
  - Implémenter `find_valid_otp()` avec filtres appropriés
  - Implémenter `invalidate_user_otps()` pour marquer comme utilisés
  - Implémenter `check_recent_otp()` pour la limitation de débit
  - _Requirements: 1.2, 2.2, 3.1, 6.3_

- [ ]* 7.1 Écrire les tests de propriété pour l'invalidation des OTP
  - **Property 2: OTP invalidation clears previous attempts**
  - **Validates: Requirements 1.2, 3.3, 4.12**

- [ ]* 7.2 Écrire les tests de propriété pour la recherche d'OTP
  - **Property 8: Only non-verified and non-used OTPs are found**
  - **Validates: Requirements 2.2**

- [ ]* 7.3 Écrire les tests depropriété pour la détection d'expiration
  - **Property 9: Expiration detection is accurate**
  - **Validates: Requirements 2.4, 4.7**

- [ ]* 7.4 Écrire les tests de propriété pour la limitation de débit
  - **Property 12: Rate limiting prevents rapid requests**
  - **Validates: Requirements 3.1, 3.2**

- [x] 8. Créer le service principal de réinitialisation
  - Créer le fichier `services/password_reset_service.py`
  - Implémenter la classe PasswordResetService
  - Implémenter `request_password_reset()` (étape 1)
  - Implémenter `verify_otp()` (étape 2)
  - Implémenter `resend_otp()` (renvoi)
  - Implémenter `reset_password()` (étape 3)
  - Implémenter `_find_user_by_email()` (méthode privée)
  - Gérer toutes les exceptions avec messages appropriés
  - _Requirements: 1.1-1.8, 2.1-2.8, 3.1-3.8, 4.1-4.13, 6.4_

- [ ]* 8.1 Écrire les tests de propriété pour la validation d'email
  - **Property 1: Email validation rejects non-existent emails**
  - **Validates: Requirements 1.1**

- [ ]* 8.2 Écrire les tests de propriété pour l'appel du service d'email
  - **Property 6: Email service is called with correct parameters**
  - **Validates: Requirements 1.6, 3.6**

- [ ]* 8.3 Écrire les tests de propriété pour la vérification d'OTP
  - **Property 10: Verification marks OTP as verified**
  - **Validates: Requirements 2.6, 2.7**

- [ ]* 8.4 Écrire les tests de propriété pour le retour du token
  - **Property 11: Verification returns reset token**
  - **Validates: Requirements 2.8**

- [ ]* 8.5 Écrire les tests de propriété pour la recherche d'OTP vérifié
  - **Property 16: Password reset requires verified OTP**
  - **Validates: Requirements 4.5**

- [ ]* 8.6 Écrire les tests de propriété pour le hashage du mot de passe
  - **Property 17: Passwords are hashed before storage**
  - **Validates: Requirements 4.9**

- [ ]* 8.7 Écrire les tests de propriété pour l'atomicité de la transaction
  - **Property 18: Password update is atomic**
  - **Validates: Requirements 4.10**

- [ ]* 8.8 Écrire les tests de propriété pour le marquage d'OTP utilisé
  - **Property 19: Successful reset marks OTP as used**
  - **Validates: Requirements 4.11**

- [x] 9. Créer le fichier __init__.py des services
  - Créer `services/__init__.py`
  - Exporter tous les services (OTPGenerationService, EmailService, etc.)
  - _Requirements: 6.5_

- [x] 10. Créer les routes API FastAPI
  - Créer le fichier `app/reset_password_app/routes.py`
  - Créer le router avec préfixe `/api/password-reset`
  - Implémenter POST `/request` (demande d'OTP)
  - Implémenter POST `/verify` (vérification d'OTP)
  - Implémenter POST `/resend` (renvoi d'OTP)
  - Implémenter POST `/reset` (réinitialisation)
  - Gérer toutes les exceptions avec codes HTTP appropriés
  - _Requirements: 7.1-7.7, 8.1-8.7_

- [ ]* 10.1 Écrire les tests d'intégration pour les routes
  - Tester le flux complet (request → verify → reset)
  - Tester les cas d'erreur (OTP invalide, expiré, etc.)
  - Tester la limitation de débit (resend)
  - Tester les codes HTTP appropriés
  - _Requirements: 7.1-7.7, 8.1-8.7_

- [x] 11. Intégrer le module dans l'application principale
  - Mettre à jour `app/reset_password_app/__init__.py`
  - Importer et inclure le router dans `main.py`
  - Vérifier que les routes sont accessibles
  - _Requirements: 7.1-7.7_

- [ ] 12. Checkpoint - Vérifier que tous les tests passent
  - Exécuter tous les tests unitaires
  - Exécuter tous les tests de propriété
  - Vérifier la couverture de code (objectifs: services 90%+, routes 85%+)
  - Corriger les erreurs de syntaxe avec getDiagnostics
  - Demander à l'utilisateur si des questions se posent

- [ ] 13. Tester manuellement le flux complet
  - Configurer les variables d'environnement SMTP
  - Tester la demande d'OTP avec un vrai email
  - Vérifier la réception de l'email
  - Tester la vérification de l'OTP
  - Tester la réinitialisation du mot de passe
  - Tester le renvoi d'OTP
  - Tester les cas d'erreur (OTP expiré, invalide, etc.)
  - _Requirements: 1.1-4.13_

- [ ] 14. Documentation et finalisation
  - Ajouter des docstrings à toutes les fonctions
  - Mettre à jour le README avec les instructions de configuration SMTP
  - Documenter les endpoints API (OpenAPI/Swagger)
  - Ajouter des exemples de requêtes dans la documentation
  - _Requirements: 7.1-7.7_

## Notes

- Les tâches marquées avec `*` sont optionnelles et peuvent être ignorées pour un MVP plus rapide
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les checkpoints assurent une validation incrémentale
- Les tests de propriété valident les propriétés de correction universelles
- Les tests unitaires valident des exemples spécifiques et des cas limites
- La configuration SMTP doit être faite avant les tests manuels (tâche 13)

