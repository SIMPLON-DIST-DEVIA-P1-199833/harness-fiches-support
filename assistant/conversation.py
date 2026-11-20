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
    reponse = outils.lire_fiche(nom,limites)
    return f"Question : {question} \n_____________________\n Réponse: {reponse}"

def poser(question, messages, service, modele, limites, confirmer, signaler):
    """Ajoute la question aux messages, envoie la conversation et garde l'historique.
    confirmer et signaler seront utilisés aux étapes 3 et 4.
    """
    # Mémoriser la taille avant d'ajouter la question.
    taille_avant = len(messages)
    nombre_outils = 0
    messages.append({"role": "user", "content": question})
    while True:
        try:
            reponse = client.envoyer(service, modele, messages, outils=outils.DEFINITIONS)
        except client.ServiceIndisponible:
            # On retire tout ce qui a été ajouté pendant ce tour pour garder
            # un historique cohérent, puis on propage.
            # En d'autres mots : nettoyer l'historique pour qu'il reste cohérent puis on laisse
            # l'interface gérer l'affichage de l'erreur
            while len(messages) > taille_avant:
                messages.pop()
            # Un raise tout seul DANS UN EXCEPT relance exactement l'erreur en cours de traitement
            # avec type/message/traces d'exec. intact
            # Un raise seul conserve le tout : on ne pert pas les messages ni les traces
            raise
        message = reponse.choices[0].message
        if getattr(message, "tool_calls", None):
            if nombre_outils + len(message.tool_calls) > limites["appels_outil_max"] :
                msg = "Nomber max d'appels d'outils pour cette question"
                messages.append({"role": "assistant", "content": msg})
                return f"Nombre maximal d'outils utilisés atteints"
            messages.append(message.model_dump(exclude_none=True))
            for appel in message.tool_calls:
                nombre_outils += 1
                signaler(f"Outil : {appel.function.name}")
                try:
                    resultat = outils.executer(appel, limites, confirmer)
                except outils.AccesRefuse as erreur:
                    resultat = str(erreur)
                    signaler(str(erreur))
                messages.append({
                    "role": "tool",
                    "tool_call_id": appel.id,
                    "content": resultat,
                })
            # On reboucle pour envoyer les résultats au modèle.
            continue
        if getattr(reponse, "usage", None) and reponse.usage.total_tokens > limites["conversation_max_jetons"]:
            signaler("Conversation trop longue : elle repart de zéro.")
            messages[:] = nouvelle_conversation(limites)
        messages.append({"role": "assistant", "content": message.content})
        return message.content