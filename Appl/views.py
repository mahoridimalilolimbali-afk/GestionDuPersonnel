from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse,  HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
from django.core.files.storage import default_storage
from .models import Domaine, OffreEmploie, DecisionOnem, Onem, Candidat, Candidature, TypeDecision, Decision, Test, Evaluation, Agent, TypeConge, DemandeConge, Agent, TypeEtatOffre, ReglageOffre, Notification, Contrat, Interview
import os
from datetime import date
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
# views.py - Au début du fichier, avec les autres imports
from django.conf import settings  # ← AJOUTEZ CETTE LIGNE
# En haut de views.py, vous devez avoir :
from django.conf import settings  # ← TRÈS IMPORTANT
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags

# Create your views here.

# CREATION DE LIEN 

def ChargerIndex(request):
    return render (request,"Appl/index.html")
@login_required   
def ChargerInterviews(request):
    return render (request,"Appl/Interviews.html")
@login_required
def ChargerTypeDecisionOffre(request):
    return render (request, "Appl/TypeDecisionOffre.html")
@login_required
def ChargerDomaine(request):
    return render (request,"Appl/Domaine.html")
@login_required
def ChargerTest(request):
    return render (request,"Appl/Test.html")
@login_required
def ChargerDashboardCandidat(request):
    return render (request,"Appl/dashboardCandidat.html")
@login_required
def ChargerDecision(request):
    return render (request,"Appl/Decision.html")
@login_required
def ChargerReglageOffre(request):
    return render (request,"Appl/ReglageOffre.html")
@login_required
def ChargerDashboardAdmin(request):
    return render (request,"Appl/dashboardAdmin.html")
@login_required
def ChargerInfoPersonnel(request):
    return render (request,"Appl/InfoPersonnel.html")
@login_required
def ChargerOffreEmploi(request):
    return render (request,"Appl/offreEmploi.html")
@login_required
def ChargerResultatTest(request):
    return render (request,"Appl/ResultatTest.html")
@login_required
def ChargerDecisionOnem(request):
    return render (request,"Appl/DecisionOnem.html")
@login_required
def ChargerAnalyseDemandeConge(request):
    return render (request,"Appl/AnalyseDemandeConge.html")
@login_required
def ChargerInfoOffre(request):
    return render (request,"Appl/InfoOffre.html")
@login_required
def ChargerDemandeConge(request):
    return render (request,"Appl/DemandeConge.html")
@login_required
def ChargerTypeDecision(request):
    return render (request,"Appl/TypeDecision.html")
@login_required
def ChargerTypeConge(request):
    return render (request,"Appl/TypeConge.html")
@login_required
def ChargerOnem(request):
    return render (request,"Appl/Onem.html")
@login_required
def ChargerListeCandidat(request):
    return render (request,"Appl/ListeCandidat.html")

def ChargerCandidat(request):
    return render (request,"Appl/Candidat.html")

def ChargerLogin(request):
    return render (request,"Appl/login.html")
@login_required
def ChargerEvaluation(request):
    return render (request,"Appl/Evaluation.html")
@login_required
def ChargerTypeEtatOffre(request):
    return render (request,"Appl/TypeEtatOffre.html")
@login_required
def ChargerDemandeConge(request):
    return render (request,"Appl/DemandeConge.html")
@login_required
def ChargerAgent(request):
    return render (request,"Appl/Agents.html")
@login_required
def ChargerReglageOffre(request):
    return render (request,"Appl/ReglageOffre.html")
@login_required
def ChargerDashboardOnem(request):
    return render (request,"Appl/dashboardOnem.html")
@login_required
def ChargerDashboardAgent(request):
    return render (request,"Appl/dashboardAgent.html")
@login_required
def ChargerMessagerie(request):
    return render (request,"Appl/Messagerie.html")





# POUR LA CONNEXION

def ConnectUtilisateur(request):
    if request.method == 'POST':
        login_input = request.POST.get("txtUt")  # Peut être email ou nom d'utilisateur
        password = request.POST.get("txtPas")
        
        # Déterminer si c'est un email ou un nom d'utilisateur
        if '@' in login_input:
            # C'est un email, chercher l'utilisateur correspondant
            try:
                user_obj = User.objects.get(email=login_input)
                username = user_obj.username
            except User.DoesNotExist:
                username = login_input
        else:
            # C'est un nom d'utilisateur
            username = login_input
        
        # Authentifier avec le nom d'utilisateur trouvé
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Vérifier si l'utilisateur est superutilisateur
            if user.is_superuser:
                return redirect("/Appl/dashboardAdmin")
            
            # Vérifier si l'utilisateur appartient au groupe CANDIDAT
            if user.groups.filter(name='CANDIDAT').exists():
                return redirect("/Appl/dashboardCandidat")
            
            # Vérifier d'autres groupes
            if user.groups.filter(name='ONEM').exists():
                return redirect("/Appl/dashboardOnem")
            
            if user.groups.filter(name='ADMIN').exists():
                return redirect("/Appl/dashboardAdmin")
            
            if user.groups.filter(name='AGENT').exists():
                return redirect("/Appl/dashboardAgent")
            
            # Redirection par défaut
            return redirect("/Appl/Attrib")
            
        else:
            messages.error(request, "Email/Nom d'utilisateur ou mot de passe incorrect")
            return redirect("/Appl/logins")
    
    return redirect("/Appl/logins")



    # 1 ACTION POUR LE DOMAINE


