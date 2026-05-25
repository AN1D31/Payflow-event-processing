# PayFlow — Procesamiento de Eventos en Tiempo Real

**Curso:** Computación en la Nube | Semestre 2026-1
**Profesor:** Julián David Florez Sánchez
**Institución:** Tecnológico de Antioquia — Institución Universitaria
**Caso:** 03 — Procesamiento de Eventos en Tiempo Real
**Plataforma:** Microsoft Azure (Free Tier / Azure for Students)
**Entrega:** 14 de mayo de 2026

---

## Integrantes

| Nombre |
|--------|
| Daniela Vanegas Guerrero |
| Andrés Felipe Bolívar Osorio |
| Jaison Esteban Córdoba Arroyo |
| Sthyd Anderson Guissao Ramírez |

---

## Descripción del caso

PayFlow es una fintech colombiana fundada en 2020 que ofrece una plataforma de pagos
digitales para pequeños y medianos comercios. Opera como intermediario entre comercios,
adquirentes bancarios y redes de pago (Visa, Mastercard, PSE), procesando transacciones
de compra, reembolsos, pagos de servicios y transferencias entre cuentas.

Actualmente cuenta con 28.000 comercios activos, procesa en promedio 85.000 transacciones
diarias y tiene presencia en Colombia, Ecuador y Perú. En temporada alta el volumen puede
triplicarse, alcanzando hasta 260.000 transacciones en un solo día.

### Problemas identificados en el sistema actual

| Problema | Descripción |
|----------|-------------|
| Cuello de botella | El procesador actual maneja hasta 40 tx/seg. En picos supera los 8 segundos de respuesta |
| Sin priorización | Una transacción de $500 COP y una de $50.000.000 COP pasan por el mismo proceso |
| Fraude reactivo | El antifraude se aplica después de autorizar. El dinero ya está comprometido |
| Sin observabilidad | El equipo se entera de problemas por quejas en WhatsApp, no por alertas automáticas |
| Acoplamiento fuerte | Si el webhook falla, la transacción completa se revierte aunque la autorización fue exitosa |

---

## Arquitectura de referencia

Este caso está basado en la arquitectura oficial de Microsoft Azure para sistemas
de procesamiento de eventos en tiempo real.

