import math

import pytest

try:
    from src.flotantes import promedio_dos
except ImportError:  # estructura plana (flotantes.py en la raíz)
    from flotantes import promedio_dos


@pytest.mark.xfail(strict=True, reason="IEEE 754: 0.1+0.2 != 0.3")
def test_criterio_01_promedio_0_1_y_0_2_igualdad_exacta():
    # Criterio de aceptación literal (sin tolerancia). En IEEE 754 el resultado
    # es 0.15000000000000002, así que la igualdad exacta no se cumple: el
    # criterio es incompatible con la aritmética de coma flotante. Se deja como
    # xfail estricto para dejar constancia; la cobertura válida de este caso
    # son los tests con pytest.approx y math.isclose.
    assert promedio_dos(0.1, 0.2) == 0.15


def test_promedio_0_1_y_0_2_aproximado_pytest_approx():
    assert promedio_dos(0.1, 0.2) == pytest.approx(0.15)


def test_promedio_0_1_y_0_2_aproximado_isclose():
    assert math.isclose(promedio_dos(0.1, 0.2), 0.15)


def test_promedio_enteros_pares():
    assert promedio_dos(2, 4) == 3


def test_promedio_opuestos_da_cero():
    assert promedio_dos(-1, 1) == 0


def test_promedio_ceros():
    assert promedio_dos(0, 0) == 0


def test_promedio_dos_negativos():
    assert promedio_dos(-2, -4) == -3


def test_promedio_enteros_con_resultado_flotante():
    assert promedio_dos(1, 2) == 1.5


def test_promedio_valores_iguales():
    assert promedio_dos(5, 5) == 5


def test_promedio_flotantes_exactos_en_binario():
    assert promedio_dos(0.5, 0.25) == 0.375


def test_promedio_desbordamiento_da_inf():
    # La suma desborda antes de dividir entre 2.
    assert promedio_dos(1e308, 1e308) == float("inf")


def test_promedio_con_infinito():
    assert promedio_dos(float("inf"), 1) == float("inf")


def test_promedio_con_nan():
    assert math.isnan(promedio_dos(float("nan"), 1))


def test_promedio_tipo_invalido_lanza_typeerror():
    with pytest.raises(TypeError):
        promedio_dos("a", 1)
