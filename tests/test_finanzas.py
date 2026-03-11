import pytest
from decimal import Decimal
from app.schemas.moneda_utils import decimal_a_unidad_menor, unidad_menor_a_decimal
from app.schemas.transaccion import TransaccionBase
from pydantic import ValidationError
from datetime import date

def test_conversion_monedas():
    # Test USD (2 decimales)
    assert decimal_a_unidad_menor(Decimal("15.50"), "USD") == 1550
    assert unidad_menor_a_decimal(1550, "USD") == Decimal("15.50")

    # Test COP (0 decimales)
    assert decimal_a_unidad_menor(Decimal("150000"), "COP") == 150000
    assert unidad_menor_a_decimal(150000, "COP") == Decimal("150000")

def test_validacion_pydantic_anti_corrupcion():
    # Fallo esperado: COP no admite decimales fraccionarios en el motor
    with pytest.raises(ValidationError) as exc_info:
        TransaccionBase(
            monto=Decimal("1500.50"),
            moneda="COP",
            fecha=date.today(),
            descripcion="Prueba error",
            categoria_id=1
        )
    assert "demasiados decimales" in str(exc_info.value)

    # Exito esperado: COP entero
    tx_cop = TransaccionBase(
        monto=Decimal("1500"),
        moneda="COP",
        fecha=date.today(),
        descripcion="Prueba OK",
        categoria_id=1
    )
    assert tx_cop.monto == Decimal("1500")

    # Exito esperado: USD con decimales
    tx_usd = TransaccionBase(
        monto=Decimal("15.50"),
        moneda="USD",
        fecha=date.today(),
        descripcion="Prueba OK",
        categoria_id=1
    )
    assert tx_usd.monto == Decimal("15.50")
