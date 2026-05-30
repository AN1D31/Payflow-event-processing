import azure.functions as func
import json
import logging
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from validar_transaccion import es_transaccion_valida
from enrutar_por_monto import es_alto_valor
from registrar_resultado import registrar_en_bd

app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="transacciones",
                               connection="EventHubConnectionAppSetting")
def procesador_transacciones(azeventhub: func.EventHubEvent):
    logging.info('⚡ Nuevo evento recibido desde Event Hubs.')
    
    mensaje = azeventhub.get_body().decode('utf-8')
    transaccion = json.loads(mensaje)
    logging.info(f"📥 Transacción en proceso: {transaccion.get('id_transaccion')}")

    if not es_transaccion_valida(transaccion):
        transaccion["estado"] = "RECHAZADA_FRAUDE"
    else:
        if es_alto_valor(transaccion):
            transaccion["estado"] = "EN_REVISION_SERVICE_BUS"
            logging.info("--> 🚀 Enviando a la cola de Service Bus...")
            
            try:
                sb_conn_str = os.environ.get("SERVICE_BUS_CONNECTION_STR")
                sb_client = ServiceBusClient.from_connection_string(sb_conn_str)
                with sb_client:
                    sender = sb_client.get_queue_sender(queue_name="transacciones-alto-valor")
                    with sender:
                        msg = ServiceBusMessage(json.dumps(transaccion))
                        sender.send_messages(msg)
                        logging.info("📨 Mensaje encolado exitosamente en Service Bus.")
            except Exception as e:
                logging.error(f"❌ Error con Service Bus: {e}")
        else:
            transaccion["estado"] = "APROBADA"

    registrar_en_bd(transaccion)
    logging.info(f"✅ Flujo completado para {transaccion.get('id_transaccion')}\n" + "-"*30)