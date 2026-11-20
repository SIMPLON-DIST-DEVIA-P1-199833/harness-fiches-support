"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""

from pathlib import Path
import json

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
    # À faire (étape 4) : décrire l’outil ecrire_fiche.
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


def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # `limites` est un dictionnaire chargé par charger_limites() (fichier configuration.py) à partir de limites.toml
    # .resolve() applique les .. et les liens symboliques : on compare les chemins absolus
    # .is_relative_to() vérifie si un chemin est à l'intérieur d'un autre
    # dossier : l'adresse du dossier des fiches, limites["dossier_fiches"], transformée avec .resolve() en chemin absolu et mis dans une variable
    # chemin : pareil pour le fichier demandé (dossier / nom), avec .resolve()
    # si ce n'est pas le cas, lever l'exception AccesRefuse (une classe définie dans ce fichier)
    # même logique pour l'extension : comparer chemin.suffix à limites["extension"], et lever AccesRefuse si elles sont différentes
    dossier = limites["dossier_fiches"].resolve()
    chemin = (dossier / nom).resolve()

    if not chemin.is_relative_to(dossier):
        raise AccesRefuse(f"Accès refusé à '{nom}' : hors du dossier des fiches.")
    if chemin.suffix != limites["extension"]:
        raise AccesRefuse(
            f"Accès refusé à '{nom}' : le fichier n'a pas l'extension attendue."
        )
    return chemin


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # ### Conversions courantes de Octet à Kilo-octets (Ko) : *`taille_octets / 1024`* -> donc * 1024
    fiche = chemin_autorise(nom, limites)
    taille_max_octet = limites["taille_max_ko"] * 1024
    if not fiche.is_file():
        raise AccesRefuse(f"Accès refusé à '{nom}' : le fichier n'existe pas.")
    if fiche.stat().st_size > taille_max_octet:
        raise AccesRefuse(
            f"Accès refusé à '{nom}' : le fichier dépasse la limite {limites['taille_max_ko']} Ko."
        )
    return fiche.read_text()


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    raise NotImplementedError("Étape 4 : ecrire_fiche")


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    nom_outil = appel.function.name
    try:
        arguments_outil = json.loads(appel.function.arguments)
    except json.JSONDecodeError:
        raise AccesRefuse(
            "Arguments illisibles : renvoyer l'appel avec un JSON lisible."
        )

    if nom_outil == "lire_fiche":
        # est-ce que la clé 'nom' dans arguments_outil existe ?
        if "nom" not in arguments_outil:
            raise AccesRefuse(
                "Argument 'nom' manquant : indiquer le nom de la fiche à lire."
            )
        return lire_fiche(arguments_outil["nom"], limites)
    raise AccesRefuse(f"Outil inconnu : {nom_outil}.")
