import pytest

from assistant.service_simule import ServiceSimule 
from assistant import conversation

def test_renvoie_la_reponse_du_modele():
  # utiliser la fonction poser
  reponse = conversation.poser()
  # test pour envoie de message
  # verification reception
  assert "bonjour" == reponse 
   