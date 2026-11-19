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
    # format remplace {fiches} dans CONSIGNES par la valeur donnée.
    return [{"role": "system", "content": CONSIGNES.format(fiches=fiches)}]


def joindre_fiche(nom, question, limites):
    """Renvoie la question suivie du contenu de la fiche jointe, ou lève AccesRefuse."""
    # All exceptions raised downstream in lire_fiche() and chemin_autorise()
    fiche = outils.lire_fiche(nom, limites)
    # splits on '\n' in service_simule.py, so question is first
    return f"{question}\nAttached fiche: {nom}\n{fiche}"


def poser(question, messages, service, modele, limites, confirmer, signaler):
    """Ajoute la question aux messages, exécute les appels d’outil et renvoie la réponse du modèle.

    confirmer(nom) renvoie True si l’utilisateur accepte d’écraser la fiche ;
    signaler(texte) affiche une opération ou un refus à l’utilisateur.
    """
    question_msg = {"role": "user", "content": question}
    # Create shallow list copy on function call
    # Only modify history if no exception is raised and we got a response
    response = client.envoyer(service, modele, messages + [question_msg])
    response_text = response.choices[0].message.content
    messages.append(question_msg)
    messages.append({"role": "assistant", "content": response_text})
    return response_text
    # role user requete, role tool sortie
    # À faire (étape 3) : exécuter les appels d’outil du modèle jusqu’à sa réponse finale.
    # À faire (étape 4) : arrêter la question au-delà des limites.
