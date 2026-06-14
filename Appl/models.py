from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

# DOMAINE
class Domaine(models.Model):
    NomDomaine = models.CharField(max_length=50)
    Description = models.CharField(max_length=50)
    
    def __str__(self):
        return self.NomDomaine
# OFFRE EMPLOI

class OffreEmploie(models.Model):
    domaine = models.ForeignKey(Domaine, on_delete=models.CASCADE, related_name='offres')
    titre = models.CharField(max_length=200)
    OffreFichier = models.FileField(upload_to='offres_emploi/%Y/%m/%d/')
    date_publication = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titre
    
    def filename(self):
        return os.path.basename(self.OffreFichier.name)
    
class Meta:
        ordering = ['-date_publication']
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"

# TABLE DECISION ONEM

class DecisionOnem(models.Model):
    Description = models.CharField(max_length=50)


# TABLE ONEM

class Onem(models.Model):
    offre = models.ForeignKey(OffreEmploie, on_delete=models.CASCADE, related_name='traitements')
    decision = models.ForeignKey(DecisionOnem, on_delete=models.SET_NULL, null=True, blank=True)
    observation = models.TextField(blank=True, null=True)
    motif = models.TextField(blank=True, null=True)
    date_verification = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Traitement de {self.offre.titre} - {self.date_verification.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Traitement ONEM"
        verbose_name_plural = "Traitements ONEM"
        ordering = ['-date_verification']



# TABLE CANDIDAT


class Candidat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=13)
    nationalite = models.CharField(max_length=50, default='Congolaise')
    lieuNaissance = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    dateNaissance = models.DateField()
    numeroTelephone = models.CharField(max_length=30)
    quartier = models.CharField(max_length=50)
    avenue = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='photos_candidats/%Y/%m/%d/', blank=True, null=True)  # ← NOUVEAU CHAMP
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"

# CANDIDATURE

class Candidature(models.Model):
    """Modèle pour les candidatures aux offres d'emploi"""
    
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='candidatures')
    offre = models.ForeignKey(OffreEmploie, on_delete=models.CASCADE, related_name='candidatures')
    cv = models.FileField(upload_to='cvs/%Y/%m/%d/')
    date_soumission = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.candidat.nom} - {self.offre.titre}"
    
class Meta:
        ordering = ['-date_soumission']
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        unique_together = ['candidat', 'offre']  # Empêche la double candidature

# TYPE DE DECISION ADMIN SUR CANDIDATURE

class TypeDecision(models.Model):
    Description = models.CharField(max_length=50)
    
    def __str__(self):
        return self.Description
    
    class Meta:
        verbose_name = "Type de décision"
        verbose_name_plural = "Types de décision"


class Decision(models.Model):
    candidature = models.ForeignKey('Candidature', on_delete=models.CASCADE, related_name='decisions')
    type_decision = models.ForeignKey(TypeDecision, on_delete=models.SET_NULL, null=True, blank=True)
    motif = models.TextField(blank=True, null=True)
    date_decision = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Décision pour {self.candidature.candidat.nom} - {self.candidature.offre.titre}"
    
    class Meta:
        verbose_name = "Décision"
        verbose_name_plural = "Décisions"
        ordering = ['-date_decision']


# TEST 

class Test(models.Model):
    offre = models.ForeignKey(OffreEmploie, on_delete=models.CASCADE, related_name='tests')
    fichier_test = models.FileField(upload_to='tests/%Y/%m/%d/')
    date_test = models.DateTimeField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Test pour {self.offre.titre} - {self.date_test.strftime('%d/%m/%Y')}"
    
    def filename(self):
        if self.fichier_test:
            import os
            return os.path.basename(self.fichier_test.name)
        return "Aucun fichier"
    
    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Tests"
        ordering = ['-date_test']


# EVALUATION ET AGENT

class Evaluation(models.Model):
    candidature = models.ForeignKey('Candidature', on_delete=models.CASCADE, related_name='evaluations')
    test = models.ForeignKey('Test', on_delete=models.CASCADE, related_name='evaluations')
    observation = models.TextField(blank=True, null=True)
    note = models.FloatField(help_text="Note en pourcentage (0-100)")
    date_evaluation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['candidature', 'test']  # Empêche d'évaluer deux fois le même test
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        ordering = ['-date_evaluation']
    
    def __str__(self):
        return f"Évaluation de {self.candidature.candidat.nom} - {self.test.offre.titre} - Test du {self.test.date_test.strftime('%d/%m/%Y')} - {self.note}%"


class Agent(models.Model):
    candidat = models.OneToOneField('Candidat', on_delete=models.CASCADE, related_name='agent')
    date_retenu = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, default='En attente')
    contrat_signe = models.BooleanField(default=False)
    matricule = models.CharField(max_length=50, unique=True, blank=True, null=True)  # ← AJOUTÉ
    
    def __str__(self):
        return f"Agent: {self.candidat.nom} {self.candidat.prenom} - {self.matricule}"
    
    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"

