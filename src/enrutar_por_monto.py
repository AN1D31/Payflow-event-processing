def es_alto_valor(transaccion: dict) -> bool:
    """
    Determina si una transacción supera el umbral de 5.000.000 COP 
    para ser enviada a la cola de alto valor en Service Bus.
    """
    try:
        monto = float(transaccion.get("monto", 0))
        if monto > 5000000:
            print(f"⚠️ Transacción de ALTO VALOR detectada: {transaccion.get('id_transaccion')} por un monto de {monto}")
            return True
        return False
    except ValueError:
        return False