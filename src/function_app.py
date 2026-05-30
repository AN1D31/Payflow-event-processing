import azure.functions as func
import json
import logging
from validar_transaccion import es_transaccion_valida
from enrutar_por_monto import es_alto_valor
from guardar_transaccion import registrar_en_bd

# Inicializamos la Function App
app = func.FunctionApp()

# El trigger que escucha los eventos que enviaste con el script generador
@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="transacciones",
                               connection="EventHubConnectionAppSetting")
def procesador_transacciones(azeventhub: func.EventHubEvent):
    logging.info('⚡ Nuevo lote de eventos recibido desde Event Hubs.')

    # 1. Decodificar el mensaje JSON
    mensaje = azeventhub.get_body().decode('utf-8')
    transaccion = json.loads(mensaje)
    logging.info(f"📥 Datos de la transacción: {transaccion}")

    # 2. Validación de fraude
    if not es_transaccion_valida(transaccion):
        transaccion["estado"] = "RECHAZADA_FRAUDE"
    else:
        # 3. Enrutamiento (Alto valor)
        if es_alto_valor(transaccion):
            transaccion["estado"] = "EN_REVISION_SERVICE_BUS"
            logging.info("--> 🚀 Enviando a la cola de Service Bus...")
            # TODO: Lógica para inyectar en Service Bus
        else:
            transaccion["estado"] = "APROBADA"

    # 4. Guardar estado final
    registrar_en_bd(transaccion)
    logging.info(f"✅ Procesamiento finalizado para {transaccion.get('id_transaccion')}\n" + "-"*30)