logger = logging.getLogger(__name__)
@login_required
def liste_domaines(request):
    """Affiche la page principale avec la liste des domaines"""
    try:
        # Récupérer tous les domaines
        domaines = Domaine.objects.all().order_by('id')
        
        # Log pour debug
        logger.info(f"Nombre de domaines trouvés: {domaines.count()}")
        print(f"Nombre de domaines trouvés: {domaines.count()}")  # Pour voir dans la console
        
        # Pagination (optionnel)
        paginator = Paginator(domaines, 10)
        page = request.GET.get('page', 1)
        
        try:
            domaines_page = paginator.page(page)
        except PageNotAnInteger:
            domaines_page = paginator.page(1)
        except EmptyPage:
            domaines_page = paginator.page(paginator.num_pages)
        
        return render(request, 'Domaine.html', {
            'domaines': domaines_page,
            'total_count': domaines.count()
        })
    except Exception as e:
        logger.error(f"Erreur dans liste_domaines: {str(e)}")
        return render(request, 'Domaine.html', {
            'domaines': [],
            'error': str(e)
        })

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_all_domaines(request):
    """API pour récupérer tous les domaines (AJAX)"""
    try:
        domaines = Domaine.objects.all().order_by('id')
        data = [{
            'id': d.id,
            'NomDomaine': d.NomDomaine,
            'Description': d.Description
        } for d in domaines]
        
        return JsonResponse({
            'success': True,
            'domaines': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def ajouter_domaine(request):
    """Ajouter un nouveau domaine"""
    try:
        data = json.loads(request.body)
        nom = data.get('NomDomaine', '').strip()
        description = data.get('Description', '').strip()
        
        if not nom:
            return JsonResponse({'success': False, 'message': 'Le nom du domaine est requis'}, status=400)
        
        # Vérifier si le domaine existe déjà
        if Domaine.objects.filter(NomDomaine=nom).exists():
            return JsonResponse({'success': False, 'message': 'Ce domaine existe déjà'}, status=400)
        
        domaine = Domaine.objects.create(
            NomDomaine=nom,
            Description=description
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Domaine "{nom}" ajouté avec succès',
            'domaine': {
                'id': domaine.id,
                'NomDomaine': domaine.NomDomaine,
                'Description': domaine.Description
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_domaine(request, id_domaine):
    """Modifier un domaine existant"""
    try:
        domaine = get_object_or_404(Domaine, id=id_domaine)
        data = json.loads(request.body)
        
        nom = data.get('NomDomaine', '').strip()
        description = data.get('Description', '').strip()
        
        if not nom:
            return JsonResponse({'success': False, 'message': 'Le nom du domaine est requis'}, status=400)
        
        # Vérifier si le nouveau nom n'existe pas déjà (sauf pour ce domaine)
        if Domaine.objects.filter(NomDomaine=nom).exclude(id=id_domaine).exists():
            return JsonResponse({'success': False, 'message': 'Ce nom de domaine existe déjà'}, status=400)
        
        ancien_nom = domaine.NomDomaine
        domaine.NomDomaine = nom
        domaine.Description = description
        domaine.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Domaine "{ancien_nom}" modifié avec succès',
            'domaine': {
                'id': domaine.id,
                'NomDomaine': domaine.NomDomaine,
                'Description': domaine.Description
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_domaine(request, id_domaine):
    """Supprimer un domaine"""
    try:
        domaine = get_object_or_404(Domaine, id=id_domaine)
        nom = domaine.NomDomaine
        domaine.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Domaine "{nom}" supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    



    # ACTION OFFRE EMPLOI
@login_required
def liste_offres(request):
    """Affiche la page principale des offres d'emploi"""
    domaines = Domaine.objects.all().order_by('NomDomaine')
    return render(request, 'OffreEmploie.html', {'domaines': domaines})

# ==================== API DOMAINES ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_all_domaines(request):
    """API pour récupérer tous les domaines"""
    try:
        domaines = Domaine.objects.all().order_by('NomDomaine')
        data = [{
            'id': d.id,
            'NomDomaine': d.NomDomaine,
            'Description': d.Description or ''
        } for d in domaines]
        
        return JsonResponse({
            'success': True,
            'domaines': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ==================== API OFFRES ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_all_offres(request):
    """API pour récupérer toutes les offres d'emploi"""
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
        
        return JsonResponse({
            'success': True,
            'offres': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def ajouter_offre(request):
    """API: Ajouter une offre d'emploi et notifier les utilisateurs ONEM"""
    try:
        titre = request.POST.get('titre', '').strip()
        domaine_id = request.POST.get('domaine_id')
        
        if not titre:
            return JsonResponse({'success': False, 'message': 'Le titre est requis'}, status=400)
        
        if not domaine_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner un domaine'}, status=400)
        
        domaine = get_object_or_404(Domaine, id=domaine_id)
        
        # Créer l'offre
        offre = OffreEmploie.objects.create(
            titre=titre,
            domaine=domaine
        )
        
        # Gérer le fichier si présent
        fichier = request.FILES.get('offre_fichier')
        if fichier:
            offre.OffreFichier = fichier
            offre.save()
        
        # ========== NOTIFIER LES UTILISATEURS ONEM ==========
        from .utils import notifier_onem_nouvelle_offre
        base_url = "https://mahoridi.pythonanywhere.com/"  # À remplacer par votre domaine en production
        email_envoye, email_message = notifier_onem_nouvelle_offre(offre, base_url)
        # ===================================================
        
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
            },
            'email_envoye': email_envoye,
            'email_message': email_message
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




@csrf_exempt
@login_required
@require_http_methods(["POST"])
def modifier_offre(request, id_offre):
    """API: Modifier une offre d'emploi et notifier les utilisateurs ONEM"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        titre = request.POST.get('titre', '').strip()
        domaine_id = request.POST.get('domaine_id')
        
        if not titre:
            return JsonResponse({'success': False, 'message': 'Le titre est requis'}, status=400)
        
        if not domaine_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner un domaine'}, status=400)
        
        domaine = get_object_or_404(Domaine, id=domaine_id)
        
        # Sauvegarder l'ancien titre pour la notification
        ancien_titre = offre.titre
        
        # Gérer le nouveau fichier si uploadé
        fichier = request.FILES.get('offre_fichier')
        if fichier:
            # Supprimer l'ancien fichier
            if offre.OffreFichier and os.path.isfile(offre.OffreFichier.path):
                os.remove(offre.OffreFichier.path)
            offre.OffreFichier = fichier
        
        offre.titre = titre
        offre.domaine = domaine
        offre.save()
        
        # ========== NOTIFIER LES UTILISATEURS ONEM DE LA MODIFICATION ==========
        from .utils import notifier_onem_modification_offre
        base_url = "https://mahoridi.pythonanywhere.com/ss"  # À remplacer par votre domaine en production
        email_envoye, email_message = notifier_onem_modification_offre(offre, ancien_titre, base_url)
        # ======================================================================
        
        return JsonResponse({
            'success': True,
            'message': f'Offre "{titre}" modifiée avec succès',
            'offre': {
                'id': offre.id,
                'titre': offre.titre,
                'domaine_id': offre.domaine.id,
                'domaine_nom': offre.domaine.NomDomaine,
                'offre_fichier': offre.OffreFichier.url if offre.OffreFichier else None,
                'nom_fichier': offre.filename(),
                'date_publication': offre.date_publication.strftime('%d/%m/%Y à %H:%M')
            },
            'email_envoye': email_envoye,
            'email_message': email_message
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




@csrf_exempt
@login_required
@require_http_methods(["POST"])
def supprimer_offre(request, id_offre):
    """Supprimer une offre d'emploi"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        titre = offre.titre
        
        # Supprimer le fichier associé
        if offre.OffreFichier and os.path.isfile(offre.OffreFichier.path):
            os.remove(offre.OffreFichier.path)
        
        offre.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Offre "{titre}" supprimée avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_http_methods(["GET"])
def telecharger_fichier(request, id_offre):
    """Télécharger le fichier d'une offre"""
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
    

# DECISION ONEM



# ==================== PAGE PRINCIPALE ====================
@login_required
def liste_decisions(request):
    """Affiche la page principale des décisions ONEM"""
    return render(request, 'DecisionOnem.html')

# ==================== API DECISIONS ONEM ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_all_decisions(request):
    """API pour récupérer toutes les décisions ONEM"""
    try:
        decisions = DecisionOnem.objects.all().order_by('-id')
        data = [{
            'id': d.id,
            'Description': d.Description,
        } for d in decisions]
        
        return JsonResponse({
            'success': True,
            'decisions': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_decision(request):
    """Ajouter une nouvelle décision ONEM"""
    try:
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        
        decision = DecisionOnem.objects.create(Description=description)
        
        return JsonResponse({
            'success': True,
            'message': f'Décision ajoutée avec succès',
            'decision': {
                'id': decision.id,
                'Description': decision.Description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_decision(request, id_decision):
    """Modifier une décision ONEM existante"""
    try:
        decision = get_object_or_404(DecisionOnem, id=id_decision)
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        
        decision.Description = description
        decision.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Décision modifiée avec succès',
            'decision': {
                'id': decision.id,
                'Description': decision.Description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_decision(request, id_decision):
    """Supprimer une décision ONEM"""
    try:
        decision = get_object_or_404(DecisionOnem, id=id_decision)
        decision.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Décision supprimée avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Domaine, OffreEmploie, DecisionOnem, Onem
import json
import os

# ==================== PAGE ONEM ====================
@login_required
def page_onem(request):
    """Affiche la page principale ONEM avec les décisions"""
    # Récupérer TOUTES les décisions
    decisions = DecisionOnem.objects.all().order_by('id')
    
    # Debug
    print(f"=== PAGE ONEM ===")
    print(f"Nombre de décisions chargées: {decisions.count()}")
    for d in decisions:
        print(f"  - ID: {d.id}, Description: {d.Description}")
    
    return render(request, 'Onem.html', {'decisions': decisions})

# ==================== API ONEM ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_offres_a_traiter(request):
    """Récupérer les offres non encore traitées"""
    try:
        offres_traitees = Onem.objects.values_list('offre_id', flat=True)
        offres = OffreEmploie.objects.exclude(id__in=offres_traitees).select_related('domaine').order_by('-date_publication')
        
        data = [{
            'id': offre.id,
            'titre': offre.titre,
            'domaine_nom': offre.domaine.NomDomaine,
            'date_publication': offre.date_publication.strftime('%d/%m/%Y à %H:%M'),
            'a_fichier': offre.OffreFichier is not None and bool(offre.OffreFichier)
        } for offre in offres]
        
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_offres_traitees(request):
    """Récupérer les offres déjà traitées"""
    try:
        traitements = Onem.objects.select_related('offre', 'offre__domaine', 'decision').all().order_by('-date_verification')
        
        data = [{
            'id': t.id,
            'offre_id': t.offre.id,
            'titre': t.offre.titre,
            'domaine_nom': t.offre.domaine.NomDomaine,
            'decision': t.decision.Description if t.decision else 'Non spécifiée',
            'decision_id': t.decision.id if t.decision else None,
            'observation': t.observation or '',
            'motif': t.motif or '',
            'date_verification': t.date_verification.strftime('%d/%m/%Y à %H:%M')
        } for t in traitements]
        
        return JsonResponse({'success': True, 'traitements': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def ouvrir_fichier_offre(request, id_offre):
    """Ouvrir le fichier d'une offre directement dans le navigateur"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        if offre.OffreFichier and os.path.exists(offre.OffreFichier.path):
            file_ext = os.path.splitext(offre.OffreFichier.path)[1].lower()
            
            if file_ext == '.pdf':
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{offre.filename()}"'
                    return response
            elif file_ext in ['.doc', '.docx']:
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/msword')
                    response['Content-Disposition'] = f'attachment; filename="{offre.filename()}"'
                    return response
            else:
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'inline; filename="{offre.filename()}"'
                    return response
                    
        return JsonResponse({'success': False, 'message': 'Fichier non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_decision_onem(request):
    """Enregistrer la décision ONEM pour une offre"""
    try:
        data = json.loads(request.body)
        offre_id = data.get('offre_id')
        decision_id = data.get('decision_id')
        observation = data.get('observation', '').strip()
        motif = data.get('motif', '').strip()
        
        print(f"DEBUG ONEM - offre_id: {offre_id}, decision_id: {decision_id}")
        
        if not offre_id:
            return JsonResponse({'success': False, 'message': 'Offre non spécifiée'}, status=400)
        
        if not decision_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner une décision'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        decision = get_object_or_404(DecisionOnem, id=decision_id)
        
        if Onem.objects.filter(offre=offre).exists():
            return JsonResponse({'success': False, 'message': 'Cette offre a déjà été traitée'}, status=400)
        
        traitement = Onem.objects.create(
            offre=offre,
            decision=decision,
            observation=observation,
            motif=motif
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Décision "{decision.Description}" enregistrée avec succès',
            'traitement': {'id': traitement.id}
        })
    except Exception as e:
        print(f"Erreur ONEM: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

        
@csrf_exempt
@require_http_methods(["POST"])
def modifier_traitement(request, id_traitement):
    """Modifier un traitement existant"""
    try:
        traitement = get_object_or_404(Onem, id=id_traitement)
        data = json.loads(request.body)
        
        decision_id = data.get('decision_id')
        observation = data.get('observation', '').strip()
        motif = data.get('motif', '').strip()
        
        decision = None
        if decision_id:
            decision = get_object_or_404(DecisionOnem, id=decision_id)
        
        traitement.decision = decision
        traitement.observation = observation
        traitement.motif = motif
        traitement.save()
        
        return JsonResponse({'success': True, 'message': 'Traitement modifié avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# ACTION CANDIDAT




def inscriptionCandidat(request):
    """Page d'inscription du candidat"""
    if request.method == 'POST':
        try:
            # Récupération des données
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
            email = request.POST.get('email')  # ← NOUVEAU : email réel
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            photo = request.FILES.get('photo')  # ← NOUVEAU : photo
            
            # Vérification des champs obligatoires
            if not all([nom, postnom, prenom, sexe, nationalite, lieuNaissance, ville, 
                       dateNaissance, numeroTelephone, quartier, email, username, password]):
                messages.error(request, 'Tous les champs sont requis')
                return redirect('inscriptionCandidat')
            
            # Vérification des mots de passe
            if password != confirm_password:
                messages.error(request, 'Les mots de passe ne correspondent pas')
                return redirect('inscriptionCandidat')
            
            # Vérification si username existe déjà
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur existe déjà')
                return redirect('inscriptionCandidat')
            
            # Vérification si email existe déjà
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Cet email est déjà utilisé')
                return redirect('inscriptionCandidat')
            
            # Vérification si téléphone existe déjà
            if Candidat.objects.filter(numeroTelephone=numeroTelephone).exists():
                messages.error(request, 'Ce numéro de téléphone est déjà utilisé')
                return redirect('inscriptionCandidat')
            
            # Vérification de l'âge (minimum 18 ans)
            birth_date = datetime.strptime(dateNaissance, '%Y-%m-%d').date()
            today = datetime.today().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                messages.error(request, 'Vous devez avoir au moins 18 ans pour vous inscrire')
                return redirect('inscriptionCandidat')
            
            # Création de l'utilisateur Django avec LE VRAI EMAIL
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=prenom,
                last_name=f"{nom} {postnom}",
                email=email  # ← Utilisation du vrai email saisi par l'utilisateur
            )
            
            # Ajout au groupe CANDIDAT
            groupe_candidat, _ = Group.objects.get_or_create(name='CANDIDAT')
            user.groups.add(groupe_candidat)
            
            # Création du profil candidat avec photo
            candidat = Candidat.objects.create(
                user=user,
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                sexe=sexe,
                nationalite=nationalite,
                lieuNaissance=lieuNaissance,
                ville=ville,
                dateNaissance=dateNaissance,
                numeroTelephone=numeroTelephone,
                quartier=quartier,
                avenue=avenue if avenue else "",
                photo=photo  # ← Sauvegarde de la photo
            )
            
            messages.success(request, f'Bienvenue {prenom} ! Votre compte a été créé avec succès. Veuillez vous connecter.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
            return redirect('Appl/Candidat.html')
    
    return render(request, "Appl/Candidat.html")






# ==================== PAGE DASHBOARD CANDIDAT ====================

@login_required
@login_required
def dashboardCandidat(request):
    """Affiche le tableau de bord du candidat avec les offres acceptées"""
    
    # Vérifier que l'utilisateur est bien un candidat
    if not request.user.groups.filter(name='CANDIDAT').exists():
        messages.error(request, 'Accès non autorisé')
        return redirect('login_candidat')
    
    # Récupérer le profil candidat
    try:
        candidat = Candidat.objects.get(user=request.user)
    except Candidat.DoesNotExist:
        messages.error(request, 'Profil candidat introuvable')
        return redirect('completer_profil')
    
    context = {
        'candidat': candidat,
        'user': request.user,
    }
    return render(request, 'dashboardCandidat.html', context)


# ==================== API: Récupérer les offres acceptées ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_offres_acceptees(request):
    """API pour récupérer les offres acceptées, actives (Actif ou Renouveler) et non expirées"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        # Récupérer la décision "Accepter"
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0})
        
        # Récupérer le candidat
        try:
            candidat = Candidat.objects.get(user=request.user)
        except Candidat.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0, 'offres_postulees_ids': []})
        
        # Récupérer les IDs des offres déjà postulées
        offres_postulees_ids = Candidature.objects.filter(
            candidat=candidat
        ).values_list('offre_id', flat=True)
        
        today = date.today()
        data = []
        
        # Récupérer les offres avec décision Accepter
        traitements = Onem.objects.filter(
            decision=decision_accepter
        ).select_related('offre', 'offre__domaine').order_by('-date_verification')
        
        for t in traitements:
            offre = t.offre
            type_etat = 'Actif'
            date_expiration = None
            afficher = True
            
            # Récupérer le réglage de l'offre
            try:
                reglage = offre.reglage
                type_etat = reglage.type_etat.designation
                date_expiration = reglage.date_expiration
                
                # Filtrer selon l'état
                if type_etat == 'Stopper':
                    afficher = False
                elif type_etat == 'Actif':
                    if date_expiration and date_expiration < today:
                        afficher = False
                elif type_etat == 'Renouveler':
                    if date_expiration and date_expiration < today:
                        afficher = False
                else:
                    afficher = False
                    
            except ReglageOffre.DoesNotExist:
                # Pas de réglage, considéré comme actif par défaut
                afficher = True
            
            if not afficher:
                continue
            
            data.append({
                'id': offre.id,
                'titre': offre.titre,
                'domaine_nom': offre.domaine.NomDomaine,
                'date_publication': offre.date_publication.strftime('%d/%m/%Y'),
                'date_expiration': date_expiration.strftime('%d/%m/%Y') if date_expiration else None,
                'type_etat': type_etat,
                'fichier_url': offre.OffreFichier.url if offre.OffreFichier else None,
            })
        
        return JsonResponse({
            'success': True,
            'offres': data,
            'total': len(data),
            'offres_postulees_ids': list(offres_postulees_ids)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
# ==================== API: Envoyer une candidature ====================

@csrf_exempt
@require_http_methods(["POST"])
def postuler_candidature(request):
    """API: Enregistrer une candidature et notifier le candidat par email"""
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
        
        # Vérifier que l'offre est acceptée
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
            if not Onem.objects.filter(offre=offre, decision=decision_accepter).exists():
                return JsonResponse({'success': False, 'message': 'Cette offre n\'est pas disponible'}, status=400)
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Offre non disponible'}, status=400)
        
        # Vérifier si déjà postulé
        if Candidature.objects.filter(candidat=candidat, offre=offre).exists():
            return JsonResponse({'success': False, 'message': 'Vous avez déjà postulé à cette offre'}, status=400)
        
        # Créer la candidature
        candidature = Candidature.objects.create(
            candidat=candidat,
            offre=offre,
            cv=cv
        )
        
        # ========== ENVOYER L'EMAIL DE CONFIRMATION DE CANDIDATURE ==========
        from .utils import notifier_candidature_envoyee
        base_url = "https://mahoridi.pythonanywhere.com"  # Votre domaine
        email_envoye, email_message = notifier_candidature_envoyee(candidature, base_url)
        # ====================================================================
        
        return JsonResponse({
            'success': True,
            'message': f'Votre candidature pour "{offre.titre}" a été envoyée avec succès !',
            'email_envoye': email_envoye,
            'email_message': email_message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_http_methods(["GET"])
def ouvrir_fichier_candidat(request, id_offre):
    """Ouvrir le fichier d'une offre pour les candidats"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        if offre.OffreFichier and os.path.exists(offre.OffreFichier.path):
            file_ext = os.path.splitext(offre.OffreFichier.path)[1].lower()
            
            if file_ext == '.pdf':
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{offre.filename()}"'
                    return response
            elif file_ext in ['.doc', '.docx']:
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/msword')
                    response['Content-Disposition'] = f'attachment; filename="{offre.filename()}"'
                    return response
            else:
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'inline; filename="{offre.filename()}"'
                    return response
                    
        return JsonResponse({'success': False, 'message': 'Fichier non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# TYPE DE DECISION ADMIN POUR L'ANALYSE DE LA CANDIDATURE


@login_required
def liste_type_decisions(request):
    """Affiche la page principale des types de décision"""
    return render(request, 'TypeDecision.html')


# ==================== API TYPE DECISION ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_all_type_decisions(request):
    """API pour récupérer tous les types de décision"""
    try:
        type_decisions = TypeDecision.objects.all().order_by('-id')
        data = [{
            'id': td.id,
            'Description': td.Description,
        } for td in type_decisions]
        
        return JsonResponse({
            'success': True,
            'type_decisions': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ajouter_type_decision(request):
    """Ajouter un nouveau type de décision"""
    try:
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        
        # Vérifier si le type de décision existe déjà
        if TypeDecision.objects.filter(Description__iexact=description).exists():
            return JsonResponse({'success': False, 'message': 'Ce type de décision existe déjà'}, status=400)
        
        type_decision = TypeDecision.objects.create(Description=description)
        
        return JsonResponse({
            'success': True,
            'message': f'Type de décision "{description}" ajouté avec succès',
            'type_decision': {
                'id': type_decision.id,
                'Description': type_decision.Description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def modifier_type_decision(request, id_type_decision):
    """Modifier un type de décision existant"""
    try:
        type_decision = get_object_or_404(TypeDecision, id=id_type_decision)
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        
        # Vérifier si une autre décision a déjà cette description
        if TypeDecision.objects.filter(Description__iexact=description).exclude(id=id_type_decision).exists():
            return JsonResponse({'success': False, 'message': 'Ce type de décision existe déjà'}, status=400)
        
        ancienne_description = type_decision.Description
        type_decision.Description = description
        type_decision.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Type de décision "{ancienne_description}" modifié avec succès',
            'type_decision': {
                'id': type_decision.id,
                'Description': type_decision.Description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def supprimer_type_decision(request, id_type_decision):
    """Supprimer un type de décision"""
    try:
        type_decision = get_object_or_404(TypeDecision, id=id_type_decision)
        description = type_decision.Description
        type_decision.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Type de décision "{description}" supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




# ==================== PAGE DECISIONS ====================

# ============================================================================
# SECTION: DECISIONS SUR CANDIDATURES AVEC ENVOI D'EMAIL
# ============================================================================
@login_required
@login_required
def liste_decisions_candidature(request):
    """Affiche la page principale des décisions sur candidatures"""
    types_decision = TypeDecision.objects.all().order_by('Description')
    return render(request, 'Decision.html', {'types_decision': types_decision})


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_candidatures_a_traiter(request):
    """API: Récupérer les candidatures sans décision"""
    try:
        candidatures_avec_decision = Decision.objects.values_list('candidature_id', flat=True)
        candidatures = Candidature.objects.exclude(
            id__in=candidatures_avec_decision
        ).select_related('candidat', 'candidat__user', 'offre', 'offre__domaine').order_by('-date_soumission')
        
        data = []
        for c in candidatures:
            data.append({
                'id': c.id,
                'candidat_nom': f"{c.candidat.nom} {c.candidat.postnom} {c.candidat.prenom}",
                'candidat_email': c.candidat.user.email if c.candidat.user else None,
                'offre_titre': c.offre.titre,
                'offre_domaine': c.offre.domaine.NomDomaine,
                'cv_url': c.cv.url if c.cv else None,
                'date_soumission': c.date_soumission.strftime('%d/%m/%Y à %H:%M')
            })
        
        return JsonResponse({'success': True, 'candidatures': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_candidatures_traitees(request):
    """API: Récupérer les candidatures avec décision"""
    try:
        decisions = Decision.objects.select_related(
            'candidature', 
            'candidature__candidat',
            'candidature__candidat__user',
            'candidature__offre',
            'type_decision'
        ).all().order_by('-date_decision')
        
        data = []
        for d in decisions:
            data.append({
                'id': d.id,
                'candidature_id': d.candidature.id,
                'candidat_nom': f"{d.candidature.candidat.nom} {d.candidature.candidat.postnom} {d.candidature.candidat.prenom}",
                'candidat_email': d.candidature.candidat.user.email if d.candidature.candidat.user else None,
                'offre_titre': d.candidature.offre.titre,
                'type_decision': d.type_decision.Description if d.type_decision else 'Non spécifié',
                'type_decision_id': d.type_decision.id if d.type_decision else None,
                'motif': d.motif or '',
                'date_decision': d.date_decision.strftime('%d/%m/%Y à %H:%M')
            })
        
        return JsonResponse({'success': True, 'decisions': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def ouvrir_cv_candidat(request, id_candidature):
    """Ouvrir le CV d'un candidat"""
    try:
        candidature = get_object_or_404(Candidature, id=id_candidature)
        if candidature.cv and os.path.exists(candidature.cv.path):
            with open(candidature.cv.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{candidature.cv.name.split("/")[-1]}"'
                return response
        return JsonResponse({'success': False, 'message': 'CV non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_decision(request):
    """API: Enregistrer une décision pour une candidature et envoyer un email"""
    try:
        data = json.loads(request.body)
        candidature_id = data.get('candidature_id')
        type_decision_id = data.get('type_decision_id')
        motif = data.get('motif', '').strip()
        
        if not candidature_id or not type_decision_id:
            return JsonResponse({'success': False, 'message': 'Données incomplètes'}, status=400)
        
        # Récupérer la candidature avec toutes les relations
        candidature = get_object_or_404(
            Candidature.objects.select_related('candidat', 'candidat__user', 'offre', 'offre__domaine'),
            id=candidature_id
        )
        
        type_decision = get_object_or_404(TypeDecision, id=type_decision_id)
        
        # Vérifier si une décision existe déjà
        if Decision.objects.filter(candidature=candidature).exists():
            return JsonResponse({'success': False, 'message': 'Cette candidature a déjà une décision'}, status=400)
        
        # Créer la décision
        decision = Decision.objects.create(
            candidature=candidature,
            type_decision=type_decision,
            motif=motif
        )
        
        # Envoyer l'email de notification
        email_envoye = False
        email_message = ""
        
        from .utils import notifier_candidat_decision
        base_url = "https://mahoridi.pythonanywhere.com"  # À remplacer par votre domaine
        
        success, msg = notifier_candidat_decision(
            candidature, 
            type_decision.Description, 
            motif, 
            base_url
        )
        email_envoye = success
        email_message = msg
        
        return JsonResponse({
            'success': True,
            'message': f'Décision "{type_decision.Description}" enregistrée avec succès',
            'decision_id': decision.id,
            'email_envoye': email_envoye,
            'email_message': email_message,
            'type_decision': type_decision.Description
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def modifier_decision(request, id_decision):
    """API: Modifier une décision existante et renvoyer un email"""
    try:
        decision = get_object_or_404(
            Decision.objects.select_related(
                'candidature', 
                'candidature__candidat',
                'candidature__candidat__user',
                'candidature__offre',
                'type_decision'
            ),
            id=id_decision
        )
        
        data = json.loads(request.body)
        type_decision_id = data.get('type_decision_id')
        motif = data.get('motif', '').strip()
        
        ancien_type = decision.type_decision.Description if decision.type_decision else "Non spécifié"
        
        if type_decision_id:
            type_decision = get_object_or_404(TypeDecision, id=type_decision_id)
            decision.type_decision = type_decision
        
        decision.motif = motif
        decision.save()
        
        # Envoyer l'email de notification pour la modification
        email_envoye = False
        email_message = ""
        
        from .utils import notifier_candidat_decision
        base_url = "https://mahoridi.pythonanywhere.com"  # À remplacer par votre domaine
        
        success, msg = notifier_candidat_decision(
            decision.candidature,
            decision.type_decision.Description,
            motif,
            base_url
        )
        email_envoye = success
        email_message = msg
        
        return JsonResponse({
            'success': True,
            'message': f'Décision modifiée avec succès (ancien: {ancien_type} → nouveau: {decision.type_decision.Description})',
            'decision_id': decision.id,
            'email_envoye': email_envoye,
            'email_message': email_message,
            'type_decision': decision.type_decision.Description if decision.type_decision else "Non spécifié"
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== PAGE TESTS ====================

def liste_tests(request):
    """Affiche la page principale des tests"""
    return render(request, 'Test.html')


# ==================== API OFFRES ACCEPTEES POUR TESTS ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_acceptees_tests(request):
    """API pour récupérer les offres acceptées pour les tests"""
    try:
        # Récupérer la décision "Accepter"
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0})
        
        # Récupérer les offres avec décision Accepter
        traitements = Onem.objects.filter(
            decision=decision_accepter
        ).select_related('offre', 'offre__domaine').order_by('-date_verification')
        
        # Récupérer les IDs des offres qui ont déjà des tests
        offres_avec_tests_ids = Test.objects.values_list('offre_id', flat=True).distinct()
        
        data = []
        for t in traitements:
            # Compter le nombre de tests pour cette offre
            nb_tests = Test.objects.filter(offre=t.offre).count()
            
            data.append({
                'id': t.offre.id,
                'titre': t.offre.titre,
                'domaine_nom': t.offre.domaine.NomDomaine,
                'date_validation': t.date_verification.strftime('%d/%m/%Y'),
                'fichier_url': t.offre.OffreFichier.url if t.offre.OffreFichier else None,
                'a_deja_test': nb_tests > 0,
                'nb_tests': nb_tests
            })
        
        return JsonResponse({
            'success': True,
            'offres': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API TESTS ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_tests_by_offre(request, id_offre):
    """API pour récupérer tous les tests d'une offre"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        tests = Test.objects.filter(offre=offre).order_by('-date_test')
        
        data = [{
            'id': t.id,
            'offre_id': t.offre.id,
            'offre_titre': t.offre.titre,
            'fichier_url': t.fichier_test.url if t.fichier_test else None,
            'nom_fichier': t.filename(),
            'date_test': t.date_test.strftime('%d/%m/%Y à %H:%M'),
            'date_creation': t.date_creation.strftime('%d/%m/%Y à %H:%M')
        } for t in tests]
        
        return JsonResponse({
            'success': True,
            'tests': data,
            'total': len(data),
            'offre_titre': offre.titre
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ajouter_test(request):
    """Ajouter un test pour une offre"""
    try:
        offre_id = request.POST.get('offre_id')
        fichier_test = request.FILES.get('fichier_test')
        date_test_str = request.POST.get('date_test')
        
        if not offre_id:
            return JsonResponse({'success': False, 'message': 'Offre non spécifiée'}, status=400)
        
        if not fichier_test:
            return JsonResponse({'success': False, 'message': 'Veuillez importer le fichier du test'}, status=400)
        
        if not date_test_str:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner une date pour le test'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        
        # Vérifier que l'offre est acceptée
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
            offre_acceptee = Onem.objects.filter(offre=offre, decision=decision_accepter).exists()
            if not offre_acceptee:
                return JsonResponse({'success': False, 'message': 'Cette offre n\'est pas acceptée'}, status=400)
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Configuration manquante'}, status=400)
        
        # Convertir la date
        try:
            date_test = datetime.strptime(date_test_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Format de date invalide'}, status=400)
        
        # Créer le test
        test = Test.objects.create(
            offre=offre,
            fichier_test=fichier_test,
            date_test=date_test
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Test programmé avec succès pour "{offre.titre}"',
            'test': {
                'id': test.id,
                'offre_id': test.offre.id,
                'offre_titre': test.offre.titre,
                'fichier_url': test.fichier_test.url if test.fichier_test else None,
                'nom_fichier': test.filename(),
                'date_test': test.date_test.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def supprimer_test(request, id_test):
    """Supprimer un test"""
    try:
        test = get_object_or_404(Test, id=id_test)
        offre_titre = test.offre.titre
        
        # Supprimer le fichier
        if test.fichier_test and os.path.exists(test.fichier_test.path):
            os.remove(test.fichier_test.path)
        
        test.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Test supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_http_methods(["GET"])
def ouvrir_fichier_test(request, id_test):
    """Ouvrir le fichier d'un test"""
    try:
        test = get_object_or_404(Test, id=id_test)
        if test.fichier_test and os.path.exists(test.fichier_test.path):
            file_ext = os.path.splitext(test.fichier_test.path)[1].lower()
            
            if file_ext == '.pdf':
                with open(test.fichier_test.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{test.filename()}"'
                    return response
            else:
                with open(test.fichier_test.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{test.filename()}"'
                    return response
                    
        return JsonResponse({'success': False, 'message': 'Fichier non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)





# ==================== PAGE EVALUATIONS ====================

def liste_evaluations(request):
    """Affiche la page principale des évaluations"""
    return render(request, 'Evaluation.html')


# ==================== API CANDIDATURES ACCEPTEES ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_candidatures_acceptees(request):
    """API pour récupérer les offres acceptées, actives (Actif ou Renouveler) et non expirées"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        # Récupérer la décision "Accepter"
        try:
            decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
        except DecisionOnem.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0})
        
        # Récupérer le candidat
        try:
            candidat = Candidat.objects.get(user=request.user)
        except Candidat.DoesNotExist:
            return JsonResponse({'success': True, 'offres': [], 'total': 0, 'offres_postulees_ids': []})
        
        # Récupérer les IDs des offres déjà postulées
        offres_postulees_ids = Candidature.objects.filter(
            candidat=candidat
        ).values_list('offre_id', flat=True)
        
        today = date.today()
        data = []
        
        # Récupérer les offres avec décision Accepter
        traitements = Onem.objects.filter(
            decision=decision_accepter
        ).select_related('offre', 'offre__domaine').order_by('-date_verification')
        
        for t in traitements:
            offre = t.offre
            type_etat = 'Actif'
            date_expiration = None
            afficher = True
            
            # Récupérer le réglage de l'offre
            try:
                reglage = offre.reglage
                type_etat = reglage.type_etat.designation
                date_expiration = reglage.date_expiration
                
                # Filtrer selon l'état
                if type_etat == 'Stopper':
                    afficher = False
                elif type_etat == 'Actif':
                    # Vérifier si la date d'expiration est dépassée
                    if date_expiration and date_expiration < today:
                        afficher = False
                elif type_etat == 'Renouveler':
                    # Vérifier si la date d'expiration est dépassée
                    if date_expiration and date_expiration < today:
                        afficher = False
                else:
                    afficher = False
                    
            except ReglageOffre.DoesNotExist:
                # Pas de réglage, considéré comme actif par défaut
                afficher = True
            
            if not afficher:
                continue
            
            data.append({
                'id': offre.id,
                'titre': offre.titre,
                'domaine_nom': offre.domaine.NomDomaine,
                'date_publication': offre.date_publication.strftime('%d/%m/%Y'),
                'date_expiration': date_expiration.strftime('%d/%m/%Y') if date_expiration else None,
                'type_etat': type_etat,
                'fichier_url': offre.OffreFichier.url if offre.OffreFichier else None,
            })
        
        return JsonResponse({
            'success': True,
            'offres': data,
            'total': len(data),
            'offres_postulees_ids': list(offres_postulees_ids)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# ==================== API RECUPERER TESTS D'UNE OFFRE ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_tests_by_offre(request, id_offre):
    """API pour récupérer tous les tests d'une offre"""
    try:
        tests = Test.objects.filter(offre_id=id_offre).order_by('date_test')
        data = [{
            'id': t.id,
            'date_test': t.date_test.strftime('%d/%m/%Y à %H:%M'),
            'fichier_url': t.fichier_test.url if t.fichier_test else None,
            'nom_fichier': t.filename(),
        } for t in tests]
        
        return JsonResponse({
            'success': True,
            'tests': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API RECUPERER EVALUATIONS D'UNE CANDIDATURE ====================


# ==================== API ENREGISTRER EVALUATION ====================










# CONVERSION EN AGENT


# ========== FONCTION POUR VÉRIFIER ET CHANGER LE STATUT AGENT ==========



#= SUPPRIMER UNE ÉVALUATION ==========
@csrf_exempt
@require_http_methods(["DELETE"])
def supprimer_evaluation(request, id_evaluation):
    """Supprimer une évaluation et recalculer le statut Agent"""
    try:
        evaluation = get_object_or_404(Evaluation, id=id_evaluation)
        candidature = evaluation.candidature
        
        # Récupérer l'offre et le nombre de tests
        offre = candidature.offre
        nombre_tests = Test.objects.filter(offre=offre).count()
        
        # Supprimer l'évaluation
        evaluation.delete()
        
        # Recompter les évaluations restantes
        evaluations_restantes = Evaluation.objects.filter(candidature=candidature).count()
        
        message_promotion = ""
        
        # Si après suppression, il n'y a plus tous les tests d'évalués, retirer le statut Agent si nécessaire
        if evaluations_restantes < nombre_tests:
            # L'utilisateur n'a plus tous ses tests évalués, donc ne peut pas être Agent
            user = candidature.candidat.user
            
            # Vérifier si l'utilisateur est dans le groupe AGENT, si oui le remettre en CANDIDAT
            if user.groups.filter(name='AGENT').exists():
                success, message_groupe = changer_groupe_utilisateur(user, 'CANDIDAT')
                message_promotion = f"⚠️ L'utilisateur a été remis en CANDIDAT car il manque des évaluations."
            
            # Mettre à jour le statut de l'agent
            try:
                agent = Agent.objects.get(candidat=candidature.candidat)
                if agent.statut == 'Approuvé':
                    agent.statut = 'En cours'
                    agent.save()
            except Agent.DoesNotExist:
                pass
        else:
            # Recalculer avec les évaluations restantes
            message_promotion = verifier_et_promouvoir_agent(candidature)
        
        return JsonResponse({
            'success': True,
            'message': 'Évaluation supprimée avec succès.',
            'promotion_message': message_promotion
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ========== FONCTION POUR OBTENIR LE STATUT D'UN CANDIDAT ==========
@csrf_exempt
def get_candidat_status(request, candidature_id):
    """Obtenir le statut d'un candidat (groupes Django, évaluations, moyenne)"""
    try:
        candidature = get_object_or_404(Candidature, id=candidature_id)
        user = candidature.candidat.user
        offre = candidature.offre
        
        # Récupérer les groupes de l'utilisateur
        groupes = list(user.groups.values_list('name', flat=True))
        
        # Récupérer les évaluations
        evaluations = Evaluation.objects.filter(candidature=candidature).values('id', 'note', 'observation', 'date_evaluation')
        
        # Calculer la moyenne si toutes les évaluations sont faites
        tous_les_tests = Test.objects.filter(offre=offre).count()
        evaluations_count = evaluations.count()
        moyenne = None
        
        if tous_les_tests > 0 and evaluations_count >= tous_les_tests:
            notes = [e['note'] for e in evaluations]
            moyenne = sum(notes) / len(notes)
        
        return JsonResponse({
            'success': True,
            'status': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'groupes': groupes,
                'is_staff': user.is_staff,
                'evaluations_count': evaluations_count,
                'total_tests_requis': tous_les_tests,
                'moyenne': moyenne,
                'est_agent': 'AGENT' in groupes,
                'evaluations': list(evaluations)
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

































# TYPE CONGE


# ==================== PAGE TYPE CONGE ====================
@login_required
def liste_type_conge(request):
    """Affiche la page principale des types de congé"""
    return render(request, 'TypeConge.html')


# ==================== API TYPE CONGE ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_all_type_conge(request):
    """API pour récupérer tous les types de congé"""
    try:
        types_conge = TypeConge.objects.all().order_by('designation')
        data = [{
            'id': tc.id,
            'designation': tc.designation,
            'duree': tc.duree,
            'description': tc.description or '',
            'date_creation': tc.date_creation.strftime('%d/%m/%Y à %H:%M'),
            'date_modification': tc.date_modification.strftime('%d/%m/%Y à %H:%M')
        } for tc in types_conge]
        
        return JsonResponse({
            'success': True,
            'types_conge': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ajouter_type_conge(request):
    """Ajouter un nouveau type de congé"""
    try:
        data = json.loads(request.body)
        designation = data.get('designation', '').strip()
        duree = data.get('duree')
        description = data.get('description', '').strip()
        
        if not designation:
            return JsonResponse({'success': False, 'message': 'La désignation est requise'}, status=400)
        
        if not duree:
            return JsonResponse({'success': False, 'message': 'La durée est requise'}, status=400)
        
        try:
            duree = int(duree)
            if duree <= 0:
                return JsonResponse({'success': False, 'message': 'La durée doit être supérieure à 0'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'La durée doit être un nombre entier'}, status=400)
        
        # Vérifier si le type de congé existe déjà
        if TypeConge.objects.filter(designation__iexact=designation).exists():
            return JsonResponse({'success': False, 'message': 'Ce type de congé existe déjà'}, status=400)
        
        type_conge = TypeConge.objects.create(
            designation=designation,
            duree=duree,
            description=description
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Type de congé "{designation}" ajouté avec succès',
            'type_conge': {
                'id': type_conge.id,
                'designation': type_conge.designation,
                'duree': type_conge.duree,
                'description': type_conge.description
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def modifier_type_conge(request, id_type_conge):
    """Modifier un type de congé existant"""
    try:
        type_conge = get_object_or_404(TypeConge, id=id_type_conge)
        data = json.loads(request.body)
        
        designation = data.get('designation', '').strip()
        duree = data.get('duree')
        description = data.get('description', '').strip()
        
        if not designation:
            return JsonResponse({'success': False, 'message': 'La désignation est requise'}, status=400)
        
        if not duree:
            return JsonResponse({'success': False, 'message': 'La durée est requise'}, status=400)
        
        try:
            duree = int(duree)
            if duree <= 0:
                return JsonResponse({'success': False, 'message': 'La durée doit être supérieure à 0'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'La durée doit être un nombre entier'}, status=400)
        
        # Vérifier si une autre entrée a déjà cette désignation
        if TypeConge.objects.filter(designation__iexact=designation).exclude(id=id_type_conge).exists():
            return JsonResponse({'success': False, 'message': 'Ce type de congé existe déjà'}, status=400)
        
        ancienne_designation = type_conge.designation
        type_conge.designation = designation
        type_conge.duree = duree
        type_conge.description = description
        type_conge.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Type de congé "{ancienne_designation}" modifié avec succès',
            'type_conge': {
                'id': type_conge.id,
                'designation': type_conge.designation,
                'duree': type_conge.duree,
                'description': type_conge.description
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def supprimer_type_conge(request, id_type_conge):
    """Supprimer un type de congé"""
    try:
        type_conge = get_object_or_404(TypeConge, id=id_type_conge)
        designation = type_conge.designation
        type_conge.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Type de congé "{designation}" supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# ==================== PAGE DEMANDE CONGE ====================
@login_required
def liste_demandes_conge(request):
    """Affiche la page principale des demandes de congé"""
    agents = Agent.objects.select_related('candidat').all().order_by('candidat__nom')
    types_conge = TypeConge.objects.all().order_by('designation')
    return render(request, 'DemandeConge.html', {
        'agents': agents,
        'types_conge': types_conge
    })


# ==================== API DEMANDES CONGE ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_all_demandes_conge(request):
    """API pour récupérer toutes les demandes de congé"""
    try:
        demandes = DemandeConge.objects.select_related(
            'agent', 'agent__candidat', 'type_conge'
        ).all().order_by('-date_demande')
        
        data = []
        for d in demandes:
            data.append({
                'id': d.id,
                'agent_id': d.agent.id,
                'agent_nom': f"{d.agent.candidat.nom} {d.agent.candidat.prenom}",
                'type_conge_id': d.type_conge.id,
                'type_conge_designation': d.type_conge.designation,
                'type_conge_duree': d.type_conge.duree,
                'motif': d.motif,
                'date_demande': d.date_demande.strftime('%d/%m/%Y à %H:%M'),
                'date_debut': d.date_debut.strftime('%d/%m/%Y'),
                'date_fin': d.date_fin.strftime('%d/%m/%Y'),
                'nombre_jours': d.nombre_jours
            })
        
        return JsonResponse({
            'success': True,
            'demandes': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_demandes_by_agent(request, id_agent):
    """API pour récupérer les demandes d'un agent spécifique"""
    try:
        demandes = DemandeConge.objects.filter(
            agent_id=id_agent
        ).select_related('type_conge').order_by('-date_demande')
        
        data = [{
            'id': d.id,
            'type_conge_designation': d.type_conge.designation,
            'motif': d.motif,
            'date_demande': d.date_demande.strftime('%d/%m/%Y à %H:%M'),
            'date_debut': d.date_debut.strftime('%d/%m/%Y'),
            'date_fin': d.date_fin.strftime('%d/%m/%Y'),
            'nombre_jours': d.nombre_jours
        } for d in demandes]
        
        return JsonResponse({
            'success': True,
            'demandes': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# AGENT

from django.http import JsonResponse
from .models import Agent

def api_agents(request):
    """API qui retourne la liste des agents en JSON"""
    agents = Agent.objects.select_related('candidat').all()
    
    data = []
    for agent in agents:
        data.append({
            'id': agent.id,
            'nom': agent.candidat.nom,
            'postnom': agent.candidat.postnom,
            'prenom': agent.candidat.prenom,
            'sexe': agent.candidat.sexe,
            'telephone': agent.candidat.numeroTelephone,
            'date_retenu': agent.date_retenu.strftime('%d/%m/%Y'),
            'statut': agent.statut
        })
    
    return JsonResponse({
        'success': True,
        'agents': data,
        'total': len(data)
    })


# TRAITEMENT ACCUEIL 


# views.py - Ajoutez/modifiez ces fonctions

from datetime import date

def api_offres_accueil(request):
    """API pour récupérer les offres actives (Actif ou Renouveler et non expirées)"""
    try:
        decision_accepter = DecisionOnem.objects.get(Description__icontains='Accepter')
        offres_acceptees = Onem.objects.filter(
            decision=decision_accepter
        ).select_related('offre', 'offre__domaine').order_by('-date_verification')
        
        data = []
        today = date.today()
        
        for o in offres_acceptees:
            offre = o.offre
            
            # Récupérer le réglage de l'offre
            try:
                reglage = offre.reglage
                type_etat = reglage.type_etat.designation
                date_expiration = reglage.date_expiration
                
                # Vérifier si l'offre doit être affichée
                # Conditions pour afficher : 
                # - État = "Actif" ET (pas de date d'expiration OU date d'expiration non dépassée)
                # - OU État = "Renouveler" ET date de renouvellement valide (si définie)
                if type_etat == 'Actif':
                    if date_expiration and date_expiration < today:
                        continue  # Ne pas afficher si expiré
                elif type_etat == 'Renouveler':
                    if date_expiration and date_expiration < today:
                        continue  # Ne pas afficher si expiré
                elif type_etat == 'Stopper':
                    continue  # Ne pas afficher si stoppé
                    
            except ReglageOffre.DoesNotExist:
                # Pas de réglage, considéré comme actif par défaut
                type_etat = 'Actif'
                date_expiration = None
            
            data.append({
                'id': offre.id,
                'titre': offre.titre,
                'domaine': offre.domaine.NomDomaine,
                'description': f"Pour plus d'information à l'offre '{offre.titre}', veuillez télécharger le fichier en cliquant sur le titre de l'offre.",
                'date_publication': offre.date_publication.strftime('%d/%m/%Y'),
                'fichier_url': offre.OffreFichier.url if offre.OffreFichier else None,
                'type_etat': type_etat,
                'date_expiration': date_expiration.strftime('%d/%m/%Y') if date_expiration else None
            })
        
        return JsonResponse({
            'success': True,
            'offres': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# API pour l'admin - gérer les réglages des offres
@csrf_exempt
@require_http_methods(["GET", "POST"])
def gerer_reglage_offre(request, id_offre):
    """Gérer le réglage d'une offre (admin)"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        
        if request.method == "GET":
            # Récupérer le réglage existant
            reglage, created = ReglageOffre.objects.get_or_create(
                offre=offre,
                defaults={
                    'type_etat': TypeEtatOffre.objects.get_or_create(designation='Actif')[0]
                }
            )
            
            data = {
                'id': reglage.id,
                'offre_id': offre.id,
                'offre_titre': offre.titre,
                'type_etat_id': reglage.type_etat.id,
                'type_etat': reglage.type_etat.designation,
                'date_expiration': reglage.date_expiration.strftime('%Y-%m-%d') if reglage.date_expiration else None,
                'date_renouvellement': reglage.date_renouvellement.strftime('%Y-%m-%d') if reglage.date_renouvellement else None,
                'motif': reglage.motif or '',
                'est_active': reglage.est_active()
            }
            return JsonResponse({'success': True, 'reglage': data})
        
        elif request.method == "POST":
            data = json.loads(request.body)
            type_etat_id = data.get('type_etat_id')
            date_expiration = data.get('date_expiration')
            date_renouvellement = data.get('date_renouvellement')
            motif = data.get('motif', '').strip()
            
            type_etat = get_object_or_404(TypeEtatOffre, id=type_etat_id)
            
            reglage, created = ReglageOffre.objects.get_or_create(
                offre=offre,
                defaults={
                    'type_etat': type_etat,
                    'motif': motif
                }
            )
            
            if not created:
                reglage.type_etat = type_etat
                reglage.motif = motif
            
            if date_expiration:
                reglage.date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d').date()
            else:
                reglage.date_expiration = None
                
            if date_renouvellement:
                reglage.date_renouvellement = datetime.strptime(date_renouvellement, '%Y-%m-%d').date()
            else:
                reglage.date_renouvellement = None
                
            reglage.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Réglage de l\'offre "{offre.titre}" mis à jour avec succès',
                'offre_statut': reglage.type_etat.designation,
                'est_active': reglage.est_active()
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# ACCUEIL ADMIN

# views.py - Ajoutez ces fonctions
from django.contrib.auth.decorators import login_required


@login_required
def admin_stats(request):
    """API pour les statistiques du dashboard admin"""
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


@login_required
def admin_activites(request):
    """API pour les dernières activités"""
    try:
        # Exemple d'activités - à adapter selon votre logique métier
        activites = [
            {'date': '10/05/2026', 'action': 'Nouvelle offre d\'emploi', 'utilisateur': 'Admin', 'statut': 'Publiée'},
            {'date': '09/05/2026', 'action': 'Inscription candidat', 'utilisateur': 'Richesse SAKINA', 'statut': 'Validée'},
            {'date': '08/05/2026', 'action': 'Candidature reçue', 'utilisateur': 'Jean KABANZA', 'statut': 'En cours'},
            {'date': '07/05/2026', 'action': 'Test programmé', 'utilisateur': 'Admin', 'statut': 'Programmé'},
        ]
        return JsonResponse({'success': True, 'activites': activites})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)












# type etat offre

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import TypeEtatOffre
import json

# ==================== PAGE TYPE ETAT OFFRE ====================
@login_required
def liste_type_etat_offre(request):
    """Affiche la page principale des types d'états d'offre"""
    return render(request, 'TypeEtatOffre.html')


# ==================== API TYPE ETAT OFFRE ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_all_type_etat_offre(request):
    """API pour récupérer tous les types d'états d'offre"""
    try:
        types_etat = TypeEtatOffre.objects.all().order_by('designation')
        data = [{
            'id': te.id,
            'designation': te.designation,
            'description': te.description or '',
        } for te in types_etat]
        
        return JsonResponse({
            'success': True,
            'types_etat': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ajouter_type_etat_offre(request):
    """Ajouter un nouveau type d'état d'offre"""
    try:
        data = json.loads(request.body)
        designation = data.get('designation', '').strip()
        description = data.get('description', '').strip()
        
        if not designation:
            return JsonResponse({'success': False, 'message': 'La désignation est requise'}, status=400)
        
        # Vérifier si le type existe déjà
        if TypeEtatOffre.objects.filter(designation__iexact=designation).exists():
            return JsonResponse({'success': False, 'message': 'Ce type d\'état existe déjà'}, status=400)
        
        type_etat = TypeEtatOffre.objects.create(
            designation=designation,
            description=description
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Type d\'état "{designation}" ajouté avec succès',
            'type_etat': {
                'id': type_etat.id,
                'designation': type_etat.designation,
                'description': type_etat.description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def modifier_type_etat_offre(request, id_type_etat):
    """Modifier un type d'état d'offre existant"""
    try:
        type_etat = get_object_or_404(TypeEtatOffre, id=id_type_etat)
        data = json.loads(request.body)
        
        designation = data.get('designation', '').strip()
        description = data.get('description', '').strip()
        
        if not designation:
            return JsonResponse({'success': False, 'message': 'La désignation est requise'}, status=400)
        
        # Vérifier si une autre entrée a déjà cette désignation
        if TypeEtatOffre.objects.filter(designation__iexact=designation).exclude(id=id_type_etat).exists():
            return JsonResponse({'success': False, 'message': 'Ce type d\'état existe déjà'}, status=400)
        
        ancienne_designation = type_etat.designation
        type_etat.designation = designation
        type_etat.description = description
        type_etat.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Type d\'état "{ancienne_designation}" modifié avec succès',
            'type_etat': {
                'id': type_etat.id,
                'designation': type_etat.designation,
                'description': type_etat.description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def supprimer_type_etat_offre(request, id_type_etat):
    """Supprimer un type d'état d'offre"""
    try:
        type_etat = get_object_or_404(TypeEtatOffre, id=id_type_etat)
        designation = type_etat.designation
        type_etat.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Type d\'état "{designation}" supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# reglage d'offre


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import OffreEmploie, Onem, DecisionOnem, ReglageOffre, TypeEtatOffre
from datetime import datetime, date
import json

# ==================== PAGE REGLAGE OFFRE ====================

def liste_reglage_offre(request):
    """Affiche la page principale des réglages d'offres"""
    types_etat = TypeEtatOffre.objects.all().order_by('designation')
    return render(request, 'ReglageOffre.html', {
        'types_etat': types_etat
    })


# ==================== API OFFRES AVEC DECISION ====================

from datetime import date

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_avec_decision(request):
    """API pour récupérer les offres avec leur décision ONEM"""
    try:
        offres = OffreEmploie.objects.all().order_by('-date_publication')
        today = date.today()
        
        data = []
        for offre in offres:
            # Récupérer la décision de l'offre via Onem
            try:
                onem = Onem.objects.get(offre=offre)
                decision = onem.decision.Description if onem.decision else "Non déterminée"
                decision_id = onem.decision.id if onem.decision else None
                date_decision = onem.date_verification
            except Onem.DoesNotExist:
                decision = "Non traitée"
                decision_id = None
                date_decision = None
            
            # Récupérer le réglage si existant
            try:
                reglage = offre.reglage
                date_expiration = reglage.date_expiration
                date_renouvellement = reglage.date_renouvellement
                type_etat = reglage.type_etat.designation if reglage.type_etat else None
                type_etat_id = reglage.type_etat.id if reglage.type_etat else None
                est_parametre = True
                
                # Vérifier si la date d'expiration est dépassée
                if date_expiration and date_expiration < today:
                    # L'offre est expirée, afficher "Expiré" dans l'affichage
                    type_etat_affiche = "Expiré"
                else:
                    type_etat_affiche = type_etat
                    
            except ReglageOffre.DoesNotExist:
                date_expiration = None
                date_renouvellement = None
                type_etat = None
                type_etat_id = None
                est_parametre = False
                type_etat_affiche = None
            
            # Vérifier si l'offre est acceptée
            est_acceptee = (decision == "Accepter")
            
            data.append({
                'id': offre.id,
                'titre': offre.titre,
                'domaine': offre.domaine.NomDomaine,
                'date_publication': offre.date_publication.strftime('%d/%m/%Y'),
                'decision': decision,
                'decision_id': decision_id,
                'date_decision': date_decision.strftime('%d/%m/%Y') if date_decision else None,
                'est_acceptee': est_acceptee,
                'est_parametre': est_parametre,
                'date_expiration': date_expiration.strftime('%d/%m/%Y') if date_expiration else None,
                'date_renouvellement': date_renouvellement.strftime('%d/%m/%Y') if date_renouvellement else None,
                'type_etat': type_etat,
                'type_etat_affiche': type_etat_affiche,  # ← Nouveau champ pour l'affichage
                'type_etat_id': type_etat_id,
                'est_expiree': date_expiration and date_expiration < today if date_expiration else False,  # ← Flag expiration
                'fichier_url': offre.OffreFichier.url if offre.OffreFichier else None
            })
        
        return JsonResponse({
            'success': True,
            'offres': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_reglage_by_offre(request, id_offre):
    """API pour récupérer le réglage d'une offre spécifique"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        
        try:
            reglage = offre.reglage
            data = {
                'id': reglage.id,
                'offre_id': reglage.offre.id,
                'offre_titre': reglage.offre.titre,
                'type_etat_id': reglage.type_etat.id if reglage.type_etat else None,
                'type_etat_designation': reglage.type_etat.designation if reglage.type_etat else None,
                'date_debut': reglage.date_debut.strftime('%d/%m/%Y'),
                'date_expiration': reglage.date_expiration.strftime('%d/%m/%Y') if reglage.date_expiration else None,
                'date_renouvellement': reglage.date_renouvellement.strftime('%d/%m/%Y') if reglage.date_renouvellement else None,
                'motif': reglage.motif or '',
                'est_active': reglage.est_active()
            }
        except ReglageOffre.DoesNotExist:
            data = None
        
        return JsonResponse({'success': True, 'reglage': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ajouter_reglage(request):
    """Ajouter ou modifier un réglage d'offre"""
    try:
        data = json.loads(request.body)
        offre_id = data.get('offre_id')
        type_etat_id = data.get('type_etat_id')
        date_expiration = data.get('date_expiration')
        date_renouvellement = data.get('date_renouvellement')
        motif = data.get('motif', '').strip()
        
        if not offre_id:
            return JsonResponse({'success': False, 'message': 'Offre non spécifiée'}, status=400)
        
        if not type_etat_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner un état'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        type_etat = get_object_or_404(TypeEtatOffre, id=type_etat_id)
        
        # Vérifier que l'offre est acceptée
        try:
            onem = Onem.objects.get(offre=offre)
            if not onem.decision or onem.decision.Description != "Accepter":
                return JsonResponse({'success': False, 'message': 'Seules les offres acceptées peuvent être paramétrées'}, status=400)
        except Onem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cette offre n\'a pas encore été traitée par l\'ONEM'}, status=400)
        
        # Créer ou mettre à jour le réglage
        reglage, created = ReglageOffre.objects.update_or_create(
            offre=offre,
            defaults={
                'type_etat': type_etat,
                'motif': motif
            }
        )
        
        if date_expiration:
            reglage.date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d').date()
        else:
            reglage.date_expiration = None
            
        if date_renouvellement:
            reglage.date_renouvellement = datetime.strptime(date_renouvellement, '%Y-%m-%d').date()
        else:
            reglage.date_renouvellement = None
            
        reglage.save()
        
        message = "Réglage enregistré avec succès"
        
        return JsonResponse({
            'success': True,
            'message': message,
            'reglage': {
                'id': reglage.id,
                'offre_id': reglage.offre.id,
                'offre_titre': reglage.offre.titre,
                'type_etat': reglage.type_etat.designation,
                'date_expiration': reglage.date_expiration.strftime('%d/%m/%Y') if reglage.date_expiration else None,
                'date_renouvellement': reglage.date_renouvellement.strftime('%d/%m/%Y') if reglage.date_renouvellement else None,
                'est_active': reglage.est_active()
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)





# OEM








from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import OffreEmploie, Domaine, DecisionOnem, Onem
import json
import os

# ==================== PAGE ONEM (TRAITEMENT DES OFFRES) ====================
@login_required
def page_onem_traitement(request):
    """Affiche la page principale ONEM pour le traitement des offres"""
    return render(request, 'Onem.html')


# ==================== API ONEM - OFFRES À TRAITER ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_offres_non_traitees(request):
    """API pour récupérer les offres non encore traitées par l'ONEM"""
    try:
        offres_traitees = Onem.objects.values_list('offre_id', flat=True)
        offres = OffreEmploie.objects.exclude(
            id__in=offres_traitees
        ).select_related('domaine').order_by('-date_publication')
        
        data = [{
            'id': offre.id,
            'titre': offre.titre,
            'domaine_nom': offre.domaine.NomDomaine,
            'date_publication': offre.date_publication.strftime('%d/%m/%Y à %H:%M'),
            'a_fichier': offre.OffreFichier is not None and bool(offre.OffreFichier)
        } for offre in offres]
        
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_offres_traitees_onem(request):
    """API pour récupérer les offres déjà traitées par l'ONEM"""
    try:
        traitements = Onem.objects.select_related(
            'offre', 'offre__domaine', 'decision'
        ).all().order_by('-date_verification')
        
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


@require_http_methods(["GET"])
def ouvrir_fichier_offre_onem(request, id_offre):
    """Ouvrir le fichier d'une offre pour l'ONEM"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        if offre.OffreFichier and os.path.exists(offre.OffreFichier.path):
            file_ext = os.path.splitext(offre.OffreFichier.path)[1].lower()
            
            if file_ext == '.pdf':
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{offre.filename()}"'
                    return response
            else:
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{offre.filename()}"'
                    return response
                    
        return JsonResponse({'success': False, 'message': 'Fichier non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_decision_onem(request):
    """Enregistrer la décision ONEM pour une offre"""
    try:
        # Afficher les données reçues dans la console Django
        print("=== DONNEES RECUES ===")
        print("Body:", request.body)
        
        data = json.loads(request.body)
        print("Data parsée:", data)
        
        offre_id = data.get('offre_id')
        decision_id = data.get('decision_id')
        observation = data.get('observation', '').strip()
        motif = data.get('motif', '').strip()
        
        print(f"offre_id: {offre_id}")
        print(f"decision_id: {decision_id}")
        
        if not offre_id:
            return JsonResponse({'success': False, 'message': 'Offre non spécifiée'}, status=400)
        
        if not decision_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner une décision'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        decision = get_object_or_404(DecisionOnem, id=decision_id)
        
        # Vérifier si l'offre a déjà été traitée
        if Onem.objects.filter(offre=offre).exists():
            return JsonResponse({'success': False, 'message': 'Cette offre a déjà été traitée'}, status=400)
        
        # Créer le traitement
        traitement = Onem.objects.create(
            offre=offre,
            decision=decision,
            observation=observation,
            motif=motif
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Décision "{decision.Description}" enregistrée avec succès',
            'traitement': {
                'id': traitement.id,
                'offre_id': offre.id,
                'titre': offre.titre,
                'decision': decision.Description,
                'date_verification': traitement.date_verification.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def modifier_traitement_onem(request, id_traitement):
    """Modifier un traitement existant"""
    try:
        traitement = get_object_or_404(Onem, id=id_traitement)
        data = json.loads(request.body)
        
        decision_id = data.get('decision_id')
        observation = data.get('observation', '').strip()
        motif = data.get('motif', '').strip()
        
        if decision_id:
            decision = get_object_or_404(DecisionOnem, id=decision_id)
            traitement.decision = decision
        
        traitement.observation = observation
        traitement.motif = motif
        traitement.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Traitement modifié avec succès',
            'traitement': {
                'id': traitement.id,
                'decision': traitement.decision.Description if traitement.decision else 'Non spécifiée',
                'date_modification': traitement.date_modification.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)









from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import OffreEmploie, Domaine, DecisionOnem, Onem
import json
import os

# ==================== PAGE ANALYSE ONEM ====================

@login_required
def page_analyse_onem(request):
    """Affiche la page principale d'analyse ONEM pour le traitement des offres"""
    return render(request, 'AnalyseOnem.html')


# ==================== API ANALYSE ONEM - OFFRES NON ANALYSEES ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_offres_non_analysees(request):
    """API pour récupérer les offres non encore analysées par l'ONEM"""
    try:
        offres_analysees = Onem.objects.values_list('offre_id', flat=True)
        offres = OffreEmploie.objects.exclude(
            id__in=offres_analysees
        ).select_related('domaine').order_by('-date_publication')
        
        data = [{
            'id': offre.id,
            'titre': offre.titre,
            'domaine_nom': offre.domaine.NomDomaine,
            'date_publication': offre.date_publication.strftime('%d/%m/%Y à %H:%M'),
            'a_fichier': offre.OffreFichier is not None and bool(offre.OffreFichier)
        } for offre in offres]
        
        return JsonResponse({'success': True, 'offres': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_offres_analysees(request):
    """API pour récupérer les offres déjà analysées par l'ONEM"""
    try:
        traitements = Onem.objects.select_related(
            'offre', 'offre__domaine', 'decision'
        ).all().order_by('-date_verification')
        
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

@login_required
@require_http_methods(["GET"])
def ouvrir_fichier_analyse_onem(request, id_offre):
    """Ouvrir le fichier d'une offre pour l'analyse ONEM"""
    try:
        offre = get_object_or_404(OffreEmploie, id=id_offre)
        if offre.OffreFichier and os.path.exists(offre.OffreFichier.path):
            file_ext = os.path.splitext(offre.OffreFichier.path)[1].lower()
            
            if file_ext == '.pdf':
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{offre.filename()}"'
                    return response
            else:
                with open(offre.OffreFichier.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{offre.filename()}"'
                    return response
                    
        return JsonResponse({'success': False, 'message': 'Fichier non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_analyse_onem(request):
    """Enregistrer l'analyse ONEM pour une offre"""
    try:
        data = json.loads(request.body)
        offre_id = data.get('offre_id')
        decision_id = data.get('decision_id')
        observation = data.get('observation', '').strip()
        motif = data.get('motif', '').strip()
        
        if not offre_id:
            return JsonResponse({'success': False, 'message': 'Offre non spécifiée'}, status=400)
        
        if not decision_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner une décision'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        decision = get_object_or_404(DecisionOnem, id=decision_id)
        
        # Vérifier si l'offre a déjà été analysée
        if Onem.objects.filter(offre=offre).exists():
            return JsonResponse({'success': False, 'message': 'Cette offre a déjà été analysée'}, status=400)
        
        # Créer l'analyse
        analyse = Onem.objects.create(
            offre=offre,
            decision=decision,
            observation=observation,
            motif=motif
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Analyse enregistrée avec succès. Décision: "{decision.Description}"',
            'analyse': {
                'id': analyse.id,
                'offre_id': offre.id,
                'titre': offre.titre,
                'decision': decision.Description,
                'date_verification': analyse.date_verification.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def modifier_analyse_onem(request, id_analyse):
    """Modifier une analyse existante"""
    try:
        analyse = get_object_or_404(Onem, id=id_analyse)
        data = json.loads(request.body)
        
        decision_id = data.get('decision_id')
        observation = data.get('observation', '').strip()
        motif = data.get('motif', '').strip()
        
        if decision_id:
            decision = get_object_or_404(DecisionOnem, id=decision_id)
            analyse.decision = decision
        
        analyse.observation = observation
        analyse.motif = motif
        analyse.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Analyse modifiée avec succès',
            'analyse': {
                'id': analyse.id,
                'decision': analyse.decision.Description if analyse.decision else 'Non spécifiée',
                'date_modification': analyse.date_modification.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ACTIVATION ET DESACTIVATION PERSONNEL


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User, Group
from .models import Candidat
import json

# ==================== PAGE LISTE CANDIDATS ====================

def liste_candidats(request):
    """Affiche la page principale des candidats"""
    groupes = Group.objects.all().order_by('name')
    return render(request, 'ListeCandidat.html', {'groupes': groupes})


# ==================== API CANDIDATS ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_all_candidats(request):
    """API pour récupérer tous les candidats avec leurs utilisateurs et groupes"""
    try:
        candidats = Candidat.objects.select_related('user').all().order_by('-date_inscription')
        
        data = []
        for c in candidats:
            # Récupérer les groupes de l'utilisateur
            groupes = []
            if c.user:
                groupes = [g.name for g in c.user.groups.all()]
            
            data.append({
                'id': c.id,
                'user_id': c.user.id if c.user else None,
                'username': c.user.username if c.user else None,
                'email': c.user.email if c.user else None,
                'nom': c.nom,
                'postnom': c.postnom,
                'prenom': c.prenom,
                'sexe': c.sexe,
                'nationalite': c.nationalite,
                'lieuNaissance': c.lieuNaissance,
                'ville': c.ville,
                'dateNaissance': c.dateNaissance.strftime('%d/%m/%Y'),
                'numeroTelephone': c.numeroTelephone,
                'quartier': c.quartier,
                'avenue': c.avenue or '',
                'date_inscription': c.date_inscription.strftime('%d/%m/%Y à %H:%M'),
                'groupes': groupes,
                'est_superuser': c.user.is_superuser if c.user else False
            })
        
        return JsonResponse({
            'success': True,
            'candidats': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def changer_role_candidat(request):
    """Changer le rôle d'un candidat (groupe utilisateur)"""
    try:
        data = json.loads(request.body)
        candidat_id = data.get('candidat_id')
        groupe_id = data.get('groupe_id')
        
        if not candidat_id:
            return JsonResponse({'success': False, 'message': 'Candidat non spécifié'}, status=400)
        
        if not groupe_id:
            return JsonResponse({'success': False, 'message': 'Groupe non spécifié'}, status=400)
        
        candidat = get_object_or_404(Candidat, id=candidat_id)
        
        if not candidat.user:
            return JsonResponse({'success': False, 'message': 'Cet utilisateur n\'a pas de compte associé'}, status=400)
        
        user = candidat.user
        nouveau_groupe = get_object_or_404(Group, id=groupe_id)
        
        # Supprimer tous les groupes existants
        user.groups.clear()
        
        # Ajouter le nouveau groupe
        user.groups.add(nouveau_groupe)
        
        return JsonResponse({
            'success': True,
            'message': f'Le rôle de {candidat.nom} {candidat.prenom} a été changé en "{nouveau_groupe.name}" avec succès',
            'nouveau_role': nouveau_groupe.name
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def supprimer_candidat(request, id_candidat):
    """Supprimer un candidat et son utilisateur associé"""
    try:
        candidat = get_object_or_404(Candidat, id=id_candidat)
        nom_complet = f"{candidat.nom} {candidat.prenom}"
        
        # Supprimer l'utilisateur associé s'il existe
        if candidat.user:
            user = candidat.user
            user.delete()
        
        # Supprimer le candidat
        candidat.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Le candidat "{nom_complet}" a été supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def get_all_groupes(request):
    """API pour récupérer tous les groupes disponibles"""
    try:
        groupes = Group.objects.all().order_by('name')
        data = [{
            'id': g.id,
            'name': g.name
        } for g in groupes]
        
        return JsonResponse({
            'success': True,
            'groupes': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)








# NOTHIFICATION

@csrf_exempt
@require_http_methods(["GET"])
def get_notifications(request):
    """API pour récupérer les notifications du candidat"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        candidat = get_object_or_404(Candidat, user=request.user)
        notifications = Notification.objects.filter(candidat=candidat).order_by('-date_creation')
        
        data = [{
            'id': n.id,
            'titre': n.titre,
            'message': n.message,
            'type': n.type_notification,
            'est_lu': n.est_lu,
            'date': n.date_creation.strftime('%d/%m/%Y à %H:%M'),
            'lien': n.lien
        } for n in notifications]
        
        non_lues = notifications.filter(est_lu=False).count()
        
        return JsonResponse({
            'success': True,
            'notifications': data,
            'non_lues': non_lues,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def marquer_notification_lue(request, id_notification):
    """Marquer une notification comme lue"""
    try:
        notification = get_object_or_404(Notification, id=id_notification)
        notification.est_lu = True
        notification.save()
        return JsonResponse({'success': True, 'message': 'Notification marquée comme lue'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def marquer_toutes_notifications_lues(request):
    """Marquer toutes les notifications comme lues"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        candidat = get_object_or_404(Candidat, user=request.user)
        Notification.objects.filter(candidat=candidat, est_lu=False).update(est_lu=True)
        return JsonResponse({'success': True, 'message': 'Toutes les notifications ont été marquées comme lues'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# DEMANDE CONGE


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import DemandeConge, Agent, TypeConge, Candidat
from datetime import datetime
import json

# ==================== PAGE DEMANDE CONGE ====================

def page_demande_conge(request):
    """Affiche la page principale des demandes de congé pour l'agent connecté"""
    return render(request, 'DemandeConge.html')


# ==================== API DEMANDES CONGE ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_mes_demandes_conge(request):
    """API pour récupérer les demandes de congé de l'agent connecté"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        # Récupérer l'agent associé à l'utilisateur connecté
        try:
            candidat = Candidat.objects.get(user=request.user)
            agent = Agent.objects.get(candidat=candidat)
        except (Candidat.DoesNotExist, Agent.DoesNotExist):
            return JsonResponse({'success': True, 'demandes': [], 'total': 0})
        
        demandes = DemandeConge.objects.filter(
            agent=agent
        ).select_related('type_conge').order_by('-date_demande')
        
        data = [{
            'id': d.id,
            'type_conge_id': d.type_conge.id,
            'type_conge_designation': d.type_conge.designation,
            'type_conge_duree': d.type_conge.duree,
            'motif': d.motif,
            'date_demande': d.date_demande.strftime('%d/%m/%Y à %H:%M'),
            'date_debut': d.date_debut.strftime('%d/%m/%Y'),
            'date_fin': d.date_fin.strftime('%d/%m/%Y'),
            'nombre_jours': d.nombre_jours
        } for d in demandes]
        
        return JsonResponse({
            'success': True,
            'demandes': data,
            'total': len(data),
            'agent_nom': f"{agent.candidat.nom} {agent.candidat.prenom}"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_all_demandes_conge_admin(request):
    """API pour récupérer toutes les demandes de congé (pour admin)"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        demandes = DemandeConge.objects.select_related(
            'agent', 'agent__candidat', 'type_conge'
        ).all().order_by('-date_demande')
        
        data = [{
            'id': d.id,
            'agent_id': d.agent.id,
            'agent_nom': f"{d.agent.candidat.nom} {d.agent.candidat.prenom}",
            'type_conge_id': d.type_conge.id,
            'type_conge_designation': d.type_conge.designation,
            'type_conge_duree': d.type_conge.duree,
            'motif': d.motif,
            'date_demande': d.date_demande.strftime('%d/%m/%Y à %H:%M'),
            'date_debut': d.date_debut.strftime('%d/%m/%Y'),
            'date_fin': d.date_fin.strftime('%d/%m/%Y'),
            'nombre_jours': d.nombre_jours
        } for d in demandes]
        
        return JsonResponse({
            'success': True,
            'demandes': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_types_conge(request):
    """API pour récupérer tous les types de congé disponibles"""
    try:
        types_conge = TypeConge.objects.all().order_by('designation')
        data = [{
            'id': t.id,
            'designation': t.designation,
            'duree': t.duree,
            'description': t.description or ''
        } for t in types_conge]
        
        return JsonResponse({'success': True, 'types_conge': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@csrf_exempt
@require_http_methods(["POST"])
def ajouter_demande_conge(request):
    """Ajouter une nouvelle demande de congé pour l'agent connecté"""
    try:
        data = json.loads(request.body)
        type_conge_id = data.get('type_conge_id')
        motif = data.get('motif', '').strip()
        date_debut = data.get('date_debut')
        date_fin = data.get('date_fin')
        
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Veuillez vous connecter'}, status=401)
        
        if not type_conge_id:
            return JsonResponse({'success': False, 'message': 'Type de congé non spécifié'}, status=400)
        
        if not motif:
            return JsonResponse({'success': False, 'message': 'Le motif est requis'}, status=400)
        
        if not date_debut:
            return JsonResponse({'success': False, 'message': 'La date de début est requise'}, status=400)
        
        if not date_fin:
            return JsonResponse({'success': False, 'message': 'La date de fin est requise'}, status=400)
        
        # Récupérer l'agent
        try:
            candidat = Candidat.objects.get(user=request.user)
            agent = Agent.objects.get(candidat=candidat)
        except (Candidat.DoesNotExist, Agent.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas enregistré comme agent'}, status=400)
        
        type_conge = get_object_or_404(TypeConge, id=type_conge_id)
        
        # Convertir les dates
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Format de date invalide'}, status=400)
        
        # Vérifier que la date de début est avant la date de fin
        if date_debut_obj > date_fin_obj:
            return JsonResponse({'success': False, 'message': 'La date de début doit être avant la date de fin'}, status=400)
        
        # Vérifier que la date de début n'est pas dans le passé
        if date_debut_obj < datetime.now().date():
            return JsonResponse({'success': False, 'message': 'La date de début ne peut pas être dans le passé'}, status=400)
        
        # Calculer le nombre de jours demandés
        delta = date_fin_obj - date_debut_obj
        nombre_jours = delta.days + 1
        
        # Vérifier que le nombre de jours ne dépasse pas la durée maximale
        if nombre_jours > type_conge.duree:
            return JsonResponse({'success': False, 'message': f'Le nombre de jours demandés ({nombre_jours}) dépasse la durée maximale de {type_conge.duree} jours'}, status=400)
        
        # Créer la demande
        demande = DemandeConge.objects.create(
            agent=agent,
            type_conge=type_conge,
            motif=motif,
            date_debut=date_debut_obj,
            date_fin=date_fin_obj
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Demande de congé "{type_conge.designation}" enregistrée avec succès',
            'demande': {
                'id': demande.id,
                'type_conge': type_conge.designation,
                'date_debut': date_debut_obj.strftime('%d/%m/%Y'),
                'date_fin': date_fin_obj.strftime('%d/%m/%Y'),
                'nombre_jours': nombre_jours
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def supprimer_demande_conge(request, id_demande):
    """Supprimer une demande de congé"""
    try:
        demande = get_object_or_404(DemandeConge, id=id_demande)
        
        # Vérifier que l'utilisateur connecté est l'agent qui a fait la demande
        if request.user.is_authenticated:
            try:
                candidat = Candidat.objects.get(user=request.user)
                agent = Agent.objects.get(candidat=candidat)
                if demande.agent.id != agent.id:
                    return JsonResponse({'success': False, 'message': 'Vous ne pouvez supprimer que vos propres demandes'}, status=403)
            except (Candidat.DoesNotExist, Agent.DoesNotExist):
                pass
        
        demande.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Demande de congé supprimée avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)






















# ==================== API CANDIDATURES AVEC TESTS NON EVALUES ====================





# ==================== API CANDIDAT - INFOS ====================
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_candidat_infos(request):
    """API pour récupérer les informations du candidat connecté"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        candidat = get_object_or_404(Candidat, user=request.user)
        
        data = {
            'id': candidat.id,
            'nom': candidat.nom,
            'postnom': candidat.postnom,
            'prenom': candidat.prenom,
            'sexe': candidat.sexe,
            'nationalite': candidat.nationalite,
            'lieuNaissance': candidat.lieuNaissance,
            'ville': candidat.ville,
            'dateNaissance': candidat.dateNaissance.strftime('%d/%m/%Y'),
            'numeroTelephone': candidat.numeroTelephone,
            'quartier': candidat.quartier,
            'avenue': candidat.avenue or ''
        }
        
        return JsonResponse({'success': True, 'candidat': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API CANDIDAT - MES EVALUATIONS ====================
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_mes_evaluations(request):
    """API pour récupérer les évaluations du candidat connecté"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        candidat = get_object_or_404(Candidat, user=request.user)
        
        # Récupérer toutes les candidatures du candidat
        candidatures = Candidature.objects.filter(candidat=candidat).values_list('id', flat=True)
        
        # Récupérer toutes les évaluations de ses candidatures
        evaluations = Evaluation.objects.filter(
            candidature_id__in=candidatures
        ).select_related('candidature', 'candidature__offre', 'candidature__offre__domaine', 'test').order_by('-date_evaluation')
        
        data = []
        for e in evaluations:
            data.append({
                'id': e.id,
                'offre_titre': e.candidature.offre.titre,
                'offre_domaine': e.candidature.offre.domaine.NomDomaine,
                'test_date': e.test.date_test.strftime('%d/%m/%Y'),
                'note': e.note,
                'observation': e.observation or '',
                'date_evaluation': e.date_evaluation.strftime('%d/%m/%Y à %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'evaluations': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)





from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import DemandeConge, AnalyseDemandeConge, Agent
from datetime import datetime
import json

# ==================== PAGE ANALYSE DEMANDES CONGE ====================
@login_required
def page_analyse_demandes_conge(request):
    """Affiche la page principale d'analyse des demandes de congé"""
    return render(request, 'AnalyseDemandeConge.html')


# ==================== API DEMANDES NON ANALYSEES ====================
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_demandes_non_analysees(request):
    """API pour récupérer les demandes de congé non encore analysées"""
    try:
        demandes_analysees = AnalyseDemandeConge.objects.values_list('demande_conge_id', flat=True)
        demandes = DemandeConge.objects.exclude(
            id__in=demandes_analysees
        ).select_related('agent', 'agent__candidat', 'type_conge').order_by('-date_demande')
        
        data = []
        for d in demandes:
            data.append({
                'id': d.id,
                'agent_id': d.agent.id,
                'agent_nom': f"{d.agent.candidat.nom} {d.agent.candidat.prenom}",
                'type_conge': d.type_conge.designation,
                'motif': d.motif,
                'date_demande': d.date_demande.strftime('%d/%m/%Y à %H:%M'),
                'date_debut': d.date_debut.strftime('%d/%m/%Y'),
                'date_fin': d.date_fin.strftime('%d/%m/%Y'),
                'nombre_jours': d.nombre_jours
            })
        
        return JsonResponse({
            'success': True,
            'demandes': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API DEMANDES ANALYSEES ====================
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_demandes_analysees(request):
    """API pour récupérer les demandes de congé déjà analysées"""
    try:
        analyses = AnalyseDemandeConge.objects.select_related(
            'demande_conge', 'demande_conge__agent', 'demande_conge__agent__candidat', 'demande_conge__type_conge'
        ).all().order_by('-date_analyse')
        
        data = []
        for a in analyses:
            data.append({
                'id': a.id,
                'demande_id': a.demande_conge.id,
                'agent_id': a.demande_conge.agent.id,
                'agent_nom': f"{a.demande_conge.agent.candidat.nom} {a.demande_conge.agent.candidat.prenom}",
                'type_conge': a.demande_conge.type_conge.designation,
                'motif_demande': a.demande_conge.motif,
                'date_demande': a.demande_conge.date_demande.strftime('%d/%m/%Y à %H:%M'),
                'date_debut': a.demande_conge.date_debut.strftime('%d/%m/%Y'),
                'date_fin': a.demande_conge.date_fin.strftime('%d/%m/%Y'),
                'nombre_jours': a.demande_conge.nombre_jours,
                'decision': a.decision,
                'motif_analyse': a.motif_analyse or '',
                'date_analyse': a.date_analyse.strftime('%d/%m/%Y à %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'analyses': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API ENREGISTRER ANALYSE ====================

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_analyse_demande(request):
    """Enregistrer l'analyse d'une demande de congé"""
    try:
        data = json.loads(request.body)
        demande_id = data.get('demande_id')
        decision = data.get('decision')
        motif_analyse = data.get('motif_analyse', '').strip()
        
        if not demande_id:
            return JsonResponse({'success': False, 'message': 'Demande non spécifiée'}, status=400)
        
        if not decision:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner une décision'}, status=400)
        
        demande = get_object_or_404(DemandeConge, id=demande_id)
        
        # Vérifier si une analyse existe déjà
        if AnalyseDemandeConge.objects.filter(demande_conge=demande).exists():
            return JsonResponse({'success': False, 'message': 'Cette demande a déjà été analysée'}, status=400)
        
        # Récupérer l'analyste (admin connecté)
        analyste = None
        if request.user.is_authenticated:
            try:
                candidat = Candidat.objects.get(user=request.user)
                analyste = Agent.objects.get(candidat=candidat)
            except (Candidat.DoesNotExist, Agent.DoesNotExist):
                pass
        
        # Créer l'analyse
        analyse = AnalyseDemandeConge.objects.create(
            demande_conge=demande,
            decision=decision,
            motif_analyse=motif_analyse,
            analyste=analyste
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Analyse enregistrée avec succès. Décision: {decision}',
            'analyse': {
                'id': analyse.id,
                'decision': analyse.decision,
                'motif_analyse': analyse.motif_analyse,
                'date_analyse': analyse.date_analyse.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API MODIFIER ANALYSE ====================

@csrf_exempt
@require_http_methods(["POST"])
def modifier_analyse_demande(request, id_analyse):
    """Modifier une analyse existante"""
    try:
        analyse = get_object_or_404(AnalyseDemandeConge, id=id_analyse)
        data = json.loads(request.body)
        
        decision = data.get('decision')
        motif_analyse = data.get('motif_analyse', '').strip()
        
        if decision:
            analyse.decision = decision
        
        analyse.motif_analyse = motif_analyse
        analyse.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Analyse modifiée avec succès. Nouvelle décision: {analyse.decision}',
            'analyse': {
                'id': analyse.id,
                'decision': analyse.decision,
                'motif_analyse': analyse.motif_analyse,
                'date_modification': analyse.date_modification.strftime('%d/%m/%Y à %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API SUPPRIMER ANALYSE ====================

@csrf_exempt
@require_http_methods(["POST"])
def supprimer_analyse_demande(request, id_analyse):
    """Supprimer une analyse"""
    try:
        analyse = get_object_or_404(AnalyseDemandeConge, id=id_analyse)
        analyse.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Analyse supprimée avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




# ANALYSE PERSONNELLE


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_analyse_by_demande(request, id_demande):
    """API pour récupérer l'analyse d'une demande de congé spécifique"""
    try:
        demande = get_object_or_404(DemandeConge, id=id_demande)
        
        try:
            analyse = demande.analyse
            data = {
                'id': analyse.id,
                'decision': analyse.decision,
                'motif_analyse': analyse.motif_analyse,
                'date_analyse': analyse.date_analyse.strftime('%d/%m/%Y à %H:%M'),
                'type_conge': demande.type_conge.designation,
                'date_debut': demande.date_debut.strftime('%d/%m/%Y'),
                'date_fin': demande.date_fin.strftime('%d/%m/%Y')
            }
            return JsonResponse({'success': True, 'analyse': data})
        except AnalyseDemandeConge.DoesNotExist:
            return JsonResponse({'success': True, 'analyse': None})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_mes_demandes_conge(request):
    """API pour récupérer les demandes de congé de l'agent connecté avec leur statut"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        try:
            candidat = Candidat.objects.get(user=request.user)
            agent = Agent.objects.get(candidat=candidat)
        except (Candidat.DoesNotExist, Agent.DoesNotExist):
            return JsonResponse({'success': True, 'demandes': [], 'total': 0, 'agent_nom': None})
        
        demandes = DemandeConge.objects.filter(
            agent=agent
        ).select_related('type_conge').order_by('-date_demande')
        
        data = []
        for d in demandes:
            # Récupérer le statut depuis l'analyse
            statut = 'en_attente'
            try:
                analyse = d.analyse
                statut = analyse.decision
                analyse_existe = True
            except AnalyseDemandeConge.DoesNotExist:
                analyse_existe = False
            
            data.append({
                'id': d.id,
                'type_conge_id': d.type_conge.id,
                'type_conge_designation': d.type_conge.designation,
                'type_conge_duree': d.type_conge.duree,
                'motif': d.motif,
                'date_demande': d.date_demande.strftime('%d/%m/%Y à %H:%M'),
                'date_debut': d.date_debut.strftime('%d/%m/%Y'),
                'date_fin': d.date_fin.strftime('%d/%m/%Y'),
                'nombre_jours': d.nombre_jours,
                'statut': statut,
                'analyse_existe': analyse_existe
            })
        
        return JsonResponse({
            'success': True,
            'demandes': data,
            'total': len(data),
            'agent_nom': f"{agent.candidat.nom} {agent.candidat.prenom}"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



# ==================== API UTILISATEUR CONNECTÉ ====================
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_utilisateur_infos(request):
    """API pour récupérer les informations de l'utilisateur connecté"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        user = request.user
        
        # Récupérer les infos du candidat
        try:
            candidat = Candidat.objects.get(user=user)
            data = {
                'id': candidat.id,
                'nom': candidat.nom,
                'postnom': candidat.postnom,
                'prenom': candidat.prenom,
                'sexe': candidat.sexe,
                'nationalite': candidat.nationalite,
                'lieuNaissance': candidat.lieuNaissance,
                'ville': candidat.ville,
                'dateNaissance': candidat.dateNaissance.strftime('%d/%m/%Y'),
                'dateNaissanceRaw': candidat.dateNaissance.strftime('%Y-%m-%d'),
                'telephone': candidat.numeroTelephone,
                'quartier': candidat.quartier,
                'avenue': candidat.avenue or '',
                'email': user.email,
                'username': user.username
            }
        except Candidat.DoesNotExist:
            data = {
                'id': None,
                'nom': '',
                'postnom': '',
                'prenom': user.first_name,
                'sexe': '',
                'nationalite': '',
                'lieuNaissance': '',
                'ville': '',
                'dateNaissance': '',
                'dateNaissanceRaw': '',
                'telephone': '',
                'quartier': '',
                'avenue': '',
                'email': user.email,
                'username': user.username
            }
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




@csrf_exempt
@require_http_methods(["POST"])
def modifier_utilisateur_infos(request):
    """API pour modifier les informations de l'utilisateur connecté"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        data = json.loads(request.body)
        
        nom = data.get('nom', '').strip()
        postnom = data.get('postnom', '').strip()
        prenom = data.get('prenom', '').strip()
        sexe = data.get('sexe', '').strip()
        nationalite = data.get('nationalite', '').strip()
        lieuNaissance = data.get('lieuNaissance', '').strip()
        ville = data.get('ville', '').strip()
        dateNaissance = data.get('dateNaissance', '').strip()
        telephone = data.get('telephone', '').strip()
        quartier = data.get('quartier', '').strip()
        avenue = data.get('avenue', '').strip()
        
        # Mettre à jour l'utilisateur
        user = request.user
        user.first_name = prenom
        user.last_name = f"{nom} {postnom}"
        user.save()
        
        # Mettre à jour ou créer le candidat
        candidat, created = Candidat.objects.update_or_create(
            user=user,
            defaults={
                'nom': nom,
                'postnom': postnom,
                'prenom': prenom,
                'sexe': sexe,
                'nationalite': nationalite,
                'lieuNaissance': lieuNaissance,
                'ville': ville,
                'dateNaissance': datetime.strptime(dateNaissance, '%Y-%m-%d').date(),
                'numeroTelephone': telephone,
                'quartier': quartier,
                'avenue': avenue if avenue else None
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Vos informations ont été mises à jour avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)





        # scanner



@csrf_exempt
@require_http_methods(["GET"])
def valider_agent(request, id_agent):
    """API pour vérifier l'authenticité d'un agent via QR code"""
    try:
        agent = get_object_or_404(Agent, id=id_agent)
        data = {
            'success': True,
            'agent': {
                'id': agent.id,
                'nom': agent.candidat.nom,
                'prenom': agent.candidat.prenom,
                'date_retenu': agent.date_retenu.strftime('%d/%m/%Y'),
                'statut': agent.statut
            },
            'message': 'Agent valide et reconnu par l\'ONEM'
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)






# MESSAGERIE VRAI SASA


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import Message, Conversation, MessagePieceJointe
from django.utils import timezone
import json
import os

# ==================== PERMISSIONS MESSAGERIE ====================
@login_required
def get_groupes_utilisateur(user):
    return [g.name for g in user.groups.all()]

def peut_envoyer_message(expediteur, destinataire):
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


# ==================== PAGE MESSAGERIE ====================

@login_required
def page_messagerie(request):
    return render(request, 'Messagerie.html')


# ==================== API CONVERSATIONS ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    try:
        user = request.user
        
        messages_envoyes = Message.objects.filter(
            expediteur=user, 
            date_suppression_expediteur__isnull=True
        ).values_list('destinataire_id', flat=True)
        
        messages_recus = Message.objects.filter(
            destinataire=user, 
            date_suppression_destinataire__isnull=True
        ).values_list('expediteur_id', flat=True)
        
        participants_ids = set(list(messages_envoyes) + list(messages_recus))
        
        conversations = []
        for participant_id in participants_ids:
            participant = User.objects.get(id=participant_id)
            
            dernier_message = Message.objects.filter(
                Q(expediteur=user, destinataire=participant, date_suppression_expediteur__isnull=True) |
                Q(expediteur=participant, destinataire=user, date_suppression_destinataire__isnull=True)
            ).order_by('-date_envoi').first()
            
            non_lus = Message.objects.filter(
                expediteur=participant,
                destinataire=user,
                est_lu=False,
                date_suppression_destinataire__isnull=True
            ).count()
            
            if dernier_message:
                conversations.append({
                    'participant_id': participant.id,
                    'participant_nom': participant.get_full_name() or participant.username,
                    'participant_username': participant.username,
                    'participant_groups': [g.name for g in participant.groups.all()],
                    'dernier_message': dernier_message.contenu[:100],
                    'dernier_message_date': dernier_message.date_envoi.strftime('%d/%m/%Y à %H:%M'),
                    'non_lus': non_lus
                })
        
        conversations.sort(key=lambda x: x['dernier_message_date'], reverse=True)
        
        return JsonResponse({'success': True, 'conversations': conversations, 'total': len(conversations)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API MESSAGES ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_messages(request, user_id):
    try:
        user = request.user
        autre = get_object_or_404(User, id=user_id)
        
        if not peut_envoyer_message(user, autre) and not peut_envoyer_message(autre, user):
            return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
        
        messages = Message.objects.filter(
            Q(expediteur=user, destinataire=autre, date_suppression_expediteur__isnull=True) |
            Q(expediteur=autre, destinataire=user, date_suppression_destinataire__isnull=True)
        ).order_by('date_envoi')
        
        Message.objects.filter(expediteur=autre, destinataire=user, est_lu=False).update(
            est_lu=True, 
            date_lu=timezone.now(),
            statut_destinataire='lu'
        )
        
        data = []
        for msg in messages:
            pieces_jointes = []
            for pj in msg.pieces_jointes.all():
                pieces_jointes.append({
                    'id': pj.id,
                    'nom': pj.nom_fichier,
                    'url': pj.fichier.url,
                    'type': pj.type_fichier,
                    'taille': pj.taille
                })
            
            data.append({
                'id': msg.id,
                'expediteur_id': msg.expediteur.id,
                'expediteur_nom': msg.expediteur.get_full_name() or msg.expediteur.username,
                'destinataire_id': msg.destinataire.id,
                'sujet': msg.sujet or '',
                'contenu': msg.contenu,
                'date_envoi': msg.date_envoi.strftime('%d/%m/%Y à %H:%M'),
                'est_modifie': msg.est_modifie,
                'est_lu': msg.est_lu,
                'est_moi': msg.expediteur.id == user.id,
                'pieces_jointes': pieces_jointes
            })
        
        return JsonResponse({
            'success': True,
            'messages': data,
            'autre_user': {
                'id': autre.id,
                'nom': autre.get_full_name() or autre.username,
                'username': autre.username,
                'groups': [g.name for g in autre.groups.all()]
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API DESTINATAIRES ====================

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_destinataires_possibles(request):
    """API: Récupérer les destinataires possibles pour la messagerie"""
    try:
        from django.db.models import Q
        
        user = request.user
        destinataires = None
        
        # SUPERUSER peut parler avec TOUS les utilisateurs
        if user.is_superuser:
            destinataires = User.objects.exclude(id=user.id)
        else:
            groupes = get_groupes_utilisateur(user)
            
            if 'CANDIDAT' in groupes:
                # CANDIDAT peut parler UNIQUEMENT avec les superusers
                destinataires = User.objects.filter(is_superuser=True).exclude(id=user.id)
            
            elif 'AGENT' in groupes:
                # AGENT peut parler avec les autres AGENTS et les superusers
                destinataires = User.objects.filter(
                    Q(groups__name='AGENT') | Q(is_superuser=True)
                ).exclude(id=user.id).distinct()
            
            elif 'ONEM' in groupes:
                # ONEM peut parler avec les autres ONEM et les superusers
                destinataires = User.objects.filter(
                    Q(groups__name='ONEM') | Q(is_superuser=True)
                ).exclude(id=user.id).distinct()
            
            else:
                # Aucun groupe reconnu, pas de destinataires
                destinataires = User.objects.none()
        
        # S'assurer que destinataires n'est pas None
        if destinataires is None:
            destinataires = User.objects.none()
        
        # Construction des données
        data = []
        for d in destinataires:
            data.append({
                'id': d.id,
                'nom': d.get_full_name() or d.username,
                'username': d.username,
                'email': d.email,
                'groups': [g.name for g in d.groups.all()]
            })
        
        return JsonResponse({
            'success': True, 
            'destinataires': data, 
            'total': len(data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)

# ==================== API ENVOYER MESSAGE ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def envoyer_message(request):
    try:
        data = json.loads(request.body)
        destinataire_id = data.get('destinataire_id')
        sujet = data.get('sujet', '').strip()
        contenu = data.get('contenu', '').strip()
        
        if not destinataire_id:
            return JsonResponse({'success': False, 'message': 'Destinataire requis'}, status=400)
        
        if not contenu:
            return JsonResponse({'success': False, 'message': 'Message vide'}, status=400)
        
        destinataire = get_object_or_404(User, id=destinataire_id)
        
        if not peut_envoyer_message(request.user, destinataire):
            return JsonResponse({'success': False, 'message': 'Vous ne pouvez pas envoyer à cet utilisateur'}, status=403)
        
        message = Message.objects.create(
            expediteur=request.user,
            destinataire=destinataire,
            sujet=sujet or 'Message',
            contenu=contenu
        )
        
        return JsonResponse({'success': True, 'message': 'Message envoyé', 'message_id': message.id})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API MODIFIER MESSAGE ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def modifier_message(request, id_message):
    try:
        message = get_object_or_404(Message, id=id_message)
        
        if message.expediteur.id != request.user.id:
            return JsonResponse({'success': False, 'message': 'Vous ne pouvez modifier que vos propres messages'}, status=403)
        
        data = json.loads(request.body)
        nouveau_contenu = data.get('contenu', '').strip()
        
        if not nouveau_contenu:
            return JsonResponse({'success': False, 'message': 'Le message ne peut pas être vide'}, status=400)
        
        message.modifier_message(nouveau_contenu)
        
        return JsonResponse({'success': True, 'message': 'Message modifié'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API SUPPRIMER MESSAGE ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def supprimer_message_pour_moi(request, id_message):
    try:
        message = get_object_or_404(Message, id=id_message)
        
        if message.expediteur.id != request.user.id and message.destinataire.id != request.user.id:
            return JsonResponse({'success': False, 'message': 'Action non autorisée'}, status=403)
        
        message.supprimer_pour_moi(request.user)
        
        return JsonResponse({'success': True, 'message': 'Message supprimé'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API SUPPRIMER TOUS LES MESSAGES ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def supprimer_tous_messages(request, user_id):
    try:
        user = request.user
        autre = get_object_or_404(User, id=user_id)
        
        messages = Message.objects.filter(
            Q(expediteur=user, destinataire=autre) |
            Q(expediteur=autre, destinataire=user)
        )
        
        for msg in messages:
            msg.supprimer_pour_moi(user)
        
        return JsonResponse({'success': True, 'message': 'Tous les messages ont été supprimés'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API UPLOAD FICHIER ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def upload_piece_jointe(request, id_message):
    try:
        message = get_object_or_404(Message, id=id_message)
        
        if message.expediteur.id != request.user.id:
            return JsonResponse({'success': False, 'message': 'Action non autorisée'}, status=403)
        
        fichier = request.FILES.get('fichier')
        if not fichier:
            return JsonResponse({'success': False, 'message': 'Aucun fichier'}, status=400)
        
        if fichier.size > 10 * 1024 * 1024:
            return JsonResponse({'success': False, 'message': 'Fichier trop volumineux (max 10MB)'}, status=400)
        
        ext = os.path.splitext(fichier.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            type_fichier = 'image'
        elif ext in ['.pdf']:
            type_fichier = 'pdf'
        elif ext in ['.doc', '.docx', '.txt', '.xls', '.xlsx']:
            type_fichier = 'document'
        else:
            type_fichier = 'autre'
        
        piece = MessagePieceJointe.objects.create(
            message=message,
            fichier=fichier,
            nom_fichier=fichier.name,
            type_fichier=type_fichier,
            taille=fichier.size
        )
        
        return JsonResponse({
            'success': True,
            'piece': {
                'id': piece.id,
                'nom': piece.nom_fichier,
                'url': piece.fichier.url,
                'type': piece.type_fichier,
                'taille': piece.taille
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API TELECHARGER FICHIER ====================

@login_required
@require_http_methods(["GET"])
def telecharger_fichier_message(request, id_piece):
    try:
        piece = get_object_or_404(MessagePieceJointe, id=id_piece)
        message = piece.message
        
        if request.user.id != message.expediteur.id and request.user.id != message.destinataire.id:
            return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
        
        if not os.path.exists(piece.fichier.path):
            return JsonResponse({'success': False, 'message': 'Fichier non trouvé'}, status=404)
        
        with open(piece.fichier.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{piece.nom_fichier}"'
            return response
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API NOMBRE MESSAGES NON LUS ====================

@login_required
def get_non_lus_count(request):
    try:
        count = Message.objects.filter(destinataire=request.user, est_lu=False).count()
        return JsonResponse({'success': True, 'non_lus': count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)





from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Agent, Candidat

@csrf_exempt
@require_http_methods(["GET"])
def valider_agent_qrcode(request, id_agent):
    """API pour valider un agent via QR code - Retourne la carte d'agent"""
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
            <title>Carte d'Agent - GRH</title>
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
                    margin: 0 auto;
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
                .carte-header h3 {{ margin: 0; font-size: 16px; }}
                .carte-header small {{ font-size: 10px; opacity: 0.8; }}
                .carte-body {{ padding: 20px; display: flex; gap: 20px; }}
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
                .carte-info .nom {{ font-size: 16px; font-weight: 700; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 6px; }}
                .carte-info .info-row {{ margin-bottom: 6px; font-size: 11px; }}
                .carte-info .info-label {{ display: inline-block; width: 70px; opacity: 0.7; }}
                .carte-footer {{
                    background: rgba(0,0,0,0.3); padding: 12px 20px;
                    display: flex; justify-content: space-between; align-items: center;
                }}
                .carte-footer .badge {{ background: #27ae60; padding: 3px 12px; border-radius: 20px; font-size: 10px; }}
                .carte-footer .date-info {{ font-size: 9px; opacity: 0.7; }}
                @media (max-width: 576px) {{
                    .carte-body {{ flex-direction: column; align-items: center; text-align: center; }}
                    .carte-info .info-label {{ width: auto; }}
                }}
            </style>
        </head>
        <body>
            <div class="carte-agent">
                <div class="carte-header">
                    <h3><i class="fas fa-building"></i> GRH ENGENNERING SARL</h3>
                    <small>RDC - Goma - N°{agent.id}</small>
                </div>
                <div class="carte-body">
                    <div class="carte-photo">
                        {'<img src="' + photo_url + '">' if photo_url else '<div class="no-photo">' + candidat.prenom[0] + candidat.nom[0] + '</div>'}
                    </div>
                    <div class="carte-info">
                        <div class="nom">{candidat.nom} {candidat.postnom} {candidat.prenom}</div>
                        <div class="info-row"><span class="info-label">Sexe :</span> <span class="info-value">{candidat.sexe}</span></div>
                        <div class="info-row"><span class="info-label">Tél :</span> <span class="info-value">{candidat.numeroTelephone}</span></div>
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
        return HttpResponse("<h1>❌ Agent non trouvé</h1>", status=404)




@csrf_exempt
@require_http_methods(["GET"])
def get_agent_photo(request, id_agent):
    """Récupérer la photo d'un agent (via son candidat associé)"""
    try:
        agent = get_object_or_404(Agent, id=id_agent)
        candidat = agent.candidat
        
        if candidat.photo:
            return JsonResponse({'success': True, 'photo_url': candidat.photo.url})
        else:
            return JsonResponse({'success': False, 'photo_url': None})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)







# EVALUATION


# ==================== FONCTIONS UTILITAIRES POUR LA PROMOTION AGENT ====================

from datetime import datetime
import random

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


def generer_matricule():
    """Génère un matricule unique pour un agent"""
    annee = datetime.now().year
    mois = datetime.now().month
    random_num = random.randint(100, 999)
    matricule = f"GRH-{annee}{mois:02d}-{random_num}"
    
    # Éviter les doublons
    while Agent.objects.filter(matricule=matricule).exists():
        random_num = random.randint(100, 999)
        matricule = f"GRH-{annee}{mois:02d}-{random_num}"
    
    return matricule


def verifier_et_promouvoir_agent(candidature):
    """
    Vérifie si le candidat a une moyenne >= 70% après tous les tests.
    Si oui, envoie un message d'admissibilité (sans créer l'agent).
    L'agent sera créé manuellement par l'admin après interview.
    """
    offre = candidature.offre
    tous_les_tests = Test.objects.filter(offre=offre)
    nombre_tests = tous_les_tests.count()
    
    if nombre_tests == 0:
        return "Aucun test défini pour cette offre.", None
    
    evaluations_existantes = Evaluation.objects.filter(candidature=candidature)
    evaluations_count = evaluations_existantes.count()
    
    # Si tous les tests ne sont pas encore évalués
    if evaluations_count < nombre_tests:
        restant = nombre_tests - evaluations_count
        return f"Encore {restant} test(s) à évaluer.", None
    
    # Tous les tests sont évalués, calculer la moyenne
    toutes_notes = evaluations_existantes.values_list('note', flat=True)
    moyenne = sum(toutes_notes) / len(toutes_notes)
    
    if moyenne >= 70:
        # 🔐 MODIFICATION : Le candidat n'est PAS promu agent automatiquement
        # Envoyer seulement l'email d'admissibilité (félicitations + invitation à attendre l'interview)
        
        from .utils import notifier_candidat_admissible
        base_url = "https://mahoridi.pythonanywhere.com/"  # Votre domaine
        email_envoye, email_msg = notifier_candidat_admissible(
            candidature, moyenne, base_url
        )
        
        if email_envoye:
            return f"✅ Candidat admissible ! (Moyenne: {moyenne:.2f}%) - Email envoyé", {
                'admissible': True,
                'moyenne': moyenne,
                'email_envoye': email_envoye
            }
        else:
            return f"✅ Candidat admissible (Moyenne: {moyenne:.2f}%) - ⚠️ Email: {email_msg}", {
                'admissible': True,
                'moyenne': moyenne,
                'email_envoye': email_envoye
            }
    else:
        # Moyenne insuffisante
        return f"❌ Moyenne {moyenne:.2f}% < 70% - Non admissible", {
            'admissible': False, 
            'moyenne': moyenne
        }






# ==================== API: CANDIDATURES AVEC TESTS À ÉVALUER ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_candidatures_tests(request):
    """API: Récupérer les candidatures acceptées avec leurs tests"""
    try:
        try:
            type_decision_accepter = TypeDecision.objects.get(Description__icontains='Accepter')
        except TypeDecision.DoesNotExist:
            return JsonResponse({'success': True, 'candidatures': [], 'total': 0})
        
        decisions_acceptees = Decision.objects.filter(
            type_decision=type_decision_accepter
        ).select_related('candidature', 'candidature__candidat', 'candidature__offre', 'candidature__offre__domaine')
        
        data = []
        for d in decisions_acceptees:
            candidature = d.candidature
            offre = candidature.offre
            
            tous_les_tests = Test.objects.filter(offre=offre).order_by('date_test')
            
            tests_data = []
            for test in tous_les_tests:
                evaluation_exists = Evaluation.objects.filter(candidature=candidature, test=test).exists()
                evaluation = Evaluation.objects.filter(candidature=candidature, test=test).first()
                
                tests_data.append({
                    'id': test.id,
                    'date_test': test.date_test.strftime('%d/%m/%Y à %H:%M'),
                    'nom_fichier': test.filename(),
                    'est_evalue': evaluation_exists,
                    'note': evaluation.note if evaluation else None,
                })
            
            tests_evalues = len([t for t in tests_data if t['est_evalue']])
            nombre_tests = len(tests_data)
            evaluation_complete = tests_evalues >= nombre_tests if nombre_tests > 0 else True
            
            data.append({
                'id': candidature.id,
                'candidat_nom': f"{candidature.candidat.nom} {candidature.candidat.postnom} {candidature.candidat.prenom}",
                'offre_id': offre.id,
                'offre_titre': offre.titre,
                'offre_domaine': offre.domaine.NomDomaine,
                'date_candidature': candidature.date_soumission.strftime('%d/%m/%Y'),
                'cv_url': candidature.cv.url if candidature.cv else None,
                'tests': tests_data,
                'nombre_tests': nombre_tests,
                'tests_evalues': tests_evalues,
                'evaluation_complete': evaluation_complete
            })
        
        return JsonResponse({'success': True, 'candidatures': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API: RÉCUPÉRER LES TESTS D'UNE OFFRE ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_tests_by_offre_evaluation(request, id_offre):
    """API: Récupérer tous les tests d'une offre pour évaluation"""
    try:
        tests = Test.objects.filter(offre_id=id_offre).order_by('date_test')
        data = [{
            'id': t.id,
            'date_test': t.date_test.strftime('%d/%m/%Y à %H:%M'),
            'nom_fichier': t.filename(),
        } for t in tests]
        return JsonResponse({'success': True, 'tests': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API: RÉCUPÉRER LES ÉVALUATIONS D'UNE CANDIDATURE ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_evaluations_by_candidature(request, id_candidature):
    """API: Récupérer les évaluations d'une candidature"""
    try:
        evaluations = Evaluation.objects.filter(
            candidature_id=id_candidature
        ).select_related('test').order_by('-date_evaluation')
        
        data = [{
            'id': e.id,
            'test_id': e.test.id,
            'test_nom': e.test.filename(),
            'note': e.note,
            'observation': e.observation,
            'date_evaluation': e.date_evaluation.strftime('%d/%m/%Y à %H:%M')
        } for e in evaluations]
        
        return JsonResponse({'success': True, 'evaluations': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== API: ENREGISTRER UNE ÉVALUATION ====================

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_evaluation(request):
    """API: Enregistrer une évaluation pour une candidature et un test"""
    try:
        data = json.loads(request.body)
        candidature_id = data.get('candidature_id')
        test_id = data.get('test_id')
        observation = data.get('observation', '').strip()
        note = data.get('note')
        
        if not candidature_id:
            return JsonResponse({'success': False, 'message': 'Candidature non spécifiée'}, status=400)
        
        if not test_id:
            return JsonResponse({'success': False, 'message': 'Test non spécifié'}, status=400)
        
        if note is None:
            return JsonResponse({'success': False, 'message': 'La note est requise'}, status=400)
        
        try:
            note = float(note)
            if note < 0 or note > 100:
                return JsonResponse({'success': False, 'message': 'La note doit être entre 0 et 100'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Note invalide'}, status=400)
        
        candidature = get_object_or_404(Candidature, id=candidature_id)
        test = get_object_or_404(Test, id=test_id)
        
        # Vérifier que le test appartient à l'offre
        if test.offre.id != candidature.offre.id:
            return JsonResponse({'success': False, 'message': 'Ce test ne correspond pas à l\'offre'}, status=400)
        
        # Vérifier que la candidature est acceptée
        try:
            type_decision_accepter = TypeDecision.objects.get(Description__icontains='Accepter')
            if not Decision.objects.filter(candidature=candidature, type_decision=type_decision_accepter).exists():
                return JsonResponse({'success': False, 'message': 'Cette candidature n\'a pas été acceptée'}, status=400)
        except TypeDecision.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Type "Accepter" non configuré'}, status=400)
        
        # Vérifier les doublons
        if Evaluation.objects.filter(candidature=candidature, test=test).exists():
            return JsonResponse({'success': False, 'message': 'Ce test a déjà été évalué'}, status=400)
        
        # Créer l'évaluation
        evaluation = Evaluation.objects.create(
            candidature=candidature,
            test=test,
            observation=observation,
            note=note
        )
        
        # Vérifier la promotion
        message_promotion, promotion_info = verifier_et_promouvoir_agent(candidature)
        
        return JsonResponse({
            'success': True,
            'message': f'Évaluation enregistrée. Note: {note}%',
            'evaluation': {
                'id': evaluation.id,
                'note': evaluation.note,
                'observation': evaluation.observation,
                'date_evaluation': evaluation.date_evaluation.strftime('%d/%m/%Y à %H:%M')
            },
            'promotion_message': message_promotion,
            'promotion_info': promotion_info
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API: MODIFIER UNE ÉVALUATION ====================

@csrf_exempt
@require_http_methods(["POST"])
def modifier_evaluation(request, id_evaluation):
    """API: Modifier une évaluation existante"""
    try:
        evaluation = get_object_or_404(Evaluation, id=id_evaluation)
        data = json.loads(request.body)
        
        observation = data.get('observation', '').strip()
        note = data.get('note')
        
        if note is not None:
            try:
                note = float(note)
                if note < 0 or note > 100:
                    return JsonResponse({'success': False, 'message': 'Note entre 0 et 100'}, status=400)
                evaluation.note = note
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Note invalide'}, status=400)
        
        evaluation.observation = observation
        evaluation.save()
        
        # Re-vérifier la promotion
        candidature = evaluation.candidature
        message_promotion, promotion_info = verifier_et_promouvoir_agent(candidature)
        
        return JsonResponse({
            'success': True,
            'message': 'Évaluation modifiée',
            'evaluation': {
                'id': evaluation.id,
                'note': evaluation.note,
                'observation': evaluation.observation,
                'date_evaluation': evaluation.date_evaluation.strftime('%d/%m/%Y à %H:%M')
            },
            'promotion_message': message_promotion,
            'promotion_info': promotion_info
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API: LISTE DES ÉVALUATIONS EFFECTUÉES ====================
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_evaluations_effectuees(request):
    """API: Récupérer toutes les évaluations effectuées"""
    try:
        evaluations = Evaluation.objects.select_related(
            'candidature', 
            'candidature__candidat',
            'candidature__offre', 
            'candidature__offre__domaine',
            'test'
        ).all().order_by('-date_evaluation')
        
        data = []
        for e in evaluations:
            est_agent = Agent.objects.filter(candidat=e.candidature.candidat, statut='Approuvé').exists()
            
            data.append({
                'id': e.id,
                'candidature_id': e.candidature.id,
                'candidat_nom': f"{e.candidature.candidat.nom} {e.candidature.candidat.postnom} {e.candidature.candidat.prenom}",
                'offre_titre': e.candidature.offre.titre,
                'offre_domaine': e.candidature.offre.domaine.NomDomaine,
                'test_date': e.test.date_test.strftime('%d/%m/%Y'),
                'note': e.note,
                'observation': e.observation or '',
                'date_evaluation': e.date_evaluation.strftime('%d/%m/%Y à %H:%M'),
                'est_agent': est_agent
            })
        
        return JsonResponse({'success': True, 'evaluations': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




# CADRE DE DEMANDE CONGE AGENT
@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_agent_infos(request):
    """API pour récupérer les informations de l'agent connecté (date de recrutement)"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        try:
            candidat = Candidat.objects.get(user=request.user)
            agent = Agent.objects.get(candidat=candidat)
            
            return JsonResponse({
                'success': True,
                'agent': {
                    'id': agent.id,
                    'date_retenu': agent.date_retenu.strftime('%Y-%m-%d'),
                    'statut': agent.statut
                }
            })
        except (Candidat.DoesNotExist, Agent.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Agent non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



# dashboard admin

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def admin_dashboard_stats(request):
    """API pour récupérer toutes les statistiques du dashboard admin"""
    try:
        from datetime import date
        
        today = date.today()
        
        # Statistiques des candidats et agents
        total_candidats = Candidat.objects.count()
        total_agents = Agent.objects.filter(statut='Approuvé').count()
        
        # Statistiques des candidatures
        type_decision_accepter = TypeDecision.objects.filter(Description__icontains='Accepter').first()
        type_decision_rejeter = TypeDecision.objects.filter(Description__icontains='Rejeter').first()
        
        if type_decision_accepter:
            candidatures_acceptees = Decision.objects.filter(type_decision=type_decision_accepter).count()
        else:
            candidatures_acceptees = 0
            
        if type_decision_rejeter:
            candidatures_rejetees = Decision.objects.filter(type_decision=type_decision_rejeter).count()
        else:
            candidatures_rejetees = 0
        
        candidatures_avec_decision = Decision.objects.values_list('candidature_id', flat=True)
        candidatures_non_traitees = Candidature.objects.exclude(id__in=candidatures_avec_decision).count()
        
        # Statistiques des tests
        total_tests = Test.objects.count()
        
        # Statistiques des offres ONEM
        total_offres = OffreEmploie.objects.count()
        offres_traitees = Onem.objects.count()
        offres_non_traitees = total_offres - offres_traitees
        
        decision_acceptee = DecisionOnem.objects.filter(Description__icontains='Accepter').first()
        decision_refusee = DecisionOnem.objects.filter(Description__icontains='Refuser').first()
        
        if decision_acceptee:
            offres_acceptees = Onem.objects.filter(decision=decision_acceptee).count()
        else:
            offres_acceptees = 0
            
        if decision_refusee:
            offres_refusees = Onem.objects.filter(decision=decision_refusee).count()
        else:
            offres_refusees = 0
        
        # Statistiques des états d'offres
        offres_actives = 0
        offres_expirees = 0
        offres_stoppees = 0
        offres_non_parametrees = 0
        
        for offre in OffreEmploie.objects.all():
            try:
                reglage = offre.reglage
                type_etat = reglage.type_etat.designation
                date_expiration = reglage.date_expiration
                
                if type_etat == 'Stopper':
                    offres_stoppees += 1
                elif type_etat in ['Actif', 'Renouveler']:
                    if date_expiration and date_expiration < today:
                        offres_expirees += 1
                    else:
                        offres_actives += 1
                else:
                    offres_non_parametrees += 1
            except ReglageOffre.DoesNotExist:
                offres_non_parametrees += 1
        
        # Moyenne des évaluations
        evaluations = Evaluation.objects.all()
        if evaluations.exists():
            moyenne_evaluations = sum(e.note for e in evaluations) / evaluations.count()
        else:
            moyenne_evaluations = 0
        
        return JsonResponse({
            'success': True,
            'total_candidats': total_candidats,
            'total_agents': total_agents,
            'candidatures_acceptees': candidatures_acceptees,
            'candidatures_rejetees': candidatures_rejetees,
            'candidatures_non_traitees': candidatures_non_traitees,
            'total_tests': total_tests,
            'offres_traitees': offres_traitees,
            'offres_non_traitees': offres_non_traitees,
            'total_offres': total_offres,
            'offres_acceptees': offres_acceptees,
            'offres_refusees': offres_refusees,
            'offres_actives': offres_actives,
            'offres_expirees': offres_expirees,
            'offres_stoppees': offres_stoppees,
            'offres_non_parametrees': offres_non_parametrees,
            'moyenne_evaluations': round(moyenne_evaluations, 1)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)




#COMMUNIQUE


# views.py - Ajoutez ces fonctions

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_utilisateurs_communication(request):
    """API: Récupérer tous les utilisateurs pour la communication"""
    try:
        from django.contrib.auth.models import User
        
        utilisateurs = User.objects.filter(is_active=True).exclude(is_superuser=True)
        data = []
        
        for user in utilisateurs:
            groupes = [g.name for g in user.groups.all()]
            data.append({
                'id': user.id,
                'nom': f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                'email': user.email,
                'groupes': ', '.join(groupes) if groupes else 'Aucun'
            })
        
        return JsonResponse({'success': True, 'utilisateurs': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_offres_communication(request):
    """API: Récupérer les offres avec nombre de candidats acceptés"""
    try:
        type_decision_accepter = TypeDecision.objects.filter(Description__icontains='Accepter').first()
        
        offres = OffreEmploie.objects.all()
        data = []
        
        for offre in offres:
            if type_decision_accepter:
                nb_candidats = Decision.objects.filter(
                    candidature__offre=offre,
                    type_decision=type_decision_accepter
                ).count()
            else:
                nb_candidats = 0
            
            data.append({
                'id': offre.id,
                'titre': offre.titre,
                'nb_candidats': nb_candidats
            })
        
        return JsonResponse({'success': True, 'offres': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def envoyer_communication(request):
    """API: Envoyer un message par email"""
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        from django.contrib.auth.models import User
        from django.core.mail import send_mail
        
        data = json.loads(request.body)
        type_dest = data.get('type')
        objet = data.get('objet', '').strip()
        contenu = data.get('contenu', '').strip()
        
        if not objet or not contenu:
            return JsonResponse({'success': False, 'message': 'Objet et message requis'}, status=400)
        
        destinataires_emails = []
        message_detail = ""
        
        if type_dest == 'utilisateur':
            # Envoyer à un utilisateur spécifique
            user_id = data.get('destinataire_id')
            user = User.objects.get(id=user_id)
            if user.email:
                destinataires_emails.append(user.email)
                message_detail = f"à {user.get_full_name() or user.username} ({user.email})"
            else:
                return JsonResponse({'success': False, 'message': 'Cet utilisateur n\'a pas d\'email'}, status=400)
        
        elif type_dest == 'groupe':
            # Envoyer à tout un groupe
            groupe_nom = data.get('groupe')
            utilisateurs = User.objects.filter(groups__name=groupe_nom, is_active=True)
            
            for user in utilisateurs:
                if user.email:
                    destinataires_emails.append(user.email)
            
            if not destinataires_emails:
                return JsonResponse({'success': False, 'message': f'Aucun utilisateur trouvé dans le groupe {groupe_nom}'}, status=400)
            
            message_detail = f"au groupe {groupe_nom} ({len(destinataires_emails)} destinataires)"
        
        elif type_dest == 'candidats_acceptes':
            # Envoyer aux candidats acceptés pour une offre
            offre_id = data.get('offre_id')
            offre = OffreEmploie.objects.get(id=offre_id)
            
            type_decision_accepter = TypeDecision.objects.get(Description__icontains='Accepter')
            decisions = Decision.objects.filter(
                candidature__offre=offre,
                type_decision=type_decision_accepter
            ).select_related('candidature__candidat__user')
            
            for decision in decisions:
                user = decision.candidature.candidat.user
                if user.email:
                    destinataires_emails.append(user.email)
            
            if not destinataires_emails:
                return JsonResponse({'success': False, 'message': f'Aucun candidat accepté pour l\'offre "{offre.titre}"'}, status=400)
            
            message_detail = f"aux candidats acceptés pour l'offre \"{offre.titre}\" ({len(destinataires_emails)} destinataires)"
        
        else:
            return JsonResponse({'success': False, 'message': 'Type de destinataire invalide'}, status=400)
        
        # Construction du message HTML
        base_url = "https://mahoridi.pythonanywhere.com"
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{objet}</title>
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
                .message-box {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                }}
                .btn {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 10px 25px;
                    text-decoration: none;
                    border-radius: 25px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 GRH ENGINEERING</h1>
                    <p>Communication officielle</p>
                </div>
                <div class="content">
                    <h2>Bonjour,</h2>
                    <div class="message-box">
                        {contenu.replace(chr(10), '<br>')}
                    </div>
                    <p style="text-align: center;">
                        <a href="{base_url}/Appl/login" class="btn">🔗 Se connecter</a>
                    </p>
                </div>
                <div class="footer">
                    <p>GRH ENGINEERING SARL - RDC, Goma</p>
                    <p>Cet email est automatique, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Envoyer les emails
        emails_envoyes = 0
        erreurs = []
        
        for email in destinataires_emails:
            try:
                plain_message = strip_tags(html_message)
                email_msg = EmailMultiAlternatives(
                    subject=objet,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                email_msg.attach_alternative(html_message, "text/html")
                email_msg.send()
                emails_envoyes += 1
            except Exception as e:
                erreurs.append(f"{email}: {str(e)}")
        
        if emails_envoyes > 0:
            return JsonResponse({
                'success': True,
                'message': f'✅ Message envoyé {message_detail}<br>📧 {emails_envoyes} email(s) envoyé(s) avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'❌ Aucun email envoyé. Erreurs: {", ".join(erreurs)}'
            }, status=400)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def ChargerCommunication(request):
    """Page de communication"""
    return render(request, "Appl/Communiquer.html")




# TYPE DECISION OFFRE

# ==================== GESTION DES TYPES DE DÉCISION ====================
@login_required
def TypeDecisionOffrePage(request):
    """Affiche la page principale des types de décision"""
    return render(request, 'TypeDecisionOffre.html')


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def TypeDecisionOffreLister(request):
    """API: Récupérer tous les types de décision"""
    try:
        types_decision = TypeDecision.objects.all().order_by('-id')
        data = [{
            'id': td.id,
            'Description': td.Description,
        } for td in types_decision]
        
        return JsonResponse({
            'success': True,
            'type_decisions': data,
            'total': len(data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def TypeDecisionOffreAjouter(request):
    """API: Ajouter un nouveau type de décision"""
    try:
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        
        # Vérifier si le type de décision existe déjà
        if TypeDecision.objects.filter(Description__iexact=description).exists():
            return JsonResponse({'success': False, 'message': 'Ce type de décision existe déjà'}, status=400)
        
        type_decision = TypeDecision.objects.create(Description=description)
        
        return JsonResponse({
            'success': True,
            'message': f'Type de décision "{description}" ajouté avec succès',
            'type_decision': {
                'id': type_decision.id,
                'Description': type_decision.Description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def TypeDecisionOffreModifier(request, id_type_decision):
    """API: Modifier un type de décision existant"""
    try:
        type_decision = get_object_or_404(TypeDecision, id=id_type_decision)
        data = json.loads(request.body)
        description = data.get('Description', '').strip()
        
        if not description:
            return JsonResponse({'success': False, 'message': 'La description est requise'}, status=400)
        
        # Vérifier si une autre décision a déjà cette description
        if TypeDecision.objects.filter(Description__iexact=description).exclude(id=id_type_decision).exists():
            return JsonResponse({'success': False, 'message': 'Ce type de décision existe déjà'}, status=400)
        
        ancienne_description = type_decision.Description
        type_decision.Description = description
        type_decision.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Type de décision "{ancienne_description}" modifié avec succès',
            'type_decision': {
                'id': type_decision.id,
                'Description': type_decision.Description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def TypeDecisionOffreSupprimer(request, id_type_decision):
    """API: Supprimer un type de décision"""
    try:
        type_decision = get_object_or_404(TypeDecision, id=id_type_decision)
        description = type_decision.Description
        type_decision.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Type de décision "{description}" supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def TypeDecisionOffreSelectionner(request, id_type_decision):
    """API: Sélectionner un type de décision spécifique"""
    try:
        type_decision = get_object_or_404(TypeDecision, id=id_type_decision)
        
        return JsonResponse({
            'success': True,
            'type_decision': {
                'id': type_decision.id,
                'Description': type_decision.Description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# ENREGISTREMENT AGENT MANUELLEMENT

# views.py - Ajoutez ces fonctions

@csrf_exempt
@require_http_methods(["GET"])
def get_candidats_non_agents(request):
    """API: Récupérer les candidats qui ne sont pas encore agents"""
    try:
        # Récupérer les IDs des candidats qui sont déjà agents
        agents_ids = Agent.objects.values_list('candidat_id', flat=True)
        
        # Récupérer les candidats qui ne sont pas agents
        candidats = Candidat.objects.exclude(id__in=agents_ids).select_related('user')
        
        data = []
        for c in candidats:
            data.append({
                'id': c.id,
                'nom': c.nom,
                'postnom': c.postnom,
                'prenom': c.prenom,
                'sexe': c.sexe,
                'telephone': c.numeroTelephone,
                'email': c.user.email if c.user else None
            })
        
        return JsonResponse({'success': True, 'candidats': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ajouter_agent(request):
    """API: Ajouter un agent à partir d'un candidat existant"""
    try:
        from django.contrib.auth.models import Group
        from datetime import datetime
        
        data = json.loads(request.body)
        candidat_id = data.get('candidat_id')
        date_retenu = data.get('date_retenu')
        
        if not candidat_id:
            return JsonResponse({'success': False, 'message': 'Candidat non spécifié'}, status=400)
        
        if not date_retenu:
            return JsonResponse({'success': False, 'message': 'Date de recrutement requise'}, status=400)
        
        # Récupérer le candidat
        candidat = get_object_or_404(Candidat, id=candidat_id)
        
        # Vérifier si le candidat est déjà agent
        if Agent.objects.filter(candidat=candidat).exists():
            return JsonResponse({'success': False, 'message': 'Ce candidat est déjà agent'}, status=400)
        
        # Convertir la date
        try:
            date_retenu_obj = datetime.strptime(date_retenu, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Format de date invalide'}, status=400)
        
        # Générer un matricule unique
        import random
        matricule = f"GRH-{candidat.id}-{random.randint(1000, 9999)}"
        while Agent.objects.filter(matricule=matricule).exists():
            matricule = f"GRH-{candidat.id}-{random.randint(1000, 9999)}"
        
        # Créer l'agent
        agent = Agent.objects.create(
            candidat=candidat,
            date_retenu=date_retenu_obj,
            statut='Approuvé',
            contrat_signe=False,
            matricule=matricule
        )
        
        # Changer le groupe de l'utilisateur de CANDIDAT à AGENT
        user = candidat.user
        email_envoye = False
        email_message = ""
        
        if user:
            # Retirer du groupe CANDIDAT
            groupe_candidat = Group.objects.filter(name='CANDIDAT').first()
            if groupe_candidat:
                user.groups.remove(groupe_candidat)
            
            # Ajouter au groupe AGENT
            groupe_agent, _ = Group.objects.get_or_create(name='AGENT')
            user.groups.add(groupe_agent)
            user.is_staff = True
            user.save()
            
            # ========== ENVOYER L'EMAIL DE NOTIFICATION ==========
            from .utils import notifier_promotion_agent_manuel
            base_url = "https://mahoridi.pythonanywhere.com"  # Votre domaine
            email_envoye, email_message = notifier_promotion_agent_manuel(agent, base_url)
            # =====================================================
        
        return JsonResponse({
            'success': True,
            'message': f'Agent ajouté avec succès ! Matricule: {matricule}',
            'agent': {
                'id': agent.id,
                'matricule': agent.matricule,
                'date_retenu': agent.date_retenu.strftime('%d/%m/%Y')
            },
            'email_envoye': email_envoye,
            'email_message': email_message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



@csrf_exempt
@require_http_methods(["POST"])
def modifier_date_recrutement(request):
    """API: Modifier la date de recrutement d'un agent"""
    try:
        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        date_retenu = data.get('date_retenu')
        
        if not agent_id:
            return JsonResponse({'success': False, 'message': 'Agent non spécifié'}, status=400)
        
        if not date_retenu:
            return JsonResponse({'success': False, 'message': 'Date de recrutement requise'}, status=400)
        
        agent = get_object_or_404(Agent, id=agent_id)
        
        # Convertir la date
        try:
            from datetime import datetime
            date_retenu_obj = datetime.strptime(date_retenu, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Format de date invalide'}, status=400)
        
        # Sauvegarder l'ancienne date
        ancienne_date = agent.date_retenu.strftime('%d/%m/%Y') if agent.date_retenu else "Non définie"
        
        # Mettre à jour la date (contourner auto_now_add)
        agent.date_retenu = date_retenu_obj
        agent.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Date de recrutement modifiée avec succès : {ancienne_date} → {date_retenu_obj.strftime("%d/%m/%Y")}',
            'agent': {
                'id': agent.id,
                'date_retenu': agent.date_retenu.strftime('%d/%m/%Y')
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# ==================== GESTION DES INTERVIEWS ====================
# ==================== GESTION DES INTERVIEWS ====================

def page_interviews(request):
    """Affiche la page principale des interviews"""
    offres = OffreEmploie.objects.filter(onem__decision__Description__icontains='Accepter')
    
    # DEBUG - Afficher dans la console
    print(f"Nombre d'offres trouvées: {offres.count()}")
    for offre in offres:
        print(f"Offre: {offre.titre} - Décision: {offre.onem_set.first().decision.Description if offre.onem_set.first() else 'Aucune'}")
    
    return render(request, 'Appl/Interviews.html', {'offres': offres})


@csrf_exempt
@require_http_methods(["GET"])
def get_candidats_admissibles_par_offre(request, id_offre):
    """API: Récupérer les candidats admissibles (moyenne ≥ 70%) pour une offre"""
    try:
        # Récupérer les candidatures acceptées pour cette offre
        type_decision_accepter = TypeDecision.objects.filter(Description__icontains='Accepter').first()
        
        if not type_decision_accepter:
            return JsonResponse({'success': False, 'message': 'Type décision non trouvé'}, status=400)
        
        # Candidatures acceptées pour cette offre
        candidatures = Candidature.objects.filter(
            offre_id=id_offre,
            decisions__type_decision=type_decision_accepter
        ).exclude(interview__isnull=False).distinct()
        
        data = []
        for c in candidatures:
            # Calculer la moyenne des évaluations
            evaluations = Evaluation.objects.filter(candidature=c)
            if evaluations.exists():
                moyenne = sum(e.note for e in evaluations) / evaluations.count()
            else:
                moyenne = 0
            
            # Vérifier si déjà interviewé
            a_deja_interview = Interview.objects.filter(candidature=c).exists()
            
            if moyenne >= 70 and not a_deja_interview:
                data.append({
                    'id': c.id,
                    'candidat_id': c.candidat.id,
                    'candidat_nom': f"{c.candidat.nom} {c.candidat.postnom} {c.candidat.prenom}",
                    'candidat_email': c.candidat.user.email if c.candidat.user else None,
                    'offre_id': c.offre.id,
                    'offre_titre': c.offre.titre,
                    'moyenne': round(moyenne, 2),
                    'date_candidature': c.date_soumission.strftime('%d/%m/%Y')
                })
        
        return JsonResponse({'success': True, 'candidats': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_interviews_list(request):
    """API: Récupérer toutes les interviews"""
    try:
        interviews = Interview.objects.select_related('candidature', 'candidature__candidat', 'offre').all().order_by('-date_interview')
        
        data = []
        for i in interviews:
            data.append({
                'id': i.id,
                'candidature_id': i.candidature.id,
                'candidat_nom': f"{i.candidature.candidat.nom} {i.candidature.candidat.postnom} {i.candidature.candidat.prenom}",
                'offre_titre': i.offre.titre,
                'date_interview': i.date_interview.strftime('%d/%m/%Y à %H:%M'),
                'observation': i.observation or '',
                'decision': i.decision,
                'motif_rejet': i.motif_rejet or '',
                'date_decision': i.date_decision.strftime('%d/%m/%Y à %H:%M')
            })
        
        return JsonResponse({'success': True, 'interviews': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_interview_by_id(request, id_interview):
    """API: Récupérer une interview spécifique"""
    try:
        interview = get_object_or_404(Interview, id=id_interview)
        
        return JsonResponse({
            'success': True,
            'interview': {
                'id': interview.id,
                'candidature_id': interview.candidature.id,
                'observation': interview.observation or '',
                'decision': interview.decision,
                'motif_rejet': interview.motif_rejet or ''
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_interview(request):
    """API: Enregistrer une interview pour un candidat admissible"""
    try:
        from datetime import datetime
        
        data = json.loads(request.body)
        candidature_id = data.get('candidature_id')
        decision = data.get('decision')
        observation = data.get('observation', '').strip()
        motif_rejet = data.get('motif_rejet', '').strip() if decision == 'rejete' else ''
        
        if not candidature_id or not decision:
            return JsonResponse({'success': False, 'message': 'Données incomplètes'}, status=400)
        
        candidature = get_object_or_404(Candidature, id=candidature_id)
        
        # Vérifier si déjà interviewé
        if Interview.objects.filter(candidature=candidature).exists():
            return JsonResponse({'success': False, 'message': 'Ce candidat a déjà été interviewé'}, status=400)
        
        # Récupérer la moyenne pour vérifier l'admissibilité
        evaluations = Evaluation.objects.filter(candidature=candidature)
        if evaluations.exists():
            moyenne = sum(e.note for e in evaluations) / evaluations.count()
        else:
            moyenne = 0
        
        if moyenne < 70:
            return JsonResponse({'success': False, 'message': 'Ce candidat n\'est pas admissible (moyenne < 70%)'}, status=400)
        
        # Créer l'interview
        interview = Interview.objects.create(
            candidature=candidature,
            offre=candidature.offre,
            decision=decision,
            observation=observation,
            motif_rejet=motif_rejet
        )
        
        email_envoye = False
        email_message = ""
        
        # Envoyer l'email de notification
        from .utils import notifier_resultat_interview
        base_url = "https://mahoridi.pythonanywhere.com"
        
        if decision == 'accepte':
            # Créer un contrat pour le candidat retenu
            contrat = Contrat.objects.create(
                candidature=candidature,
                candidat=candidature.candidat,
                offre=candidature.offre,
                titre_contrat=f"Proposition de contrat - {candidature.offre.titre}",
                description=f"Nous avons le plaisir de vous informer que votre candidature pour le poste de {candidature.offre.titre} a été retenue après l'interview."
            )
            email_envoye, email_message = notifier_resultat_interview(candidature, 'accepte', observation, base_url, contrat.id)
        else:
            email_envoye, email_message = notifier_resultat_interview(candidature, 'rejete', motif_rejet, base_url)
        
        return JsonResponse({
            'success': True,
            'message': f'Interview enregistrée avec succès. Décision: {decision}',
            'interview': {
                'id': interview.id,
                'decision': interview.decision
            },
            'email_envoye': email_envoye,
            'email_message': email_message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def modifier_interview(request, id_interview):
    """API: Modifier une interview existante"""
    try:
        data = json.loads(request.body)
        interview = get_object_or_404(Interview, id=id_interview)
        
        observation = data.get('observation', '').strip()
        decision = data.get('decision')
        motif_rejet = data.get('motif_rejet', '').strip() if decision == 'rejete' else ''
        
        ancienne_decision = interview.decision
        interview.observation = observation
        interview.decision = decision
        interview.motif_rejet = motif_rejet
        interview.save()
        
        # Envoyer un email en cas de modification de décision (optionnel)
        email_envoye = False
        email_message = ""
        
        if ancienne_decision != decision:
            from .utils import notifier_resultat_interview
            base_url = "https://mahoridi.pythonanywhere.com"
            email_envoye, email_message = notifier_resultat_interview(interview.candidature, decision, observation, base_url)
        
        return JsonResponse({
            'success': True,
            'message': f'Interview modifiée avec succès',
            'email_envoye': email_envoye,
            'email_message': email_message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def supprimer_interview(request, id_interview):
    """API: Supprimer une interview"""
    try:
        interview = get_object_or_404(Interview, id=id_interview)
        interview.delete()
        return JsonResponse({'success': True, 'message': 'Interview supprimée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
# ==================== GESTION DES CONTRATS ====================

@login_required
def mes_contrats(request):
    """Page des contrats pour le candidat connecté"""
    return render(request, 'Appl/MesContrats.html')


@csrf_exempt
@require_http_methods(["GET"])
def get_mes_contrats(request):
    """API: Récupérer les contrats du candidat connecté"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        candidat = get_object_or_404(Candidat, user=request.user)
        contrats = Contrat.objects.filter(candidat=candidat).select_related('offre', 'interview')
        
        data = []
        for c in contrats:
            data.append({
                'id': c.id,
                'offre_titre': c.offre.titre,
                'offre_domaine': c.offre.domaine.NomDomaine,
                'titre_contrat': c.titre_contrat,
                'description': c.description,
                'date_debut': c.date_debut.strftime('%d/%m/%Y') if c.date_debut else 'À définir',
                'date_fin': c.date_fin.strftime('%d/%m/%Y') if c.date_fin else 'À définir',
                'salaire': f"{c.salaire:,.0f} FC" if c.salaire else 'À définir',
                'prime': f"{c.prime:,.0f} FC" if c.prime else '0 FC',
                'fichier_url': c.fichier_contrat.url if c.fichier_contrat else None,
                'statut': c.statut,
                'date_creation': c.date_creation.strftime('%d/%m/%Y à %H:%M')
            })
        
        return JsonResponse({'success': True, 'contrats': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def repondre_contrat(request, id_contrat):
    """API: Réponse du candidat au contrat (Accepter/Refuser)"""
    try:
        data = json.loads(request.body)
        decision = data.get('decision')
        motif_refus = data.get('motif_refus', '').strip() if decision == 'refuser' else ''
        
        contrat = get_object_or_404(Contrat, id=id_contrat)
        
        # Vérifier que le contrat appartient au candidat connecté
        if contrat.candidat.user.id != request.user.id:
            return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
        
        if contrat.statut != 'en_attente':
            return JsonResponse({'success': False, 'message': 'Ce contrat a déjà été traité'}, status=400)
        
        if decision == 'accepter':
            contrat.statut = 'accepte'
            contrat.date_signature = datetime.now()
            contrat.save()
            
            # Le candidat devient AGENT
            from django.contrib.auth.models import Group
            user = request.user
            groupe_candidat = Group.objects.filter(name='CANDIDAT').first()
            if groupe_candidat:
                user.groups.remove(groupe_candidat)
            
            groupe_agent, _ = Group.objects.get_or_create(name='AGENT')
            user.groups.add(groupe_agent)
            user.is_staff = True
            user.save()
            
            # Créer l'agent
            import random
            matricule = f"GRH-{contrat.candidat.id}-{random.randint(1000, 9999)}"
            while Agent.objects.filter(matricule=matricule).exists():
                matricule = f"GRH-{contrat.candidat.id}-{random.randint(1000, 9999)}"
            
            agent, created = Agent.objects.get_or_create(
                candidat=contrat.candidat,
                defaults={
                    'statut': 'Approuvé',
                    'matricule': matricule
                }
            )
            if not created and agent.statut != 'Approuvé':
                agent.statut = 'Approuvé'
                if not agent.matricule:
                    agent.matricule = matricule
                agent.save()
            
            # Envoyer email de confirmation
            from .utils import notifier_contrat_accepte
            base_url = "https://mahoridi.pythonanywhere.com"
            notifier_contrat_accepte(contrat, base_url)
            
            return JsonResponse({
                'success': True,
                'message': 'Félicitations ! Vous êtes maintenant agent chez GRH ENGINEERING. Un email de confirmation vous a été envoyé.'
            })
            
        elif decision == 'refuser':
            contrat.statut = 'refuse'
            contrat.motif_refus = motif_refus
            contrat.save()
            
            # Envoyer email de refus
            from .utils import notifier_contrat_refuse
            base_url = "https://mahoridi.pythonanywhere.com"
            notifier_contrat_refuse(contrat, motif_refus, base_url)
            
            return JsonResponse({
                'success': True,
                'message': 'Nous avons bien pris en compte votre décision. Nous vous souhaitons bonne chance dans vos recherches.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Décision invalide'}, status=400)
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)        


# views.py - Ajoutez ces vues

@csrf_exempt
@require_http_methods(["POST"])
def mettre_a_jour_contrat(request, id_contrat):
    """API: Le candidat complète les informations du contrat (type, dates, etc.)"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Non authentifié'}, status=401)
        
        data = json.loads(request.body)
        contrat = get_object_or_404(Contrat, id=id_contrat)
        
        # Vérifier que le contrat appartient au candidat connecté
        if contrat.candidat.user.id != request.user.id:
            return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
        
        if contrat.statut != 'en_attente':
            return JsonResponse({'success': False, 'message': 'Ce contrat a déjà été traité'}, status=400)
        
        type_contrat = data.get('type_contrat')
        date_debut = data.get('date_debut')
        date_fin = data.get('date_fin')
        duree_mois = data.get('duree_mois')
        
        if not type_contrat:
            return JsonResponse({'success': False, 'message': 'Veuillez choisir le type de contrat'}, status=400)
        
        contrat.type_contrat = type_contrat
        
        if type_contrat == 'determine':
            if not date_debut:
                return JsonResponse({'success': False, 'message': 'Veuillez indiquer la date de début'}, status=400)
            if not date_fin and not duree_mois:
                return JsonResponse({'success': False, 'message': 'Veuillez indiquer la date de fin ou la durée'}, status=400)
            
            from datetime import datetime
            contrat.date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            
            if date_fin:
                contrat.date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            elif duree_mois:
                contrat.duree_mois = int(duree_mois)
        else:
            # Contrat indéterminé - pas de dates
            contrat.date_debut = None
            contrat.date_fin = None
            contrat.duree_mois = None
        
        contrat.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Informations du contrat enregistrées. Vous pouvez maintenant l\'accepter ou le refuser.',
            'contrat': {
                'id': contrat.id,
                'type_contrat': contrat.type_contrat,
                'duree_texte': contrat.duree_contrat_str()
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# views.py - Ajoutez ces vues pour l'admin

@login_required
def contrats_admin(request):
    """Page admin pour gérer les contrats"""
    return render(request, 'Appl/ContratsAdmin.html')


@csrf_exempt
@require_http_methods(["GET"])
def get_contrats_admin(request):
    """API: Récupérer tous les contrats pour l'admin"""
    try:
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
        
        contrats = Contrat.objects.select_related('candidat', 'offre').all().order_by('-date_proposition')
        
        data = []
        for c in contrats:
            data.append({
                'id': c.id,
                'candidat_nom': f"{c.candidat.nom} {c.candidat.prenom}",
                'offre_titre': c.offre.titre,
                'titre_contrat': c.titre_contrat,
                'description': c.description,
                'salaire': float(c.salaire_base) if c.salaire_base else None,
                'prime': float(c.prime) if c.prime else 0,
                'avantages': c.avantages,
                'type_contrat': c.type_contrat,
                'duree_texte': c.duree_contrat_str(),
                'statut': c.statut,
                'motif_refus': c.motif_refus,
                'date_creation': c.date_proposition.strftime('%d/%m/%Y')
            })
        
        return JsonResponse({'success': True, 'contrats': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def modifier_contrat_admin(request, id_contrat):
    """API: Modifier un contrat (admin)"""
    try:
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
        
        contrat = get_object_or_404(Contrat, id=id_contrat)
        
        titre_contrat = request.POST.get('titre_contrat', '').strip()
        description = request.POST.get('description', '').strip()
        salaire = request.POST.get('salaire')
        prime = request.POST.get('prime', 0)
        avantages = request.POST.get('avantages', '').strip()
        
        if titre_contrat:
            contrat.titre_contrat = titre_contrat
        if description:
            contrat.description = description
        if salaire:
            contrat.salaire_base = float(salaire)
        if prime:
            contrat.prime = float(prime)
        if avantages:
            contrat.avantages = avantages
        
        fichier = request.FILES.get('fichier_contrat')
        if fichier:
            contrat.fichier_contrat = fichier
        
        contrat.save()
        
        return JsonResponse({'success': True, 'message': 'Contrat modifié avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)      



        # views.py - Ajoutez ces vues

@csrf_exempt
@require_http_methods(["GET"])
def get_candidats_par_offre_pour_contrat(request, id_offre):
    """API: Récupérer les candidats ayant réussi l'interview pour une offre"""
    try:
        # Récupérer les candidatures acceptées pour cette offre
        type_decision_accepter = TypeDecision.objects.filter(Description__icontains='Accepter').first()
        
        if not type_decision_accepter:
            return JsonResponse({'success': False, 'message': 'Type décision non trouvé'}, status=400)
        
        # Candidatures acceptées
        candidatures = Candidature.objects.filter(
            offre_id=id_offre,
            decisions__type_decision=type_decision_accepter
        ).exclude(interview__isnull=True).exclude(contrats__isnull=False).distinct()
        
        data = []
        for c in candidatures:
            data.append({
                'id': c.candidat.id,
                'nom': c.candidat.nom,
                'postnom': c.candidat.postnom,
                'prenom': c.candidat.prenom,
                'email': c.candidat.user.email if c.candidat.user else None
            })
        
        return JsonResponse({'success': True, 'candidats': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def creer_contrat_admin(request):
    """API: Créer un contrat manuellement (admin)"""
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        
        offre_id = request.POST.get('offre_id')
        candidat_id = request.POST.get('candidat_id')
        titre_contrat = request.POST.get('titre_contrat', '').strip()
        description = request.POST.get('description', '').strip()
        salaire = request.POST.get('salaire')
        prime = request.POST.get('prime', 0)
        avantages = request.POST.get('avantages', '').strip()
        
        if not offre_id or not candidat_id:
            return JsonResponse({'success': False, 'message': 'Offre et candidat requis'}, status=400)
        
        offre = get_object_or_404(OffreEmploie, id=offre_id)
        candidat = get_object_or_404(Candidat, id=candidat_id)
        
        # Vérifier si un contrat existe déjà
        if Contrat.objects.filter(candidat=candidat, offre=offre).exists():
            return JsonResponse({'success': False, 'message': 'Un contrat existe déjà pour ce candidat et cette offre'}, status=400)
        
        # Créer le contrat
        contrat = Contrat.objects.create(
            candidat=candidat,
            offre=offre,
            candidature=None,  # Pas de candidature associée
            titre_contrat=titre_contrat or f"Contrat - {offre.titre}",
            description=description,
            salaire_base=float(salaire) if salaire else None,
            prime=float(prime) if prime else 0,
            avantages=avantages,
            statut='en_attente'
        )
        
        # Ajouter le fichier
        fichier = request.FILES.get('fichier_contrat')
        if fichier:
            contrat.fichier_contrat = fichier
            contrat.save()
        
        # Envoyer l'email au candidat
        base_url = "https://mahoridi.pythonanywhere.com"
        sujet = f"📄 Nouveau contrat à signer - {offre.titre}"
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Contrat à signer - GRH ENGINEERING</title></head>
        <body style="font-family: Poppins, Arial, sans-serif;">
            <div style="max-width: 600px; margin: auto; background: white; border-radius: 15px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white;">📄 Nouveau contrat</h1>
                </div>
                <div style="padding: 30px;">
                    <h2>Bonjour {candidat.nom} {candidat.prenom},</h2>
                    <p>Un contrat pour le poste <strong>"{offre.titre}"</strong> vous a été proposé.</p>
                    <p>Veuillez vous connecter à votre espace candidat pour consulter et signer votre contrat.</p>
                    <div style="text-align: center;">
                        <a href="{base_url}/Appl/mes-contrats" style="background: #27ae60; color: white; padding: 12px 35px; text-decoration: none; border-radius: 25px;">📄 Voir mon contrat</a>
                    </div>
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
                to=[candidat.user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            email_envoye = True
            email_message = f"Email envoyé à {candidat.user.email}"
        except Exception as e:
            email_envoye = False
            email_message = str(e)
        
        return JsonResponse({
            'success': True,
            'message': f'Contrat créé avec succès pour {candidat.nom} {candidat.prenom}',
            'email_envoye': email_envoye,
            'email_message': email_message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def supprimer_contrat_admin(request, id_contrat):
    """API: Supprimer un contrat"""
    try:
        contrat = get_object_or_404(Contrat, id=id_contrat)
        contrat.delete()
        return JsonResponse({'success': True, 'message': 'Contrat supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)  


@csrf_exempt
@require_http_methods(["GET"])
def get_candidatures_tests_par_offre(request, id_offre):
    """API: Récupérer les candidatures acceptées pour une offre avec leurs tests"""
    try:
        # Récupérer le type de décision "Accepter"
        type_decision_accepter = TypeDecision.objects.filter(Description__icontains='Accepter').first()
        
        if not type_decision_accepter:
            return JsonResponse({'success': False, 'message': 'Type décision "Accepter" non trouvé'}, status=400)
        
        # Récupérer les candidatures acceptées pour cette offre
        candidatures = Candidature.objects.filter(
            offre_id=id_offre,
            decisions__type_decision=type_decision_accepter
        ).select_related('candidat', 'offre', 'offre__domaine').distinct()
        
        data = []
        for c in candidatures:
            # Récupérer tous les tests de l'offre
            tous_les_tests = Test.objects.filter(offre_id=id_offre).order_by('date_test')
            
            tests_data = []
            for test in tous_les_tests:
                evaluation = Evaluation.objects.filter(candidature=c, test=test).first()
                
                tests_data.append({
                    'id': test.id,
                    'nom_fichier': test.filename(),
                    'date_test': test.date_test.strftime('%d/%m/%Y'),
                    'est_evalue': evaluation is not None,
                    'evaluation_id': evaluation.id if evaluation else None,
                    'note': evaluation.note if evaluation else None,
                    'observation': evaluation.observation if evaluation else None,
                    'date_evaluation': evaluation.date_evaluation.strftime('%d/%m/%Y %H:%M') if evaluation else None
                })
            
            # Calculer la moyenne
            evaluations_existantes = Evaluation.objects.filter(candidature=c)
            if evaluations_existantes.exists():
                moyenne = sum(e.note for e in evaluations_existantes) / evaluations_existantes.count()
            else:
                moyenne = 0
            
            data.append({
                'id': c.id,
                'candidat_id': c.candidat.id,
                'candidat_nom': f"{c.candidat.nom} {c.candidat.postnom} {c.candidat.prenom}",
                'offre_id': c.offre.id,
                'offre_titre': c.offre.titre,
                'candidat_email': c.candidat.user.email if c.candidat.user else None,
                'tests': tests_data,
                'nombre_tests': len(tous_les_tests),
                'tests_evalues': len([t for t in tests_data if t['est_evalue']]),
                'moyenne': round(moyenne, 2)
            })
        
        return JsonResponse({'success': True, 'candidatures': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_interview(request):
    """API: Enregistrer une interview pour un candidat admissible"""
    try:
        data = json.loads(request.body)
        candidature_id = data.get('candidature_id')
        offre_id = data.get('offre_id')
        observation = data.get('observation', '').strip()
        decision = data.get('decision')
        motif_rejet = data.get('motif_rejet', '').strip() if decision == 'rejete' else ''
        
        if not candidature_id or not decision:
            return JsonResponse({'success': False, 'message': 'Données incomplètes'}, status=400)
        
        candidature = get_object_or_404(Candidature, id=candidature_id)
        
        if Interview.objects.filter(candidature=candidature).exists():
            return JsonResponse({'success': False, 'message': 'Ce candidat a déjà été interviewé'}, status=400)
        
        interview = Interview.objects.create(
            candidature=candidature,
            offre_id=offre_id or candidature.offre.id,
            observation=observation,
            decision=decision,
            motif_rejet=motif_rejet
        )
        
        # Envoyer l'email au candidat
        from .utils import notifier_resultat_interview
        base_url = "https://mahoridi.pythonanywhere.com"
        email_envoye, email_message = notifier_resultat_interview(candidature, decision, observation, base_url)
        
        return JsonResponse({
            'success': True,
            'message': f'Interview enregistrée avec succès. Décision: {decision}',
            'interview_id': interview.id,
            'email_envoye': email_envoye,
            'email_message': email_message
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)