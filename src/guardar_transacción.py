import os
import logging
# from azure.cosmos import CosmosClient # Descomentar cuando configures la BD

# Las credenciales se inyectarán desde la configuración de la Azure Function
COSMOS_URL = os.environ.get("COSMOS_DB_URL", "URL_AQUI")
COSMOS_KEY = os.environ.get("COSMOS_DB_KEY", "KEY_AQUI")
DATABASE_NAME = "PayFlowDB"
CONTAINER_NAME = "Transacciones"

def registrar_en_bd(transaccion: dict):
    """
    Guarda el registro con el estado final de la transacción en la base de datos.
    """
    estado = transaccion.get("estado", "DESCONOCIDO")
    id_tx = transaccion.get("id_transaccion", "N/A")
    
    # Aquí iría la lógica de Cosmos DB o SQL Database
    # client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
    # database = client.get_database_client(DATABASE_NAME)
    # container = database.get_container_client(CONTAINER_NAME)
    # transaccion["id"] = str(id_tx) # Cosmos requiere que el ID sea string
    # container.create_item(body=transaccion)
    
    logging.info(f"💾 BD LOG: Transacción {id_tx} guardada exitosamente con estado [{estado}].")