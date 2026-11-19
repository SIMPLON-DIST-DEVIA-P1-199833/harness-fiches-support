import pytest

from assistant import conversation
from assistant.service_simule import ServiceSimule, texte
from assistant.outils import AccesRefuse


# TEST: poser()
def refuser(nom):
    return False


def ignorer(texte):
    pass


def test_poser_valid_get_model_response(limites):
    service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])
    messages = conversation.nouvelle_conversation(limites)
    reponse = conversation.poser(
        "Bonjour", messages, service, "simule", limites, refuser, ignorer
    )
    assert reponse == "Bonjour, que puis-je faire ?"


# TEST: joindre_fiche()
def test_joindre_fiche_valid(limites):
    result = conversation.joindre_fiche(
        "modifier-taux-tva.md", "Résume cette fiche.", limites
    )
    assert result.split("\n")[0] == "Résume cette fiche."
    assert "modifier-taux-tva.md" in result
    assert "# Modifier le taux de TVA" in result


# This essentially checks that joindre_fiche() goes through lire_fiche() correctly
def test_joindre_fiche_fail_outside_folder(limites, tmp_path):
    path = tmp_path / ".env.md"
    path.write_text("LITELLM_API_KEY=my_secret_key", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        conversation.joindre_fiche("../.env.md", "Résume cette fiche", limites)
