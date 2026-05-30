import logging

def registrar_en_bd(transaccion: dict):
    """
    Guarda el registro con el estado final de la transacción en la base de datos (Cosmos DB o SQL).
    """
    estado = transaccion.get("estado", "DESCONOCIDO")
    id_tx = transaccion.get("id_transaccion", "N/A")
    
    # Aquí irá la conexión al SDK de Cosmos DB o Azure SQL más adelante
    # Por ahora, simulamos la escritura para comprobar que el flujo llega hasta el final
    
    logging.info(f"💾 BD LOG: Transacción {id_tx} registrada exitosamente en la base de datos con estado [{estado}].")
    return True