# utils.py
from django.core.mail import EmailMultiAlternatives
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
    """Envoie un email de manière asynchrone"""
    if recipient_list:
        EmailThread(subject, html_message, recipient_list).start()


def notifier_candidat_decision(candidature, type_decision_text, motif, base_url=None):
    """
    Notifie le candidat par email après une décision sur sa candidature
    
    Args:
        candidature: objet Candidature
        type_decision_text: texte de la décision (ex: "Accepter", "Rejeter")
        motif: motif de la décision (optionnel)
        base_url: URL de base de l'application
    
    Returns:
        tuple: (success, message)
    """
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    # Récupérer l'email du candidat depuis l'utilisateur Django
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        return False, f"Le candidat {candidat.nom} {candidat.prenom} n'a pas d'adresse email enregistrée."
    
    # URL de base par défaut (à remplacer par votre domaine)
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com"
    
    # Déterminer le type de message
    type_decision_lower = type_decision_text.lower()
    
    if "accept" in type_decision_lower or "valid" in type_decision_lower:
        sujet = f"✅ Félicitations ! Votre candidature a été acceptée - {offre.titre}"
        statut = "acceptée"
        couleur = "#27ae60"
        icone = "🎉"
        message_supp = "Nous vous félicitons ! Vous serez contacté(e) prochainement pour la suite du processus."
        bouton_texte = "📋 Voir mes candidatures"
        lien_bouton = f"{base_url}/Appl/dashboardCandidat"
    elif "refus" in type_decision_lower or "rejet" in type_decision_lower:
        sujet = f"❌ Mise à jour de votre candidature - {offre.titre}"
        statut = "refusée"
        couleur = "#e74c3c"
        icone = "😔"
        message_supp = "Nous vous remercions de votre intérêt et vous encourageons à postuler à d'autres offres."
        bouton_texte = "🔍 Voir d'autres offres"
        lien_bouton = f"{base_url}/Appl/index"
    else:
        sujet = f"📋 Mise à jour de votre candidature - {offre.titre}"
        statut = "en cours d'examen"
        couleur = "#f39c12"
        icone = "📋"
        message_supp = "Nous vous tiendrons informé(e) dès qu'une décision sera prise."
        bouton_texte = "📋 Voir ma candidature"
        lien_bouton = f"https://mahoridi.pythonanywhere.com/"
    
    # Construction du message HTML
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
                <h1>{icone} GRH ENGINEERING SARL</h1>
                <p>Suivi de votre candidature</p>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Nous vous informons que votre candidature pour l'offre <strong>"{offre.titre}"</strong> a été <strong style="color:{couleur};">{statut}</strong>.</p>
                
                <div style="text-align: center;">
                    <span class="status-badge">{icone} Décision : {type_decision_text}</span>
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
                    <a href="{lien_bouton}" class="btn">
                        {bouton_texte}
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    Cliquez sur le bouton ci-dessus pour accéder à votre espace personnel.
                </p>
            </div>
            <div class="footer">
                <p>Ce message est automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2025 GRH ENGINEERING SARL - RDC, Goma</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Envoyer l'email
    envoyer_email_async(sujet, html_message, [email_destinataire])
    return True, f"Email envoyé à {email_destinataire}"








