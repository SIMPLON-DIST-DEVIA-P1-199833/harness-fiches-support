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
    # À faire (étape 3)[fait]
    contenu = outils.lire_fiche(nom, limites)
    return f"La question de l'user: {question} \n\n Le nom de la fiche jointe: {nom} \n\n Le contenu de la fiche: {contenu}"



def poser(question, messages, service, modele, limites, confirmer, signaler):
    """Ajoute la question aux messages, exécute les appels d’outil et renvoie la réponse du modèle.

    confirmer(nom) renvoie True si l’utilisateur accepte d’écraser la fiche ;
    signaler(texte) affiche une opération ou un refus à l’utilisateur.
    """
    # À faire (étape 2) [fait] : envoyer la conversation avec client.envoyer et garder l’historique.
    # À faire (étape 3) [fait] : exécuter les appels d’outil du modèle jusqu’à sa réponse finale. 
    # À faire (étape 4)[fait] : arrêter la question au-delà des limites.
    taille_initiale = len(messages)
    appels = 0

    try: 
        messages.append({"role": "user", "content": question})
        reponse = client.envoyer(service, modele, messages, outils.DEFINITIONS)
        message = reponse.choices[0].message

        while message.tool_calls :
            appels += len(message.tool_calls)
            if appels > limites["appels_outil_max"]:
                del messages[taille_initiale:]
                return "Question arrêtée : trop d'appels d'outil. Reformule ou pose une autre question."
            messages.append(message)

            for appel in message.tool_calls:

                if appel.function.name == "ecrire_fiche":
                    signaler("Écriture en cours...")
                else:
                    signaler("Lecture en cours...")

                try:
                    resultat = outils.executer(appel, limites, confirmer)
                except outils.AccesRefuse as erreur:
                    signaler(f"Refusé : {erreur}")
                    resultat = str(erreur)
                messages.append({
                    "role": "tool",
                    "tool_call_id": appel.id,       
                    "content": resultat,            
                })
            
            reponse = client.envoyer(service, modele, messages, outils.DEFINITIONS)    
            message = reponse.choices[0].message
    
    except Exception:
        del messages[taille_initiale:]
        raise
    
    texte = message.content
    messages.append({"role": "assistant","content": texte})
    return texte
