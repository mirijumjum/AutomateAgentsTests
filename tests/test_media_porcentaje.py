import pytest

try:
    from src.main import media, porcentaje
except ImportError:  # estructura plana (main.py en la raíz)
    from main import media, porcentaje


# --- media: criterios de aceptación ---

def test_media_basica():
    assert media([1, 2, 3]) == 2


def test_media_un_elemento():
    assert media([5]) == 5


def test_media_negativos():
    assert media([-1, -2, -3]) == -2


def test_media_flotantes():
    assert media([1.5, 2.5]) == pytest.approx(2.0)


def test_media_lista_vacia():
    with pytest.raises((ZeroDivisionError, ValueError)):
        media([])


# --- media: edge cases ---

def test_media_positivos_y_negativos_compensan():
    assert media([-2, 2]) == 0


def test_media_error_coma_flotante():
    assert media([0.1, 0.2, 0.3]) == pytest.approx(0.2)


def test_media_enteros_devuelve_float():
    resultado = media([1, 2])
    assert resultado == 1.5
    assert isinstance(resultado, float)


# --- porcentaje: criterios de aceptación ---

def test_porcentaje_basico():
    assert porcentaje(50, 200) == 25.0


def test_porcentaje_valor_cero():
    assert porcentaje(0, 100) == 0


def test_porcentaje_total_cero():
    with pytest.raises((ZeroDivisionError, ValueError)):
        porcentaje(10, 0)


# --- porcentaje: edge cases ---

def test_porcentaje_valor_mayor_que_total():
    assert porcentaje(200, 100) == 200.0


def test_porcentaje_valor_negativo():
    assert porcentaje(-25, 100) == -25.0


def test_porcentaje_total_negativo():
    assert porcentaje(25, -100) == -25.0


def test_porcentaje_con_decimales():
    assert porcentaje(1, 3) == pytest.approx(33.3333, rel=1e-4)


def test_porcentaje_cero_entre_cero():
    with pytest.raises((ZeroDivisionError, ValueError)):
        porcentaje(0, 0)