# TYPE CONGE

class TypeConge(models.Model):
    designation = models.CharField(max_length=100, unique=True)
    duree = models.IntegerField(help_text="Durée en jours")
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.designation} ({self.duree} jours)"
    
    class Meta:
        verbose_name = "Type de congé"
        verbose_name_plural = "Types de congé"
        ordering = ['designation']

# DEMANDE CONGE

class DemandeConge(models.Model):
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='demandes_conge')
    type_conge = models.ForeignKey('TypeConge', on_delete=models.CASCADE, related_name='demandes')
    motif = models.TextField()
    date_demande = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    
    def __str__(self):
        return f"Demande de {self.agent.candidat.nom} - {self.type_conge.designation}"
    
    @property
    def nombre_jours(self):
        """Calculer le nombre de jours de congé demandés"""
        delta = self.date_fin - self.date_debut
        return delta.days + 1
    
    class Meta:
        verbose_name = "Demande de congé"
        verbose_name_plural = "Demandes de congé"
        ordering = ['-date_demande']


# reglage de l'offre

class TypeEtatOffre(models.Model):
    """Types d'états pour une offre"""
    designation = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.designation
    
    class Meta:
        verbose_name = "Type d'état d'offre"
        verbose_name_plural = "Types d'états d'offre"
        ordering = ['designation']


class ReglageOffre(models.Model):
    """Configuration des états et dates pour chaque offre"""
    offre = models.OneToOneField('OffreEmploie', on_delete=models.CASCADE, related_name='reglage')
    type_etat = models.ForeignKey(TypeEtatOffre, on_delete=models.CASCADE, related_name='reglages')
    date_debut = models.DateField(auto_now_add=True)
    date_expiration = models.DateField(null=True, blank=True)
    date_renouvellement = models.DateField(null=True, blank=True)
    motif = models.TextField(blank=True, null=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.offre.titre} - {self.type_etat.designation}"
    
    def est_active(self):
        """Vérifie si l'offre est active"""
        from datetime import date
        today = date.today()
        
        if self.type_etat.designation == 'Stopper':
            return False
        
        if self.type_etat.designation == 'Renouveler' and self.date_renouvellement:
            # Vérifier si le renouvellement est toujours valide
            if today > self.date_renouvellement:
                return False
        
        if self.date_expiration and today > self.date_expiration:
            # L'offre est expirée mais peut être renouvelée
            if self.type_etat.designation != 'Renouveler':
                return False
        
        return self.type_etat.designation == 'Actif'
    
    class Meta:
        verbose_name = "Réglage d'offre"
        verbose_name_plural = "Réglages d'offres"
        ordering = ['-date_debut']


        # NOTHIFICATION


class Notification(models.Model):
    TYPE_CHOICES = [
        ('candidature_acceptee', 'Candidature acceptée'),
        ('candidature_refusee', 'Candidature refusée'),
        ('test_programme', 'Test programmé'),
        ('rappel_test', 'Rappel de test'),
        ('info_generale', 'Information générale'),
    ]
    
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(max_length=50, choices=TYPE_CHOICES)
    est_lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    lien = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.titre} - {self.candidat.nom}"
    
    class Meta:
        ordering = ['-date_creation']


# ANALYSE DEMANDE

class AnalyseDemandeConge(models.Model):
    demande_conge = models.OneToOneField('DemandeConge', on_delete=models.CASCADE, related_name='analyse')
    decision = models.CharField(max_length=50, choices=[
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('en_attente', 'En attente')
    ], default='en_attente')
    motif_analyse = models.TextField(blank=True, null=True)
    date_analyse = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    analyste = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='analyses')
    
    def __str__(self):
        return f"Analyse de la demande de {self.demande_conge.agent.candidat.nom} - {self.decision}"
    
    class Meta:
        verbose_name = "Analyse demande de congé"
        verbose_name_plural = "Analyses demandes de congé"
        ordering = ['-date_analyse']




