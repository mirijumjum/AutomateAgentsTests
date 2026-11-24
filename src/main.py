def sumar(a: float, b: float) -> float:
    return a + b


def restar(a: float, b: float) -> float:
    return a - b


def dividir(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("No se puede dividir entre cero")
    return a / b

def media(numeros: list[float]) -> float:
    return sum(numeros) / len(numeros)


def porcentaje(valor: float, total: float) -> float:
    return valor / total * 100