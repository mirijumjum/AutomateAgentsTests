import pytest

try:
    from src.main import media, porcentaje
except ImportError:
    from main import media, porcentaje


def test_media():
    assert media([1, 2, 3]) == 2


def test_media_un_elemento():
    assert media([5]) == 5


def test_media_flotantes():
    assert media([1.5, 2.5]) == pytest.approx(2.0)


def test_media_negativos():
    assert media([-1, -3]) == -2


def test_media_lista_vacia_comportamiento_actual():
    # Comportamiento actual: lanza ZeroDivisionError (no ValueError)
    with pytest.raises(ZeroDivisionError):
        media([])


def test_porcentaje():
    assert porcentaje(25, 200) == 12.5


def test_porcentaje_flotantes():
    assert porcentaje(0.5, 2) == pytest.approx(25.0)


def test_porcentaje_negativo():
    assert porcentaje(-1, 4) == -25


def test_porcentaje_valor_cero():
    assert porcentaje(0, 10) == 0


def test_porcentaje_total_cero_comportamiento_actual():
    # Comportamiento actual: lanza ZeroDivisionError (dividir lanza ValueError)
    with pytest.raises(ZeroDivisionError):
        porcentaje(1, 0)
