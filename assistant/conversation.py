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
    contenu = outils.lire_fiche(nom, limites)
    return f"{question}\n\nFiche jointe {nom} :\n\n{contenu}"


def poser(question, messages, service, modele, limites, confirmer, signaler):
    """Ajoute la question aux messages, exécute les appels d’outil et renvoie la réponse du modèle."""
    messages.append({"role": "user", "content": question})
    while True:
        reponse = client.envoyer(service, modele, messages, outils.DEFINITIONS)
        message = reponse.choices[0].message
        messages.append(message.model_dump(exclude_none=True))  # objet du SDK converti en dictionnaire
        if not message.tool_calls:
            return message.content or ""  # content vaut None sans texte : or "" donne alors ""
        # À faire (étape 4) : arrêter la question au-delà du nombre d’appels d’outil fixé.
        for appel in message.tool_calls:
            resultat = executer_et_signaler(appel, limites, confirmer, signaler)
            messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})


def executer_et_signaler(appel, limites, confirmer, signaler):
    """Exécute un appel d’outil, signale l’opération à l’utilisateur et renvoie le résultat pour le modèle."""
    try:
        resultat = outils.executer(appel, limites, confirmer)
    except outils.AccesRefuse as refus:
        signaler(str(refus))
        return str(refus)
    signaler(f"Outil {appel.function.name} exécuté.")
    return resultat
