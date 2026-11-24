# AutomateAgentsTests

Pequeña calculadora en Python (`src/main.py`) usada para probar pipelines de agentes.

## Instalación

```bash
pip install -r requirements-dev.txt   # ruff y pytest
```

## Uso

```python
from src.main import sumar, restar, dividir, media, porcentaje

sumar(2, 3)             # 5
restar(5, 3)            # 2
dividir(6, 3)           # 2.0
media([1, 2, 3])        # 2.0
porcentaje(25, 200)     # 12.5
```

## Funciones

| Función | Parámetros | Devuelve | Excepciones |
|---|---|---|---|
| `sumar(a, b)` | `a: float`, `b: float` | `a + b` | — |
| `restar(a, b)` | `a: float`, `b: float` | `a - b` | — |
| `dividir(a, b)` | `a: float`, `b: float` | `a / b` | `ValueError("No se puede dividir entre cero")` si `b == 0` |
| `media(numeros)` | `numeros: list[float]` | Media aritmética (`sum(numeros) / len(numeros)`) | `ZeroDivisionError` si la lista está vacía |
| `porcentaje(valor, total)` | `valor: float`, `total: float` | `valor / total * 100` | `ZeroDivisionError` si `total == 0` |

> Nota: `media` y `porcentaje` no validan sus entradas; el error ante división
> entre cero es el `ZeroDivisionError` nativo de Python, a diferencia de
> `dividir`, que lanza `ValueError`.

## Tests

```bash
pytest
```
