"""Configuration de l’assistant : service d’IA dans .env, limites dans limites.toml."""

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

# __file__ : chemin de ce fichier ; resolve() le rend absolu, chaque .parent remonte d’un dossier.
RACINE = Path(__file__).resolve().parent.parent
# Default model chosen if missing or '' in .env file
DEFAULT_MODEL = "gpt-luna"


# Exception propre au projet : raise ConfigurationInvalide("message"), puis except ConfigurationInvalide.
class ConfigurationInvalide(Exception):
    """La configuration ne permet pas de démarrer l’assistant."""


# Entre deux Path, ou un Path et une chaîne, / assemble un chemin.
def charger_limites(chemin=RACINE / "limites.toml"):
    """Renvoie les limites de limites.toml dans un dictionnaire."""
    with open(
        chemin, "rb"
    ) as fichier:  # "rb" : lecture en binaire, demandée par tomllib
        limites = tomllib.load(fichier)
    limites["dossier_fiches"] = RACINE / limites["dossier_fiches"]
    return limites


# Error message for the charger_configuration() function
MISSING_VAR_MESSAGE = (
    "{var} missing in .env local file.\n"
    "If .env does not exist, copy .env.example into .env. "
    "Then fill in LITELLM_BASE_URL and LITELLM_API_KEY.\n"
    "If MODELE is missing, it defaults to {default_model}."
)


def charger_configuration():
    """Lit .env et renvoie la configuration du service d’IA dans un dictionnaire."""
    load_dotenv(RACINE / ".env")
    service = os.getenv(
        "SERVICE", "litellm"
    )  # variable d’environnement SERVICE, sinon "litellm"
    if service == "simule":
        return {"service": "simule", "modele": "simule"}
    url = os.getenv("LITELLM_BASE_URL")
    api_key = os.getenv("LITELLM_API_KEY")
    model = os.getenv("MODELE") or DEFAULT_MODEL
    # Not checking 'model' since DEFAULT_MODEL constant is defined at the top of the file
    if not url:
        raise ConfigurationInvalide(
            MISSING_VAR_MESSAGE.format(
                var="LITELLM_BASE_URL", default_model=DEFAULT_MODEL
            )
        )
    if not api_key:
        raise ConfigurationInvalide(
            MISSING_VAR_MESSAGE.format(
                var="LITELLM_API_KEY", default_model=DEFAULT_MODEL
            )
        )
    return {"service": "litellm", "url": url, "cle": api_key, "modele": model}
