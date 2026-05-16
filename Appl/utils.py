# utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def envoyer_email_candidat(candidat, sujet, message_html, message_texte=None):
    """
    Envoie un email à un candidat
    """
    try:
        if not candidat.user.email:
            return False, "Le candidat n'a pas d'adresse email"
        
        if message_texte is None:
            message_texte = strip_tags(message_html)
        
        send_mail(
            sujet,
            message_texte,
            settings.DEFAULT_FROM_EMAIL,
            [candidat.user.email],
            html_message=message_html,
            fail_silently=False
        )
        logger.info(f"Email envoyé à {candidat.user.email} - Sujet: {sujet}")
        return True, "Email envoyé avec succès"
    except Exception as e:
        logger.error(f"Erreur envoi email à {candidat.user.email}: {str(e)}")
        return False, str(e)


def notifier_acceptation_candidature(candidature, base_url):
    """
    Notifie le candidat que sa candidature a été acceptée
    """
    candidat = candidature.candidat
    offre = candidature.offre
    
    sujet = f"✅ Votre candidature pour {offre.titre} a été acceptée - GRH ENGINEERING"
    
    message_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Acceptation de candidature</title>
    </head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎉 Félicitations !</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Bonjour {candidat.user.first_name} {candidat.user.last_name},</h2>
                <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                    Votre candidature pour le poste <strong style="color: #27ae60;">"{offre.titre}"</strong> 
                    a été <strong style="color: #27ae60;">ACCEPTÉE</strong>.
                </p>
                <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                    Nous avons été impressionnés par votre profil et nous souhaitons poursuivre 
                    le processus de recrutement avec vous.
                </p>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{base_url}/candidat/evaluations/{candidature.id}/" 
                       style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
                              color: white; padding: 14px 35px; text-decoration: none; 
                              border-radius: 50px; font-weight: bold; display: inline-block;">
                        📋 Passer les tests d'évaluation
                    </a>
                </div>
                <p style="color: #34495e; font-size: 14px;">
                    Veuillez cliquer sur le bouton ci-dessus pour accéder à vos tests d'évaluation.
                </p>
                <hr style="margin: 25px 0; border: none; border-top: 1px solid #ecf0f1;">
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    GRH ENGINEERING SARL - RDC, Goma<br>
                    Cet email est généré automatiquement, merci de ne pas y répondre.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return envoyer_email_candidat(candidat, sujet, message_html)


def notifier_refus_candidature(candidature, motif):
    """
    Notifie le candidat que sa candidature a été refusée
    """
    candidat = candidature.candidat
    offre = candidature.offre
    
    sujet = f"📋 Suite de votre candidature pour {offre.titre} - GRH ENGINEERING"
    
    message_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Résultat de candidature</title>
    </head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">📢 Suite de votre candidature</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Bonjour {candidat.user.first_name} {candidat.user.last_name},</h2>
                <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                    Nous vous remercions d'avoir postulé au poste <strong style="color: #e74c3c;">"{offre.titre}"</strong> 
                    au sein de GRH ENGINEERING SARL.
                </p>
                <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                    Après examen attentif de votre candidature, nous avons le regret de vous informer que 
                    <strong style="color: #e74c3c;">votre candidature n'a pas été retenue</strong> pour cette offre.
                </p>
                {f'<p style="color: #7f8c8d; font-style: italic;">Motif: {motif}</p>' if motif else ''}
                <div style="text-align: center; margin: 35px 0;">
                    <a href="https://mahoridi.pythonanywhere.com/" 
                       style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                              color: white; padding: 14px 35px; text-decoration: none; 
                              border-radius: 50px; font-weight: bold; display: inline-block;">
                        🔍 Voir nos offres
                    </a>
                </div>
                <p style="color: #34495e; font-size: 14px;">
                    Nous vous encourageons vivement à consulter régulièrement nos offres d'emploi. 
                    Votre profil pourrait parfaitement correspondre à une autre opportunité.
                </p>
                <hr style="margin: 25px 0; border: none; border-top: 1px solid #ecf0f1;">
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    GRH ENGINEERING SARL - RDC, Goma<br>
                    Cet email est généré automatiquement, merci de ne pas y répondre.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return envoyer_email_candidat(candidat, sujet, message_html)


def notifier_promotion_agent(candidature, moyenne):
    """
    Notifie le candidat qu'il est promu Agent
    """
    candidat = candidature.candidat
    offre = candidature.offre
    
    sujet = f"🎉 Félicitations ! Vous êtes maintenant Agent chez GRH ENGINEERING"
    
    message_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Promotion Agent</title>
    </head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🌟 Félicitations ! 🌟</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Bonjour {candidat.user.first_name} {candidat.user.last_name},</h2>
                <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                    Suite à vos évaluations pour le poste <strong>"{offre.titre}"</strong>, 
                    vous avez obtenu une moyenne de <strong style="color: #f39c12;">{moyenne:.2f}%</strong>.
                </p>
                <p style="color: #34495e; font-size: 18px; line-height: 1.6; text-align: center; background: #fef9e7; padding: 15px; border-radius: 10px;">
                    🎉 <strong>Vous êtes désormais Agent chez GRH ENGINEERING !</strong> 🎉
                </p>
                <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                    Vous pouvez dès maintenant accéder à votre espace Agent et commencer à travailler avec nous.
                </p>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="https://mahoridi.pythonanywhere.com" 
                       style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                              color: white; padding: 14px 35px; text-decoration: none; 
                              border-radius: 50px; font-weight: bold; display: inline-block;">
                        🚀 Accéder à mon espace Agent
                    </a>
                </div>
                <hr style="margin: 25px 0; border: none; border-top: 1px solid #ecf0f1;">
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    GRH ENGINEERING SARL - RDC, Goma<br>
                    Bienvenue dans notre équipe !
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return envoyer_email_candidat(candidat, sujet, message_html)