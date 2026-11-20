import pytest

from assistant import conversation
from assistant.service_simule import (
    ServiceSimule,
    texte,
    appel_outil,
    appel_mal_forme,
    panne,
)
from assistant.outils import AccesRefuse, DEFINITIONS


def refuser(nom):
    return False


def ignorer(texte):
    pass


def tool_messages(messages):
    """Return the tool messages of a convo"""
    return [message for message in messages if message["role"] == "tool"]


# TEST: poser()
# TODO : add some more tests
# test service keeps history when exception happens
# test with empty last answer
def test_poser_valid_model_response(limites):
    service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])
    messages = conversation.nouvelle_conversation(limites)
    reponse = conversation.poser(
        "Bonjour", messages, service, "simule", limites, refuser, ignorer
    )
    assert reponse == "Bonjour, que puis-je faire ?"


def test_poser_valid_tool_and_answer(limites):
    service = ServiceSimule(
        [
            appel_outil("lire_fiche", nom="modifier-taux-tva.md"),
            texte("Answer after reading the fiche."),
        ]
    )
    messages = conversation.nouvelle_conversation(limites)
    reponse = conversation.poser(
        "TVA ?", messages, service, "simule", limites, refuser, ignorer
    )
    assert reponse == "Answer after reading the fiche."
    assert [message["role"] for message in messages] == [
        "system",
        "user",
        "assistant",
        "tool",
        "assistant",
    ]
    assert "# Modifier le taux de TVA" in tool_messages(messages)[0]["content"]


def test_poser_valid_tools_sent_to_model(limites):
    service = ServiceSimule([texte("Coucou")])
    messages = conversation.nouvelle_conversation(limites)
    conversation.poser("Coucou", messages, service, "simule", limites, refuser, ignorer)
    assert service.requetes[0]["tools"] == DEFINITIONS


def test_poser_fail_refusal_sent_to_model(limites, tmp_path):
    path = tmp_path / ".env.md"
    path.write_text("LITELLM_API_KEY=my_secret_key", encoding="utf-8")
    service = ServiceSimule(
        [appel_outil("lire_fiche", nom="../.env.md"), texte("Access refused")]
    )
    messages = conversation.nouvelle_conversation(limites)
    signals = []
    reponse = conversation.poser(
        "Lis .env", messages, service, "simule", limites, refuser, signals.append
    )
    assert reponse == "Access refused"
    tool_content = tool_messages(messages)[0]["content"]
    assert "refused" in tool_content
    assert "my_secret_key" not in tool_content
    assert signals


def test_poser_fail_invalid_args(limites):
    service = ServiceSimule([appel_mal_forme("lire_fiche", '{"nom": '), texte("Error")])
    messages = conversation.nouvelle_conversation(limites)
    conversation.poser(
        "invalide", messages, service, "simule", limites, refuser, ignorer
    )
    assert "Invalid JSON" in tool_messages(messages)[0]["content"]


def test_poser_fail_unknown_tool(limites):
    service = ServiceSimule(
        [
            appel_outil("supprimer_fiche", nom="modifier-taux-tva.md"),
            texte("Unknown"),
        ]
    )
    messages = conversation.nouvelle_conversation(limites)
    conversation.poser(
        "supprime", messages, service, "simule", limites, refuser, ignorer
    )
    assert "unknown tool" in tool_messages(messages)[0]["content"]


# Run appel_outil from service_simule.py to test this < makes a response
def test_poser_valid_at_call_limit(limites):
    max_tool_calls = limites["appels_outil_max"]
    tool_call = appel_outil("lire_fiche", nom="modifier-taux-tva.md")
    # Call service the same amount of times as max_tool_calls
    # `[tool_call] * max_tool_calls` creates a list of tool calls
    service = ServiceSimule(
        [tool_call] * max_tool_calls + [texte("Answer after the last tool call")]
    )
    messages = conversation.nouvelle_conversation(limites)
    response = conversation.poser(
        "TVA ?", messages, service, "simule", limites, refuser, ignorer
    )
    assert response == "Answer after the last tool call"


def test_poser_fail_too_many_calls(limites):
    max_tool_calls = limites["appels_outil_max"]
    tool_call = appel_outil("lire_fiche", nom="modifier-taux-tva.md")
    # One too many tool call
    service = ServiceSimule([tool_call] * (max_tool_calls + 1))
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(conversation.LimiteAtteinte):
        # Same behaviour as the simulated 'boucle' command
        conversation.poser(
            "boucle", messages, service, "simule", limites, refuser, ignorer
        )


def test_poser_fail_too_many_calls_keeps_history(limites):
    max_tool_calls = limites["appels_outil_max"]
    tool_call = appel_outil("lire_fiche", nom="modifier-taux-tva.md")
    service = ServiceSimule([tool_call] * (max_tool_calls + 1))
    messages = conversation.nouvelle_conversation(limites)
    # Copy history before the question to compare afterwards
    message_history = list(messages)
    with pytest.raises(conversation.LimiteAtteinte):
        conversation.poser(
            "boucle", messages, service, "simule", limites, refuser, ignorer
        )
    # Make sure messages remains unchanged
    assert messages == message_history


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
