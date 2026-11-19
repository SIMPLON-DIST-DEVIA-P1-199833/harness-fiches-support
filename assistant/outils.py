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
                "properties": {"nom": {"type": "string", "description": "Nom du fichier, par exemple modifier-taux-tva.md"}},
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
    return sorted(chemin.name for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"]))


def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # À faire (étape 3)[fait] : refuser tout chemin hors du dossier, y compris par .., chemin absolu
    # ou lien symbolique, et toute autre extension que celle des limites.
    dossier = limites["dossier_fiches"].resolve()
    extension = limites["extension"]
    chemin = (dossier/nom).resolve()
    if not chemin.is_relative_to(dossier) :
        raise AccesRefuse("La fiche doit être dans le dossier autorisé") # Je choisis de ne pas indiquer le dossier pour raison de sécurite
    if extension != chemin.suffix : # Je choisis d'être strict de respecter la casse .MD ne passe pas
        raise AccesRefuse(f"La fiche doit être en extension {extension}") # Je choisis d'indiquer l'extension si jamais extension change dans limites.
    return chemin


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # À faire (étape 3) [fait] : contrôler le chemin et la taille, puis lire la fiche.
    chemin = chemin_autorise(nom, limites)
    if not chemin.is_file() :
        raise AccesRefuse(f"La fiche {nom} n'existe pas")
    if chemin.stat().st_size > limites["taille_max_ko"]*1024 :
        raise AccesRefuse(f"La fiche depasse la taille maximale de {limites["taille_max_ko"]}Ko")
    contenu = chemin.read_text(encoding="utf-8")
    return contenu

def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    raise NotImplementedError("Étape 4 : ecrire_fiche")


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    # À faire (étape 3) [fait] : lire les arguments JSON de appel.function.arguments,
    # puis lancer l’outil nommé appel.function.name ; tout appel invalide est refusé.
    try : 
        arguments = json.loads(appel.function.arguments)
        nom = arguments["nom"]    
    except (json.JSONDecodeError, KeyError):
        raise AccesRefuse("Arguments invalides : attendu un JSON avec la clé 'nom'")
    if appel.function.name == "lire_fiche":
        contenu = lire_fiche(nom, limites)
        return contenu
    raise AccesRefuse(f"Outil inconnu : {appel.function.name}") 

