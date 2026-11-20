"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""
import json
import os
from pathlib import Path

DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "lire_fiche",
            "description": "Lit une fiche de procédure et renvoie son contenu Markdown.",
            "parameters": {
                "type": "object",
                "properties": {"nom": {"type": "string", "description": "Nom du fichier, par exemple modifier-taux-tva.md"}},
                "required": ["nom"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ecrire_fiche",
            "description": "Crée ou écrase une fiche de procédure (Markdown) dans le dossier des fiches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {"type": "string", "description": "Nom du fichier, par exemple suspendre-compte.md"},
                    "contenu": {"type": "string", "description": "Contenu Markdown de la fiche"},
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
    return sorted(chemin.name for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"]))


def chemin_autorise(nom, limites): #Ici nom = nom du fichier
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    if not isinstance(nom, str) or not nom.strip():
        raise AccesRefuse("Nom de fiche invalide.")
    chemin = Path(nom)
    #Chemin absolu = à la racine du systeme donc hors du dossier de travail
    # .. renvoie au dossier parent donc même remarque
    if chemin.is_absolute() or ".." in chemin.parts:
        raise AccesRefuse("Accès refusé : chemin hors du dossier des fiches.")
    #vérifier l'extension
    if chemin.suffix != limites["extension"]:
        raise AccesRefuse(
            f"Accès refusé : seule l'extension {limites['extension']} est autorisée."
        )
    dossier = Path(limites["dossier_fiches"]).resolve()
    cible = (dossier / chemin).resolve()
    if not cible.is_relative_to(dossier):
        raise AccesRefuse("Accès refusé : chemin hors du dossier des fiches.")
    return cible


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    chemin = chemin_autorise(nom,limites)
    # Passage en octets : 1ko = 1024 octets 
    taille_max = limites["taille_max_ko"] * 1024
    if not chemin.is_file():
        raise AccesRefuse("Le fichier n'existe pas")
    if chemin.stat().st_size > taille_max:
        raise AccesRefuse("Fichier trop lourd")
    try:    
        with open(chemin, "r", encoding="utf-8") as fiche:
            return fiche.read()
    except OSError as e:
        raise AccesRefuse("Erreur dans la lecture du fichier")

        

def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    chemin = chemin_autorise(nom,limites)
    taille_contenu = len(contenu.encode("utf-8"))
    # Passage en octets : 1ko = 1024 octets 
    taille_max = limites["taille_max_ko"] * 1024
    if taille_contenu > taille_max:
        raise AccesRefuse("Fichier trop lourd")
    if chemin.exists():
        if not confirmer(nom):
            raise AccesRefuse("Confirmation fausse")
    try:
        with open(chemin, "w", encoding="utf-8") as fiche:
            fiche.write(contenu)
            return f"Nouvelle fiche crée."
    except OSError as e:
        raise AccesRefuse("Erreur dans l'écriture du fichier")


def executer(appel, limites, confirmer = None):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    #Renvoie un dicto qui contient des arguments
    try:
        arguments = json.loads(appel.function.arguments)
    except (json.JSONDecodeError, TypeError):
        raise AccesRefuse("Arguments invalides pour l'outil.")
    #On se sert du fait que json.loads retourne un dico pour vérifier 
    #qu'on a bien ce que l'on veut (ex. '{"nom": "fiche.md"}')
    if not isinstance(arguments, dict):
        raise AccesRefuse("Arguments invalides pour l'outil.")
    nom_outil = appel.function.name
    if nom_outil == "lire_fiche":
        nom_fiche = arguments.get("nom")
        if not isinstance(nom_fiche, str) or not nom_fiche.strip():
            raise AccesRefuse("Argument 'nom' manquant pour lire fiche")
        return lire_fiche(nom_fiche, limites)
    if nom_outil == "ecrire_fiche":
        nom_fichier = arguments.get("nom")
        contenu = arguments.get("contenu")
        if not isinstance(nom_fichier, str) or not nom_fichier.strip():
            raise AccesRefuse("Argument 'nom' manquant pour ecrire_fiche.")
        if not isinstance(contenu, str):
            raise AccesRefuse("Argument 'contenu' manquant pour ecrire_fiche.")
        if confirmer is None:
            raise AccesRefuse("Confirmation impossible : pas de fonction confirmer.")
        return ecrire_fiche(nom_fichier, contenu, limites, confirmer)
    #Cas où il n'y a pas d'outils correspondant
    raise AccesRefuse(f"Outil inconnu : {nom_outil}")
