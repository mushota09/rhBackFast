"""Service for sending user account emails"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from app.core.config import settings


logger = logging.getLogger(__name__)


class UserEmailService:
    """Service for sending user account creation emails"""

    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.smtp_tls = settings.SMTP_TLS

    def send_welcome_email(
        self,
        email: str,
        user_name: str,
        password: str
    ) -> bool:
        """
        Envoie un email de bienvenue avec les identifiants de connexion

        Args:
            email: Adresse email du destinataire
            user_name: Nom complet de l'utilisateur
            password: Mot de passe initial

        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        try:
            # Vérifier la configuration SMTP
            if not self.smtp_host:
                logger.warning("Configuration SMTP manquante. Email non envoyé.")
                return False

            subject = "Bienvenue - Votre compte a été créé"

            # Charger le template HTML
            html_content = self._render_welcome_template(email, user_name, password)
            plain_content = self._render_plain_text(email, user_name, password)

            # Créer le message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = email

            # Attacher les versions texte et HTML
            part1 = MIMEText(plain_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part1)
            message.attach(part2)

            # Envoyer l'email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)

            logger.info(f"Email de bienvenue envoyé avec succès à {email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"Erreur SMTP lors de l'envoi de l'email à {email}: {e}")
            return False
        except Exception as e:
            logger.error()
   # Chemin vers le template
        template_path = Path(__file__).parent / "templates" / "welcome_email.html"

        try:
            # Lire le template
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Remplacer les variables
            html_content = template_content.replace("{{ user_name }}", user_name)
            html_content = html_content.replace("{{ user_email }}", email)
            html_content = html_content.replace("{{ password }}", password)

            return html_content

        except FileNotFoundError:
            logger.error(f"Template d'email introuvable: {template_path}")
            return self._render_fallback_html(email, user_name, password)
        except Exception as e:
            logger.error(f"Erreur lors du rendu du template: {e}")
            return self._render_fallback_html(email, user_name, password)

    def _render_plain_text(
        self,
        email: str,
        user_name: str,
        password: str
    ) -> str:
        """
        Génère la version texte brut de l'email

        Args:
            email: Adresse email de l'utilisateur
            user_name: Nom complet de l'utilisateur
            password: Mot de passe initial

        Returns:
            str: Contenu texte brut de l'email
        """
        lines = [
            "RH Management System",
            "=" * 50,
            "",
            f"Bonjour {user_name},",
            "",
            "Votre compte a été créé avec succès dans le système RH Management.",
            "Vous pouvez maintenant accéder à votre espace personnel.",
            "",
            "VOS IDENTIFIANTS DE CONNEXION",
            "-" * 50,
            f"Email : {email}",
            f"Mot de passe : {password}",
            "",
            "🔒 IMPORTANT",
            "Pour votre sécurité, nous vous recommandons fortement de changer",
            "votre mot de passe lors de votre première connexion.",
            "",
            "Si vous avez des questions ou besoin d'assistance, n'hésitez pas",
            "à contacter votre administrateur système.",
            "",
            "=" * 50,
            "Cet email a été envoyé automatiquement par le système",
            "RH Management System.",
            "",
            "© 2024 RH Management System. Tous droits réservés.",
        ]

        return "\n".join(lines)

    def _render_fallback_html(
        self,
        email: str,
        user_name: str,
        password: str
    ) -> str:
        """
        Génère un template HTML simple en cas d'erreur de chargement du template

        Args:
            email: Adresse email de l'utilisateur
            user_name: Nom complet de l'utilisateur
            password: Mot de passe initial

        Returns:
            str: Contenu HTML simple
        """
        return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenue</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #F0FFFF; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; text-align: center;">🎉 Bienvenue !</h2>
        <p>Bonjour <strong>{user_name}</strong>,</p>
        <p>Votre compte a été créé avec succès dans le système RH Management.</p>

        <div style="background-color: #F0FFFF; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #667eea;">
            <h3 style="color: #667eea; margin-top: 0;">🔐 Vos identifiants de connexion</h3>
            <p><strong>Email :</strong> {email}</p>
            <p><strong>Mot de passe :</strong> <code style="background-color: #f8f9fa; padding: 5px 10px; border-radius: 4px; color: #667eea;">{password}</code></p>
        </div>

        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0;"><strong>🔒 Important :</strong> Pour votre sécurité, nous vous recommandons fortement de changer votre mot de passe lors de votre première connexion.</p>
        </div>

        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
        <p style="font-size: 12px; color: #6c757d; text-align: center;">
            © 2024 RH Management System. Tous droits réservés.
        </p>
    </div>
</body>
</html>
"""