# VRAIE MESSAGERIE


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class Message(models.Model):
    """Modèle pour la messagerie interne"""
    
    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('recu', 'Reçu'),
        ('lu', 'Lu'),
        ('supprime', 'Supprimé'),
        ('modifie', 'Modifié'),
    ]
    
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_recus')
    sujet = models.CharField(max_length=200, blank=True, null=True)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(null=True, blank=True)
    date_lu = models.DateTimeField(null=True, blank=True)
    date_suppression_expediteur = models.DateTimeField(null=True, blank=True)
    date_suppression_destinataire = models.DateTimeField(null=True, blank=True)
    statut_expediteur = models.CharField(max_length=20, choices=STATUT_CHOICES, default='envoye')
    statut_destinataire = models.CharField(max_length=20, choices=STATUT_CHOICES, default='recu')
    est_lu = models.BooleanField(default=False)
    est_modifie = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.expediteur.username} → {self.destinataire.username}"
    
    def marquer_comme_lu(self):
        if not self.est_lu:
            self.est_lu = True
            self.date_lu = timezone.now()
            self.statut_destinataire = 'lu'
            self.save()
    
    def modifier_message(self, nouveau_contenu):
        self.contenu = nouveau_contenu
        self.est_modifie = True
        self.date_modification = timezone.now()
        self.statut_expediteur = 'modifie'
        self.statut_destinataire = 'modifie'
        self.save()
    
    def supprimer_pour_moi(self, user):
        if user.id == self.expediteur.id:
            self.date_suppression_expediteur = timezone.now()
            self.statut_expediteur = 'supprime'
        elif user.id == self.destinataire.id:
            self.date_suppression_destinataire = timezone.now()
            self.statut_destinataire = 'supprime'
        self.save()
    
    def est_visible_pour(self, user):
        if user.id == self.expediteur.id:
            return self.date_suppression_expediteur is None
        elif user.id == self.destinataire.id:
            return self.date_suppression_destinataire is None
        return False
    
    class Meta:
        ordering = ['-date_envoi']
        verbose_name = "Message"
        verbose_name_plural = "Messages"


class Conversation(models.Model):
    """Modèle pour suivre les conversations entre utilisateurs"""
    
    participants = models.ManyToManyField(User, related_name='conversations')
    dernier_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    date_dernier_message = models.DateTimeField(auto_now=True)
    sujet = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        participants_noms = ", ".join([p.username for p in self.participants.all()])
        return f"Conversation: {participants_noms}"
    
    class Meta:
        ordering = ['-date_dernier_message']


class MessagePieceJointe(models.Model):
    """Modèle pour les pièces jointes aux messages"""
    
    TYPE_FICHIER = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('pdf', 'PDF'),
        ('autre', 'Autre'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='pieces_jointes')
    fichier = models.FileField(upload_to='messages/%Y/%m/%d/')
    nom_fichier = models.CharField(max_length=255)
    type_fichier = models.CharField(max_length=20, choices=TYPE_FICHIER, default='document')
    taille = models.IntegerField(default=0)
    date_upload = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom_fichier
    
    def extension(self):
        return os.path.splitext(self.nom_fichier)[1].lower()




class Interview(models.Model):
    """Modèle pour gérer les interviews des candidats"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('rejete', 'Rejeté'),
    ]
    
    candidature = models.OneToOneField('Candidature', on_delete=models.CASCADE, related_name='interview')
    offre = models.ForeignKey('OffreEmploie', on_delete=models.CASCADE, related_name='interviews')
    date_interview = models.DateTimeField(auto_now_add=True)
    observation = models.TextField(blank=True, null=True)
    decision = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    motif_rejet = models.TextField(blank=True, null=True)
    date_decision = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Interview"
        verbose_name_plural = "Interviews"
        ordering = ['-date_interview']
    
    def __str__(self):
        # Correction : utiliser candidature.candidat au lieu de candidat
        return f"Interview {self.candidature.candidat.nom} {self.candidature.candidat.prenom} - {self.offre.titre} - {self.decision}"

# models.py - Modèle Contrat corrigé

# models.py - Modèle Contrat simplifié

class Contrat(models.Model):
    TYPE_CONTRAT_CHOICES = [
        ('determine', 'Contrat à durée déterminée (CDD)'),
        ('indetermine', 'Contrat à durée indéterminée (CDI)'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('accepte', 'Accepté par le candidat'),
        ('refuse', 'Refusé par le candidat'),
        ('signe', 'Signé'),
    ]
    
    # Relations
    interview = models.OneToOneField('Interview', on_delete=models.CASCADE, related_name='contrat')
    offre = models.ForeignKey('OffreEmploie', on_delete=models.CASCADE, related_name='contrats')
    candidat = models.ForeignKey('Candidat', on_delete=models.CASCADE, related_name='contrats')
    
    # Type de contrat
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT_CHOICES)
    
    # Fichier du contrat (PDF ou DOC)
    fichier_contrat = models.FileField(upload_to='contrats/', null=True, blank=True)
    
    # Pour contrat déterminé (CDD)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    
    # Statut et motif de refus
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    motif_refus = models.TextField(blank=True, null=True)
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_signature = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Contrat {self.candidat.nom} - {self.offre.titre}"
    
    def duree_contrat_str(self):
        if self.type_contrat == 'indetermine':
            return "Durée indéterminée"
        elif self.date_debut and self.date_fin:
            return f"Du {self.date_debut.strftime('%d/%m/%Y')} au {self.date_fin.strftime('%d/%m/%Y')}"
        return "À définir"