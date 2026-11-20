"""Interface en ligne de commande de l’assistant."""

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from assistant import client, conversation, outils
from assistant.configuration import (
    ConfigurationInvalide,
    charger_configuration,
    charger_limites,
)

AIDE = """Pose ta question, puis valide avec Entrée.
/joindre <fiche.md> <question> : joindre une fiche à ta question
/nouvelle : repartir d’une conversation vide
/fiches : liste les fiches disponibles
/quitter : quitter"""

console = Console()


def confirmer(nom):
    """Demande à l’utilisateur s’il accepte d’écraser la fiche."""
    # À faire (étape 4).
    raise NotImplementedError("Étape 4 : confirmer")


def signaler(texte):
    """Affiche une opération ou un refus, sans l’enregistrer dans la conversation."""
    console.print(f"[italic]{texte}[/italic]")


def lancer(verifier=False):
    """Démarre l’assistant et renvoie le code de sortie du programme."""
    try:
        configuration = charger_configuration()
        limites = charger_limites()
        service = client.creer_client(configuration, limites)
    except ConfigurationInvalide as erreur:  # erreur : l’exception levée ; l’afficher donne son message
        console.print(f"Erreur : {erreur}")
        return 1
    if verifier:
        console.print(client.verifier_acces(service, configuration["modele"]))
        return 0

    messages = conversation.nouvelle_conversation(limites)
    console.print(f"Assistant des fiches support, modèle {configuration['modele']}.\n{AIDE}")
    while True:
        try:
            saisie = Prompt.ask("\nToi").strip()
        except (EOFError, KeyboardInterrupt):  # l’une ou l’autre : Ctrl+D ou Ctrl+C
            return 0
        if saisie == "/quitter":
            return 0
        if saisie == "/nouvelle":
            messages = conversation.nouvelle_conversation(limites)
            signaler("Nouvelle conversation.")
            continue
        if saisie == "/fiches":
            console.print(conversation.lister_fiches(limites))
            continue
        if saisie.startswith("/joindre"):
            parties = saisie.split(maxsplit=2)
            if len(parties) != 3:
                console.print("Usage: /joindre <nomfiche.md> <question>")
                continue
            else:
                try:
                    saisie = conversation.joindre_fiche(parties[1], parties[2], limites)
                    console.print(Markdown(saisie))
                except outils.AccesRefuse as e:
                    saisie = f"Accès refusé: {e}"
        if not saisie:
            continue
        question = saisie
        # FAIT À faire (étape 2) : afficher les erreurs du service sans quitter.
        # FAIT À faire (étape 3) : /joindre <fiche.md> <question> joint la fiche à la question.
        signaler("Le service réfléchit…")
        try:
            reponse = conversation.poser(
                question, messages, service, configuration["modele"], limites, confirmer, signaler
            )
            console.print(Markdown(reponse))
        except client.ServiceIndisponible as si:
            reponse = f"Le service est indisponible ({si})"
            console.print(Markdown(reponse), style="red on white")
        except outils.AccesRefuse as ar:
            reponse = f"Accès refusé ({ar})"
            console.print(Markdown(reponse), style="blue on white")
