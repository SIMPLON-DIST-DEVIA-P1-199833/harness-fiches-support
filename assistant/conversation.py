"""Cœur de l’assistant : la conversation et la boucle des appels d’outil."""

from assistant import client, outils

CONSIGNES = """Tu es l’assistant de l’équipe support de Batifact, éditeur d’un logiciel de facturation pour artisans.
Réponds en français, brièvement, à partir des fiches de procédure, et cite la fiche utilisée.
Utilise lire_fiche pour consulter une fiche et ecrire_fiche pour enregistrer un brouillon de fiche.
Fiches disponibles : {fiches}"""


class LimiteAtteinte(Exception):
    """La question en cours s’arrête sur une limite fixée par l’équipe."""


def nouvelle_conversation(limites):
    """Renvoie la liste des messages d’une nouvelle conversation."""
    fiches = ", ".join(outils.lister_fiches(limites))
    return [{"role": "system", "content": CONSIGNES.format(fiches=fiches)}]


def joindre_fiche(nom, question, limites):
    """Renvoie la question suivie du contenu de la fiche jointe, ou lève AccesRefuse."""
    # À faire (étape 3).
    raise NotImplementedError("Étape 3 : joindre_fiche")


def poser(question, messages, service, modele, limites, confirmer, signaler):
    """Ajoute la question aux messages, exécute les appels d’outil et renvoie la réponse du modèle.

    confirmer(nom) renvoie True si l’utilisateur accepte d’écraser la fiche ;
    signaler(texte) affiche une opération ou un refus à l’utilisateur.
    """
    # À faire (étape 2) : envoyer la conversation avec client.envoyer et garder l’historique.
    # À faire (étape 3) : exécuter les appels d’outil du modèle jusqu’à sa réponse finale.
    # À faire (étape 4) : arrêter la question au-delà des limites.
    raise NotImplementedError("Étape 2 : poser")
