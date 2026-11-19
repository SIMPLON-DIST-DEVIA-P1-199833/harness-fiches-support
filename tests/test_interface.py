import pytest
from assistant.interface import parse_join


# TESTS: interface.parse_join()
def test_valid_joindre_command():
    assert parse_join("/joindre fiche.md Résume cette fiche.") == (
        "fiche.md",
        "Résume cette fiche.",
    )


def test_valid_multiple_whitespaces():
    assert parse_join("/joindre     fiche.md      Résume cette fiche.") == (
        "fiche.md",
        "Résume cette fiche.",
    )


def test_fail_joindre_wrong_command():
    assert parse_join("/joindreabc fiche.md Résume cette fiche.") is None


def test_fail_joindre_no_arg():
    assert parse_join("/joindre") is None


def test_fail_joindre_missing_arg():
    assert parse_join("/joindre fiche.md") is None
