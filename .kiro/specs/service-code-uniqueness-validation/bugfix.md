# Bugfix Requirements Document

## Introduction

Le endpoint POST "/" pour la création de services dans `user_app/routes.py` ne vérifie pas si le code du service existe déjà avant de créer un nouveau service. Cela entraîne une erreur de contrainte de base de données au lieu d'un message d'erreur convivial pour l'utilisateur. Ce bug affecte l'expérience utilisateur et la gestion des erreurs de l'API.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a POST request is made to create a service with a code that already exists in the database THEN the system attempts to insert the duplicate code and triggers a database constraint violation error

1.2 WHEN the database constraint violation occurs THEN the system returns a generic database error instead of a user-friendly error message

### Expected Behavior (Correct)

2.1 WHEN a POST request is made to create a service with a code that already exists in the database THEN the system SHALL check for the existing code before attempting to insert and return an HTTP 400 error with the message "Ce code existe déjà"

2.2 WHEN the duplicate code check detects an existing code THEN the system SHALL not attempt to insert the record into the database

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a POST request is made to create a service with a unique code that does not exist in the database THEN the system SHALL CONTINUE TO create the service successfully and return the created service with HTTP 201 status

3.2 WHEN a POST request is made with valid service data (titre, description, is_active) THEN the system SHALL CONTINUE TO store all fields correctly in the database

3.3 WHEN authentication is required for the endpoint THEN the system SHALL CONTINUE TO enforce authentication via the get_current_user dependency
