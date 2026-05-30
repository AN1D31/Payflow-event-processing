import asyncio
import json
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

EVENT_HUB_CONNECTION_STR = "wi4TnEFymo5K/SaoAHx8TWaKaxu06kay4+AEhIQ/Dew="
EVENT_HUB_NAME = "transacciones"

def generar_lote_transacciones():
    """Genera los 3 tipos de transacciones exigidas por el caso."""
    return [
        # 1. Transacción normal (Monto bajo)
        {"id_transaccion": "TX1001", "comercio": "Tienda A", "monto": 45000, "tipo": "normal"},
        
        # 2. Transacción de alto valor (> $5.000.000 COP)
        {"id_transaccion": "TX1002", "comercio": "Concesionario B", "monto": 8500000, "tipo": "alto_valor"},
        
        # 3. Transacción inválida (Monto negativo para probar la regla antifraude)
        {"id_transaccion": "TX1003", "comercio": "Local C", "monto": -1500, "tipo": "invalida"}
    ]

async def run():
    # Crear un productor con la cadena de conexión
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME
    )
    
    async with producer:
        # Crear un lote (batch) de eventos
        event_data_batch = await producer.create_batch()
        transacciones = generar_lote_transacciones()
        
        # Agregar transacciones al lote
        for transaccion in transacciones:
            mensaje_json = json.dumps(transaccion)
            event_data_batch.add(EventData(mensaje_json))
            print(f"Preparando envío: {mensaje_json}")
            
        # Enviar el lote a Azure Event Hubs
        await producer.send_batch(event_data_batch)
        print("\n✅ ¡Lote de 3 transacciones enviado exitosamente a Azure Event Hubs!")

if __name__ == "__main__":
    print("Iniciando simulador de transacciones PayFlow...")
    asyncio.run(run())