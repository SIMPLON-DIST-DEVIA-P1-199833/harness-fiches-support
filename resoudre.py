"""Termine l’étape en cours avec la version de référence, pour passer à la suivante.

Usage : python resoudre.py [étape]
Sans numéro, des contrôles exécutés sur une copie de ton code déterminent l’étape en cours :
la première dont un contrôle échoue, ou la dernière si tous réussissent.
Seuls les fichiers de code modifiés par cette étape sont corrigés, dans un commit ajouté à ta branche.
Ton travail est d’abord enregistré dans un commit : il reste dans ton historique.
Le formateur te donne le jeton d’accès à la référence.
"""

import base64
import getpass
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

DEPOT_REFERENCE = "https://github.com/nimser/harness-fiches-support.git"
DERNIERE_ETAPE = 5
BRANCHES = ["main", *(f"fin-etape-{n}" for n in range(1, DERNIERE_ETAPE + 1)), "controles"]
NON_CORRIGES = {"README.md"}
DELAI_CONTROLES_S = 60


def git(*arguments, entree=None, env=None):
    """Lance une commande Git et renvoie le résultat, sans s’arrêter en cas d’échec."""
    return subprocess.run(["git", *arguments], input=entree, capture_output=True, env=env)


def ref(branche):
    return f"refs/resoudre/{branche}"


def arreter(message):
    print(message)
    sys.exit(1)


def lire_etape_demandee():
    if len(sys.argv) == 1:
        return None
    if len(sys.argv) == 2 and sys.argv[1].isdigit() and 1 <= int(sys.argv[1]) <= DERNIERE_ETAPE:
        return int(sys.argv[1])
    arreter(f"Usage : python resoudre.py [étape de 1 à {DERNIERE_ETAPE}]")


def recuperer_reference(jeton):
    """Télécharge les branches de référence et les contrôles, sans ajouter de dépôt distant."""
    identifiants = base64.b64encode(f"x-access-token:{jeton}".encode()).decode()
    env = dict(
        os.environ,
        GIT_TERMINAL_PROMPT="0",
        GIT_CONFIG_COUNT="1",
        GIT_CONFIG_KEY_0="http.https://github.com/.extraHeader",
        GIT_CONFIG_VALUE_0=f"Authorization: Basic {identifiants}",
    )
    references = [f"refs/heads/{branche}:{ref(branche)}" for branche in BRANCHES]
    if git("fetch", "--no-tags", "--force", DEPOT_REFERENCE, *references, env=env).returncode != 0:
        arreter("Référence inaccessible : jeton refusé ou expiré, ou connexion impossible. Demande un nouveau jeton au formateur.")


def supprimer_references():
    for branche in BRANCHES:
        git("update-ref", "-d", ref(branche))