def notifier_promotion_agent(candidature, moyenne, base_url=None, matricule=None):
    """
    Notifie le candidat qu'il a été promu Agent suite aux évaluations
    """
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        return False, f"Le candidat {candidat.nom} {candidat.prenom} n'a pas d'adresse email."
    
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com/"
    
    if not matricule:
        matricule = "À déterminer"
    
    sujet = f"🎉 Félicitations ! Vous êtes maintenant Agent chez GRH ENGINEERING"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Promotion Agent - GRH ENGINEERING</title>
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
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ padding: 30px; }}
            .score-box {{
                background: #fef9e7;
                border: 2px solid #f39c12;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .score-box .moyenne {{
                font-size: 48px;
                font-weight: 700;
                color: #f39c12;
            }}
            .matricule-box {{
                background: #e8f0fe;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                font-family: monospace;
                font-size: 18px;
                font-weight: bold;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 12px 35px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Félicitations ! 🎉</h1>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Suite à vos évaluations pour le poste <strong>"{offre.titre}"</strong>, 
                vous avez obtenu une moyenne de <strong>{moyenne:.2f}%</strong>.</p>
                
                <div class="score-box">
                    <div class="moyenne">{moyenne:.2f}%</div>
                    <p>Moyenne obtenue - Seuil requis: 70%</p>
                </div>
                
                <p style="font-size: 18px; text-align: center; font-weight: bold; color: #27ae60;">
                    🎉 Vous êtes désormais Agent chez GRH ENGINEERING SARL ! 🎉
                </p>
                
                <div class="matricule-box">
                    <strong>📋 Votre matricule :</strong> {matricule}
                </div>
                
                <p>Vous pouvez dès maintenant accéder à votre espace Agent et commencer à travailler avec nous.</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}" class="btn">
                        🚀 Accéder à mon espace Agent
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Connectez-vous avec vos identifiants habituels pour accéder à votre nouveau tableau de bord.
                </p>
            </div>
            <div class="footer">
                <p>GRH ENGINEERING SARL - RDC, Goma</p>
                <p>Bienvenue dans notre équipe !</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        plain_message = strip_tags(html_message)
        email = EmailMultiAlternatives(
            subject=sujet,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True, f"Email de promotion envoyé à {email_destinataire}"
    except Exception as e:
        return False, str(e)







# utils.py - Ajoutez cette fonction

def notifier_onem_nouvelle_offre(offre, base_url=None):
    """
    Notifie tous les utilisateurs du groupe ONEM qu'une nouvelle offre est disponible
    """
    from django.contrib.auth.models import User, Group
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com/"
    
    # Récupérer tous les utilisateurs du groupe ONEM
    try:
        groupe_onem = Group.objects.get(name='ONEM')
        utilisateurs_onem = User.objects.filter(groups=groupe_onem, is_active=True)
    except Group.DoesNotExist:
        return False, "Le groupe ONEM n'existe pas"
    
    if not utilisateurs_onem.exists():
        return False, "Aucun utilisateur dans le groupe ONEM"
    
    sujet = f"📢 Nouvelle offre d'emploi - {offre.titre}"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Nouvelle offre d'emploi - GRH ENGINEERING</title>
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
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .info-box p {{ margin: 8px 0; }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 35px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #eee;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📢 Nouvelle Offre d'Emploi</h1>
                <p>GRH ENGINEERING SARL</p>
            </div>
            <div class="content">
                <h2>Bonjour,</h2>
                
                <p>Une nouvelle offre d'emploi vient d'être publiée sur la plateforme GRH ENGINEERING.</p>
                
                <div class="info-box">
                    <p><strong>📋 Détails de l'offre :</strong></p>
                    <p>• Titre : <strong>{offre.titre}</strong></p>
                    <p>• Domaine : <strong>{offre.domaine.NomDomaine}</strong></p>
                    <p>• Date de publication : <strong>{offre.date_publication.strftime('%d/%m/%Y à %H:%M')}</strong></p>
                </div>
                
                <p>Veuillez vous connecter à votre espace ONEM pour analyser cette offre et prendre une décision.</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}" class="btn">
                        🔍 Analyser l'offre
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Cliquez sur le bouton ci-dessus pour accéder à votre tableau de bord ONEM.
                </p>
            </div>
            <div class="footer">
                <p>Cet email est automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2025 GRH ENGINEERING SARL - RDC, Goma</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Envoyer les emails à tous les utilisateurs ONEM
    emails_envoyes = 0
    erreurs = []
    
    for user in utilisateurs_onem:
        if user.email:
            try:
                plain_message = strip_tags(html_message)
                email = EmailMultiAlternatives(
                    subject=sujet,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
                emails_envoyes += 1
            except Exception as e:
                erreurs.append(f"{user.email}: {str(e)}")
    
    if emails_envoyes > 0:
        return True, f"✅ Notification envoyée à {emails_envoyes} utilisateur(s) ONEM"
    else:
        return False, f"❌ Aucun email envoyé. {', '.join(erreurs)}"



# utils.py - Ajoutez cette fonction

def notifier_onem_modification_offre(offre, ancien_titre, base_url=None):
    """
    Notifie tous les utilisateurs du groupe ONEM qu'une offre a été modifiée
    """
    from django.contrib.auth.models import User, Group
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com/"
    
    # Récupérer tous les utilisateurs du groupe ONEM
    try:
        groupe_onem = Group.objects.get(name='ONEM')
        utilisateurs_onem = User.objects.filter(groups=groupe_onem, is_active=True)
    except Group.DoesNotExist:
        return False, "Le groupe ONEM n'existe pas"
    
    if not utilisateurs_onem.exists():
        return False, "Aucun utilisateur dans le groupe ONEM"
    
    sujet = f"✏️ Offre d'emploi modifiée - {offre.titre}"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Offre modifiée - GH ENGINEERING</title>
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
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #f39c12;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .info-box p {{ margin: 8px 0; }}
            .modification-box {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 12px 35px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #eee;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✏️ Offre d'Emploi Modifiée</h1>
                <p>GH ENGINEERING SARL</p>
            </div>
            <div class="content">
                <h2>Bonjour,</h2>
                
                <p>Une offre d'emploi a été <strong>modifiée</strong> sur la plateforme GH ENGINEERING.</p>
                
                <div class="modification-box">
                    <p><strong>🔄 Changement effectué :</strong></p>
                    <p>• Ancien titre : <strong>{ancien_titre}</strong></p>
                    <p>• Nouveau titre : <strong>{offre.titre}</strong></p>
                </div>
                
                <div class="info-box">
                    <p><strong>📋 Nouveaux détails de l'offre :</strong></p>
                    <p>• Titre : <strong>{offre.titre}</strong></p>
                    <p>• Domaine : <strong>{offre.domaine.NomDomaine}</strong></p>
                    <p>• Date de modification : <strong>{offre.date_modification.strftime('%d/%m/%Y à %H:%M')}</strong></p>
                </div>
                
                <p>Veuillez vous connecter à votre espace ONEM pour analyser cette offre modifiée.</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}" class="btn">
                        🔍 Analyser l'offre modifiée
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Cliquez sur le bouton ci-dessus pour accéder à votre tableau de bord ONEM.
                </p>
            </div>
            <div class="footer">
                <p>Cet email est automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2025 GRH ENGINEERING SARL - RDC, Goma</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Envoyer les emails à tous les utilisateurs ONEM
    emails_envoyes = 0
    erreurs = []
    
    for user in utilisateurs_onem:
        if user.email:
            try:
                plain_message = strip_tags(html_message)
                email = EmailMultiAlternatives(
                    subject=sujet,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
                emails_envoyes += 1
            except Exception as e:
                erreurs.append(f"{user.email}: {str(e)}")
    
    if emails_envoyes > 0:
        return True, f"✅ Notification de modification envoyée à {emails_envoyes} utilisateur(s) ONEM"
    else:
        return False, f"❌ Aucun email envoyé. {', '.join(erreurs)}"


        # utils.py - Ajoutez cette fonction

def notifier_promotion_agent_manuel(agent, base_url=None):
    """
    Notifie le candidat qu'il a été promu Agent (ajout manuel par admin)
    """
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    
    candidat = agent.candidat
    user = candidat.user
    
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        return False, f"Le candidat {candidat.nom} {candidat.prenom} n'a pas d'adresse email."
    
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com/"
    
    sujet = f"🎉 Félicitations ! Vous êtes maintenant Agent chez GH ENGINEERING"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Promotion Agent - GH ENGINEERING</title>
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
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #f39c12;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 12px 35px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
            }}
            .matricule-box {{
                background: #e8f0fe;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                font-family: monospace;
                font-size: 18px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Félicitations ! 🎉</h1>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Nous avons le plaisir de vous informer que vous avez été promu(e) au statut d'<strong>Agent</strong> au sein de GRH ENGINEERING SARL.</p>
                
                <div class="info-box">
                    <p><strong>📋 Vos informations :</strong></p>
                    <p>• Matricule : <strong>{agent.matricule}</strong></p>
                    <p>• Date de recrutement : <strong>{agent.date_retenu.strftime('%d/%m/%Y')}</strong></p>
                    <p>• Statut : <strong>Approuvé</strong></p>
                </div>
                
                <div class="matricule-box">
                    🆔 Votre matricule : {agent.matricule}
                </div>
                
                <p>Vous pouvez dès maintenant accéder à votre espace Agent en utilisant vos identifiants habituels.</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}" class="btn">
                        🚀 Accéder à mon espace Agent
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Connectez-vous avec vos identifiants pour découvrir votre nouveau tableau de bord.
                </p>
            </div>
            <div class="footer">
                <p>GH ENGINEERING SARL - RDC, Goma</p>
                <p>Bienvenue dans notre équipe !</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        plain_message = strip_tags(html_message)
        email = EmailMultiAlternatives(
            subject=sujet,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True, f"Email de promotion envoyé à {email_destinataire}"
    except Exception as e:
        return False, str(e)


        # utils.py - Ajoutez cette fonction

def notifier_candidat_admissible(candidature, moyenne, base_url=None):
    """
    Notifie le candidat qu'il a réussi les tests et est admissible.
    VOUS POUVEZ MODIFIER LE CONTENU DE CET EMAIL SELON VOS BESOINS.
    """
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        return False, f"Le candidat {candidat.nom} {candidat.prenom} n'a pas d'adresse email."
    
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com/"
    
    # ========== VOUS POUVEZ MODIFIER LE CONTENU CI-DESSOUS ==========
    sujet = f"✅ Félicitations ! Vous êtes admissible - GRH ENGINEERING"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Résultat de votre candidature - GssH ENGINEERING</title>
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
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .score-box {{
                background: #fef9e7;
                border: 2px solid #f39c12;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .score-box .moyenne {{
                font-size: 48px;
                font-weight: 700;
                color: #27ae60;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                padding: 12px 35px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Félicitations ! 🎉</h1>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Suite à vos évaluations pour le poste <strong>"{offre.titre}"</strong>, 
                vous avez obtenu une moyenne de <strong>{moyenne:.2f}%</strong>.</p>
                
                <div class="score-box">
                    <div class="moyenne">{moyenne:.2f}%</div>
                    <p>Votre moyenne - Seuil requis: 70%</p>
                </div>
                
                <p style="font-size: 18px; text-align: center; font-weight: bold; color: #27ae60;">
                    ✅ Vous êtes admissible pour la suite du processus !
                </p>
                
                <p>Notre équipe vous contactera prochainement pour la suite.</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}" class="btn">
                        📋 Suivre ma candidature
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Connectez-vous pour suivre l'évolution de votre dossier.
                </p>
            </div>
            <div class="footer">
                <p>GH ENGINEERING SARL - RDC, Goma</p>
            </div>
        </div>
    </body>
    </html>
    """
    # ========== FIN DE LA PARTIE MODIFIABLE ==========
    
    try:
        plain_message = strip_tags(html_message)
        email = EmailMultiAlternatives(
            subject=sujet,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True, f"Email d'admissibilité envoyé à {email_destinataire}"
    except Exception as e:
        return False, str(e)
    




    # utils.py - Ajoutez cette fonction

def notifier_candidature_envoyee(candidature, base_url=None):
    """
    Notifie le candidat que sa candidature a été bien reçue
    """
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        return False, f"Le candidat {candidat.nom} {candidat.prenom} n'a pas d'adresse email."
    
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com"
    
    sujet = f"📋 Confirmation de votre candidature - {offre.titre} - GH ENGINEERING"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Confirmation de candidature - GH ENGINEERING</title>
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
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .header h1 i {{ margin-right: 10px; }}
            .content {{ padding: 30px; }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #27ae60;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .info-box p {{ margin: 8px 0; }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                padding: 12px 35px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #eee;
            }}
            .status-badge {{
                display: inline-block;
                background: #27ae60;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-check-circle"></i> GH ENGINEERING SARL</h1>
                <p>Confirmation de votre candidature</p>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Nous vous remercions pour l'intérêt que vous portez à notre entreprise.</p>
                
                <div class="info-box">
                    <p><strong>📋 Détails de votre candidature :</strong></p>
                    <p>• Offre : <strong>{offre.titre}</strong></p>
                    <p>• Domaine : <strong>{offre.domaine.NomDomaine}</strong></p>
                    <p>• Date de soumission : <strong>{candidature.date_soumission.strftime('%d/%m/%Y à %H:%M')}</strong></p>
                    <p>• Statut : <span class="status-badge">En cours d'analyse</span></p>
                </div>
                
                <p>Votre candidature a été <strong>enregistrée avec succès</strong> dans notre système. Nous vous contacterons dès qu'une décision sera prise concernant votre dossier.</p>
                
                <p>Notre équipe RH examine actuellement l'ensemble des candidatures reçues pour cette offre. Vous recevrez une notification par email dès qu'une mise à jour sera disponible.</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}" class="btn">
                        📊 Suivre ma candidature
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    Cliquez sur le bouton ci-dessus pour accéder à votre espace personnel et suivre l'évolution de votre candidature.
                </p>
            </div>
            <div class="footer">
                <p>Cet email est automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2026 GH ENGINEERING SARL - RDC, Goma</p>
                <p><small>Pour toute information, contactez-nous au +243 835 137 057</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        plain_message = strip_tags(html_message)
        email = EmailMultiAlternatives(
            subject=sujet,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True, f"Email de confirmation envoyé à {email_destinataire}"
    except Exception as e:
        return False, str(e)
    


 # utils.py - Ajoutez ces fonctions

def notifier_resultat_interview(candidature, decision, commentaire, base_url=None, contrat_id=None):
    """Notifier le candidat du résultat de son interview"""
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        return False, "Pas d'adresse email"
    
    if decision == 'accepte':
        sujet = f"🎉 Félicitations ! Vous êtes retenu pour le poste {offre.titre}"
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Félicitations - GRH ENGINEERING</title></head>
        <body style="font-family: Poppins, Arial, sans-serif;">
            <div style="max-width: 600px; margin: auto; background: white; border-radius: 15px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white;">🎉 Félicitations !</h1>
                </div>
                <div style="padding: 30px;">
                    <h2>Bonjour {candidat.nom} {candidat.prenom},</h2>
                    <p>Nous avons le plaisir de vous informer que votre candidature pour le poste <strong>"{offre.titre}"</strong> a été <strong style="color:#27ae60;">RETENUE</strong> après l'interview.</p>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 20px 0;">
                        <p><strong>📝 Commentaire :</strong><br>{commentaire or 'Félicitations pour votre prestation !'}</p>
                    </div>
                    <p>Veuillez vous connecter à votre espace candidat pour consulter et signer votre contrat.</p>
                    <div style="text-align: center;">
                        <a href="{base_url}/Appl/mes-contrats" style="background: #27ae60; color: white; padding: 12px 35px; text-decoration: none; border-radius: 25px;">📄 Voir mon contrat</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        sujet = f"📋 Résultat de votre candidature - {offre.titre}"
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Résultat candidature - GRH ENGINEERING</title></head>
        <body style="font-family: Poppins, Arial, sans-serif;">
            <div style="max-width: 600px; margin: auto; background: white; border-radius: 15px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white;">📋 Résultat</h1>
                </div>
                <div style="padding: 30px;">
                    <h2>Bonjour {candidat.nom} {candidat.prenom},</h2>
                    <p>Nous vous remercons pour votre participation à l'interview pour le poste <strong>"{offre.titre}"</strong>.</p>
                    <p>Après délibération, nous avons le regret de vous informer que votre candidature n'a <strong style="color:#e74c3c;">PAS ÉTÉ RETENUE</strong>.</p>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 10px; margin: 20px 0;">
                        <p><strong>📝 Motif :</strong><br>{commentaire or 'Autres profils mieux correspondants'}</p>
                    </div>
                    <p>Nous vous encourageons à postuler à d'autres offres qui pourraient correspondre à votre profil.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    envoyer_email_async(sujet, html_message, [email_destinataire])
    return True, f"Email envoyé à {email_destinataire}"


def notifier_contrat_accepte(contrat, base_url=None):
    """Notifier le candidat que son contrat a été accepté"""
    candidat = contrat.candidat
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Contrat accepté - GRH ENGINEERING</title></head>
    <body style="font-family: Poppins, Arial, sans-serif;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 15px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); padding: 30px; text-align: center;">
                <h1 style="color: white;">✅ Contrat accepté</h1>
            </div>
            <div style="padding: 30px;">
                <h2>Bonjour {candidat.nom} {candidat.prenom},</h2>
                <p>Félicitations ! Vous avez accepté le contrat pour le poste <strong>"{contrat.offre.titre}"</strong>.</p>
                <p>Vous êtes désormais <strong>Agent chez GRH ENGINEERING</strong> !</p>
                <p>Votre matricule vous a été attribué. Vous pouvez vous connecter à votre espace agent pour accéder à vos fonctionnalités.</p>
                <div style="text-align: center;">
                    <a href="{base_url}/Appl/dashboardAgent" style="background: #27ae60; color: white; padding: 12px 35px; text-decoration: none; border-radius: 25px;">🚀 Accéder à mon espace Agent</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    envoyer_email_async("✅ Contrat accepté - Bienvenue chez GRH ENGINEERING", html_message, [candidat.user.email])   







def notifier_resultat_interview(candidature, decision, observation, base_url=None):
    """
    Notifie le candidat du résultat de son interview
    """
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    
    candidat = candidature.candidat
    offre = candidature.offre
    user = candidat.user
    
    email_destinataire = user.email if user and user.email else None
    
    if not email_destinataire:
        return False, "Pas d'adresse email"
    
    if not base_url:
        base_url = "https://mahoridi.pythonanywhere.com"
    
    # Sujet commun quel que soit la décision
    sujet = f"📋 Suite de votre candidature - {offre.titre} - GRH ENGINEERING"
    
    # Message commun : Nous vous tiendrons au courant
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Suite de votre candidature - GRH ENGINEERING</title>
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
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .info-box p {{
                margin: 8px 0;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 35px;
                text-decoration: none;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #eee;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 GH ENGINEERING SARL</h1>
                <p>Service des Ressources Humaines</p>
            </div>
            <div class="content">
                <h2>Bonjour {candidat.nom} {candidat.postnom} {candidat.prenom},</h2>
                
                <p>Nous accusons bonne réception de votre participation à l'entretien pour le poste de <strong>"{offre.titre}"</strong>.</p>
                
                <div class="info-box">
                    <p><strong>📋 Récapitulatif de votre candidature :</strong></p>
                    <p>• Offre : <strong>{offre.titre}</strong></p>
                    <p>• Domaine : <strong>{offre.domaine.NomDomaine}</strong></p>
                    <p>• Date de l'entretien : <strong>{candidature.date_soumission.strftime('%d/%m/%Y') if candidature.date_soumission else 'Récemment'}</strong></p>
                </div>
                
                <p>Nous vous remercions pour le temps que vous nous avez accordé et pour l'intérêt que vous portez à notre entreprise.</p>
                
                <p style="font-size: 16px; text-align: center; padding: 15px; background: #e8f0fe; border-radius: 10px;">
                    <strong>📢 Nous vous tiendrons informé(e) de la suite dans un très bref délai.</strong>
                </p>
                
                <p>Nous revenons vers vous dès qu'une décision sera prise concernant votre candidature.</p>
                
                <div style="text-align: center;">
                    <a href="{base_url}" class="btn">
                        📊 Suivre ma candidature
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    Cliquez sur le bouton ci-dessus pour accéder à votre espace personnel.
                </p>
            </div>
            <div class="footer">
                <p>Cet email est automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2025 GRH ENGINEERING SARL - RDC, Goma</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        plain_message = strip_tags(html_message)
        email = EmailMultiAlternatives(
            subject=sujet,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True, f"Email envoyé à {email_destinataire}"
    except Exception as e:
        return False, str(e)