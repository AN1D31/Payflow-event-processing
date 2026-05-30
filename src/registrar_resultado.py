import os
import logging
from azure.cosmos import CosmosClient

COSMOS_URL = os.environ.get("COSMOS_DB_URL")
COSMOS_KEY = os.environ.get("COSMOS_DB_KEY")
DATABASE_NAME = "PayFlowDB"
CONTAINER_NAME = "Transacciones"

def registrar_en_bd(transaccion: dict):
    try:
        client = CosmosClient(url=COSMOS_URL, credential=COSMOS_KEY)

        database = client.create_database_if_not_exists(id=DATABASE_NAME)
        container = database.create_container_if_not_exists(
            id=CONTAINER_NAME,
            partition_key={"paths": ["/id"], "kind": "Hash"}
        )

        transaccion["id"] = str(transaccion.get("id_transaccion"))
        
        container.upsert_item(transaccion)
        logging.info(f"💾 BD LOG: Transacción {transaccion['id']} guardada exitosamente en Cosmos DB.")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error al guardar en Cosmos DB: {e}")
        return False