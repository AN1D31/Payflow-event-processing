def es_transaccion_valida(transaccion: dict) -> bool:
    """
    Verifica que la transacción tenga el formato correcto y reglas de negocio básicas.
    Rechaza montos negativos (simulando una regla antifraude).
    """
    try:
        monto = float(transaccion.get("monto", 0))
        if monto <= 0:
            print(f"❌ Transacción inválida/fraudulenta detectada (Monto negativo): {transaccion.get('id_transaccion')}")
            return False
        return True
    except ValueError:
        return False