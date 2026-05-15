from django.urls import path,include
from .views import *
from .import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    #LIEN VERS PAGES

    path('', ChargerIndex),
    path('Domaine',ChargerDomaine),
    path('AnalyseDemandeConge', ChargerAnalyseDemandeConge),
    path('OffreEmploi',ChargerOffreEmploi),
    path('OffreEmploi',ChargerOffreEmploi),
    path('DecisionOnem',ChargerDecisionOnem),
    path('Onem',ChargerOnem),
    path('Candidat',ChargerCandidat),
    path('dashboardCandidat',ChargerDashboardCandidat),
    path('logins', ChargerLogin),
    path('TypeDecision', ChargerTypeDecision),
    path('Decision', ChargerDecision),
    path('Test', ChargerTest),
    path('Evaluation', ChargerEvaluation),
    path('TypeConge', ChargerTypeConge),
    path('DemandeConge', ChargerDemandeConge),
    path('InfoOffre', ChargerInfoOffre),
    path('Agents', ChargerAgent),
    path('ReglageOffre', ChargerReglageOffre),
    path('dashboardAdmin', ChargerDashboardAdmin),
    path('TypeEtatOffre', ChargerTypeEtatOffre),
    path('ReglageOffre', ChargerReglageOffre),
    path('dashboardOnem', ChargerDashboardOnem),
    path('ListeCandidat',ChargerListeCandidat),
    path('dashboardAgent', ChargerDashboardAgent),
    path('ResultatTest', ChargerResultatTest),
    path('InfoPersonnel', ChargerInfoPersonnel),
    path('Messagerie', ChargerMessagerie),
    # ACTION DE DOMAINE

    path('domaines/', views.liste_domaines, name='liste_domaines'),
    
    path('api/domaines/', views.get_all_domaines, name='get_all_domaines'),
    path('api/domaines/ajouter/', views.ajouter_domaine, name='ajouter_domaine'),
    path('api/domaines/modifier/<int:id_domaine>/', views.modifier_domaine, name='modifier_domaine'),
    path('api/domaines/supprimer/<int:id_domaine>/', views.supprimer_domaine, name='supprimer_domaine'),



   


    # Pour offre d'emploi

    # Pages principales
    path('offres/', views.liste_offres, name='liste_offres'),
    
    # API Domaines
    path('api/domaines/', views.get_all_domaines, name='get_all_domaines'),
    
    # API Offres
    path('api/offres/', views.get_all_offres, name='get_all_offres'),
    path('api/offres/ajouter/', views.ajouter_offre, name='ajouter_offre'),
    path('api/offres/modifier/<int:id_offre>/', views.modifier_offre, name='modifier_offre'),
    path('api/offres/supprimer/<int:id_offre>/', views.supprimer_offre, name='supprimer_offre'),
    path('api/offres/telecharger/<int:id_offre>/', views.telecharger_fichier, name='telecharger_fichier'),



# DECISION ONEM

    # Page des décisions ONEM
    path('decisions/', views.liste_decisions, name='liste_decisions'),
    
    # API Décisions ONEM
    path('api/decisions/', views.get_all_decisions, name='get_all_decisions'),
    path('api/decisions/ajouter/', views.ajouter_decision, name='ajouter_decision'),
    path('api/decisions/modifier/<int:id_decision>/', views.modifier_decision, name='modifier_decision'),
    path('api/decisions/supprimer/<int:id_decision>/', views.supprimer_decision, name='supprimer_decision'),


    

 # ONEM

 
    # Pages principales
    path('offres/', views.liste_offres, name='liste_offres'),
    path('decisions/', views.liste_decisions, name='liste_decisions'),
    path('onem/', views.page_onem, name='page_onem'),
    
    # API Domaines
    path('api/domaines/', views.get_all_domaines, name='get_all_domaines'),
    
    # API Offres
    path('api/offres/', views.get_all_offres, name='get_all_offres'),
    path('api/offres/ajouter/', views.ajouter_offre, name='ajouter_offre'),
    path('api/offres/modifier/<int:id_offre>/', views.modifier_offre, name='modifier_offre'),
    path('api/offres/supprimer/<int:id_offre>/', views.supprimer_offre, name='supprimer_offre'),
    path('api/offres/telecharger/<int:id_offre>/', views.telecharger_fichier, name='telecharger_fichier'),
    
    # API Décisions
    path('api/decisions/', views.get_all_decisions, name='get_all_decisions'),
    path('api/decisions/ajouter/', views.ajouter_decision, name='ajouter_decision'),
    path('api/decisions/modifier/<int:id_decision>/', views.modifier_decision, name='modifier_decision'),
    path('api/decisions/supprimer/<int:id_decision>/', views.supprimer_decision, name='supprimer_decision'),
    
    # API ONEM
    # API ONEM
    path('api/onem/offres-a-traiter/', views.get_offres_a_traiter, name='get_offres_a_traiter'),
    path('api/onem/offres-traitees/', views.get_offres_traitees, name='get_offres_traitees'),
    path('api/onem/ouvrir-fichier/<int:id_offre>/', views.ouvrir_fichier_offre, name='ouvrir_fichier_offre'),
    path('api/onem/enregistrer-decision/', views.enregistrer_decision, name='enregistrer_decision'),
    path('api/onem/modifier-traitement/<int:id_traitement>/', views.modifier_traitement, name='modifier_traitement'),

    # CANDIDAT

    path('inscription-candidat/', views.inscriptionCandidat, name='inscriptionCandidat'),
    path('login/', views.ConnectUtilisateur, name='login'),  # ← Le nom 'login' ici
    # ... autres URLs
    path('dashboard-candidat/', views.dashboardCandidat, name='dashboardCandidat'),
    
    # API Candidat
    path('api/candidat/offres-acceptees/', views.get_offres_acceptees, name='get_offres_acceptees'),
    path('api/candidature/postuler/', views.postuler_candidature, name='postuler_candidature'),
    # Ajoutez cette ligne dans vos urlpatterns
    path('api/candidat/ouvrir-fichier/<int:id_offre>/', views.ouvrir_fichier_candidat, name='ouvrir_fichier_candidat'),


