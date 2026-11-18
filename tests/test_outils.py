import pytest

from assistant.outils import AccesRefuse, lire_fiche, chemin_autorise


# TESTS: assistant.outils.chemin_autorise()
def test_valid_authorized_path(limites):
    path = chemin_autorise("modifier-taux-tva.md", limites)
    assert path == limites["dossier_fiches"].resolve() / "modifier-taux-tva.md"


def test_fail_absolute_path(limites, tmp_path):
    with pytest.raises(AccesRefuse):
        chemin_autorise(str(tmp_path / "test.md"), limites)


def test_fail_parent_folder_path(limites):
    with pytest.raises(AccesRefuse):
        chemin_autorise("../test.md", limites)


def test_fail_bad_extension_path(limites):
    with pytest.raises(AccesRefuse):
        chemin_autorise("test.txt", limites)


def test_fail_empty_name_path(limites):
    with pytest.raises(AccesRefuse):
        chemin_autorise("", limites)


def test_fail_symbolic_link_outside_folder(limites, tmp_path):
    # See: https://docs.python.org/fr/3/library/pathlib.html#pathlib.Path.symlink_to
    outside_fiche = tmp_path / "protected_file.md"
    outside_fiche.write_text("protected_file", encoding="utf-8")
    path = limites["dossier_fiches"] / "its_a_trap.md"
    path.symlink_to(outside_fiche)
    with pytest.raises(AccesRefuse):
        chemin_autorise("its_a_trap.md", limites)


# TESTS: assistant.outils.lire_fiche()
def test_valid_read_fiche(limites):
    fiche = lire_fiche("modifier-taux-tva.md", limites)
    assert "# Modifier le taux de TVA" in fiche


def test_valid_read_fiche_at_size_limit(limites):
    # Declared as ko in the limites.toml, so have to multiply to check
    max_size = limites["taille_max_ko"] * 1000
    fiche = limites["dossier_fiches"] / "fiche_at_size_limit.md"
    # See: https://docs.python.org/fr/3/library/pathlib.html#pathlib.Path.write_text
    fiche.write_text("a" * max_size, encoding="utf-8")
    assert lire_fiche("fiche_at_size_limit.md", limites) == "a" * max_size


# Same test but with +1 so it fails
def test_fail_read_fiche_too_big(limites):
    max_size = limites["taille_max_ko"] * 1000 + 1
    fiche = limites["dossier_fiches"] / "fiche_too_big.md"
    fiche.write_text("a" * max_size, encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("fiche_too_big.md", limites)


def test_fail_read_fiche_outside_folder(limites, tmp_path):
    # Must create file to test this
    fiche = tmp_path / ".env.md"
    fiche.write_text("LITELLM_API_KEY=secret_key", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)


def test_fail_read_fiche_doesnt_exist(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("test.md", limites)