def preparer_copie(dossier):
    """Copie ton code dans un dossier temporaire, avec les contrôles et le service simulé de référence."""
    shutil.copytree("assistant", dossier / "assistant", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy("limites.toml", dossier / "limites.toml")
    simule = git("show", f"{ref('fin-etape-5')}:assistant/service_simule.py").stdout
    (dossier / "assistant" / "service_simule.py").write_bytes(simule)
    archive = git("archive", "--format=tar", ref("controles"), "controles").stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as contenu:
        contenu.extractall(dossier, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
    (dossier / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")


def controler(dossier, etape):
    """Exécute les contrôles d’une étape et renvoie la liste des contrôles échoués."""
    rapport = dossier / f"rapport-{etape}.json"
    env = {nom: valeur for nom, valeur in os.environ.items() if nom != "SERVICE" and not nom.startswith("LITELLM_")}
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", RESOUDRE_RAPPORT=str(rapport))
    commande = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"controles/test_etape_{etape}.py"]
    try:
        resultat = subprocess.run(commande, cwd=dossier, env=env, capture_output=True, timeout=DELAI_CONTROLES_S)
    except subprocess.TimeoutExpired:
        return [f"contrôles interrompus après {DELAI_CONTROLES_S} s : ton code tourne peut-être sans fin"]
    if resultat.returncode == 0:
        return []
    if rapport.exists():
        echecs = json.loads(rapport.read_text(encoding="utf-8"))
        if echecs:
            return echecs
    return ["contrôles interrompus : " + (resultat.stdout + resultat.stderr).decode(errors="replace").strip()[-300:]]


def etape_en_cours():
    """Contrôle ton code, affiche le résultat et renvoie l’étape en cours."""
    if subprocess.run([sys.executable, "-m", "pytest", "--version"], capture_output=True).returncode != 0:
        arreter("pytest est introuvable : active l’environnement du projet (.venv), puis relance.")
    print("Contrôle de ton code…")
    with tempfile.TemporaryDirectory() as temporaire:
        dossier = Path(temporaire)
        preparer_copie(dossier)
        echecs = {n: controler(dossier, n) for n in range(1, DERNIERE_ETAPE)}
    etape = next((n for n, liste in echecs.items() if liste), DERNIERE_ETAPE)
    for n, liste in echecs.items():
        resume = "contrôles réussis" if not liste else "1 contrôle échoue" if len(liste) == 1 else f"{len(liste)} contrôles échouent"
        print(f"  Étape {n} : {resume}")
        if n == etape:
            for echec in liste:
                print(f"    - {echec}")
    if etape == DERNIERE_ETAPE:
        print(f"Étape en cours : {etape}, tests et démonstration.")
    else:
        print(f"Étape en cours : {etape}.")
    deja_faites = [str(n) for n, liste in echecs.items() if n > etape and not liste]
    if deja_faites:
        print(f"Attention : les contrôles de l’étape {', '.join(deja_faites)} réussissent déjà. "
              f"La correction de l’étape {etape} peut remplacer une partie de ce travail ; il restera dans ton historique.")
    return etape


def enregistrer_travail(etape):
    """Enregistre les modifications en cours dans un commit, .env exclu."""
    if not git("status", "--porcelain").stdout:
        return
    git("add", "-A")
    commit = git("commit", "-m", f"Sauvegarde avant la résolution de l’étape {etape}")
    if commit.returncode != 0:
        arreter("Le commit de sauvegarde a échoué :\n" + commit.stderr.decode())


def appliquer_reference(etape):
    """Corrige les fichiers modifiés par l’étape avec leur version de fin d’étape, dans un commit."""
    debut = ref("main" if etape == 1 else f"fin-etape-{etape - 1}")
    fin = ref(f"fin-etape-{etape}")
    modifies = git("diff", "--name-only", "-z", debut, fin).stdout.decode().split("\0")
    fichiers = [chemin for chemin in modifies if chemin and chemin not in NON_CORRIGES]
    restauration = git(
        "restore", f"--source={fin}", "--staged", "--worktree",
        "--pathspec-from-file=-", "--pathspec-file-nul", entree="\0".join(fichiers).encode(),
    )
    if restauration.returncode != 0:
        arreter("La correction a échoué :\n" + restauration.stderr.decode())
    if git("diff", "--cached", "--quiet").returncode == 0:
        print(f"Ton code correspond déjà à la fin de l’étape {etape} : aucun commit ajouté.")
        return
    commit = git("commit", "-m", f"Résolution de l’étape {etape} (version de référence)")
    if commit.returncode != 0:
        arreter("Le commit de résolution a échoué :\n" + commit.stderr.decode())
    print(f"Étape {etape} résolue : un commit corrige {', '.join(fichiers)}.")


def main():
    demandee = lire_etape_demandee()
    racine = git("rev-parse", "--show-toplevel")
    if racine.returncode != 0:
        arreter("Lance ce script dans ton dépôt cloné.")
    os.chdir(racine.stdout.decode().strip())
    if git("branch", "--show-current").stdout.decode().strip() != "main":
        arreter("Passe d’abord sur ta branche main : git switch main")
    if os.path.exists(".env") and git("check-ignore", "-q", ".env").returncode != 0:
        arreter("Arrêt : .env n’est pas ignoré par Git. Ajoute-le à .gitignore avant de continuer.")
    jeton = getpass.getpass("Jeton donné par le formateur : ").strip()
    if not jeton:
        arreter("Jeton absent : rien n’a été modifié.")

    recuperer_reference(jeton)
    try:
        etape = demandee or etape_en_cours()
        if git("status", "--porcelain").stdout:
            print("Tes modifications en cours seront d’abord enregistrées dans un commit.")
        reponse = input(f"Résoudre l’étape {etape} ? (un commit faisant les corrections nécessaires sera ajouté à ta branche) (o/N) ")
        if reponse.strip().lower() != "o":
            arreter("Rien n’a été modifié.")
        enregistrer_travail(etape)
        appliquer_reference(etape)
    finally:
        supprimer_references()
    print(f"Tu peux commencer l’étape {etape + 1}. Pense à pousser : git push" if etape < DERNIERE_ETAPE else "Pense à pousser : git push")


if __name__ == "__main__":
    main()
