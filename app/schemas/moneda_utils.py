from decimal import Decimal

DIVISAS_SOPORTADAS = {
    "USD": 2,
    "EUR": 2,
    "MXN": 2,
    "COP": 0,
    "CLP": 0,
    "ARS": 0,
}

def decimal_a_unidad_menor(monto: Decimal, moneda: str) -> int:
    decimales = DIVISAS_SOPORTADAS.get(moneda.upper(), 2)
    multiplicador = Decimal(10) ** decimales
    return int(monto * multiplicador)

def unidad_menor_a_decimal(monto_bd: int, moneda: str) -> Decimal:
    decimales = DIVISAS_SOPORTADAS.get(moneda.upper(), 2)
    divisor = Decimal(10) ** decimales
    return Decimal(monto_bd) / divisor
