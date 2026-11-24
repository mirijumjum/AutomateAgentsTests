import pytest

try:
    from src.main import dividir, restar, sumar
except ImportError:  # estructura plana (main.py en la raíz)
    from main import dividir, restar, sumar


def test_sumar():
    assert sumar(2, 3) == 5


def test_restar():
    assert restar(5, 3) == 2


def test_dividir():
    assert dividir(6, 3) == 2


def test_dividir_entre_cero():
    with pytest.raises(ValueError):
        dividir(1, 0)
