import pytest

# Used to test ecrire_fiche()
# See : https://docs.python.org/fr/3/library/unittest.mock.html
from unittest.mock import Mock

# Used to test executer()
# See: https://docs.python.org/fr/3/library/types.html#types.SimpleNamespace
# Essentially creates an empty object we can give attributes to
# This way you don't need to declare a Class yourself
from types import SimpleNamespace

from assistant.outils import (
    AccesRefuse,
    lire_fiche,
    chemin_autorise,
    executer,
    ecrire_fiche,
)


# TESTS: chemin_autorise()
def test_chemin_autorise_valid_path(limites):
    path = chemin_autorise("modifier-taux-tva.md", limites)
    assert path == limites["dossier_fiches"].resolve() / "modifier-taux-tva.md"


def test_chemin_autorise_fail_absolute_path(limites, tmp_path):
    with pytest.raises(AccesRefuse):
        chemin_autorise(str(tmp_path / "test.md"), limites)


def test_chemin_autorise_fail_parent_folder_path(limites):
    with pytest.raises(AccesRefuse):
        chemin_autorise("../test.md", limites)


def test_chemin_autorise_fail_bad_extension_path(limites):
    with pytest.raises(AccesRefuse):
        chemin_autorise("test.txt", limites)


def test_chemin_autorise_fail_empty_name_path(limites):
    with pytest.raises(AccesRefuse):
        chemin_autorise("", limites)


def test_chemin_autorise_fail_not_a_string_path(limites):
    with pytest.raises(AccesRefuse):
        chemin_autorise(5, limites)


