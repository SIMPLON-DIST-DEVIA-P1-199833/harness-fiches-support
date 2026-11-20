"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""

import json

from pathlib import Path

DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "lire_fiche",
            "description": "Lit une fiche de procédure et renvoie son contenu Markdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {
                        "type": "string",
                        "description": "Nom du fichier, par exemple modifier-taux-tva.md",
                    }
                },
                "required": ["nom"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ecrire_fiche",
            "description": "Ecrit une fiche de procédure et l'enregistre dans le dossier des fiches. Un ecrasement de fiche existante requiert la confirmation du technicien.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {
                        "type": "string",
                        "description": "Nom du fichier, par exemple suspendre-compte.md",
                    },
                    "contenu": {
                        "type": "string",
                        "description": "Contenu du fichier complet, que ce soit pour la creation d'une nouvelle fiche ou la modification d'une fiche existant. Au format Markdown, en suivant le format des fiches existantes: # Titre, puis les sections ## Symptôme, ## Étapes, ## Vérification",
                    },
                },
                "required": ["nom", "contenu"],
            },
        },
    },
]
# Adding this so if we add other tools later, conditions in executer() would still work
KNOWN_TOOLS = {definition["function"]["name"] for definition in DEFINITIONS}


class AccesRefuse(Exception):
    """Une limite fixée par l’équipe interdit l’opération demandée."""


def lister_fiches(limites):
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(
        chemin.name
        for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"])
    )


# See : https://www.stephane-robert.info/docs/developper/programmation/python/pathlib/#normaliser-avec-resolve
# More readable than official python doc
def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # See: https://docs.python.org/fr/3/library/pathlib.html#pathlib.Path.resolve gives absolute path
    try:
        if not isinstance(nom, str) or not nom:
            raise AccesRefuse(
                f"Access refused - {nom!r} is not a valid type (str) or name"
            )
        folder = Path(limites["dossier_fiches"]).resolve()
        path = (folder / nom).resolve()
        if not path.is_relative_to(folder):
            raise AccesRefuse(f"Acces refused - {nom} outside of the fiches folder")
        # Subfolders not authorized
        if path.parent != folder:
            raise AccesRefuse("Access refused - Subfolders are not allowed")
        if path.suffix != limites["extension"]:
            raise AccesRefuse(
                f"Access refused - only {limites['extension']} files are valid"
            )
    # Catch all in case we are passed bullshit in the name
    except ValueError as error:
        raise AccesRefuse("Access refused - not a valid name :)") from error
    return path


def _check_file_size(size, limites):
    """Raise AccesRefuse if size (in bytes) is above the fiche size limit."""
    max_size = limites["taille_max_ko"] * 1000
    if size > max_size:
        raise AccesRefuse(
            f"Access refused - File size is too big by {size - max_size} bytes. You are limited to {limites['taille_max_ko']}ko."
        )


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    path = chemin_autorise(nom, limites)
    if not path.is_file():
        raise AccesRefuse(
            f"Access refused - {nom!r} was not found or is not a valid file"
        )
    # Size of file in bytes
    file_size = path.stat().st_size
    _check_file_size(file_size, limites)
    try:
        fiche = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise AccesRefuse("Access refused - File is not valid utf-8") from error
    # Covers any disk read failures
    except OSError as error:
        raise AccesRefuse("Access refused - File could not be opened") from error
    return fiche


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    path = chemin_autorise(nom, limites)
    if not isinstance(contenu, str):
        raise AccesRefuse(
            f"Access refused - Content to add inside the fiche should be of type str, it is {type(contenu)}"
        )
    # Size of content in bytes
    content_size = len(contenu.encode("utf-8"))
    _check_file_size(content_size, limites)
    # Check if fiche existed before write
    path_existed = path.is_file()
    # Tests if fiche existed and THEN tests if technician confirmed the write
    if path_existed and not confirmer(nom):
        raise AccesRefuse(
            f"Access refused - overwriting {nom!r} was declined by the technician"
        )
    try:
        path.write_text(contenu, encoding="utf-8")
    # Covers any disk write failures
    except OSError as error:
        raise AccesRefuse(f"Access refused - {nom!r} could not be written") from error
    return f"{nom} overwritten" if path_existed else f"{nom} created"


def _parse_arguments(call):
    """Return the tool call arguments as a dict, or raise AccesRefuse."""
    try:
        # Args written by the model, follow schema for parameters in DEFINITIONS
        args = json.loads(call.function.arguments)
    # Need TypeError, otherwise a test with None (not string) as args would pass for example. See test_fail_executer_none_type()
    except (json.JSONDecodeError, TypeError) as error:
        raise AccesRefuse("Access refused - Invalid JSON arguments") from error
    if not isinstance(args, dict):
        raise AccesRefuse("Access refused - arguments should be a JSON object")
    return args


def _check_required_arg(args, name):
    """Return args[name], or raise AccesRefuse if model did not send it."""
    my_arg = args.get(name)
    if my_arg is None:
        raise AccesRefuse(f"Access refused - Missing argument {name!r}")
    return my_arg


def executer(call, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    args = _parse_arguments(call)
    func_name = call.function.name
    # See constant KNOWN_TOOLS declared at top of file
    if func_name not in KNOWN_TOOLS:
        raise AccesRefuse(f"Access refused - {func_name} is an unknown tool call")
    fiche_name = _check_required_arg(args, "nom")
    if func_name == "lire_fiche":
        result = lire_fiche(fiche_name, limites)
    elif func_name == "ecrire_fiche":
        content = _check_required_arg(args, "contenu")
        result = ecrire_fiche(fiche_name, content, limites, confirmer)
    # Handle any tool we added in DEFINITION that was not implemented yet
    else:
        raise AccesRefuse(
            f"Access refused - {func_name} tool call is described in DEFINITIONS but not implemented yet"
        )
    return result
