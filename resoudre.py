"""Termine le code de l’étape en cours avec la version de référence, pour passer à la suivante.

Usage : python resoudre.py
L’étape en cours est la plus petite étape dont il reste un « À faire (étape n) » dans assistant/ ;
sans « À faire », c’est la dernière étape. Seuls les fichiers de code modifiés par cette étape sont remplacés.
Ton travail est d’abord enregistré dans un commit ; il reste dans ton historique.
Le formateur te donne le jeton d’accès à la référence.
"""

import base64
import getpass
import os
import re
import subprocess
import sys
from pathlib import Path

DEPOT_REFERENCE = "https://github.com/nimser/harness-fiches-support.git"
DERNIERE_ETAPE = 5
MARQUEUR = re.compile(r"À faire \(étape (\d+)\)|NotImplementedError\(\"Étape (\d+)")
NON_REMPLACES = {"README.md"}
REFS = {"debut": "refs/resoudre/debut", "fin": "refs/resoudre/fin"}


def git(*arguments, entree=None, env=None):
    """Lance une commande Git et renvoie le résultat, sans s’arrêter en cas d’échec."""
    return subprocess.run(["git", *arguments], input=entree, capture_output=True, env=env)


def arreter(message):
    print(message)
    sys.exit(1)


def etape_en_cours():
    """Renvoie l’étape en cours et les fichiers où il reste des « À faire » de cette étape."""
    restes = {}
    for chemin in sorted(Path("assistant").glob("*.py")):
        for trouve in MARQUEUR.finditer(chemin.read_text(encoding="utf-8")):
            etape = int(trouve.group(1) or trouve.group(2))
            restes.setdefault(etape, set()).add(str(chemin))
    if not restes:
        return DERNIERE_ETAPE, []
    etape = min(restes)
    return etape, sorted(restes[etape])


def enregistrer_travail(etape):
    """Enregistre les modifications en cours dans un commit, .env exclu."""
    if os.path.exists(".env") and git("check-ignore", "-q", ".env").returncode != 0:
        arreter("Arrêt : .env n’est pas ignoré par Git. Ajoute-le à .gitignore avant de continuer.")
    if not git("status", "--porcelain").stdout:
        return
    git("add", "-A")
    commit = git("commit", "-m", f"Sauvegarde avant la résolution de l’étape {etape}")
    if commit.returncode != 0:
        arreter("Le commit de sauvegarde a échoué :\n" + commit.stderr.decode())


def recuperer_reference(etape, jeton):
    """Télécharge le début et la fin de l’étape sans ajouter de dépôt distant."""
    debut = "main" if etape == 1 else f"fin-etape-{etape - 1}"
    identifiants = base64.b64encode(f"x-access-token:{jeton}".encode()).decode()
    env = dict(
        os.environ,
        GIT_TERMINAL_PROMPT="0",
        GIT_CONFIG_COUNT="1",
        GIT_CONFIG_KEY_0="http.https://github.com/.extraHeader",
        GIT_CONFIG_VALUE_0=f"Authorization: Basic {identifiants}",
    )
    resultat = git(
        "fetch", "--no-tags", "--force", DEPOT_REFERENCE,
        f"refs/heads/{debut}:{REFS['debut']}", f"refs/heads/fin-etape-{etape}:{REFS['fin']}", env=env,
    )
    if resultat.returncode != 0:
        arreter("Référence inaccessible : jeton refusé ou expiré, ou connexion impossible. Demande un nouveau jeton au formateur.")


def appliquer_reference(etape):
    """Remplace les fichiers modifiés par l’étape par leur version de fin d’étape, puis enregistre un commit."""
    modifies = git("diff", "--name-only", "-z", REFS["debut"], REFS["fin"]).stdout.decode().split("\0")
    fichiers = [chemin for chemin in modifies if chemin and chemin not in NON_REMPLACES]
    restauration = git(
        "restore", f"--source={REFS['fin']}", "--staged", "--worktree",
        "--pathspec-from-file=-", "--pathspec-file-nul", entree="\0".join(fichiers).encode(),
    )
    for ref in REFS.values():
        git("update-ref", "-d", ref)
    if restauration.returncode != 0:
        arreter("La restauration a échoué :\n" + restauration.stderr.decode())
    if git("diff", "--cached", "--quiet").returncode == 0:
        print(f"Ton code correspond déjà à la fin de l’étape {etape}.")
        return
    commit = git("commit", "-m", f"Résolution de l’étape {etape} (version de référence)")
    if commit.returncode != 0:
        arreter("Le commit de résolution a échoué :\n" + commit.stderr.decode())
    print(f"Étape {etape} résolue : un commit contient la version de référence de {', '.join(fichiers)}.")


def main():
    if len(sys.argv) != 1:
        arreter("Usage : python resoudre.py")
    racine = git("rev-parse", "--show-toplevel")
    if racine.returncode != 0:
        arreter("Lance ce script dans ton dépôt cloné.")
    os.chdir(racine.stdout.decode().strip())
    if git("branch", "--show-current").stdout.decode().strip() != "main":
        arreter("Passe d’abord sur ta branche main : git switch main")

    etape, restes = etape_en_cours()
    if restes:
        print(f"Étape en cours : {etape}. Il reste un « À faire (étape {etape}) » dans {', '.join(restes)}.")
    else:
        print(f"Étape en cours : {etape}, plus aucun « À faire » dans assistant/.")
    print(f"Les fichiers de code de l’étape {etape} seront remplacés par la version de référence ; ton README est conservé.")
    print("Ton travail actuel est d’abord enregistré dans un commit.")
    if input("Continuer ? (o/N) ").strip().lower() != "o":
        arreter("Rien n’a été modifié.")
    jeton = getpass.getpass("Jeton donné par le formateur : ").strip()
    if not jeton:
        arreter("Jeton absent : rien n’a été modifié.")

    enregistrer_travail(etape)
    recuperer_reference(etape, jeton)
    appliquer_reference(etape)
    if etape < DERNIERE_ETAPE:
        print(f"Tu peux commencer l’étape {etape + 1}. Pense à pousser : git push")
    else:
        print("Pense à pousser : git push")


if __name__ == "__main__":
    main()
