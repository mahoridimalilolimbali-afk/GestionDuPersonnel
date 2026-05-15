# utils.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, html_message, recipient_list):
        self.subject = subject
        self.html_message = html_message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)
    
    def run(self):
        try:
            plain_message = strip_tags(self.html_message)
            email = EmailMultiAlternatives(
                subject=self.subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=self.recipient_list
            )
            email.attach_alternative(self.html_message, "text/html")
            email.send()
        except Exception as e:
            print(f"Erreur d'envoi d'email: {e}")


def envoyer_email_async(subject, html_message, recipient_list):
    if recipient_list:
        EmailThread(subject, html_message, recipient_list).start()


def notifier_candidat_decision(candidature, type_decision, motif):
    """Notifier le candidat par email après une décision sur sa candidature"""
    
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    # Récupérer l'email du candidat
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        print(f"⚠️ Pas d'email pour le candidat {candidat.nom} {candidat.prenom}")
        return False
    
    # Déterminer le type de message
    if type_decision == 'Accepter':
        sujet = f"✅ Félicitations ! Votre candidature a été acceptée - {offre.titre}"
        statut = "acceptée"
        couleur = "#27ae60"
        icone = "🎉"
        message_supp = "Nous vous félicitons ! Vous serez contacté(e) prochainement pour la suite du processus."
    elif type_decision == 'Rejeter':
        sujet = f"❌ Mise à jour de votre candidature - {offre.titre}"
        statut = "refusée"
        couleur = "#e74c3c"
        icone = "😔"
        message_supp = "Nous vous remercions de votre intérêt et vous encourageons à postuler à d'autres offres."
    else:
        sujet = f"📋 Mise à jour de votre candidature - {offre.titre}"
        statut = "en cours d'examen"
        couleur = "#f39c12"
        icone = "📋"
        message_supp = "Nous vous tiendrons informé(e) dès qu'une décision sera prise."
    
    # Construction du message HTML
    base_url = "https://votre-domaine.com"  # À remplacer par votre domaine après hébergement
    # Pour les tests locaux, utilisez : base_url = "http://127.0.0.1:8000"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{sujet}</title>
        <style>
            body {{
                font-family: 'Poppins', Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .status-badge {{
                display: inline-block;
                background: {couleur};
                color: white;
                padding: 8px 20px;
                border-radius: 30px;
                font-weight: bold;
                margin: 15px 0;
            }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid {couleur};
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .info-box p {{ margin: 8px 0; }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .btn:hover {{ opacity: 0.9; }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #eee;
            }}
            .motif {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                margin: 15px 0;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{icone} ONEM - Office National de l'Emploi</h1>
                <p>Suivi de votre candidature</p>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Nous vous informons que votre candidature pour l'offre <strong>"{offre.titre}"</strong> a été <strong style="color:{couleur};">{statut}</strong>.</p>
                
                <div style="text-align: center;">
                    <span class="status-badge">{icone} Décision : {type_decision}</span>
                </div>
                
                <div class="info-box">
                    <p><strong>📋 Détails de votre candidature :</strong></p>
                    <p>• Offre : <strong>{offre.titre}</strong></p>
                    <p>• Domaine : <strong>{offre.domaine.NomDomaine}</strong></p>
                    <p>• Date de candidature : <strong>{candidature.date_soumission.strftime('%d/%m/%Y à %H:%M')}</strong></p>
                </div>
                
                {f'<div class="motif"><strong>📝 Motif :</strong><br>{motif}</div>' if motif else ''}
                
                <p>{message_supp}</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}/dashboard-candidat/" class="btn">
                        🔍 Voir le détail de ma candidature
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    Cliquez sur le bouton ci-dessus pour accéder à votre espace personnel et suivre l'évolution de vos candidatures.
                </p>
            </div>
            <div class="footer">
                <p>Ce message est automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2024 ONEM - Office National de l'Emploi</p>
                <p><small>Si vous avez des questions, veuillez nous contacter à l'adresse : contact@onem-rdc.com</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Envoyer l'email
    envoyer_email_async(sujet, html_message, [email_destinataire])
    print(f"✅ Email envoyé à {email_destinataire} pour la candidature {offre.titre}")
    return True# utils.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, html_message, recipient_list):
        self.subject = subject
        self.html_message = html_message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)
    
    def run(self):
        try:
            plain_message = strip_tags(self.html_message)
            email = EmailMultiAlternatives(
                subject=self.subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=self.recipient_list
            )
            email.attach_alternative(self.html_message, "text/html")
            email.send()
        except Exception as e:
            print(f"Erreur d'envoi d'email: {e}")


def envoyer_email_async(subject, html_message, recipient_list):
    if recipient_list:
        EmailThread(subject, html_message, recipient_list).start()


def notifier_candidat_decision(candidature, type_decision, motif):
    """Notifier le candidat par email après une décision sur sa candidature"""
    
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    # Récupérer l'email du candidat
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        print(f"⚠️ Pas d'email pour le candidat {candidat.nom} {candidat.prenom}")
        return False
    
    # Déterminer le type de message
    if type_decision == 'Accepter':
        sujet = f"✅ Félicitations ! Votre candidature a été acceptée - {offre.titre}"
        statut = "acceptée"
        couleur = "#27ae60"
        icone = "🎉"
        message_supp = "Nous vous félicitons ! Vous serez contacté(e) prochainement pour la suite du processus."
    elif type_decision == 'Rejeter':
        sujet = f"❌ Mise à jour de votre candidature - {offre.titre}"
        statut = "refusée"
        couleur = "#e74c3c"
        icone = "😔"
        message_supp = "Nous vous remercions de votre intérêt et vous encourageons à postuler à d'autres offres."
    else:
        sujet = f"📋 Mise à jour de votre candidature - {offre.titre}"
        statut = "en cours d'examen"
        couleur = "#f39c12"
        icone = "📋"
        message_supp = "Nous vous tiendrons informé(e) dès qu'une décision sera prise."
    
    # Construction du message HTML
    base_url = "https://votre-domaine.com"  # À remplacer par votre domaine après hébergement
    # Pour les tests locaux, utilisez : base_url = "http://127.0.0.1:8000"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{sujet}</title>
        <style>
            body {{
                font-family: 'Poppins', Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .status-badge {{
                display: inline-block;
                background: {couleur};
                color: white;
                padding: 8px 20px;
                border-radius: 30px;
                font-weight: bold;
                margin: 15px 0;
            }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid {couleur};
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .info-box p {{ margin: 8px 0; }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .btn:hover {{ opacity: 0.9; }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #eee;
            }}
            .motif {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                margin: 15px 0;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{icone} ONEM - Office National de l'Emploi</h1>
                <p>Suivi de votre candidature</p>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Nous vous informons que votre candidature pour l'offre <strong>"{offre.titre}"</strong> a été <strong style="color:{couleur};">{statut}</strong>.</p>
                
                <div style="text-align: center;">
                    <span class="status-badge">{icone} Décision : {type_decision}</span>
                </div>
                
                <div class="info-box">
                    <p><strong>📋 Détails de votre candidature :</strong></p>
                    <p>• Offre : <strong>{offre.titre}</strong></p>
                    <p>• Domaine : <strong>{offre.domaine.NomDomaine}</strong></p>
                    <p>• Date de candidature : <strong>{candidature.date_soumission.strftime('%d/%m/%Y à %H:%M')}</strong></p>
                </div>
                
                {f'<div class="motif"><strong>📝 Motif :</strong><br>{motif}</div>' if motif else ''}
                
                <p>{message_supp}</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}/dashboard-candidat/" class="btn">
                        🔍 Voir le détail de ma candidature
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    Cliquez sur le bouton ci-dessus pour accéder à votre espace personnel et suivre l'évolution de vos candidatures.
                </p>
            </div>
            <div class="footer">
                <p>Ce message est automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2024 ONEM - Office National de l'Emploi</p>
                <p><small>Si vous avez des questions, veuillez nous contacter à l'adresse : contact@onem-rdc.com</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Envoyer l'email
    envoyer_email_async(sujet, html_message, [email_destinataire])
    print(f"✅ Email envoyé à {email_destinataire} pour la candidature {offre.titre}")
    return True