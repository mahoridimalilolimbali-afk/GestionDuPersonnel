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
                    <a href="https://mahoridi.pythonanywhere.com/" class="btn">
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
        <title>Offre modifiée - GRH ENGINEERING</title>
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
                <p>GRH ENGINEERING SARL</p>
            </div>
            <div class="content">
                <h2>Bonjour,</h2>
                
                <p>Une offre d'emploi a été <strong>modifiée</strong> sur la plateforme GRH ENGINEERING.</p>
                
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