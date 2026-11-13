"""Remplace ton code par la version de référence de fin d’étape, pour passer à l’étape suivante.

Usage : python resoudre.py <étape>, par exemple python resoudre.py 2 avant de commencer l’étape 3.
Ton travail est d’abord enregistré dans un commit ; il reste dans ton historique.
Les fichiers que tu as ajoutés et qui n’existent pas dans la référence sont conservés.
Le formateur te donne le jeton d’accès à la référence.
"""

import base64
import getpass
import os
import subprocess
import sys

DEPOT_REFERENCE = "https://github.com/nimser/harness-fiches-support.git"
DERNIERE_ETAPE = 5


def git(*arguments, entree=None, env=None):
    """Lance une commande Git et renvoie le résultat, sans s’arrêter en cas d’échec."""
    return subprocess.run(["git", *arguments], input=entree, capture_output=True, env=env)


def arreter(message):
    print(message)
    sys.exit(1)


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
    """Télécharge la branche fin-etape-<etape> sans ajouter de dépôt distant."""
    identifiants = base64.b64encode(f"x-access-token:{jeton}".encode()).decode()
    env = dict(
        os.environ,
        GIT_TERMINAL_PROMPT="0",
        GIT_CONFIG_COUNT="1",
        GIT_CONFIG_KEY_0="http.https://github.com/.extraHeader",
        GIT_CONFIG_VALUE_0=f"Authorization: Basic {identifiants}",
    )
    resultat = git("fetch", "--no-tags", DEPOT_REFERENCE, f"fin-etape-{etape}", env=env)
    if resultat.returncode != 0:
        arreter("Référence inaccessible : jeton refusé ou expiré, ou connexion impossible. Demande un nouveau jeton au formateur.")


def appliquer_reference(etape):
    """Remplace les fichiers de la référence par leur version de fin d’étape, puis enregistre un commit."""
    fichiers = git("ls-tree", "-r", "-z", "--name-only", "FETCH_HEAD").stdout
    restauration = git(
        "restore", "--source=FETCH_HEAD", "--staged", "--worktree",
        "--pathspec-from-file=-", "--pathspec-file-nul", entree=fichiers,
    )
    if restauration.returncode != 0:
        arreter("La restauration a échoué :\n" + restauration.stderr.decode())
    if git("diff", "--cached", "--quiet").returncode == 0:
        print(f"Ton dépôt correspond déjà à la fin de l’étape {etape}.")
        return
    commit = git("commit", "-m", f"Résolution de l’étape {etape} (version de référence)")
    if commit.returncode != 0:
        arreter("Le commit de résolution a échoué :\n" + commit.stderr.decode())
    print(f"Étape {etape} résolue : un commit contient la version de référence.")


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or not 1 <= int(sys.argv[1]) <= DERNIERE_ETAPE:
        arreter(f"Usage : python resoudre.py <étape>, avec une étape de 1 à {DERNIERE_ETAPE}.")
    etape = int(sys.argv[1])
    racine = git("rev-parse", "--show-toplevel")
    if racine.returncode != 0:
        arreter("Lance ce script dans ton dépôt cloné.")
    os.chdir(racine.stdout.decode().strip())
    if git("branch", "--show-current").stdout.decode().strip() != "main":
        arreter("Passe d’abord sur ta branche main : git switch main")

    print(f"Tes fichiers seront remplacés par la version de référence de fin d’étape {etape}.")
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