# POUR LE LOGIN

    path('ConnectUtilisateur/', views.ConnectUtilisateur, name='ConnectUtilisateur'),

    # URLs Type Decision


    path('type-decisions/', views.liste_type_decisions, name='liste_type_decisions'),
    
    # API Type Decision
    path('api/type-decisions/', views.get_all_type_decisions, name='get_all_type_decisions'),
    path('api/type-decisions/ajouter/', views.ajouter_type_decision, name='ajouter_type_decision'),
    path('api/type-decisions/modifier/<int:id_type_decision>/', views.modifier_type_decision, name='modifier_type_decision'),
    path('api/type-decisions/supprimer/<int:id_type_decision>/', views.supprimer_type_decision, name='supprimer_type_decision'),
    

    # DECISION

    # URLs Décisions
    path('decisions-candidature/', views.liste_decisions_candidature, name='liste_decisions_candidature'),
    
    # API Décisions
    path('api/decisions/candidatures-a-traiter/', views.get_candidatures_a_traiter, name='get_candidatures_a_traiter'),
    path('api/decisions/candidatures-traitees/', views.get_candidatures_traitees, name='get_candidatures_traitees'),
    path('api/decisions/ouvrir-cv/<int:id_candidature>/', views.ouvrir_cv_candidat, name='ouvrir_cv_candidat'),
    path('api/decisions/enregistrer/', views.enregistrer_decision, name='enregistrer_decision'),
    path('api/decisions/modifier/<int:id_decision>/', views.modifier_decision, name='modifier_decision'),
    
    # TEST
    path('tests/', views.liste_tests, name='liste_tests'),
    
    # API Tests
    path('api/tests/offres-acceptees/', views.get_offres_acceptees_tests, name='get_offres_acceptees_tests'),
    path('api/tests/offre/<int:id_offre>/', views.get_tests_by_offre, name='get_tests_by_offre'),
    path('api/tests/ajouter/', views.ajouter_test, name='ajouter_test'),
    path('api/tests/supprimer/<int:id_test>/', views.supprimer_test, name='supprimer_test'),
    path('api/tests/ouvrir-fichier/<int:id_test>/', views.ouvrir_fichier_test, name='ouvrir_fichier_test'),

        # URLs Évaluations
    path('evaluations/', views.liste_evaluations, name='liste_evaluations'),
    
    # API Évaluations
    path('api/evaluations/candidatures-acceptees/', views.get_candidatures_acceptees, name='get_candidatures_acceptees'),
    path('api/evaluations/evaluations-effectuees/', views.get_evaluations_effectuees, name='get_evaluations_effectuees'),
    path('api/evaluations/tests/<int:id_offre>/', views.get_tests_by_offre, name='get_tests_by_offre'),
    path('api/evaluations/candidature/<int:id_candidature>/', views.get_evaluations_by_candidature, name='get_evaluations_by_candidature'),
    path('api/evaluations/enregistrer/', views.enregistrer_evaluation, name='enregistrer_evaluation'),
    path('api/evaluations/modifier/<int:id_evaluation>/', views.modifier_evaluation, name='modifier_evaluation'),


     
    # URLs Type Congé
    path('type-conge/', views.liste_type_conge, name='liste_type_conge'),
    
    # API Type Congé
    path('api/type-conge/', views.get_all_type_conge, name='get_all_type_conge'),
    path('api/type-conge/ajouter/', views.ajouter_type_conge, name='ajouter_type_conge'),
    path('api/type-conge/modifier/<int:id_type_conge>/', views.modifier_type_conge, name='modifier_type_conge'),
    path('api/type-conge/supprimer/<int:id_type_conge>/', views.supprimer_type_conge, name='supprimer_type_conge'),

    
        
    # Liste des Agents
    path('api/agents/', views.api_agents, name='api_agents'),

    # TRAITEMENT ACCUEIL
    path('api/offres-accueil/', views.api_offres_accueil, name='api_offres_accueil'),

    # reglage offre

    path('api/offre/reglage/<int:id_offre>/', views.gerer_reglage_offre, name='gerer_reglage_offre'),

    # ACCUEIL ADMIN

    path('api/admin/stats/', views.admin_stats, name='admin_stats'),
    path('api/admin/activites/', views.admin_activites, name='admin_activites'),


    # etat offre

      # URLs Type Etat Offre
    path('type-etat-offre/', views.liste_type_etat_offre, name='liste_type_etat_offre'),
    
    # API Type Etat Offre
    path('api/type-etat-offre/', views.get_all_type_etat_offre, name='get_all_type_etat_offre'),
    path('api/type-etat-offre/ajouter/', views.ajouter_type_etat_offre, name='ajouter_type_etat_offre'),
    path('api/type-etat-offre/modifier/<int:id_type_etat>/', views.modifier_type_etat_offre, name='modifier_type_etat_offre'),
    path('api/type-etat-offre/supprimer/<int:id_type_etat>/', views.supprimer_type_etat_offre, name='supprimer_type_etat_offre'),

    #URLs Réglage Offre
    path('reglage-offre/', views.liste_reglage_offre, name='liste_reglage_offre'),
    
    # API Réglage Offre
    path('api/offres-avec-decision/', views.get_offres_avec_decision, name='get_offres_avec_decision'),
    path('api/reglage/offre/<int:id_offre>/', views.get_reglage_by_offre, name='get_reglage_by_offre'),
    path('api/reglages/ajouter/', views.ajouter_reglage, name='ajouter_reglage'),







    path('onem-traitement/', views.page_onem_traitement, name='page_onem_traitement'),
    
    # API ONEM
    path('api/onem/offres-non-traitees/', views.get_offres_non_traitees, name='get_offres_non_traitees'),
    path('api/onem/offres-traitees/', views.get_offres_traitees_onem, name='get_offres_traitees_onem'),
    path('api/onem/ouvrir-fichier/<int:id_offre>/', views.ouvrir_fichier_offre_onem, name='ouvrir_fichier_offre_onem'),
    path('api/onem/enregistrer-decision/', views.enregistrer_decision_onem, name='enregistrer_decision_onem'),
    path('api/onem/modifier-traitement/<int:id_traitement>/', views.modifier_traitement_onem, name='modifier_traitement_onem'),

