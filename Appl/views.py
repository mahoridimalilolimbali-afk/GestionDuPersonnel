# views.py - Gestion du Personnel - GRH ENGINEERING SARL
# Application: Appl
# Auteur: GRH ENGINEERING

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils import timezone
from django.core.files.storage import default_storage
from datetime import datetime, date
import json
import os
import logging

from .models import (
    Domaine, OffreEmploie, DecisionOnem, Onem, Candidat, Candidature,
    TypeDecision, Decision, Test, Evaluation, Agent, TypeConge, DemandeConge,
    AnalyseDemandeConge, TypeEtatOffre, ReglageOffre, Notification,
    Message, Conversation, MessagePieceJointe
)

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: PAGES DE RENDU (TEMPLATES)
# ============================================================================

def ChargerIndex(request):
    """Page d'accueil"""
    return render(request, "Appl/index.html")

def ChargerDomaine(request):
    """Page de gestion des domaines"""
    return render(request, "Appl/Domaine.html")

def ChargerTest(request):
    """Page de gestion des tests"""
    return render(request, "Appl/Test.html")

def ChargerDashboardCandidat(request):
    """Dashboard candidat"""
    return render(request, "Appl/dashboardCandidat.html")

def ChargerDecision(request):
    """Page des décisions sur candidatures"""
    return render(request, "Appl/Decision.html")

def ChargerReglageOffre(request):
    """Page des réglages d'offres"""
    return render(request, "Appl/ReglageOffre.html")

def ChargerDashboardAdmin(request):
    """Dashboard administrateur"""
    return render(request, "Appl/dashboardAdmin.html")

def ChargerInfoPersonnel(request):
    """Page informations personnelles"""
    return render(request, "Appl/InfoPersonnel.html")

def ChargerOffreEmploi(request):
    """Page des offres d'emploi"""
    return render(request, "Appl/OffreEmploi.html")

def ChargerResultatTest(request):
    """Page des résultats de tests"""
    return render(request, "Appl/ResultatTest.html")

def ChargerDecisionOnem(request):
    """Page des décisions ONEM"""
    return render(request, "Appl/DecisionOnem.html")

def ChargerAnalyseDemandeConge(request):
    """Page d'analyse des demandes de congé"""
    return render(request, "Appl/AnalyseDemandeConge.html")

def ChargerInfoOffre(request):
    """Page informations offre"""
    return render(request, "Appl/InfoOffre.html")

def ChargerDemandeConge(request):
    """Page demande de congé"""
    return render(request, "Appl/DemandeConge.html")

def ChargerTypeDecision(request):
    """Page des types de décision"""
    return render(request, "Appl/TypeDecision.html")

def ChargerTypeConge(request):
    """Page des types de congé"""
    return render(request, "Appl/TypeConge.html")

def ChargerOnem(request):
    """Page ONEM"""
    return render(request, "Appl/Onem.html")

def ChargerListeCandidat(request):
    """Page liste des candidats"""
    return render(request, "Appl/ListeCandidat.html")

def ChargerCandidat(request):
    """Page inscription candidat"""
    return render(request, "Appl/Candidat.html")

def ChargerLogin(request):
    """Page de connexion"""
    return render(request, "Appl/login.html")

def ChargerEvaluation(request):
    """Page des évaluations"""
    return render(request, "Appl/Evaluation.html")

def ChargerTypeEtatOffre(request):
    """Page des types d'état d'offre"""
    return render(request, "Appl/TypeEtatOffre.html")

def ChargerAgent(request):
    """Page des agents"""
    return render(request, "Appl/Agents.html")

def ChargerDashboardOnem(request):
    """Dashboard ONEM"""
    return render(request, "Appl/dashboardOnem.html")

def ChargerDashboardAgent(request):
    """Dashboard Agent"""
    return render(request, "Appl/dashboardAgent.html")

def ChargerMessagerie(request):
    """Page messagerie"""
    return render(request, "Appl/Messagerie.html")


# ============================================================================
# SECTION 2: AUTHENTIFICATION
# ============================================================================

def ConnectUtilisateur(request):
    """Authentification et redirection selon le groupe utilisateur"""
    if request.method == 'POST':
        login_input = request.POST.get("txtUt")
        password = request.POST.get("txtPas")
        
        # Déterminer si c'est un email ou un nom d'utilisateur
        if '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                username = user_obj.username
            except User.DoesNotExist:
                username = login_input
        else:
            username = login_input
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if user.is_superuser:
                return redirect("/Appl/dashboardAdmin")
            if user.groups.filter(name='CANDIDAT').exists():
                return redirect("/Appl/dashboardCandidat")
            if user.groups.filter(name='ONEM').exists():
                return redirect("/Appl/dashboardOnem")
            if user.groups.filter(name='ADMIN').exists():
                return redirect("/Appl/dashboardAdmin")
            if user.groups.filter(name='AGENT').exists():
                return redirect("/Appl/dashboardAgent")
            
            return redirect("/Appl/Attrib")
        else:
            messages.error(request, "Email/Nom d'utilisateur ou mot de passe incorrect")
            return redirect("/Appl/logins")
    
    return redirect("/Appl/logins")


# ============================================================================
# SECTION 3: GESTION DES DOMAINES (CRUD)
# ============================================================================

def liste_domaines(request):
    """Affiche la page principale avec la liste des domaines"""
    try:
        domaines = Domaine.objects.all().order_by('id')
        logger.info(f"Nombre de domaines trouvés: {domaines.count()}")
        
        paginator = Paginator(domaines, 10)
        page = request.GET.get('page', 1)
        
        try:
            domaines_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            domaines_page = paginator.page(1)
        
        return render(request, 'Domaine.html', {
            'domaines': domaines_page,
            'total_count': domaines.count()
        })
    except Exception as e:
        logger.error(f"Erreur dans liste_domaines: {str(e)}")
        return render(request, 'Domaine.html', {'domaines': [], 'error': str(e)})

