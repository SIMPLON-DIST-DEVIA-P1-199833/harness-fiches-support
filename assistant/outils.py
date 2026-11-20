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
                f"Access refused - {nom} is not a valid type (str) or name"
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


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    path = chemin_autorise(nom, limites)
    if not path.is_file():
        raise AccesRefuse(
            f"Access refused - {nom!r} was not found or is not a valid file"
        )
    # Size of file in bytes
    file_size = path.stat().st_size
    max_size = limites["taille_max_ko"] * 1000
    if file_size > max_size:
        raise AccesRefuse(
            f"Access refused - File size is too big by {file_size - max_size} bytes. You are limited to {limites['taille_max_ko']}ko."
        )
    try:
        fiche = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise AccesRefuse("Access refused - File is not valid utf-8") from error
    except OSError as error:
        raise AccesRefuse("Access refused - File could not be opened") from error
    return fiche


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    raise NotImplementedError("Étape 4 : ecrire_fiche")


def executer(call, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    try:
        # Args written by the model, follow schema for parameters in DEFINITIONS
        args = json.loads(call.function.arguments)
    # Need TypeError, otherwise a test with None (not string) as args would pass for example. See test_fail_executer_none_type()
    except (json.JSONDecodeError, TypeError) as error:
        raise AccesRefuse("Access refused - Invalid JSON arguments") from error
    if not isinstance(args, dict):
        raise AccesRefuse("Access refused - arguments should be a JSON object")
    fiche_name = args.get("nom")
    # Name of the tool call
    func_name = call.function.name
    if func_name != "lire_fiche":
        raise AccesRefuse(f"Access refused - {func_name} is an unknown tool call")
    if fiche_name is None:
        raise AccesRefuse("Access refused - Missing argument 'nom'")
    result = lire_fiche(fiche_name, limites)
    return result