# Dans urls.py



        # ==================== ANALYSE ONEM ====================
    
    # Page d'analyse ONEM
    path('analyse-onem/', views.page_analyse_onem, name='page_analyse_onem'),
    
    # API Analyse ONEM
    path('api/analyse-onem/offres-non-analysees/', views.get_offres_non_analysees, name='get_offres_non_analysees'),
    path('api/analyse-onem/offres-analysees/', views.get_offres_analysees, name='get_offres_analysees'),
    path('api/analyse-onem/ouvrir-fichier/<int:id_offre>/', views.ouvrir_fichier_analyse_onem, name='ouvrir_fichier_analyse_onem'),
    path('api/analyse-onem/enregistrer/', views.enregistrer_analyse_onem, name='enregistrer_analyse_onem'),
    path('api/analyse-onem/modifier/<int:id_analyse>/', views.modifier_analyse_onem, name='modifier_analyse_onem'),


    # NOTHIFICATION 

    # URLs Notifications
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/marquer-lue/<int:id_notification>/', views.marquer_notification_lue, name='marquer_notification_lue'),
    path('api/notifications/marquer-toutes-lues/', views.marquer_toutes_notifications_lues, name='marquer_toutes_notifications_lues'),


        # URLs Gestion des candidats
    path('liste-candidats/', views.liste_candidats, name='liste_candidats'),
    
    # API Candidats
    path('api/candidats/', views.get_all_candidats, name='get_all_candidats'),
    path('api/candidats/changer-role/', views.changer_role_candidat, name='changer_role_candidat'),
    path('api/candidats/supprimer/<int:id_candidat>/', views.supprimer_candidat, name='supprimer_candidat'),
    path('api/groupes/', views.get_all_groupes, name='get_all_groupes'),




    # URLs Demandes Congé
    path('mes-demandes-conge/', views.page_demande_conge, name='page_demande_conge'),
    
    # API Demandes Congé
    path('api/mes-demandes-conge/', views.get_mes_demandes_conge, name='get_mes_demandes_conge'),
    path('api/demandes-conge-admin/', views.get_all_demandes_conge_admin, name='get_all_demandes_conge_admin'),
    path('api/types-conge/', views.get_types_conge, name='get_types_conge'),
    path('api/demandes-conge/ajouter/', views.ajouter_demande_conge, name='ajouter_demande_conge'),
    path('api/demandes-conge/supprimer/<int:id_demande>/', views.supprimer_demande_conge, name='supprimer_demande_conge'),


   # URLs Évaluations
    path('evaluations/', views.liste_evaluations, name='liste_evaluations'),
    
    # API Évaluations
    path('api/evaluations/candidatures-tests/', views.get_candidatures_avec_tests_non_evalues, name='get_candidatures_avec_tests_non_evalues'),
    path('api/evaluations/evaluations-effectuees/', views.get_evaluations_effectuees, name='get_evaluations_effectuees'),
    path('api/evaluations/tests/<int:id_offre>/', views.get_tests_by_offre_evaluation, name='get_tests_by_offre_evaluation'),
    path('api/evaluations/enregistrer/', views.enregistrer_evaluation, name='enregistrer_evaluation'),
    path('api/evaluations/modifier/<int:id_evaluation>/', views.modifier_evaluation, name='modifier_evaluation'),



    # APIs pour le candidat
    path('api/candidat/infos/', views.get_candidat_infos, name='get_candidat_infos'),
    path('api/candidat/mes-evaluations/', views.get_mes_evaluations, name='get_mes_evaluations'),


        # URLs Analyse Demandes Congé
    path('analyse-demandes-conge/', views.page_analyse_demandes_conge, name='page_analyse_demandes_conge'),
    
    # API Analyse Demandes Congé
    path('api/analyse-demandes/non-analysees/', views.get_demandes_non_analysees, name='get_demandes_non_analysees'),
    path('api/analyse-demandes/analysees/', views.get_demandes_analysees, name='get_demandes_analysees'),
    path('api/analyse-demandes/enregistrer/', views.enregistrer_analyse_demande, name='enregistrer_analyse_demande'),
    path('api/analyse-demandes/modifier/<int:id_analyse>/', views.modifier_analyse_demande, name='modifier_analyse_demande'),
    path('api/analyse-demandes/supprimer/<int:id_analyse>/', views.supprimer_analyse_demande, name='supprimer_analyse_demande'),