@csrf_exempt
@require_http_methods(["GET"])
def get_all_domaines(request):
    """API: Récupérer tous les domaines"""
    try:
        domaines = Domaine.objects.all().order_by('id')
        data = [{'id': d.id, 'NomDomaine': d.NomDomaine, 'Description': d.Description} for d in domaines]
        return JsonResponse({'success': True, 'domaines': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_domaine(request):
    """API: Ajouter un domaine"""
    try:
        data = json.loads(request.body)
        nom = data.get('NomDomaine', '').strip()
        description = data.get('Description', '').strip()
        
        if not nom:
            return JsonResponse({'success': False, 'message': 'Le nom du domaine est requis'}, status=400)
        
        if Domaine.objects.filter(NomDomaine=nom).exists():
            return JsonResponse({'success': False, 'message': 'Ce domaine existe déjà'}, status=400)
        
        domaine = Domaine.objects.create(NomDomaine=nom, Description=description)
        
        return JsonResponse({
            'success': True,
            'message': f'Domaine "{nom}" ajouté avec succès',
            'domaine': {'id': domaine.id, 'NomDomaine': domaine.NomDomaine, 'Description': domaine.Description}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_domaine(request, id_domaine):
    """API: Modifier un domaine"""
    try:
        domaine = get_object_or_404(Domaine, id=id_domaine)
        data = json.loads(request.body)
        
        nom = data.get('NomDomaine', '').strip()
        description = data.get('Description', '').strip()
        
        if not nom:
            return JsonResponse({'success': False, 'message': 'Le nom du domaine est requis'}, status=400)
        
        if Domaine.objects.filter(NomDomaine=nom).exclude(id=id_domaine).exists():
            return JsonResponse({'success': False, 'message': 'Ce nom de domaine existe déjà'}, status=400)
        
        ancien_nom = domaine.NomDomaine
        domaine.NomDomaine = nom
        domaine.Description = description
        domaine.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Domaine "{ancien_nom}" modifié avec succès',
            'domaine': {'id': domaine.id, 'NomDomaine': domaine.NomDomaine, 'Description': domaine.Description}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_domaine(request, id_domaine):
    """API: Supprimer un domaine"""
    try:
        domaine = get_object_or_404(Domaine, id=id_domaine)
        nom = domaine.NomDomaine
        domaine.delete()
        return JsonResponse({'success': True, 'message': f'Domaine "{nom}" supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 4: GESTION DES OFFRES D'EMPLOI (CRUD)
# ============================================================================

def liste_offres(request):
    """Affiche la page principale des offres d'emploi"""
    domaines = Domaine.objects.all().order_by('NomDomaine')
    return render(request, 'OffreEmploie.html', {'domaines': domaines})

@csrf_exempt
@require_http_methods(["GET"])
def get_all_offres(request):
    """API: Récupérer toutes les offres d'emploi"""
    try:
        offres = OffreEmploie.objects.select_related('domaine').all()
        data = [{
            'id': offre.id,
            'titre': offre.titre,
            'domaine_id': offre.domaine.id,
            'domaine_nom': offre.domaine.NomDomaine,
            'offre_fichier': offre.OffreFichier.url if offre.OffreFichier else None,
            'nom_fichier': offre.filename(),
            'date_publication': offre.date_publication.strftime('%d/%m/%Y à %H:%M')
        } for offre in offres]
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_offre(request):
    """API: Ajouter une offre d'emploi"""
    try:
        titre = request.POST.get('titre', '').strip()
        domaine_id = request.POST.get('domaine_id')
        
        if not titre:
            return JsonResponse({'success': False, 'message': 'Le titre est requis'}, status=400)
        if not domaine_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner un domaine'}, status=400)
        
        domaine = get_object_or_404(Domaine, id=domaine_id)
        offre = OffreEmploie.objects.create(titre=titre, domaine=domaine)
        
        fichier = request.FILES.get('offre_fichier')
        if fichier:
            offre.OffreFichier = fichier
            offre.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Offre "{titre}" ajoutée avec succès',
            'offre': {
                'id': offre.id,
                'titre': offre.titre,
                'domaine_id': offre.domaine.id,
                'domaine_nom': offre.domaine.NomDomaine,
                'offre_fichier': offre.OffreFichier.url if offre.OffreFichier else None,
                'nom_fichier': offre.filename(),
                'date_publication': offre.date_publication.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_offre(request, id_offre):
    """API: Modifier une offre d'emploi"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        titre = request.POST.get('titre', '').strip()
        domaine_id = request.POST.get('domaine_id')
        
        if not titre:
            return JsonResponse({'success': False, 'message': 'Le titre est requis'}, status=400)
        
        domaine = get_object_or_404(Domaine, id=domaine_id)
        
        fichier = request.FILES.get('offre_fichier')
        if fichier:
            if offre.OffreFichier and os.path.isfile(offre.OffreFichier.path):
                os.remove(offre.OffreFichier.path)
            offre.OffreFichier = fichier
        
        offre.titre = titre
        offre.domaine = domaine
        offre.save()
        
        return JsonResponse({'success': True, 'message': f'Offre "{titre}" modifiée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_offre(request, id_offre):
    """API: Supprimer une offre d'emploi"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        titre = offre.titre
        if offre.OffreFichier and os.path.isfile(offre.OffreFichier.path):
            os.remove(offre.OffreFichier.path)
        offre.delete()
        return JsonResponse({'success': True, 'message': f'Offre "{titre}" supprimée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_http_methods(["GET"])
def telecharger_fichier(request, id_offre):
    """API: Télécharger le fichier d'une offre"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        if offre.OffreFichier and os.path.exists(offre.OffreFichier.path):
            with open(offre.OffreFichier.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{offre.filename()}"'
                return response
        return JsonResponse({'success': False, 'message': 'Fichier non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 5: GESTION DES DECISIONS ONEM (CRUD)
# ============================================================================

def liste_decisions_onem(request):
    """Affiche la page principale des décisions ONEM"""
    return render(request, 'DecisionOnem.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_all_decisions_onem(request):
    """API: Récupérer toutes les décisions ONEM"""
    try:
        decisions = DecisionOnem.objects.all().order_by('-id')
        data = [{'id': d.id, 'Description': d.Description} for d in decisions]
        return JsonResponse({'success': True, 'decisions': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_decision_onem(request):
    """API: Ajouter une décision ONEM"""
    try:
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        decision = DecisionOnem.objects.create(Description=description)
        return JsonResponse({'success': True, 'message': 'Décision ajoutée avec succès', 'decision': {'id': decision.id, 'Description': decision.Description}})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_decision_onem(request, id_decision):
    """API: Modifier une décision ONEM"""
    try:
        decision = get_object_or_404(DecisionOnem, id=id_decision)
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        decision.Description = description
        decision.save()
        return JsonResponse({'success': True, 'message': 'Décision modifiée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_decision_onem(request, id_decision):
    """API: Supprimer une décision ONEM"""
    try:
        decision = get_object_or_404(DecisionOnem, id=id_decision)
        decision.delete()
        return JsonResponse({'success': True, 'message': 'Décision supprimée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 6: TRAITEMENT ONEM (VALIDATION DES OFFRES)
# ============================================================================

def page_onem(request):
    """Affiche la page principale ONEM"""
    decisions = DecisionOnem.objects.all().order_by('id')
    return render(request, 'Onem.html', {'decisions': decisions})

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_non_traitees(request):
    """API: Récupérer les offres non encore traitées"""
    try:
        offres_traitees = Onem.objects.values_list('offre_id', flat=True)
        offres = OffreEmploie.objects.exclude(id__in=offres_traitees).select_related('domaine').order_by('-date_publication')
        data = [{
            'id': offre.id,
            'titre': offre.titre,
            'domaine_nom': offre.domaine.NomDomaine,
            'date_publication': offre.date_publication.strftime('%d/%m/%Y à %H:%M'),
            'a_fichier': offre.OffreFichier is not None
        } for offre in offres]
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_traitees_onem(request):
    """API: Récupérer les offres déjà traitées"""
    try:
        traitements = Onem.objects.select_related('offre', 'offre__domaine', 'decision').all().order_by('-date_verification')
        data = [{
            'id': t.id,
            'offre_id': t.offre.id,
            'titre': t.offre.titre,
            'domaine_nom': t.offre.domaine.NomDomaine,
            'decision': t.decision.Description if t.decision else 'En attente',
            'decision_id': t.decision.id if t.decision else None,
            'observation': t.observation or '',
            'motif': t.motif or '',
            'date_verification': t.date_verification.strftime('%d/%m/%Y à %H:%M')
        } for t in traitements]
        return JsonResponse({'success': True, 'traitements': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_traitement_onem(request):
    """API: Enregistrer le traitement ONEM pour une offre"""
    try:
        data = json.loads(request.body)
        offre_id = data.get('offre_id')
        decision_id = data.get('decision_id')
        observation = data.get('observation', '').strip()
        motif = data.get('motif', '').strip()
        
        if not offre_id or not decision_id:
            return JsonResponse({'success': False, 'message': 'Offre et décision requises'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        decision = get_object_or_404(DecisionOnem, id=decision_id)
        
        if Onem.objects.filter(offre=offre).exists():
            return JsonResponse({'success': False, 'message': 'Cette offre a déjà été traitée'}, status=400)
        
        traitement = Onem.objects.create(
            offre=offre, decision=decision, observation=observation, motif=motif
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Décision "{decision.Description}" enregistrée avec succès',
            'traitement': {'id': traitement.id}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_traitement_onem(request, id_traitement):
    """API: Modifier un traitement existant"""
    try:
        traitement = get_object_or_404(Onem, id=id_traitement)
        data = json.loads(request.body)
        
        if data.get('decision_id'):
            decision = get_object_or_404(DecisionOnem, id=data.get('decision_id'))
            traitement.decision = decision
        
        traitement.observation = data.get('observation', '').strip()
        traitement.motif = data.get('motif', '').strip()
        traitement.save()
        
        return JsonResponse({'success': True, 'message': 'Traitement modifié avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 7: INSCRIPTION CANDIDAT
# ============================================================================

def inscriptionCandidat(request):
    """Page d'inscription du candidat"""
    if request.method == 'POST':
        try:
            nom = request.POST.get('nom')
            postnom = request.POST.get('postnom')
            prenom = request.POST.get('prenom')
            sexe = request.POST.get('sexe')
            nationalite = request.POST.get('nationalite')
            lieuNaissance = request.POST.get('lieuNaissance')
            ville = request.POST.get('ville')
            dateNaissance = request.POST.get('dateNaissance')
            numeroTelephone = request.POST.get('numeroTelephone')
            quartier = request.POST.get('quartier')
            avenue = request.POST.get('avenue')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            photo = request.FILES.get('photo')
            
            # Validations
            if not all([nom, postnom, prenom, sexe, nationalite, lieuNaissance, ville, dateNaissance, numeroTelephone, quartier, email, username, password]):
                messages.error(request, 'Tous les champs sont requis')
                return redirect('inscriptionCandidat')
            
            if password != confirm_password:
                messages.error(request, 'Les mots de passe ne correspondent pas')
                return redirect('inscriptionCandidat')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur existe déjà')
                return redirect('inscriptionCandidat')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Cet email est déjà utilisé')
                return redirect('inscriptionCandidat')
            
            if Candidat.objects.filter(numeroTelephone=numeroTelephone).exists():
                messages.error(request, 'Ce numéro de téléphone est déjà utilisé')
                return redirect('inscriptionCandidat')
            
            # Vérification âge (minimum 18 ans)
            birth_date = datetime.strptime(dateNaissance, '%Y-%m-%d').date()
            today = datetime.today().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                messages.error(request, 'Vous devez avoir au moins 18 ans pour vous inscrire')
                return redirect('inscriptionCandidat')
            
            # Création utilisateur
            user = User.objects.create_user(
                username=username, password=password,
                first_name=prenom, last_name=f"{nom} {postnom}", email=email
            )
            
            # Ajout au groupe CANDIDAT
            groupe_candidat, _ = Group.objects.get_or_create(name='CANDIDAT')
            user.groups.add(groupe_candidat)
            
            # Création candidat
            candidat = Candidat.objects.create(
                user=user, nom=nom, postnom=postnom, prenom=prenom,
                sexe=sexe, nationalite=nationalite, lieuNaissance=lieuNaissance,
                ville=ville, dateNaissance=dateNaissance, numeroTelephone=numeroTelephone,
                quartier=quartier, avenue=avenue or "", photo=photo
            )
            
            messages.success(request, f'Bienvenue {prenom} ! Votre compte a été créé avec succès.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
            return redirect('Appl/Candidat.html')
    
    return render(request, "Appl/Candidat.html")


# ============================================================================
# SECTION 8: DASHBOARD CANDIDAT - OFFRES ACCEPTEES
# ============================================================================

@login_required
def dashboardCandidat(request):
    """Dashboard du candidat connecté"""
    if not request.user.groups.filter(name='CANDIDAT').exists():
        messages.error(request, 'Accès non autorisé')
        return redirect('login_candidat')
    
    try:
        candidat = Candidat.objects.get(user=request.user)
    except Candidat.DoesNotExist:
        messages.error(request, 'Profil candidat introuvable')
        return redirect('completer_profil')
    
    return render(request, 'dashboardCandidat.html', {'candidat': candidat, 'user': request.user})

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_acceptees(request):
    """API: Récupérer les offres acceptées pour le candidat"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0})
        
        try:
            candidat = Candidat.objects.get(user=request.user)
        except Candidat.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0, 'offres_postulees_ids': []})
        
        offres_postulees_ids = list(Candidature.objects.filter(candidat=candidat).values_list('offre_id', flat=True))
        today = date.today()
        data = []
        
        traitements = Onem.objects.filter(decision=decision_accepter).select_related('offre', 'offre__domaine')
        
        for t in traitements:
            offre = t.offre
            afficher = True
            try:
                reglage = offre.reglage
                type_etat = reglage.type_etat.designation
                date_expiration = reglage.date_expiration
                if type_etat == 'Stopper':
                    afficher = False
                elif type_etat in ['Actif', 'Renouveler']:
                    if date_expiration and date_expiration < today:
                        afficher = False
            except ReglageOffre.DoesNotExist:
                afficher = True
            
            if afficher:
                data.append({
                    'id': offre.id,
                    'titre': offre.titre,
                    'domaine_nom': offre.domaine.NomDomaine,
                    'date_publication': offre.date_publication.strftime('%d/%m/%Y'),
                    'fichier_url': offre.OffreFichier.url if offre.OffreFichier else None,
                })
        
        return JsonResponse({'success': True, 'offres': data, 'total': len(data), 'offres_postulees_ids': offres_postulees_ids})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def postuler_candidature(request):
    """API: Envoyer une candidature pour une offre"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Veuillez vous connecter'}, status=401)
        
        if not request.user.groups.filter(name='CANDIDAT').exists():
            return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
        
        offre_id = request.POST.get('offre_id')
        cv = request.FILES.get('cv')
        
        if not offre_id or not cv:
            return JsonResponse({'success': False, 'message': 'Offre et CV requis'}, status=400)
        
        candidat = get_object_or_404(Candidat, user=request.user)
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        
        # Vérifier si l'offre est acceptée
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
            if not Onem.objects.filter(offre=offre, decision=decision_accepter).exists():
                return JsonResponse({'success': False, 'message': 'Cette offre n\'est pas disponible'}, status=400)
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Offre non disponible'}, status=400)
        
        if Candidature.objects.filter(candidat=candidat, offre=offre).exists():
            return JsonResponse({'success': False, 'message': 'Vous avez déjà postulé à cette offre'}, status=400)
        
        Candidature.objects.create(candidat=candidat, offre=offre, cv=cv)
        
        return JsonResponse({'success': True, 'message': f'Votre candidature pour "{offre.titre}" a été envoyée avec succès !'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 9: GESTION DES TESTS
# ============================================================================

def liste_tests(request):
    """Page principale des tests"""
    return render(request, 'Test.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_acceptees_tests(request):
    """API: Récupérer les offres acceptées pour les tests"""
    try:
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0})
        
        traitements = Onem.objects.filter(decision=decision_accepter).select_related('offre', 'offre__domaine')
        
        data = []
        for t in traitements:
            nb_tests = Test.objects.filter(offre=t.offre).count()
            data.append({
                'id': t.offre.id,
                'titre': t.offre.titre,
                'domaine_nom': t.offre.domaine.NomDomaine,
                'date_validation': t.date_verification.strftime('%d/%m/%Y'),
                'a_deja_test': nb_tests > 0,
                'nb_tests': nb_tests
            })
        
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_tests_by_offre(request, id_offre):
    """API: Récupérer les tests d'une offre"""
    try:
        tests = Test.objects.filter(offre_id=id_offre).order_by('-date_test')
        data = [{
            'id': t.id,
            'offre_id': t.offre.id,
            'offre_titre': t.offre.titre,
            'fichier_url': t.fichier_test.url if t.fichier_test else None,
            'nom_fichier': t.filename(),
            'date_test': t.date_test.strftime('%d/%m/%Y à %H:%M')
        } for t in tests]
        return JsonResponse({'success': True, 'tests': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_test(request):
    """API: Ajouter un test pour une offre"""
    try:
        offre_id = request.POST.get('offre_id')
        fichier_test = request.FILES.get('fichier_test')
        date_test_str = request.POST.get('date_test')
        
        if not all([offre_id, fichier_test, date_test_str]):
            return JsonResponse({'success': False, 'message': 'Tous les champs sont requis'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        
        # Vérifier que l'offre est acceptée
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
            if not Onem.objects.filter(offre=offre, decision=decision_accepter).exists():
                return JsonResponse({'success': False, 'message': 'Cette offre n\'est pas acceptée'}, status=400)
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Configuration manquante'}, status=400)
        
        date_test = datetime.strptime(date_test_str, '%Y-%m-%dT%H:%M')
        test = Test.objects.create(offre=offre, fichier_test=fichier_test, date_test=date_test)
        
        return JsonResponse({'success': True, 'message': f'Test programmé avec succès', 'test': {'id': test.id}})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_test(request, id_test):
    """API: Supprimer un test"""
    try:
        test = get_object_or_404(Test, id=id_test)
        if test.fichier_test and os.path.exists(test.fichier_test.path):
            os.remove(test.fichier_test.path)
        test.delete()
        return JsonResponse({'success': True, 'message': 'Test supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 10: GESTION DES EVALUATIONS ET CONVERSION EN AGENT
# ============================================================================

def liste_evaluations(request):
    """Page principale des évaluations"""
    return render(request, 'Evaluation.html')

# Fonction utilitaire pour changer le groupe d'un utilisateur
def changer_groupe_utilisateur(user, nouveau_groupe_nom):
    """Change le groupe d'un utilisateur Django"""
    try:
        nouveau_groupe, _ = Group.objects.get_or_create(name=nouveau_groupe_nom)
        user.groups.clear()
        user.groups.add(nouveau_groupe)
        user.is_staff = (nouveau_groupe_nom.upper() == 'AGENT')
        user.save()
        return True, f"Utilisateur ajouté au groupe {nouveau_groupe_nom}"
    except Exception as e:
        return False, str(e)

# Fonction pour vérifier et promouvoir un candidat en agent
def verifier_et_promouvoir_agent(candidature):
    """Vérifie et promeut le candidat en Agent si moyenne >= 70%"""
    offre = candidature.offre
    tous_les_tests = Test.objects.filter(offre=offre)
    nombre_tests = tous_les_tests.count()
    
    if nombre_tests == 0:
        return "Aucun test défini pour cette offre."
    
    evaluations_existantes = Evaluation.objects.filter(candidature=candidature).count()
    
    if evaluations_existantes < nombre_tests:
        restant = nombre_tests - evaluations_existantes
        return f"Encore {restant} test(s) à évaluer pour devenir agent."
    
    toutes_notes = Evaluation.objects.filter(candidature=candidature).values_list('note', flat=True)
    moyenne = sum(toutes_notes) / len(toutes_notes)
    
    if moyenne >= 70:
        user = candidature.candidat.user
        changer_groupe_utilisateur(user, 'AGENT')
        agent, created = Agent.objects.get_or_create(candidat=candidature.candidat)
        if created:
            agent.matricule = f"GRH-{user.id}-{user.date_joined.strftime('%Y%m%d')}"
        agent.statut = 'Approuvé'
        agent.save()
        return f"✅ Félicitations! Le candidat a été promu AGENT (moyenne: {moyenne:.2f}%)"
    else:
        return f"❌ Note insuffisante (moyenne: {moyenne:.2f}%). Le candidat n'est pas promu agent."

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_evaluation(request):
    """API: Enregistrer une évaluation pour une candidature"""
    try:
        data = json.loads(request.body)
        candidature_id = data.get('candidature_id')
        observation = data.get('observation', '').strip()
        note = data.get('note')
        
        if not candidature_id or note is None:
            return JsonResponse({'success': False, 'message': 'Candidature et note requises'}, status=400)
        
        try:
            note = float(note)
            if note < 0 or note > 100:
                return JsonResponse({'success': False, 'message': 'La note doit être entre 0 et 100'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Note invalide'}, status=400)
        
        candidature = get_object_or_404(Candidature, id=candidature_id)
        
        # Vérifier que la candidature a été acceptée
        try:
            type_decision_accepter = TypeDecision.objects.get(Description__icontains='Accepter')
            Decision.objects.get(candidature=candidature, type_decision=type_decision_accepter)
        except (TypeDecision.DoesNotExist, Decision.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Cette candidature n\'a pas été acceptée'}, status=400)
        
        evaluation = Evaluation.objects.create(candidature=candidature, observation=observation, note=note)
        
        # Vérifier la promotion en agent
        message_promotion = verifier_et_promouvoir_agent(candidature)
        
        return JsonResponse({
            'success': True,
            'message': f'Évaluation enregistrée avec succès. Note: {note}%',
            'evaluation': {
                'id': evaluation.id,
                'note': evaluation.note,
                'observation': evaluation.observation,
                'date_evaluation': evaluation.date_evaluation.strftime('%d/%m/%Y à %H:%M')
            },
            'promotion_message': message_promotion
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_evaluation(request, id_evaluation):
    """API: Modifier une évaluation existante"""
    try:
        evaluation = get_object_or_404(Evaluation, id=id_evaluation)
        data = json.loads(request.body)
        
        if data.get('note') is not None:
            note = float(data.get('note'))
            if note < 0 or note > 100:
                return JsonResponse({'success': False, 'message': 'La note doit être entre 0 et 100'}, status=400)
            evaluation.note = note
        
        evaluation.observation = data.get('observation', '').strip()
        evaluation.save()
        
        message_promotion = verifier_et_promouvoir_agent(evaluation.candidature)
        
        return JsonResponse({
            'success': True,
            'message': 'Évaluation modifiée avec succès',
            'evaluation': {
                'id': evaluation.id,
                'note': evaluation.note,
                'observation': evaluation.observation,
                'date_evaluation': evaluation.date_evaluation.strftime('%d/%m/%Y à %H:%M')
            },
            'promotion_message': message_promotion
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def supprimer_evaluation(request, id_evaluation):
    """API: Supprimer une évaluation"""
    try:
        evaluation = get_object_or_404(Evaluation, id=id_evaluation)
        evaluation.delete()
        return JsonResponse({'success': True, 'message': 'Évaluation supprimée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 11: LISTE DES AGENTS (API)
# ============================================================================

def api_agents(request):
    """API: Liste des agents"""
    agents = Agent.objects.select_related('candidat').all()
    data = [{
        'id': agent.id,
        'nom': agent.candidat.nom,
        'postnom': agent.candidat.postnom,
        'prenom': agent.candidat.prenom,
        'sexe': agent.candidat.sexe,
        'telephone': agent.candidat.numeroTelephone,
        'date_retenu': agent.date_retenu.strftime('%d/%m/%Y'),
        'statut': agent.statut
    } for agent in agents]
    return JsonResponse({'success': True, 'agents': data, 'total': len(data)})


# ============================================================================
# SECTION 12: ACCUEIL - OFFRES ACTIVES
# ============================================================================

def api_offres_accueil(request):
    """API: Offres actives pour la page d'accueil"""
    try:
        decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
        offres_acceptees = Onem.objects.filter(decision=decision_accepter).select_related('offre', 'offre__domaine')
        
        data = []
        today = date.today()
        
        for o in offres_acceptees:
            offre = o.offre
            try:
                reglage = offre.reglage
                type_etat = reglage.type_etat.designation
                date_expiration = reglage.date_expiration
                if type_etat in ['Actif', 'Renouveler'] and date_expiration and date_expiration < today:
                    continue
                if type_etat == 'Stopper':
                    continue
            except ReglageOffre.DoesNotExist:
                pass
            
            data.append({
                'id': offre.id,
                'titre': offre.titre,
                'domaine': offre.domaine.NomDomaine,
                'date_publication': offre.date_publication.strftime('%d/%m/%Y'),
                'fichier_url': offre.OffreFichier.url if offre.OffreFichier else None
            })
        
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# SECTION 13: ADMIN STATISTIQUES
# ============================================================================

@login_required
def admin_stats(request):
    """API: Statistiques pour l'admin"""
    try:
        stats = {
            'total_offres': OffreEmploie.objects.filter(onem__decision__Description__icontains='Accepter').count(),
            'total_candidats': Candidat.objects.count(),
            'total_candidatures': Candidature.objects.count(),
            'total_agents': Agent.objects.filter(statut='Approuvé').count(),
        }
        return JsonResponse({'success': True, **stats})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# SECTION 14: TYPE ETAT OFFRE (CRUD)
# ============================================================================

def liste_type_etat_offre(request):
    """Page des types d'état d'offre"""
    return render(request, 'TypeEtatOffre.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_all_type_etat_offre(request):
    """API: Récupérer tous les types d'état d'offre"""
    try:
        types_etat = TypeEtatOffre.objects.all().order_by('designation')
        data = [{'id': te.id, 'designation': te.designation, 'description': te.description or ''} for te in types_etat]
        return JsonResponse({'success': True, 'types_etat': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_type_etat_offre(request):
    """API: Ajouter un type d'état d'offre"""
    try:
        data = json.loads(request.body)
        designation = data.get('designation', '').strip()
        description = data.get('description', '').strip()
        
        if not designation:
            return JsonResponse({'success': False, 'message': 'La désignation est requise'}, status=400)
        
        if TypeEtatOffre.objects.filter(designation__iexact=designation).exists():
            return JsonResponse({'success': False, 'message': 'Ce type existe déjà'}, status=400)
        
        type_etat = TypeEtatOffre.objects.create(designation=designation, description=description)
        return JsonResponse({'success': True, 'message': f'Type "{designation}" ajouté'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 15: REGLAGE OFFRE (CRUD)
# ============================================================================

def liste_reglage_offre(request):
    """Page des réglages d'offres"""
    types_etat = TypeEtatOffre.objects.all().order_by('designation')
    return render(request, 'ReglageOffre.html', {'types_etat': types_etat})

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_avec_decision(request):
    """API: Récupérer les offres avec leur décision ONEM"""
    try:
        offres = OffreEmploie.objects.all().order_by('-date_publication')
        today = date.today()
        data = []
        
        for offre in offres:
            try:
                onem = Onem.objects.get(offre=offre)
                decision = onem.decision.Description if onem.decision else "Non déterminée"
                decision_id = onem.decision.id if onem.decision else None
            except Onem.DoesNotExist:
                decision = "Non traitée"
                decision_id = None
            
            try:
                reglage = offre.reglage
                date_expiration = reglage.date_expiration
                type_etat = reglage.type_etat.designation if reglage.type_etat else None
                est_expiree = date_expiration and date_expiration < today if date_expiration else False
            except ReglageOffre.DoesNotExist:
                date_expiration = None
                type_etat = None
                est_expiree = False
            
            data.append({
                'id': offre.id,
                'titre': offre.titre,
                'domaine': offre.domaine.NomDomaine,
                'decision': decision,
                'decision_id': decision_id,
                'est_acceptee': decision == "Accepter",
                'date_expiration': date_expiration.strftime('%d/%m/%Y') if date_expiration else None,
                'type_etat': type_etat,
                'est_expiree': est_expiree
            })
        
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_reglage(request):
    """API: Ajouter ou modifier un réglage d'offre"""
    try:
        data = json.loads(request.body)
        offre_id = data.get('offre_id')
        type_etat_id = data.get('type_etat_id')
        date_expiration = data.get('date_expiration')
        motif = data.get('motif', '').strip()
        
        if not offre_id or not type_etat_id:
            return JsonResponse({'success': False, 'message': 'Offre et état requis'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        type_etat = get_object_or_404(TypeEtatOffre, id=type_etat_id)
        
        reglage, _ = ReglageOffre.objects.update_or_create(
            offre=offre,
            defaults={'type_etat': type_etat, 'motif': motif}
        )
        
        if date_expiration:
            reglage.date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d').date()
            reglage.save()
        
        return JsonResponse({'success': True, 'message': 'Réglage enregistré avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 16: GESTION DES CANDIDATS (LISTE, ROLE, SUPPRESSION)
# ============================================================================

def liste_candidats(request):
    """Page liste des candidats"""
    groupes = Group.objects.all().order_by('name')
    return render(request, 'ListeCandidat.html', {'groupes': groupes})

@csrf_exempt
@require_http_methods(["GET"])
def get_all_candidats(request):
    """API: Récupérer tous les candidats"""
    try:
        candidats = Candidat.objects.select_related('user').all().order_by('-date_inscription')
        data = [{
            'id': c.id,
            'nom': c.nom,
            'postnom': c.postnom,
            'prenom': c.prenom,
            'sexe': c.sexe,
            'email': c.user.email if c.user else None,
            'numeroTelephone': c.numeroTelephone,
            'groupes': [g.name for g in c.user.groups.all()] if c.user else []
        } for c in candidats]
        return JsonResponse({'success': True, 'candidats': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def changer_role_candidat(request):
    """API: Changer le rôle d'un candidat"""
    try:
        data = json.loads(request.body)
        candidat = get_object_or_404(Candidat, id=data.get('candidat_id'))
        nouveau_groupe = get_object_or_404(Group, id=data.get('groupe_id'))
        
        if candidat.user:
            candidat.user.groups.clear()
            candidat.user.groups.add(nouveau_groupe)
        
        return JsonResponse({'success': True, 'message': f'Rôle changé en "{nouveau_groupe.name}"'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_candidat(request, id_candidat):
    """API: Supprimer un candidat"""
    try:
        candidat = get_object_or_404(Candidat, id=id_candidat)
        if candidat.user:
            candidat.user.delete()
        candidat.delete()
        return JsonResponse({'success': True, 'message': 'Candidat supprimé'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 17: VALIDATION AGENT PAR QR CODE
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def valider_agent_qrcode(request, id_agent):
    """API: Valider un agent via QR code - Affiche la carte d'agent"""
    try:
        agent = get_object_or_404(Agent, id=id_agent)
        candidat = agent.candidat
        photo_url = candidat.photo.url if candidat.photo and hasattr(candidat.photo, 'url') else None
        code_validation = f"GRH-{agent.id}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Carte d'Agent - GRH ENGINEERING</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .carte-agent {{
                    max-width: 550px;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 20px;
                    overflow: hidden;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                    color: white;
                }}
                .carte-header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px 20px;
                    text-align: center;
                }}
                .carte-header h3 {{ font-size: 16px; }}
                .carte-header small {{ font-size: 10px; opacity: 0.8; }}
                .carte-body {{ padding: 20px; display: flex; gap: 20px; flex-wrap: wrap; }}
                .carte-photo img {{
                    width: 100px; height: 100px; border-radius: 50%;
                    object-fit: cover; border: 3px solid #667eea;
                }}
                .carte-photo .no-photo {{
                    width: 100px; height: 100px; border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex; align-items: center; justify-content: center;
                    font-size: 40px; font-weight: bold;
                }}
                .carte-info {{ flex: 1; }}
                .carte-info .nom {{ font-size: 16px; font-weight: 700; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.2); }}
                .carte-info .info-row {{ margin-bottom: 6px; font-size: 11px; }}
                .carte-info .info-label {{ display: inline-block; width: 70px; opacity: 0.7; }}
                .carte-footer {{ background: rgba(0,0,0,0.3); padding: 12px 20px; display: flex; justify-content: space-between; }}
                .carte-footer .badge {{ background: #27ae60; padding: 3px 12px; border-radius: 20px; font-size: 10px; }}
                @media (max-width: 576px) {{ .carte-body {{ flex-direction: column; align-items: center; text-align: center; }} }}
            </style>
        </head>
        <body>
            <div class="carte-agent">
                <div class="carte-header">
                    <h3>🏢 GRH ENGENNERING SARL</h3>
                    <small>RDC - Goma - N°{agent.id}</small>
                </div>
                <div class="carte-body">
                    <div class="carte-photo">
                        {'<img src="' + photo_url + '">' if photo_url else '<div class="no-photo">' + (candidat.prenom[0] if candidat.prenom else 'A') + (candidat.nom[0] if candidat.nom else 'G') + '</div>'}
                    </div>
                    <div class="carte-info">
                        <div class="nom">{candidat.nom or ''} {candidat.postnom or ''} {candidat.prenom or ''}</div>
                        <div class="info-row"><span class="info-label">Sexe :</span> <span class="info-value">{candidat.sexe or ''}</span></div>
                        <div class="info-row"><span class="info-label">Tél :</span> <span class="info-value">{candidat.numeroTelephone or ''}</span></div>
                        <div class="info-row"><span class="info-label">Recruté le :</span> <span class="info-value">{agent.date_retenu.strftime('%d/%m/%Y')}</span></div>
                        <div class="info-row"><span class="info-label">Matricule :</span> <span class="info-value">{code_validation}</span></div>
                    </div>
                </div>
                <div class="carte-footer">
                    <div class="date-info"><i class="fas fa-calendar-alt"></i> Scan validé</div>
                    <div><span class="badge"><i class="fas fa-check-circle"></i> Agent actif</span></div>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"<h1>❌ Erreur: {str(e)}</h1>", status=404)


# ============================================================================
# SECTION 18: MESSAGERIE
# ============================================================================

@login_required
def page_messagerie(request):
    """Page de messagerie"""
    return render(request, 'Messagerie.html')

def get_groupes_utilisateur(user):
    """Retourne la liste des groupes d'un utilisateur"""
    return [g.name for g in user.groups.all()]

def peut_envoyer_message(expediteur, destinataire):
    """Vérifie si l'expéditeur peut envoyer un message au destinataire"""
    if expediteur.is_superuser or expediteur.groups.filter(name='ADMIN').exists():
        return True
    
    groupes_exp = get_groupes_utilisateur(expediteur)
    groupes_dest = get_groupes_utilisateur(destinataire)
    
    if 'CANDIDAT' in groupes_exp:
        return 'CANDIDAT' in groupes_dest or destinataire.is_superuser
    if 'AGENT' in groupes_exp:
        return 'AGENT' in groupes_dest or destinataire.is_superuser
    if 'ONEM' in groupes_exp:
        return 'ONEM' in groupes_dest or destinataire.is_superuser
    
    return False

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """API: Récupérer les conversations de l'utilisateur"""
    try:
        user = request.user
        messages_envoyes = Message.objects.filter(expediteur=user, date_suppression_expediteur__isnull=True).values_list('destinataire_id', flat=True)
        messages_recus = Message.objects.filter(destinataire=user, date_suppression_destinataire__isnull=True).values_list('expediteur_id', flat=True)
        participants_ids = set(list(messages_envoyes) + list(messages_recus))
        
        conversations = []
        for participant_id in participants_ids:
            participant = User.objects.get(id=participant_id)
            dernier_message = Message.objects.filter(
                Q(expediteur=user, destinataire=participant, date_suppression_expediteur__isnull=True) |
                Q(expediteur=participant, destinataire=user, date_suppression_destinataire__isnull=True)
            ).order_by('-date_envoi').first()
            
            non_lus = Message.objects.filter(expediteur=participant, destinataire=user, est_lu=False, date_suppression_destinataire__isnull=True).count()
            
            if dernier_message:
                conversations.append({
                    'participant_id': participant.id,
                    'participant_nom': participant.get_full_name() or participant.username,
                    'non_lus': non_lus
                })
        
        return JsonResponse({'success': True, 'conversations': conversations})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_messages(request, user_id):
    """API: Récupérer les messages avec un utilisateur"""
    try:
        user = request.user
        autre = get_object_or_404(User, id=user_id)
        
        messages = Message.objects.filter(
            Q(expediteur=user, destinataire=autre, date_suppression_expediteur__isnull=True) |
            Q(expediteur=autre, destinataire=user, date_suppression_destinataire__isnull=True)
        ).order_by('date_envoi')
        
        Message.objects.filter(expediteur=autre, destinataire=user, est_lu=False).update(est_lu=True, date_lu=timezone.now())
        
        data = [{
            'id': msg.id,
            'expediteur_id': msg.expediteur.id,
            'expediteur_nom': msg.expediteur.get_full_name() or msg.expediteur.username,
            'contenu': msg.contenu,
            'date_envoi': msg.date_envoi.strftime('%d/%m/%Y à %H:%M'),
            'est_moi': msg.expediteur.id == user.id
        } for msg in messages]
        
        return JsonResponse({'success': True, 'messages': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def envoyer_message(request):
    """API: Envoyer un message"""
    try:
        data = json.loads(request.body)
        destinataire = get_object_or_404(User, id=data.get('destinataire_id'))
        contenu = data.get('contenu', '').strip()
        
        if not contenu:
            return JsonResponse({'success': False, 'message': 'Message vide'}, status=400)
        
        if not peut_envoyer_message(request.user, destinataire):
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
        
        message = Message.objects.create(
            expediteur=request.user,
            destinataire=destinataire,
            contenu=contenu,
            sujet=data.get('sujet', '')
        )
        
        return JsonResponse({'success': True, 'message': 'Message envoyé', 'message_id': message.id})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
def get_non_lus_count(request):
    """API: Nombre de messages non lus"""
    try:
        count = Message.objects.filter(destinataire=request.user, est_lu=False).count()
        return JsonResponse({'success': True, 'non_lus': count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# SECTION 19: TYPES DE DECISION POUR CANDIDATURES (CRUD)
# ============================================================================

def liste_type_decisions(request):
    """Page des types de décision"""
    return render(request, 'TypeDecision.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_all_type_decisions(request):
    """API: Récupérer tous les types de décision"""
    try:
        types = TypeDecision.objects.all().order_by('-id')
        data = [{'id': t.id, 'Description': t.Description} for t in types]
        return JsonResponse({'success': True, 'type_decisions': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_type_decision(request):
    """API: Ajouter un type de décision"""
    try:
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        if not description:
            return JsonResponse({'success': False, 'message': 'Description requise'}, status=400)
        
        if TypeDecision.objects.filter(Description__iexact=description).exists():
            return JsonResponse({'success': False, 'message': 'Ce type existe déjà'}, status=400)
        
        type_decision = TypeDecision.objects.create(Description=description)
        return JsonResponse({'success': True, 'message': f'Type "{description}" ajouté'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 20: DECISIONS SUR CANDIDATURES
# ============================================================================

def liste_decisions_candidature(request):
    """Page des décisions sur candidatures"""
    types_decision = TypeDecision.objects.all().order_by('Description')
    return render(request, 'Decision.html', {'types_decision': types_decision})

@csrf_exempt
@require_http_methods(["GET"])
def get_candidatures_a_traiter(request):
    """API: Candidatures sans décision"""
    try:
        candidatures_avec_decision = Decision.objects.values_list('candidature_id', flat=True)
        candidatures = Candidature.objects.exclude(id__in=candidatures_avec_decision).select_related('candidat', 'offre', 'offre__domaine')
        
        data = [{
            'id': c.id,
            'candidat_nom': f"{c.candidat.nom} {c.candidat.postnom} {c.candidat.prenom}",
            'offre_titre': c.offre.titre,
            'offre_domaine': c.offre.domaine.NomDomaine,
            'cv_url': c.cv.url if c.cv else None,
            'date_soumission': c.date_soumission.strftime('%d/%m/%Y à %H:%M')
        } for c in candidatures]
        
        return JsonResponse({'success': True, 'candidatures': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_decision_candidature(request):
    """API: Enregistrer une décision pour une candidature"""
    try:
        data = json.loads(request.body)
        candidature = get_object_or_404(Candidature, id=data.get('candidature_id'))
        type_decision = get_object_or_404(TypeDecision, id=data.get('type_decision_id'))
        motif = data.get('motif', '')
        
        decision = Decision.objects.create(
            candidature=candidature,
            type_decision=type_decision,
            motif=motif
        )
        
        return JsonResponse({'success': True, 'message': 'Décision enregistrée', 'decision_id': decision.id})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 21: TYPES DE CONGE (CRUD)
# ============================================================================

def liste_type_conge(request):
    """Page des types de congé"""
    return render(request, 'TypeConge.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_all_type_conge(request):
    """API: Récupérer tous les types de congé"""
    try:
        types = TypeConge.objects.all().order_by('designation')
        data = [{'id': t.id, 'designation': t.designation, 'duree': t.duree, 'description': t.description or ''} for t in types]
        return JsonResponse({'success': True, 'types_conge': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_type_conge(request):
    """API: Ajouter un type de congé"""
    try:
        data = json.loads(request.body)
        designation = data.get('designation', '').strip()
        duree = data.get('duree')
        description = data.get('description', '').strip()
        
        if not designation or not duree:
            return JsonResponse({'success': False, 'message': 'Désignation et durée requises'}, status=400)
        
        type_conge = TypeConge.objects.create(designation=designation, duree=duree, description=description)
        return JsonResponse({'success': True, 'message': f'Type "{designation}" ajouté'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 22: DEMANDES DE CONGE
# ============================================================================

def liste_demandes_conge(request):
    """Page des demandes de congé"""
    types_conge = TypeConge.objects.all().order_by('designation')
    return render(request, 'DemandeConge.html', {'types_conge': types_conge})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_mes_demandes_conge(request):
    """API: Demandes de congé de l'agent connecté"""
    try:
        candidat = Candidat.objects.get(user=request.user)
        agent = Agent.objects.get(candidat=candidat)
        demandes = DemandeConge.objects.filter(agent=agent).select_related('type_conge')
        
        data = [{
            'id': d.id,
            'type_conge_designation': d.type_conge.designation,
            'motif': d.motif,
            'date_debut': d.date_debut.strftime('%d/%m/%Y'),
            'date_fin': d.date_fin.strftime('%d/%m/%Y'),
            'nombre_jours': d.nombre_jours,
            'date_demande': d.date_demande.strftime('%d/%m/%Y')
        } for d in demandes]
        
        return JsonResponse({'success': True, 'demandes': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def ajouter_demande_conge(request):
    """API: Ajouter une demande de congé"""
    try:
        data = json.loads(request.body)
        candidat = Candidat.objects.get(user=request.user)
        agent = Agent.objects.get(candidat=candidat)
        type_conge = get_object_or_404(TypeConge, id=data.get('type_conge_id'))
        
        date_debut = datetime.strptime(data.get('date_debut'), '%Y-%m-%d').date()
        date_fin = datetime.strptime(data.get('date_fin'), '%Y-%m-%d').date()
        nombre_jours = (date_fin - date_debut).days + 1
        
        if nombre_jours > type_conge.duree:
            return JsonResponse({'success': False, 'message': f'Durée maximale: {type_conge.duree} jours'}, status=400)
        
        demande = DemandeConge.objects.create(
            agent=agent,
            type_conge=type_conge,
            motif=data.get('motif', ''),
            date_debut=date_debut,
            date_fin=date_fin
        )
        
        return JsonResponse({'success': True, 'message': 'Demande envoyée'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 23: ANALYSE DES DEMANDES DE CONGE (ADMIN)
# ============================================================================

def page_analyse_demandes_conge(request):
    """Page d'analyse des demandes de congé"""
    return render(request, 'AnalyseDemandeConge.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_demandes_non_analysees(request):
    """API: Demandes de congé non encore analysées"""
    try:
        demandes_analysees = AnalyseDemandeConge.objects.values_list('demande_conge_id', flat=True)
        demandes = DemandeConge.objects.exclude(id__in=demandes_analysees).select_related('agent__candidat', 'type_conge')
        
        data = [{
            'id': d.id,
            'agent_nom': f"{d.agent.candidat.nom} {d.agent.candidat.prenom}",
            'type_conge': d.type_conge.designation,
            'motif': d.motif,
            'date_debut': d.date_debut.strftime('%d/%m/%Y'),
            'date_fin': d.date_fin.strftime('%d/%m/%Y'),
            'nombre_jours': d.nombre_jours
        } for d in demandes]
        
        return JsonResponse({'success': True, 'demandes': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_analyse_demande(request):
    """API: Enregistrer l'analyse d'une demande de congé"""
    try:
        data = json.loads(request.body)
        demande = get_object_or_404(DemandeConge, id=data.get('demande_id'))
        decision = data.get('decision')
        motif_analyse = data.get('motif_analyse', '')
        
        AnalyseDemandeConge.objects.create(
            demande_conge=demande,
            decision=decision,
            motif_analyse=motif_analyse
        )
        
        return JsonResponse({'success': True, 'message': f'Analyse enregistrée: {decision}'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# SECTION 24: INFORMATIONS UTILISATEUR CONNECTÉ
# ============================================================================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_utilisateur_infos(request):
    """API: Informations de l'utilisateur connecté"""
    try:
        user = request.user
        try:
            candidat = Candidat.objects.get(user=user)
            data = {
                'nom': candidat.nom,
                'postnom': candidat.postnom,
                'prenom': candidat.prenom,
                'email': user.email,
                'telephone': candidat.numeroTelephone,
                'sexe': candidat.sexe
            }
        except Candidat.DoesNotExist:
            data = {'email': user.email, 'username': user.username}
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# SECTION 25: NOTIFICATIONS
# ============================================================================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """API: Notifications du candidat"""
    try:
        candidat = Candidat.objects.get(user=request.user)
        notifications = Notification.objects.filter(candidat=candidat).order_by('-date_creation')
        
        data = [{
            'id': n.id,
            'titre': n.titre,
            'message': n.message,
            'est_lu': n.est_lu,
            'date': n.date_creation.strftime('%d/%m/%Y à %H:%M')
        } for n in notifications]
        
        return JsonResponse({'success': True, 'notifications': data, 'non_lues': notifications.filter(est_lu=False).count()})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)