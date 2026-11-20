
from assistant import conversation
from assistant.service_simule import ServiceSimule, texte


def refuser(nom):
    return False


def ignorer(texte):
    pass


def test_renvoie_la_reponse_du_modele(limites):
    service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])

    messages = conversation.nouvelle_conversation(limites)

    reponse = conversation.poser(
        "Bonjour", messages, service, "simule",
        limites, refuser, ignorer
    )

    assert reponse == "Bonjour, que puis-je faire ?"


def test_garde_l_historique(limites):

    service = ServiceSimule([
        texte("Premiere réponse"),
        texte("Deuxieme réponse")
    ])

    messages = conversation.nouvelle_conversation(limites)

    reponse = conversation.poser(
        "Bonjour", messages, service, "simule",
        limites, refuser, ignorer
    )

    reponse_deux = conversation.poser(
        "Tu peux préciser ?", messages, service, "simule",
        limites, refuser, ignorer
    )

    contenus = [m["content"] for m in service.requetes[1]["messages"]]
    assert "Bonjour" in contenus
    assert "Premiere réponse" in contenus

