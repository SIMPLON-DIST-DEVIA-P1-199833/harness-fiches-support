import pytest

from assistant import conversation
from assistant.service_simule import ServiceSimule, texte


def test_renvoie_la_reponse_du_modele(limites):
    service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])
    messages = conversation.nouvelle_conversation(limites)

    def refuser(nom):
        return False

    def ignorer(texte):
        pass

    reponse = conversation.poser(
        "Bonjour", messages, service, "simule", limites, refuser, ignorer
    )
    assert reponse == "Bonjour, que puis-je faire ?"


def test_garde_l_historique(limites):
    service = ServiceSimule(
        [
            texte("Voici la réponse à ta première question."),
            texte("Voici la réponse à ta deuxième question."),
        ]
    )

    messages = conversation.nouvelle_conversation(limites)

    def refuser(nom):
        return False

    def ignorer(texte):
        pass

    conversation.poser(
        "Bonjour", messages, service, "simule", limites, refuser, ignorer
    )
    conversation.poser(
        "Comment vas-tu ?", messages, service, "simule", limites, refuser, ignorer
    )

    contenus = [m["content"] for m in service.requetes[1]["messages"]]
    assert "Bonjour" in contenus
    assert "Voici la réponse à ta première question." in contenus
