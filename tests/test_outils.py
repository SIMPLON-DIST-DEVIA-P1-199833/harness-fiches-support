import pytest
from pathlib import Path

from assistant.outils import AccesRefuse, lire_fiche


def test_refuse_une_fiche_hors_du_dossier(limites, tmp_path):
    (tmp_path / ".env.md").write_text("LITELLM_API_KEY=secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)


def test_lecture_fiche_valide(limites):
    fiche_dir = Path(limites["dossier_fiches"])
    fiche_dir.mkdir(parents=True, exist_ok=True)

    f = fiche_dir / "test.md"
    f.write_text("Contenu de test")

    assert lire_fiche("test.md", limites) == "Contenu de test"


def test_lire_fiche_non_existent(limites):
    fiche_dir = Path(limites["dossier_fiches"])
    fiche_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(AccesRefuse, match="n'existe pas"):
        lire_fiche("un_fichier_inexistant.md", limites)


def test_refuse_chemin_absolu(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("/etc/passwd", limites)


def test_refuse_extension_incorrecte(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("fiche.txt", limites)
