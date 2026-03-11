import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine
from app.models.base import Base

import pytest_asyncio

@pytest_asyncio.fixture(autouse=True, loop_scope="function")
async def prepare_database():
    # Setup: Re-crear base de datos limpia para tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_flujo_completo_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Onboarding
        resp_onboarding = await client.post("/api/v1/onboarding/", json={
            "moneda_principal": "COP",
            "ingreso_mensual_promedio": 3000000,
            "saldo_actual": 500000,
            "meta_principal": "Moto"
        })
        assert resp_onboarding.status_code == 201

        # 2. Categorías
        resp_cat1 = await client.post("/api/v1/categorias/", json={
            "nombre": "Ahorro",
            "tipo": "AHORRO_INVERSION",
            "color_hex": "#10B981"
        })
        assert resp_cat1.status_code == 201
        cat_ahorro_id = resp_cat1.json()["id"]

        resp_cat2 = await client.post("/api/v1/categorias/", json={
            "nombre": "Antojos",
            "tipo": "GASTO_HORMIGA",
            "color_hex": "#EF4444"
        })
        assert resp_cat2.status_code == 201
        cat_gasto_id = resp_cat2.json()["id"]

        # 3. Transacciones
        from datetime import date
        today_str = date.today().isoformat()

        resp_tx1 = await client.post("/api/v1/transacciones/", json={
            "monto": 1000000,
            "moneda": "COP",
            "fecha": "2024-05-15",
            "descripcion": "Mi ahorro",
            "categoria_id": cat_ahorro_id
        })
        assert resp_tx1.status_code == 201

        resp_tx2 = await client.post("/api/v1/transacciones/", json={
            "monto": 5000,
            "moneda": "COP",
            "fecha": today_str,
            "descripcion": "Empanadas",
            "categoria_id": cat_gasto_id
        })
        assert resp_tx2.status_code == 201

        # 4. Analytics Dashboard
        resp_dash = await client.get("/api/v1/analitica/dashboard")
        assert resp_dash.status_code == 200
        dash_data = resp_dash.json()

        # Validar lógica de negocio
        assert dash_data["fondo_intocable"] == "1000000.00"
        assert dash_data["gastos_hormiga_mes"] == "5000.00"
        assert dash_data["alerta_fuga_capital"] == False

        # Verificar la restricción de validación (Capa Anti-Corrupción)
        resp_tx_mala = await client.post("/api/v1/transacciones/", json={
            "monto": 5000.50,
            "moneda": "COP",
            "fecha": "2024-05-16",
            "descripcion": "Centavos inválidos",
            "categoria_id": cat_gasto_id
        })
        assert resp_tx_mala.status_code == 422
