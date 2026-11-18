import pytest

from assistant import client, conversation
from assistant.service_simule import ServiceSimule, texte

def refuser(nom):
  return False

def ignorer(texte):
  pass

def test_renvoie_la_reponse_du_modele(limites):
  # utiliser la fonction poser
  service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])
  messages = conversation.nouvelle_conversation(limites)
  reponse = conversation.poser(
    "Bonjour", messages, service, "simule", limites, refuser, ignorer
  )
  # test pour envoie de message
  # verification reception
  
  assert reponse == "Bonjour, que puis-je faire ?" 