# MES DEMANDES
    path('api/mes-demandes-conge/analyse/<int:id_demande>/', views.get_analyse_by_demande, name='get_analyse_by_demande'),


    # APIs Utilisateur
    path('api/utilisateur/infos/', views.get_utilisateur_infos, name='get_utilisateur_infos'),
    path('api/utilisateur/modifier/', views.modifier_utilisateur_infos, name='modifier_utilisateur_infos'),






    # Messagerie
    
    # ==================== MESSAGERIE ====================
    
    # Page
    path('messagerie/', views.page_messagerie, name='messagerie'),
    
    # API Conversations
    path('api/messagerie/conversations/', views.get_conversations, name='get_conversations'),
    path('api/messagerie/messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('api/messagerie/destinataires/', views.get_destinataires_possibles, name='get_destinataires_possibles'),
    
    # API Actions
    path('api/messagerie/envoyer/', views.envoyer_message, name='envoyer_message'),
    path('api/messagerie/modifier/<int:id_message>/', views.modifier_message, name='modifier_message'),
    path('api/messagerie/supprimer/<int:id_message>/', views.supprimer_message_pour_moi, name='supprimer_message_pour_moi'),
    path('api/messagerie/supprimer-tous/<int:user_id>/', views.supprimer_tous_messages, name='supprimer_tous_messages'),
    
    # API Fichiers
    path('api/messagerie/upload/<int:id_message>/', views.upload_piece_jointe, name='upload_piece_jointe'),
    path('api/messagerie/telecharger/<int:id_piece>/', views.telecharger_fichier_message, name='telecharger_fichier_message'),
    path('api/messagerie/non-lus/', views.get_non_lus_count, name='get_non_lus_count'),

]
# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
