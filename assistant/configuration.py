"""Configuration de l’assistant : service d’IA dans .env, limites dans limites.toml."""

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

# __file__ : chemin de ce fichier ; resolve() le rend absolu, chaque .parent remonte d’un dossier.
RACINE = Path(__file__).resolve().parent.parent


# Exception propre au projet : raise ConfigurationInvalide("message"), puis except ConfigurationInvalide.
class ConfigurationInvalide(Exception):
    """La configuration ne permet pas de démarrer l’assistant."""


# Entre deux Path, ou un Path et une chaîne, / assemble un chemin.
def charger_limites(chemin=RACINE / "limites.toml"):
    """Renvoie les limites de limites.toml dans un dictionnaire."""
    with open(chemin, "rb") as fichier:  # "rb" : lecture en binaire, demandée par tomllib
        limites = tomllib.load(fichier)
    limites["dossier_fiches"] = RACINE / limites["dossier_fiches"]
    return limites


def charger_configuration():
    """Lit .env et renvoie la configuration du service d’IA dans un dictionnaire."""
    load_dotenv(RACINE / ".env")
    service = os.getenv("SERVICE", "litellm")  # variable d’environnement SERVICE, sinon "litellm"
    if service == "simule":
        return {"service": "simule", "modele": "simule"}
    # À faire (étape 1) [fait] : lire LITELLM_API_KEY, LITELLM_BASE_URL et MODELE ;
    cle = os.getenv("LITELLM_API_KEY")
    url = os.getenv("LITELLM_BASE_URL")
    modele = os.getenv("MODELE")

    # lever ConfigurationInvalide avec un message qui dit quoi faire si la clé ou l’adresse manque ;
    if not cle :
        raise ConfigurationInvalide("La variable LITELLM_API_KEY est absente ou vide dans .env, ajoutez une clé valide")
    if not url : 
        raise ConfigurationInvalide("La variable LITELLM_BASE_URL est absente ou vide dans .env, ajoutez une URL valide")
    if not modele :
        raise ConfigurationInvalide("La variable MODELE est absente ou vide dans .env, ajoutez un modèle disponible")

    # renvoyer {"service": "litellm", "url": ..., "cle": ..., "modele": ...}.
    return {"service": "litellm", "url": url, "cle": cle, "modele": modele}
