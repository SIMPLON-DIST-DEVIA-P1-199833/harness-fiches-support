import pytest

from assistant.client import ServiceIndisponible, envoyer
from assistant.configuration import ConfigurationInvalide
from assistant.service_simule import ServiceSimule, cle_refusee, delai_depasse, panne


def test_panne_devient_indisponible():
    service = ServiceSimule([panne()])
    with pytest.raises(ServiceIndisponible):
        envoyer(service, "simule", [{"role": "user", "content": "Bonjour"}])


def test_cle_refusee_devient_configuration_invalide():
    service = ServiceSimule([cle_refusee()])
    with pytest.raises(ConfigurationInvalide):
        envoyer(service, "simule", [{"role": "user", "content": "Bonjour"}])


def test_delai_depasse_devient_indisponible():
    service = ServiceSimule([delai_depasse()])
    with pytest.raises(ServiceIndisponible):
        envoyer(service, "simule", [{"role": "user", "content": "Bonjour"}])