def test_chemin_autorise_fail_subfolder_path(limites):
    subfolder = limites["dossier_fiches"] / "subfolder"
    subfolder.mkdir()
    path = subfolder / "test_fiche.md"
    path.write_text("# Test Fiche", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        chemin_autorise("subfolder/test_fiche.md", limites)


def test_chemin_autorise_fail_symbolic_link_outside_folder(limites, tmp_path):
    # See: https://docs.python.org/fr/3/library/pathlib.html#pathlib.Path.symlink_to
    outside_fiche = tmp_path / "protected_file.md"
    outside_fiche.write_text("protected_file", encoding="utf-8")
    path = limites["dossier_fiches"] / "its_a_trap.md"
    path.symlink_to(outside_fiche)
    with pytest.raises(AccesRefuse):
        chemin_autorise("its_a_trap.md", limites)


# TESTS: lire_fiche()
def test_lire_fiche_valid(limites):
    fiche = lire_fiche("modifier-taux-tva.md", limites)
    assert "# Modifier le taux de TVA" in fiche


def test_lire_fiche_valid_at_size_limit(limites):
    # Declared as ko in the limites.toml, so have to multiply to check
    max_size = limites["taille_max_ko"] * 1000
    fiche = limites["dossier_fiches"] / "fiche_at_size_limit.md"
    # See: https://docs.python.org/fr/3/library/pathlib.html#pathlib.Path.write_text
    fiche.write_text("a" * max_size, encoding="utf-8")
    assert lire_fiche("fiche_at_size_limit.md", limites) == "a" * max_size


# Same test but with +1 so it fails
def test_lire_fiche_fail_too_big(limites):
    max_size = limites["taille_max_ko"] * 1000 + 1
    fiche = limites["dossier_fiches"] / "fiche_too_big.md"
    fiche.write_text("a" * max_size, encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("fiche_too_big.md", limites)


def test_lire_fiche_fail_outside_folder(limites, tmp_path):
    # Must create file to test this
    fiche = tmp_path / ".env.md"
    fiche.write_text("LITELLM_API_KEY=secret_key", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)


def test_lire_fiche_fail_doesnt_exist(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("test.md", limites)


def test_lire_fiche_fail_not_utf8(limites):
    # A fiche saved in Latin-1 encoding instead of UTF-8
    fiche = limites["dossier_fiches"] / "latin1.md"
    fiche.write_text("Facture modifiée", encoding="latin-1")
    with pytest.raises(AccesRefuse):
        lire_fiche("latin1.md", limites)


# TESTS: executer()
def fake_tool_call(name, args):
    """Build object with same shape as a tool call from the SDK
    call.function.name
    call.function.arguments
    """
    return SimpleNamespace(function=SimpleNamespace(name=name, arguments=args))


def test_executer_valid_lire_fiche(limites):
    call = fake_tool_call("lire_fiche", '{"nom": "modifier-taux-tva.md"}')
    assert "# Modifier le taux de TVA" in executer(call, limites, None)


def test_executer_fail_invalid_json(limites):
    call = fake_tool_call("lire_fiche", '{"nom": ')
    with pytest.raises(AccesRefuse):
        executer(call, limites, None)


def test_executer_fail_invalid_type(limites):
    call = fake_tool_call("lire_fiche", "[]")
    with pytest.raises(AccesRefuse):
        executer(call, limites, None)


def test_executer_fail_none_type(limites):
    call = fake_tool_call("lire_fiche", None)
    with pytest.raises(AccesRefuse):
        executer(call, limites, None)


def test_executer_fail_unknown_tool(limites):
    call = fake_tool_call("delete_fiche", '{"nom": "modifier-taux-tva.md"}')
    with pytest.raises(AccesRefuse):
        executer(call, limites, None)


def test_executer_fail_empty_args(limites):
    call = fake_tool_call("lire_fiche", "{}")
    with pytest.raises(AccesRefuse):
        executer(call, limites, None)


# Same test as in test_conversation.test_fail_joindre_fiche_outside_folder()
# Makes sure that executer() goes through lire_fiche()
def test_executer_fail_outside_folder(limites, tmp_path):
    path = tmp_path / ".env.md"
    path.write_text("LITELLM_API_KEY=my_secret_key", encoding="utf-8")
    call = fake_tool_call("lire_fiche", '{"nom": "../.env.md"}')
    with pytest.raises(AccesRefuse):
        executer(call, limites, None)


# TESTS: ecrire_fiche()

# Constants so we can easily modify later without breaking everything
EXISTING_FICHE = "existing-fiche.md"
NEW_FICHE = "new-fiche.md"
ORIGINAL_CONTENT = "# Original content"
NEW_CONTENT = "# New content"


# Fixture so we can re-use this in all our ecrire_fiche() tests. Only used in this file
@pytest.fixture
def existing_fiche(limites):
    """Create fiche in temporary fiches folder, return its path."""
    fiche = limites["dossier_fiches"] / EXISTING_FICHE
    fiche.write_text(ORIGINAL_CONTENT, encoding="utf-8")
    return fiche


# Could have done it with helper functions instead of mock, but then we'd need a class or something to handle cases where we need to check the call
# Mock essentially replaces the interactive confirmer from the interface
def test_ecrire_fiche_valid_create_fiche(limites):
    """Check new fiche is created with expected content"""
    accept = Mock(return_value=True)
    ecrire_fiche(NEW_FICHE, NEW_CONTENT, limites, accept)
    new_fiche_path = limites["dossier_fiches"] / NEW_FICHE
    # Will raise FileNotFound exception if file does not exist
    assert new_fiche_path.read_text(encoding="utf-8") == NEW_CONTENT


def test_ecrire_fiche_valid_create_fiche_no_confirmation_needed(limites):
    """Check no confirmation is asked when new fiche is created"""
    accept = Mock(return_value=True)
    ecrire_fiche(NEW_FICHE, NEW_CONTENT, limites, accept)
    # assert_not_called() > Mock method, AssertionError if mock was called
    accept.assert_not_called()


def test_ecrire_fiche_valid_replace_fiche_with_new_content(limites, existing_fiche):
    """Check existing fiche is replaced when technician confirms"""
    accept = Mock(return_value=True)
    ecrire_fiche(EXISTING_FICHE, NEW_CONTENT, limites, accept)
    assert existing_fiche.read_text(encoding="utf-8") == NEW_CONTENT


def test_ecrire_fiche_valid_confirmation_asked_once(limites, existing_fiche):
    """Check confirmation is asked once for a single fiche being overwritten"""
    accept = Mock(return_value=True)
    ecrire_fiche(EXISTING_FICHE, NEW_CONTENT, limites, accept)
    accept.assert_called_once_with(EXISTING_FICHE)


def test_ecrire_fiche_valid_content_at_size_limit(limites):
    """Check content of new fiche at size limit is written fully"""
    max_fiche_size_content = (limites["taille_max_ko"] * 1000) * "a"
    accept = Mock(return_value=True)
    ecrire_fiche(NEW_FICHE, max_fiche_size_content, limites, accept)
    new_fiche_path = limites["dossier_fiches"] / NEW_FICHE
    assert new_fiche_path.read_text(encoding="utf-8") == max_fiche_size_content


def test_ecrire_fiche_fail_content_too_big(limites):
    """Check content of new fiche above size limit is not written and does not create a new fiche"""
    too_big_content = (limites["taille_max_ko"] * 1000 + 1) * "a"
    accept = Mock(return_value=True)
    new_fiche_path = limites["dossier_fiches"] / NEW_FICHE
    with pytest.raises(AccesRefuse, match="too big"):
        ecrire_fiche(NEW_FICHE, too_big_content, limites, accept)
    assert not new_fiche_path.exists()


def test_ecrire_fiche_fail_overwrite_declined(limites, existing_fiche):
    """Check existing fiche remains unchanged when technician declines"""
    decline = Mock(return_value=False)
    with pytest.raises(AccesRefuse, match="declined"):
        ecrire_fiche(EXISTING_FICHE, NEW_CONTENT, limites, decline)
    assert existing_fiche.read_text(encoding="utf-8") == ORIGINAL_CONTENT


def test_ecrire_fiche_fail_outside_folder(limites, tmp_path):
    """Check writing outside the fiche folder is refused and creates nothing"""
    accept = Mock(return_value=True)
    # Inclue keyword check from error message so we know it fails at the right place
    with pytest.raises(AccesRefuse, match="outside"):
        ecrire_fiche("../outside.md", NEW_CONTENT, limites, accept)
    assert not (tmp_path / "outside.md").exists()
