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


def _handle_tool_call(tool_call, limites, confirmer, signaler):
    """Run/refuse a tool call from model and build its answer
    A response is always sent back to the model, whether the tool call was refused or not

    Returns:
        dict: tool message for the convo, with call_id and tool result
    """
    try:
        result = outils.executer(tool_call, limites, confirmer)
        signaler(
            f"Tool_call: {tool_call.function.name}: {tool_call.function.arguments}"
        )
    # Send refusal to the model
    except outils.AccesRefuse as error:
        result = f"{error}"
        signaler(result)
    return {"role": "tool", "tool_call_id": tool_call.id, "content": result}


def poser(question, messages, service, modele, limites, confirmer, signaler):
    """Ajoute la question aux messages, exécute les appels d’outil et renvoie la réponse du modèle.

    confirmer(nom) renvoie True si l’utilisateur accepte d’écraser la fiche ;
    signaler(texte) affiche une opération ou un refus à l’utilisateur.
    """
    question_msg = {"role": "user", "content": question}
    # Create shallow list copy
    # Only modify history if no exception is raised and we got a response
    convo = messages + [question_msg]
    # Count tool calls for each question
    count_tool_calls = 0
    while True:
        # Model gets tool description. Model only asks, our code still does the reading, handling, executing
        response = client.envoyer(service, modele, convo, outils.DEFINITIONS)
        model_reply = response.choices[0].message
        # No tool call, final response if true, get out of loop
        if not model_reply.tool_calls:
            # Handle final answer without content
            if not model_reply.content:
                raise client.ServiceIndisponible(
                    "AI service returned an empty answer, ask your question again."
                )
            convo.append({"role": "assistant", "content": model_reply.content})
            break
        # Convert tool call object from model to dict, then add it to convo
        convo.append(model_reply.to_dict(exclude_none=True))
        for tool_call in model_reply.tool_calls:
            if count_tool_calls >= limites["appels_outil_max"]:
                raise LimiteAtteinte(
                    f"Maximum amount ({limites['appels_outil_max']}) of tool calls reached. Ask again, but be more precise"
                )
            # Increment if max is not reached yet
            count_tool_calls += 1
            tool_message = _handle_tool_call(tool_call, limites, confirmer, signaler)
            convo.append(tool_message)
    # Use slicing to modify list in place.
    # > Replace all elems in messages by elems in convo
    messages[:] = convo
    return model_reply.content
