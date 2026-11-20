"""Cœur de l’assistant : la conversation et la boucle des appels d’outil."""

from assistant import client, outils
import json

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
    # À faire (étape 3).
    raise NotImplementedError("Étape 3 : joindre_fiche")


def poser(question, messages, service, modele, limites, confirmer, signaler) -> str:
    """Ajoute la question aux messages, exécute les appels d’outil et renvoie la réponse du modèle.

    confirmer(nom) renvoie True si l’utilisateur accepte d’écraser la fiche ;
    signaler(texte) affiche une opération ou un refus à l’utilisateur.
    """
    # À faire (étape 2) : envoyer la conversation avec client.envoyer et garder l’historique.
    messages.append({"role": "user", "content": question})

    while True:
        reponse_obj = client.envoyer(service, modele, messages, outils.DEFINITIONS)
        message = reponse_obj.choices[0].message
        if not message:
            raise client.ServiceIndisponible("Message IA reçu vide.")

        messages.append(message.model_dump(exclude_none=True))
        if not message.tool_calls:
            return str(message.content)
        else:
            for tool_call in message.tool_calls:
                try:
                    result = outils.executer(tool_call, limites, confirmer)
                    signaler(
                        f"L'outil {tool_call.function.name} a été lancé"  # pyright: ignore[reportAttributeAccessIssue]
                    )
                except outils.AccesRefuse as e:
                    signaler(e)
                    result = str(e)
                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": result}
                )

    # À faire (étape 3) : exécuter les appels d’outil du modèle jusqu’à sa réponse finale.
    # À faire (étape 4) : arrêter la question au-delà des limites.