- [Event-driven architecture](https://learn.microsoft.com/es-es/azure/architecture/guide/architecture-styles/event-driven)
- [Azure Event Hubs](https://learn.microsoft.com/es-es/azure/event-hubs/event-hubs-about)
- [Azure Functions — trigger por Event Hubs](https://learn.microsoft.com/es-es/azure/azure-functions/functions-bindings-event-hubs)
- [Azure Service Bus](https://learn.microsoft.com/es-es/azure/service-bus-messaging/service-bus-messaging-overview)
- [Azure Cosmos DB](https://learn.microsoft.com/es-es/azure/cosmos-db/introduction)
- [Azure Monitor](https://learn.microsoft.com/es-es/azure/azure-monitor/overview)

---

## Stack de servicios Azure

| Servicio | Responsabilidad en PayFlow | Tier |
|----------|---------------------------|------|
| Azure Event Hubs | Punto de entrada. Buffer distribuido ante picos de demanda. Recibe hasta 500 tx/seg | Basic — 1 TU |
| Azure Functions | Valida, evalúa fraude, enruta por monto y registra cada transacción | Consumption Plan |
| Azure Service Bus | Cola de prioridad para transacciones mayores a $5M COP con reintentos automáticos | Basic tier |
| Cosmos DB | Persiste el estado final de cada transacción procesada | Free tier — 25 GB |
| Azure Monitor + App Insights | Alertas automáticas en menos de 30 segundos. Trazas distribuidas por transacción | Gratuito 5 GB/mes |

---

## Modelo C4

### C1 — Contexto del sistema

![Diagrama C1 - Contexto](assets/C1.png)

PayFlow actúa como sistema central de procesamiento de pagos digitales. Recibe eventos
desde los terminales POS y el sistema legado, solicita autorización al adquirente bancario
y notifica el resultado al comercio mediante webhook. El equipo de riesgo monitorea alertas
de fraude y el equipo de operaciones supervisa la disponibilidad del sistema.

### C2 — Contenedores

![Diagrama C2 - Contenedores](assets/C2.png)

El sistema está compuesto por cinco servicios Azure desplegados en la región Brazil South,
cumpliendo la regulación de la Superintendencia Financiera de Colombia. Los eventos fluyen
desde Event Hubs hacia Azure Functions, que orquesta la validación, el antifraude, el
enrutamiento por monto y el registro en Cosmos DB. Las transacciones mayores a $5M COP
se enrutan por un canal diferenciado en Service Bus con garantía de entrega at-least-once.

### C3 — Componentes

> Diagrama en construcción — próximo commit

---

## Decisiones Arquitectónicas (ADRs)

### ADR-01: Uso de Azure Event Hubs como punto de entrada sobre Azure Service Bus para ingesta de transacciones

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow procesa en promedio 85.000 transacciones diarias, con picos de hasta 260.000 en temporada alta, lo que equivale a aproximadamente 500 tx/seg en momentos de alta demanda. El sistema actual tiene un cuello de botella crítico: el procesador legado solo soporta 40 tx/seg, generando tiempos de respuesta superiores a 8 segundos en picos. Se necesita un buffer distribuido que absorba ráfagas de tráfico sin perder eventos y que desacople la ingesta del procesamiento.

#### Alternativas evaluadas

**Opción A — Azure Event Hubs (elegida)**
- ✅ Diseñado para ingesta masiva de eventos en tiempo real (millones de eventos/seg escalables)
- ✅ Modelo de consumidor particionado: múltiples instancias de Azure Functions pueden leer en paralelo
- ✅ Retención configurable de eventos (hasta 7 días en Basic tier)
- ✅ Basic tier con 1 Throughput Unit soporta 1 MB/seg de entrada — suficiente para 500 tx/seg
- ❌ No tiene garantía de orden global entre particiones
- ❌ No es ideal para enrutamiento complejo por atributos del mensaje

**Opción B — Azure Service Bus como entrada principal**
- ✅ Garantía de orden FIFO dentro de una sesión
- ✅ Soporte nativo de dead-letter queue y reintentos automáticos
- ❌ No está diseñado para ingesta de alto volumen en tiempo real
- ❌ Throughput limitado comparado con Event Hubs para cargas de tipo streaming
- ❌ Más costoso en el tier que soportaría la carga de PayFlow

#### Decisión

Se elige **Azure Event Hubs** como punto de entrada para todas las transacciones entrantes. Su modelo de streaming particionado permite absorber los picos de 500 tx/seg sin saturar el procesador, resolviendo directamente el cuello de botella identificado. Azure Service Bus se mantiene en la arquitectura pero en un rol diferente: como cola de prioridad para transacciones mayores a $5M COP (ver ADR-02).

#### Consecuencias

- ✅ El sistema puede recibir hasta 500 tx/seg sin intervención manual
- ✅ Las Azure Functions escalan horizontalmente leyendo desde particiones paralelas
- ✅ Los eventos se retienen hasta 1 día en Basic tier, permitiendo reprocesamiento ante fallos
- ⚠️ No hay garantía de orden global: transacciones del mismo comercio podrían procesarse en distinto orden si caen en particiones diferentes
- ⚠️ En Basic tier no hay soporte para Capture ni Virtual Network integration, lo que limita opciones de auditoría avanzada

---

### ADR-02: Uso de Azure Service Bus para enrutamiento prioritario de transacciones de alto valor

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow no diferencia actualmente entre una transacción de $500 COP y una de $50.000.000 COP: ambas pasan por el mismo proceso con la misma prioridad. Esto representa un riesgo de negocio significativo: en momentos de alta carga, una transacción de alto valor puede quedar represada detrás de cientos de micropagos. Adicionalmente, si el webhook de notificación al comercio falla, el sistema revierte toda la transacción aunque la autorización bancaria fue exitosa, generando acoplamiento fuerte entre componentes.

#### Alternativas evaluadas

**Opción A — Azure Service Bus con colas diferenciadas (elegida)**
- ✅ Soporte nativo de sesiones y priorización por atributos del mensaje
- ✅ Reintentos automáticos configurables (hasta 10 intentos con backoff exponencial)
- ✅ Dead-letter queue integrada para transacciones que fallan repetidamente
- ✅ Garantía de entrega at-least-once, desacoplando el webhook del flujo principal
- ✅ Basic tier disponible dentro del presupuesto del proyecto
- ❌ No es ideal para ingesta masiva de alto volumen (por eso se usa Event Hubs para entrada)

**Opción B — Manejo de prioridad dentro de Azure Functions (lógica en código)**
- ✅ Sin costo adicional de servicio
- ✅ Implementación más simple inicialmente
- ❌ La priorización depende de que la Function esté activa; si escala, la lógica se fragmenta
- ❌ Sin reintentos automáticos ni dead-letter queue: un fallo en el webhook sigue revirtiendo la transacción
- ❌ No resuelve el acoplamiento fuerte identificado como problema crítico

**Opción C — Azure Storage Queues**
- ✅ Muy bajo costo
- ❌ No soporta priorización ni sesiones
- ❌ Visibilidad de mensaje limitada a 7 días
- ❌ Sin dead-letter queue nativa

#### Decisión

Se elige **Azure Service Bus** en Basic tier como canal diferenciado para transacciones mayores a $5M COP. La Azure Function de enrutamiento evalúa el monto de cada transacción al salir de Event Hubs y despacha las de alto valor a Service Bus, donde se procesan con garantía de entrega at-least-once. Esto desacopla el webhook del flujo principal: si la notificación al comercio falla, Service Bus reintenta automáticamente sin revertir la autorización.

#### Consecuencias

- ✅ Las transacciones de alto valor tienen canal dedicado con garantía de procesamiento
- ✅ El acoplamiento entre autorización y webhook queda eliminado
- ✅ Reintentos automáticos reducen intervención manual del equipo de infraestructura
- ✅ Dead-letter queue permite auditar transacciones fallidas sin pérdida de datos
- ⚠️ Basic tier de Service Bus no soporta tópicos (solo colas), limitando patrones pub/sub futuros
- ⚠️ Agrega un servicio adicional a monitorear, incrementando levemente la complejidad operativa

---

### ADR-03: Uso de Azure Functions con Consumption Plan sobre Azure Container Apps para el procesamiento

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow necesita procesar hasta 500 tx/seg en picos sin intervención manual, con un presupuesto mensual ajustado y un equipo de infraestructura de una sola persona. El sistema actual procesa en un servidor fijo que no escala, lo que genera los 8 segundos de latencia en horas pico. La nueva arquitectura debe escalar automáticamente y minimizar la carga operativa.

#### Alternativas evaluadas

**Opción A — Azure Functions con Consumption Plan (elegida)**
- ✅ Escala automáticamente de 0 a N instancias sin configuración manual
- ✅ Trigger nativo para Event Hubs: cada partición dispara instancias paralelas automáticamente
- ✅ Primer millón de ejecuciones por mes gratuitas — dentro del presupuesto
- ✅ Sin administración de infraestructura: el equipo de una persona no gestiona servidores
- ✅ El equipo tiene experiencia en Node.js y Python, ambos soportados nativamente
- ❌ Cold start de 1-3 segundos en instancias inactivas puede afectar latencia en primeras llamadas
- ❌ Tiempo máximo de ejecución de 5 minutos en Consumption Plan (suficiente para el caso)

**Opción B — Azure Container Apps**
- ✅ Más control sobre el entorno de ejecución
- ✅ Sin límite de tiempo de ejecución por función
- ❌ Requiere conocimiento de contenedores (Docker, Kubernetes) que el equipo no tiene
- ❌ Costo mayor: no hay tier gratuito equivalente al millón de ejecuciones de Functions
- ❌ Escala más lenta ante picos abruptos comparado con Functions + Event Hubs trigger

**Opción C — Azure App Service (plan dedicado)**
- ✅ Sin cold starts
- ❌ Costo fijo mensual, repite el mismo problema del sistema legado
- ❌ Escalado horizontal requiere configuración manual de autoscaling rules

#### Decisión

Se elige **Azure Functions con Consumption Plan** por su escalado automático nativo con Event Hubs, su modelo de pago por ejecución y la alineación con las capacidades del equipo en Node.js/Python. El cold start se mitiga mediante el patrón de instancias mínimas pre-calentadas configurables en el plan.

#### Consecuencias

- ✅ El sistema escala automáticamente ante los picos de 260.000 transacciones diarias en temporada alta
- ✅ Costo proporcional al uso real: en horas de baja demanda el costo es cercano a cero
- ✅ Cero administración de servidores para el equipo de infraestructura
- ⚠️ Cold start puede generar latencia adicional de 1-3 segundos en las primeras invocaciones tras un período de inactividad
- ⚠️ El límite de 5 minutos de ejecución debe tenerse en cuenta si en el futuro se agregan procesos de larga duración (usar Durable Functions en ese caso)

---

### ADR-04: Uso de Cosmos DB sobre Azure SQL Database para la persistencia de transacciones

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow procesa transacciones de múltiples tipos: compras, reembolsos, pagos de servicios y transferencias. Cada tipo tiene atributos distintos (una transferencia tiene cuenta origen y destino; un reembolso referencia una transacción previa; un pago de servicio incluye referencia de factura). En un modelo relacional estricto esto requeriría múltiples tablas con joins complejos. Adicionalmente, el sistema debe escribir el estado de cada transacción a alta velocidad (hasta 500 tx/seg en picos) con baja latencia.

#### Alternativas evaluadas

**Opción A — Azure Cosmos DB (elegida)**
- ✅ Modelo de documento flexible: cada tipo de transacción puede tener sus propios atributos sin migración de esquema
- ✅ Free tier incluye 1.000 RU/s y 25 GB — suficiente para la fase piloto
- ✅ Latencia de escritura inferior a 10ms en P99 con replicación en Brazil South
- ✅ Escala horizontalmente sin intervención manual
- ✅ Integración nativa con Azure Functions mediante bindings de salida
- ❌ Cambio de paradigma desde el modelo relacional del sistema actual
- ❌ Consultas analíticas complejas (joins entre colecciones) son más costosas en RU/s

**Opción B — Azure SQL Database (tier gratuito)**
- ✅ El equipo puede tener experiencia previa con SQL
- ✅ Tier gratuito de 32 GB disponible
- ✅ Soporte nativo de transacciones ACID y joins complejos
- ❌ Esquema rígido: agregar atributos por tipo de transacción requiere migraciones
- ❌ Escalado vertical limitado en tier gratuito; no escala horizontalmente de forma automática
- ❌ En cargas de 500 tx/seg con escrituras concurrentes, puede generar contención de locks

#### Decisión

Se elige **Azure Cosmos DB** con el modelo de documentos (Core API). La flexibilidad de esquema es crítica dado que PayFlow maneja múltiples tipos de transacción con atributos variables. El free tier cubre las necesidades de la fase piloto y la integración nativa con Azure Functions reduce el código de infraestructura necesario. El cambio de paradigma (relacional a NoSQL) se justifica por los requerimientos de escalabilidad y la heterogeneidad de los datos.

#### Consecuencias

- ✅ Escritura de transacciones a alta velocidad sin contención de locks
- ✅ Esquema flexible permite agregar nuevos tipos de transacción sin migraciones costosas
- ✅ Free tier cubre la fase piloto dentro del presupuesto
- ⚠️ El equipo debe aprender el modelo de consistencia de Cosmos DB y el diseño de partition keys (se recomienda usar `comercioId` como partition key)
- ⚠️ Las consultas analíticas históricas pueden consumir muchas RU/s; para reportes complejos se recomienda exportar a Azure Synapse en el futuro
- ⚠️ Solo una cuenta por suscripción puede activar el free tier de Cosmos DB

---

### ADR-05: Uso de Azure Monitor + Application Insights sobre solución de monitoreo externa para observabilidad

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

El sistema actual de PayFlow no tiene observabilidad: el equipo se entera de problemas por quejas de comercios en WhatsApp, no por alertas automáticas. Esto implica tiempos de detección de incidentes prolongados en un sistema financiero donde cada segundo de fallo representa transacciones fallidas. La nueva arquitectura requiere alertas automáticas en menos de 30 segundos ante anomalías y trazabilidad distribuida por transacción para diagnóstico rápido.

#### Alternativas evaluadas

**Opción A — Azure Monitor + Application Insights (elegida)**
- ✅ Integración nativa con Azure Functions, Event Hubs, Service Bus y Cosmos DB sin instrumentación manual
- ✅ Trazas distribuidas automáticas: cada transacción tiene un correlation ID que atraviesa todos los servicios
- ✅ Alertas configurables con tiempo de detección inferior a 30 segundos
- ✅ Tier gratuito incluye 5 GB/mes de datos de telemetría — suficiente para la fase piloto
- ✅ Sin agentes externos ni configuración de infraestructura adicional
- ❌ Las consultas avanzadas con KQL (Kusto Query Language) tienen curva de aprendizaje
- ❌ Retención de logs limitada a 90 días en el tier gratuito

**Opción B — Datadog**
- ✅ UI más intuitiva y dashboards más ricos visualmente
- ✅ Alertas más configurables con integraciones a Slack, PagerDuty, etc.
- ❌ Costo significativo: desde $15 USD/host/mes, incompatible con el presupuesto del proyecto
- ❌ Requiere instalación de agente y configuración adicional para integrar con servicios Azure

**Opción C — Logs manuales en Cosmos DB o Blob Storage**
- ✅ Sin costo adicional
- ❌ Sin alertas automáticas: no resuelve el problema de observabilidad reactiva
- ❌ Sin correlación entre servicios: imposible trazar una transacción de extremo a extremo
- ❌ Requiere desarrollo custom para cualquier dashboard o alerta

#### Decisión

Se elige **Azure Monitor + Application Insights** por su integración nativa con todo el stack Azure sin costo adicional dentro del tier gratuito. La instrumentación automática de Azure Functions captura trazas, excepciones y métricas de rendimiento sin modificar el código de negocio. Las alertas de Azure Monitor se configuran sobre métricas clave: tasa de errores en Functions, latencia de Event Hubs y uso de RU/s en Cosmos DB.

#### Consecuencias

- ✅ El equipo pasa de detección reactiva (quejas por WhatsApp) a alertas automáticas en menos de 30 segundos
- ✅ Cada transacción es trazable de extremo a extremo mediante correlation ID automático
- ✅ Sin costo adicional en la fase piloto (dentro de los 5 GB/mes gratuitos)
- ✅ Cero esfuerzo de instrumentación en el código: la integración es automática con Azure Functions
- ⚠️ El equipo debe aprender KQL para consultas avanzadas en Log Analytics
- ⚠️ Retención de 90 días puede ser insuficiente para auditorías regulatorias financieras; en producción se recomienda exportar logs a Blob Storage para retención extendida

---

## Implementación

> En construcción — próximo commit

---

## Evidencias

> En construcción — próximo commit

---

## Conclusiones

> En construcción — próximo commit# PayFlow — Procesamiento de Eventos en Tiempo Real

**Curso:** Computación en la Nube | Semestre 2026-1
**Profesor:** Julián David Florez Sánchez
**Institución:** Tecnológico de Antioquia — Institución Universitaria
**Caso:** 03 — Procesamiento de Eventos en Tiempo Real
**Plataforma:** Microsoft Azure (Free Tier / Azure for Students)
**Entrega:** 14 de mayo de 2026

---

## Integrantes

| Nombre |
|--------|
| Daniela Vanegas Guerrero |
| Andrés Felipe Bolívar Osorio |
| Jaison Esteban Córdoba Arroyo |
| Sthyd Anderson Guissao Ramírez |

---

## Descripción del caso

PayFlow es una fintech colombiana fundada en 2020 que ofrece una plataforma de pagos
digitales para pequeños y medianos comercios. Opera como intermediario entre comercios,
adquirentes bancarios y redes de pago (Visa, Mastercard, PSE), procesando transacciones
de compra, reembolsos, pagos de servicios y transferencias entre cuentas.

Actualmente cuenta con 28.000 comercios activos, procesa en promedio 85.000 transacciones
diarias y tiene presencia en Colombia, Ecuador y Perú. En temporada alta el volumen puede
triplicarse, alcanzando hasta 260.000 transacciones en un solo día.

### Problemas identificados en el sistema actual

| Problema | Descripción |
|----------|-------------|
| Cuello de botella | El procesador actual maneja hasta 40 tx/seg. En picos supera los 8 segundos de respuesta |
| Sin priorización | Una transacción de $500 COP y una de $50.000.000 COP pasan por el mismo proceso |
| Fraude reactivo | El antifraude se aplica después de autorizar. El dinero ya está comprometido |
| Sin observabilidad | El equipo se entera de problemas por quejas en WhatsApp, no por alertas automáticas |
| Acoplamiento fuerte | Si el webhook falla, la transacción completa se revierte aunque la autorización fue exitosa |

---

## Arquitectura de referencia

Este caso está basado en la arquitectura oficial de Microsoft Azure para sistemas
de procesamiento de eventos en tiempo real.

- [Event-driven architecture](https://learn.microsoft.com/es-es/azure/architecture/guide/architecture-styles/event-driven)
- [Azure Event Hubs](https://learn.microsoft.com/es-es/azure/event-hubs/event-hubs-about)
- [Azure Functions — trigger por Event Hubs](https://learn.microsoft.com/es-es/azure/azure-functions/functions-bindings-event-hubs)
- [Azure Service Bus](https://learn.microsoft.com/es-es/azure/service-bus-messaging/service-bus-messaging-overview)
- [Azure Cosmos DB](https://learn.microsoft.com/es-es/azure/cosmos-db/introduction)
- [Azure Monitor](https://learn.microsoft.com/es-es/azure/azure-monitor/overview)

---

## Stack de servicios Azure

| Servicio | Responsabilidad en PayFlow | Tier |
|----------|---------------------------|------|
| Azure Event Hubs | Punto de entrada. Buffer distribuido ante picos de demanda. Recibe hasta 500 tx/seg | Basic — 1 TU |
| Azure Functions | Valida, evalúa fraude, enruta por monto y registra cada transacción | Consumption Plan |
| Azure Service Bus | Cola de prioridad para transacciones mayores a $5M COP con reintentos automáticos | Basic tier |
| Cosmos DB | Persiste el estado final de cada transacción procesada | Free tier — 25 GB |
| Azure Monitor + App Insights | Alertas automáticas en menos de 30 segundos. Trazas distribuidas por transacción | Gratuito 5 GB/mes |

---

## Modelo C4

### C1 — Contexto del sistema

![Diagrama C1 - Contexto](assets/C1.png)

PayFlow actúa como sistema central de procesamiento de pagos digitales. Recibe eventos
desde los terminales POS y el sistema legado, solicita autorización al adquirente bancario
y notifica el resultado al comercio mediante webhook. El equipo de riesgo monitorea alertas
de fraude y el equipo de operaciones supervisa la disponibilidad del sistema.

### C2 — Contenedores

![Diagrama C2 - Contenedores](assets/C2.png)

El sistema está compuesto por cinco servicios Azure desplegados en la región Brazil South,
cumpliendo la regulación de la Superintendencia Financiera de Colombia. Los eventos fluyen
desde Event Hubs hacia Azure Functions, que orquesta la validación, el antifraude, el
enrutamiento por monto y el registro en Cosmos DB. Las transacciones mayores a $5M COP
se enrutan por un canal diferenciado en Service Bus con garantía de entrega at-least-once.

### C3 — Componentes

> Diagrama en construcción — próximo commit

---

## Decisiones Arquitectónicas (ADRs)

### ADR-01: Uso de Azure Event Hubs como punto de entrada sobre Azure Service Bus para ingesta de transacciones

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow procesa en promedio 85.000 transacciones diarias, con picos de hasta 260.000 en temporada alta, lo que equivale a aproximadamente 500 tx/seg en momentos de alta demanda. El sistema actual tiene un cuello de botella crítico: el procesador legado solo soporta 40 tx/seg, generando tiempos de respuesta superiores a 8 segundos en picos. Se necesita un buffer distribuido que absorba ráfagas de tráfico sin perder eventos y que desacople la ingesta del procesamiento.

#### Alternativas evaluadas

**Opción A — Azure Event Hubs (elegida)**
- ✅ Diseñado para ingesta masiva de eventos en tiempo real (millones de eventos/seg escalables)
- ✅ Modelo de consumidor particionado: múltiples instancias de Azure Functions pueden leer en paralelo
- ✅ Retención configurable de eventos (hasta 7 días en Basic tier)
- ✅ Basic tier con 1 Throughput Unit soporta 1 MB/seg de entrada — suficiente para 500 tx/seg
- ❌ No tiene garantía de orden global entre particiones
- ❌ No es ideal para enrutamiento complejo por atributos del mensaje

**Opción B — Azure Service Bus como entrada principal**
- ✅ Garantía de orden FIFO dentro de una sesión
- ✅ Soporte nativo de dead-letter queue y reintentos automáticos
- ❌ No está diseñado para ingesta de alto volumen en tiempo real
- ❌ Throughput limitado comparado con Event Hubs para cargas de tipo streaming
- ❌ Más costoso en el tier que soportaría la carga de PayFlow

#### Decisión

Se elige **Azure Event Hubs** como punto de entrada para todas las transacciones entrantes. Su modelo de streaming particionado permite absorber los picos de 500 tx/seg sin saturar el procesador, resolviendo directamente el cuello de botella identificado. Azure Service Bus se mantiene en la arquitectura pero en un rol diferente: como cola de prioridad para transacciones mayores a $5M COP (ver ADR-02).

#### Consecuencias

- ✅ El sistema puede recibir hasta 500 tx/seg sin intervención manual
- ✅ Las Azure Functions escalan horizontalmente leyendo desde particiones paralelas
- ✅ Los eventos se retienen hasta 1 día en Basic tier, permitiendo reprocesamiento ante fallos
- ⚠️ No hay garantía de orden global: transacciones del mismo comercio podrían procesarse en distinto orden si caen en particiones diferentes
- ⚠️ En Basic tier no hay soporte para Capture ni Virtual Network integration, lo que limita opciones de auditoría avanzada

---

### ADR-02: Uso de Azure Service Bus para enrutamiento prioritario de transacciones de alto valor

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow no diferencia actualmente entre una transacción de $500 COP y una de $50.000.000 COP: ambas pasan por el mismo proceso con la misma prioridad. Esto representa un riesgo de negocio significativo: en momentos de alta carga, una transacción de alto valor puede quedar represada detrás de cientos de micropagos. Adicionalmente, si el webhook de notificación al comercio falla, el sistema revierte toda la transacción aunque la autorización bancaria fue exitosa, generando acoplamiento fuerte entre componentes.

#### Alternativas evaluadas

**Opción A — Azure Service Bus con colas diferenciadas (elegida)**
- ✅ Soporte nativo de sesiones y priorización por atributos del mensaje
- ✅ Reintentos automáticos configurables (hasta 10 intentos con backoff exponencial)
- ✅ Dead-letter queue integrada para transacciones que fallan repetidamente
- ✅ Garantía de entrega at-least-once, desacoplando el webhook del flujo principal
- ✅ Basic tier disponible dentro del presupuesto del proyecto
- ❌ No es ideal para ingesta masiva de alto volumen (por eso se usa Event Hubs para entrada)

**Opción B — Manejo de prioridad dentro de Azure Functions (lógica en código)**
- ✅ Sin costo adicional de servicio
- ✅ Implementación más simple inicialmente
- ❌ La priorización depende de que la Function esté activa; si escala, la lógica se fragmenta
- ❌ Sin reintentos automáticos ni dead-letter queue: un fallo en el webhook sigue revirtiendo la transacción
- ❌ No resuelve el acoplamiento fuerte identificado como problema crítico

**Opción C — Azure Storage Queues**
- ✅ Muy bajo costo
- ❌ No soporta priorización ni sesiones
- ❌ Visibilidad de mensaje limitada a 7 días
- ❌ Sin dead-letter queue nativa

#### Decisión

Se elige **Azure Service Bus** en Basic tier como canal diferenciado para transacciones mayores a $5M COP. La Azure Function de enrutamiento evalúa el monto de cada transacción al salir de Event Hubs y despacha las de alto valor a Service Bus, donde se procesan con garantía de entrega at-least-once. Esto desacopla el webhook del flujo principal: si la notificación al comercio falla, Service Bus reintenta automáticamente sin revertir la autorización.

#### Consecuencias

- ✅ Las transacciones de alto valor tienen canal dedicado con garantía de procesamiento
- ✅ El acoplamiento entre autorización y webhook queda eliminado
- ✅ Reintentos automáticos reducen intervención manual del equipo de infraestructura
- ✅ Dead-letter queue permite auditar transacciones fallidas sin pérdida de datos
- ⚠️ Basic tier de Service Bus no soporta tópicos (solo colas), limitando patrones pub/sub futuros
- ⚠️ Agrega un servicio adicional a monitorear, incrementando levemente la complejidad operativa

---

### ADR-03: Uso de Azure Functions con Consumption Plan sobre Azure Container Apps para el procesamiento

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow necesita procesar hasta 500 tx/seg en picos sin intervención manual, con un presupuesto mensual ajustado y un equipo de infraestructura de una sola persona. El sistema actual procesa en un servidor fijo que no escala, lo que genera los 8 segundos de latencia en horas pico. La nueva arquitectura debe escalar automáticamente y minimizar la carga operativa.

#### Alternativas evaluadas

**Opción A — Azure Functions con Consumption Plan (elegida)**
- ✅ Escala automáticamente de 0 a N instancias sin configuración manual
- ✅ Trigger nativo para Event Hubs: cada partición dispara instancias paralelas automáticamente
- ✅ Primer millón de ejecuciones por mes gratuitas — dentro del presupuesto
- ✅ Sin administración de infraestructura: el equipo de una persona no gestiona servidores
- ✅ El equipo tiene experiencia en Node.js y Python, ambos soportados nativamente
- ❌ Cold start de 1-3 segundos en instancias inactivas puede afectar latencia en primeras llamadas
- ❌ Tiempo máximo de ejecución de 5 minutos en Consumption Plan (suficiente para el caso)

**Opción B — Azure Container Apps**
- ✅ Más control sobre el entorno de ejecución
- ✅ Sin límite de tiempo de ejecución por función
- ❌ Requiere conocimiento de contenedores (Docker, Kubernetes) que el equipo no tiene
- ❌ Costo mayor: no hay tier gratuito equivalente al millón de ejecuciones de Functions
- ❌ Escala más lenta ante picos abruptos comparado con Functions + Event Hubs trigger

**Opción C — Azure App Service (plan dedicado)**
- ✅ Sin cold starts
- ❌ Costo fijo mensual, repite el mismo problema del sistema legado
- ❌ Escalado horizontal requiere configuración manual de autoscaling rules

#### Decisión

Se elige **Azure Functions con Consumption Plan** por su escalado automático nativo con Event Hubs, su modelo de pago por ejecución y la alineación con las capacidades del equipo en Node.js/Python. El cold start se mitiga mediante el patrón de instancias mínimas pre-calentadas configurables en el plan.

#### Consecuencias

- ✅ El sistema escala automáticamente ante los picos de 260.000 transacciones diarias en temporada alta
- ✅ Costo proporcional al uso real: en horas de baja demanda el costo es cercano a cero
- ✅ Cero administración de servidores para el equipo de infraestructura
- ⚠️ Cold start puede generar latencia adicional de 1-3 segundos en las primeras invocaciones tras un período de inactividad
- ⚠️ El límite de 5 minutos de ejecución debe tenerse en cuenta si en el futuro se agregan procesos de larga duración (usar Durable Functions en ese caso)

---

### ADR-04: Uso de Cosmos DB sobre Azure SQL Database para la persistencia de transacciones

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

PayFlow procesa transacciones de múltiples tipos: compras, reembolsos, pagos de servicios y transferencias. Cada tipo tiene atributos distintos (una transferencia tiene cuenta origen y destino; un reembolso referencia una transacción previa; un pago de servicio incluye referencia de factura). En un modelo relacional estricto esto requeriría múltiples tablas con joins complejos. Adicionalmente, el sistema debe escribir el estado de cada transacción a alta velocidad (hasta 500 tx/seg en picos) con baja latencia.

#### Alternativas evaluadas

**Opción A — Azure Cosmos DB (elegida)**
- ✅ Modelo de documento flexible: cada tipo de transacción puede tener sus propios atributos sin migración de esquema
- ✅ Free tier incluye 1.000 RU/s y 25 GB — suficiente para la fase piloto
- ✅ Latencia de escritura inferior a 10ms en P99 con replicación en Brazil South
- ✅ Escala horizontalmente sin intervención manual
- ✅ Integración nativa con Azure Functions mediante bindings de salida
- ❌ Cambio de paradigma desde el modelo relacional del sistema actual
- ❌ Consultas analíticas complejas (joins entre colecciones) son más costosas en RU/s

**Opción B — Azure SQL Database (tier gratuito)**
- ✅ El equipo puede tener experiencia previa con SQL
- ✅ Tier gratuito de 32 GB disponible
- ✅ Soporte nativo de transacciones ACID y joins complejos
- ❌ Esquema rígido: agregar atributos por tipo de transacción requiere migraciones
- ❌ Escalado vertical limitado en tier gratuito; no escala horizontalmente de forma automática
- ❌ En cargas de 500 tx/seg con escrituras concurrentes, puede generar contención de locks

#### Decisión

Se elige **Azure Cosmos DB** con el modelo de documentos (Core API). La flexibilidad de esquema es crítica dado que PayFlow maneja múltiples tipos de transacción con atributos variables. El free tier cubre las necesidades de la fase piloto y la integración nativa con Azure Functions reduce el código de infraestructura necesario. El cambio de paradigma (relacional a NoSQL) se justifica por los requerimientos de escalabilidad y la heterogeneidad de los datos.

#### Consecuencias

- ✅ Escritura de transacciones a alta velocidad sin contención de locks
- ✅ Esquema flexible permite agregar nuevos tipos de transacción sin migraciones costosas
- ✅ Free tier cubre la fase piloto dentro del presupuesto
- ⚠️ El equipo debe aprender el modelo de consistencia de Cosmos DB y el diseño de partition keys (se recomienda usar `comercioId` como partition key)
- ⚠️ Las consultas analíticas históricas pueden consumir muchas RU/s; para reportes complejos se recomienda exportar a Azure Synapse en el futuro
- ⚠️ Solo una cuenta por suscripción puede activar el free tier de Cosmos DB

---

### ADR-05: Uso de Azure Monitor + Application Insights sobre solución de monitoreo externa para observabilidad

**Fecha:** Mayo 2026
**Estado:** Aceptado

#### Contexto

El sistema actual de PayFlow no tiene observabilidad: el equipo se entera de problemas por quejas de comercios en WhatsApp, no por alertas automáticas. Esto implica tiempos de detección de incidentes prolongados en un sistema financiero donde cada segundo de fallo representa transacciones fallidas. La nueva arquitectura requiere alertas automáticas en menos de 30 segundos ante anomalías y trazabilidad distribuida por transacción para diagnóstico rápido.

#### Alternativas evaluadas

**Opción A — Azure Monitor + Application Insights (elegida)**
- ✅ Integración nativa con Azure Functions, Event Hubs, Service Bus y Cosmos DB sin instrumentación manual
- ✅ Trazas distribuidas automáticas: cada transacción tiene un correlation ID que atraviesa todos los servicios
- ✅ Alertas configurables con tiempo de detección inferior a 30 segundos
- ✅ Tier gratuito incluye 5 GB/mes de datos de telemetría — suficiente para la fase piloto
- ✅ Sin agentes externos ni configuración de infraestructura adicional
- ❌ Las consultas avanzadas con KQL (Kusto Query Language) tienen curva de aprendizaje
- ❌ Retención de logs limitada a 90 días en el tier gratuito

**Opción B — Datadog**
- ✅ UI más intuitiva y dashboards más ricos visualmente
- ✅ Alertas más configurables con integraciones a Slack, PagerDuty, etc.
- ❌ Costo significativo: desde $15 USD/host/mes, incompatible con el presupuesto del proyecto
- ❌ Requiere instalación de agente y configuración adicional para integrar con servicios Azure

**Opción C — Logs manuales en Cosmos DB o Blob Storage**
- ✅ Sin costo adicional
- ❌ Sin alertas automáticas: no resuelve el problema de observabilidad reactiva
- ❌ Sin correlación entre servicios: imposible trazar una transacción de extremo a extremo
- ❌ Requiere desarrollo custom para cualquier dashboard o alerta

#### Decisión

Se elige **Azure Monitor + Application Insights** por su integración nativa con todo el stack Azure sin costo adicional dentro del tier gratuito. La instrumentación automática de Azure Functions captura trazas, excepciones y métricas de rendimiento sin modificar el código de negocio. Las alertas de Azure Monitor se configuran sobre métricas clave: tasa de errores en Functions, latencia de Event Hubs y uso de RU/s en Cosmos DB.

#### Consecuencias

- ✅ El equipo pasa de detección reactiva (quejas por WhatsApp) a alertas automáticas en menos de 30 segundos
- ✅ Cada transacción es trazable de extremo a extremo mediante correlation ID automático
- ✅ Sin costo adicional en la fase piloto (dentro de los 5 GB/mes gratuitos)
- ✅ Cero esfuerzo de instrumentación en el código: la integración es automática con Azure Functions
- ⚠️ El equipo debe aprender KQL para consultas avanzadas en Log Analytics
- ⚠️ Retención de 90 días puede ser insuficiente para auditorías regulatorias financieras; en producción se recomienda exportar logs a Blob Storage para retención extendida

---

## Implementación

> En construcción — próximo commit

---

## Evidencias

> En construcción — próximo commit

---

## Conclusiones

> En construcción — próximo commit
