"""Service for sending OTP emails"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending OTP emails"""

    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.smtp_tls = settings.SMTP_TLS

    async def send_otp_email(
        self,
        email: str,
        otp: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Envoie un email contenant le code OTP

        Args:
            email: Adresse email du destinataire
            otp: Code OTP à 6 chiffres
            user_name: Nom de l'utilisateur (optionnel)

        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon

        Raises:
            RuntimeError: Si la configuration SMTP n'est pas définie
        """
        try:
            # Vérifier la configuration SMTP
            if not self.smtp_host:
                logger.error("Configuration SMTP manquante. Impossible d'envoyer l'email.")
                raise RuntimeError("Configuration SMTP non définie")

            subject = "Code de vérification - Réinitialisation mot de passe"

            # Charger le template HTML
            html_content = self._render_otp_template(otp, user_name)
            plain_content = self._render_plain_text(otp, user_name)

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

            logger.info(f"Email OTP envoyé avec succès à {email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"Erreur SMTP lors de l'envoi de l'email à {email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email à {email}: {e}")
            return False

    def _render_otp_template(self, otp: str, user_name: Optional[str]) -> str:
        """
        Génère le contenu HTML de l'email à partir du template

        Args:
            otp: Code OTP à 6 chiffres
            user_name: Nom de l'utilisateur (optionnel)

        Returns:
            str: Contenu HTML de l'email
        """
        # Chemin vers le template
        template_path = Path(__file__).parent.parent / "templates" / "otp_email.html"

        try:
            # Lire le template
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Remplacer les variables
            # Si user_name n'est pas fourni, utiliser une salutation générique
            display_name = user_name if user_name else "Utilisateur"

            html_content = template_content.replace("{{ user_name }}", display_name)
            html_content = html_content.replace("{{ otp_code }}", otp)

            return html_content

        except FileNotFoundError:
            logger.error(f"Template d'email introuvable: {template_path}")
            # Fallback vers un template simple
            return self._render_fallback_html(otp, user_name)
        except Exception as e:
            logger.error(f"Erreur lors du rendu du template: {e}")
            return self._render_fallback_html(otp, user_name)

    def _render_plain_text(self, otp: str, user_name: Optional[str]) -> str:
        """
        Génèrela version texte brut de l'email

        Args:
            otp: Code OTP à 6 chiffres
            user_name: Nom de l'utilisateur (optionnel)

        Returns:
            str: Contenu texte brut de l'email
        """
        display_name = user_name if user_name else "Utilisateur"

        lines = [
            "RH Management System",
            "=" * 50,
            "",
            f"Bonjour {display_name},",
            "",
            "Vous avez demandé la réinitialisation de votre mot de passe.",
            "Utilisez le code de vérification ci-dessous pour continuer :",
            "",
            f"    CODE DE VÉRIFICATION : {otp}",
            "",
            "⏱️  IMPORTANT : Ce code est valide pendant 15 minutes seulement.",
            "",
            "Entrez ce code dans l'application pour vérifier votre identité",
            "et procéder à la réinitialisation de votre mot de passe.",
            "",
            "🔒 AVERTISSEMENT DE SÉCURITÉ",
            "Si vous n'avez pas demandé cette réinitialisation, veuillez",
            "ignorer cet email et contacter immédiatement votre administrateur",
            "système. Ne partagez jamais ce code avec qui que ce soit.",
            "",
            "=" * 50,
            "Cet email a été envoyé automatiquement par le système",
            "RH Management System. Merci de ne pas répondre à cet email.",
            "",
            "© 2024 RH Management System. Tous droits réservés.",
        ]

        return "\n".join(lines)

    def _render_fallback_html(self, otp: str, user_name: Optional[str]) -> str:
        """
        Génère un template HTML simple en cas d'erreur de chargement du template

        Args:
            otp: Code OTP à 6 chiffres
            user_name: Nom de l'utilisateur (optionnel)

        Returns:
            str: Contenu HTML simple
        """
        display_name = user_name if user_name else "Utilisateur"

        return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code de vérification</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #28a745;">RH Management System</h2>
   <p>Bonjour {display_name},</p>
        <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
        <p>Votre code de vérification est :</p>
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border: 2px solid #28a745; border-radius: 8px;">
            <h1 style="color: #28a745; font-size: 36px; letter-spacing: 8px; margin: 0;">{otp}</h1>
        </div>
        <p><strong>Important :</strong> Ce code est valide pendant 15 minutes seulement.</p>
        <div style="background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
            <p style="margin: 0;"><strong>🔒 Avertissement de sécurité</strong></p>
            <p style="margin: 10px 0 0 0;">Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email et contacter immédiatement votre administrateur système.</p>
        </div>
        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
        <p style="font-size: 12px; color: #6c757d; text-align: center;">
            © 2024 RH Management System. Tous droits réservés.
        </p>
    </div>
</body>
</html>
"""

