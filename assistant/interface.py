"""Interface en ligne de commande de l’assistant."""

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from assistant import client, conversation
from assistant.configuration import (
    ConfigurationInvalide,
    charger_configuration,
    charger_limites,
)
from assistant.outils import AccesRefuse

AIDE = """Pose ta question, puis valide avec Entrée.
/joindre <fiche.md> <question> : joindre une fiche à ta question
/nouvelle : repartir d’une conversation vide
/quitter : quitter"""

console = Console()


# See: https://rich.readthedocs.io/en/stable/prompt.html
def confirmer(nom):
    """Demande à l’utilisateur s’il accepte d’écraser la fiche."""
    # 2 options possible, otherwise keep asking in a loop
    # if no response is provided (empty), default to False ('n')
    response = Confirm.ask(
        f"Do you really wish to overwrite {nom!r} ?",
        choices=["y", "n"],
        default=False,
        case_sensitive=False,
    )
    return response


def signaler(texte):
    """Affiche une opération ou un refus, sans l’enregistrer dans la conversation."""
    console.print(f"[italic]{texte}[/italic]")


# Taking the parsing logic out of lancer() so it can be tested
def parse_join(user_input: str) -> tuple | None:
    """Return (fiche_name, question) tuple for a valid /joindre command, otherwise None."""
    args = user_input.split(maxsplit=2)
    # Being strict with the command so you can't pass /joindreabc for example
    if len(args) != 3 or args[0] != "/joindre":
        return None
    return args[1], args[2]


def lancer(verifier=False):
    """Démarre l’assistant et renvoie le code de sortie du programme."""
    try:
        configuration = charger_configuration()
        limites = charger_limites()
        service = client.creer_client(configuration, limites)
    # erreur : l’exception levée ; l’afficher donne son message
    except ConfigurationInvalide as erreur:
        console.print(f"Erreur : {erreur}")
        return 1
    if verifier:
        console.print(client.verifier_acces(service, configuration["modele"]))
        return 0
    messages = conversation.nouvelle_conversation(limites)
    console.print(
        f"Assistant des fiches support, modèle {configuration['modele']}.\n{AIDE}"
    )
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
            # Split on whitespace as default
            parsed_input = parse_join(saisie)
            if parsed_input is None:
                signaler(
                    "Expected different arguments, please respect this format:\n/joindre <fiche.md> <question>"
                )
                continue
            file_name, ques_text = parsed_input
            try:
                # joindre_fiche takes file_name as 1st arg and question as 2nd
                question = conversation.joindre_fiche(file_name, ques_text, limites)
            # Keep looping if we get an exception
            except AccesRefuse as error:
                signaler(f"Error while using /joindre: {error}")
                continue
        signaler("Le service réfléchit…")
        try:
            reponse = conversation.poser(
                question,
                messages,
                service,
                configuration["modele"],
                limites,
                confirmer,
                signaler,
            )
            console.print(Markdown(reponse))
        # Print caught error in console and continue so we keep looping
        # Need to add the LimiteAtteinte exception, otherwise the program would exit when it reaches the limit. Test this with `boucle` when running the service SIMULE
        except (client.ServiceIndisponible, conversation.LimiteAtteinte) as erreur:
            console.print(f"Erreur : {erreur}")
            continue
        # Quit if Ctrl+D / Ctrl+C during a question, same as above for saisie
        except (EOFError, KeyboardInterrupt):
            return 0
