import pytest

from assistant.outils import AccesRefuse, lire_fiche


def test_refuse_une_fiche_hors_du_dossier(limites, tmp_path):
    (tmp_path / ".env.md").write_text("LITELLM_API_KEY=secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)


def test_lit_une_fiche_du_dossier(limites):
    assert lire_fiche("modifier-taux-tva.md", limites).startswith("# Modifier le taux de TVA")


def test_refuse_un_lien_symbolique_vers_l_exterieur(limites, tmp_path):
    secret = tmp_path / "secret.md"
    secret.write_text("secret", encoding="utf-8")
    (limites["dossier_fiches"] / "lien.md").symlink_to(secret)
    with pytest.raises(AccesRefuse):
        lire_fiche("lien.md", limites)


def test_refuse_un_chemin_absolu(limites, tmp_path):
    secret = tmp_path / "secret.md"
    secret.write_text("secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche(str(secret), limites)


def test_refuse_une_autre_extension(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("notes.txt", limites)


def test_refuse_une_fiche_trop_grande(limites):
    (limites["dossier_fiches"] / "grande.md").write_text("x" * (limites["taille_max_ko"] * 1024 + 1), encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("grande.md", limites)
