"""Interface en ligne de commande de l’assistant."""

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from assistant import client, conversation
from assistant.configuration import ConfigurationInvalide, charger_configuration, charger_limites

AIDE = """Pose ta question, puis valide avec Entrée.
/joindre <fiche.md> <question> : joindre une fiche à ta question
/nouvelle : repartir d’une conversation vide
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
        try:
            console.print(client.verifier_acces(service, configuration["modele"]))
        except client.ServiceIndisponible as erreur:
            console.print(f"Erreur : {erreur}")
            return 1
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
        if not saisie:
            continue
        question = saisie
        if saisie.startswith("/joindre"):
            morceaux = saisie.split(maxsplit=2)
            if len(morceaux) < 3:
                console.print("Usage: /joindre <fiche.md> < question>")
                continue

            try:
                question = conversation.joindre_fiche(morceaux[1], morceaux[2], limites)
            except outils.AccesRefuse as refus:
                signaler(refus)
                continue

        try:
            signaler("Le service réfléchit…")
            reponse = conversation.poser(
                question, messages, service, configuration["modele"], limites, confirmer, signaler
            )
        except client.ServiceIndisponible as erreur:
            console.print(f"Erreur : {erreur}")
            continue
        console.print(Markdown(reponse))
