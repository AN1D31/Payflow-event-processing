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

PayFlow procesa en promedio 85.000 transacciones diarias, con picos de hasta 260.000 en
temporada alta, lo que equivale a aproximadamente 500 tx/seg en momentos de alta demanda.
El sistema actual tiene un cuello de botella crítico: el procesador legado solo soporta 40
tx/seg, generando tiempos de respuesta superiores a 8 segundos en picos. Se necesita un
buffer distribuido que absorba ráfagas de tráfico sin perder eventos y que desacople la
ingesta del procesamiento.

#### Alternativas evaluadas

**Opción A — Azure Event Hubs (elegida)**
- ✅ Diseñado para ingesta masiva de eventos en tiempo real (millones de eventos/seg escalables)
- ✅ Modelo de consumidor particionado: múltiples instancias de Azure Functions pueden leer en paralelo
- ✅ Retención configurable de eventos (hasta 7 días en Basic tier)
- ✅ Basic tier con 1 Throughput Unit soporta 1 MB/seg de entrada — suficiente para 500 tx/se# PayFlow — Procesamiento de Eventos en Tiempo Real

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

PayFlow procesa en promedio 85.000 transacciones diarias, con picos de hasta 260.000 en
temporada alta, lo que equivale a aproximadamente 500 tx/seg en momentos de alta demanda.
El sistema actual tiene un cuello de botella crítico: el procesador legado solo soporta 40
tx/seg, generando tiempos de respuesta superiores a 8 segundos en picos. Se necesita un
buffer distribuido que absorba ráfagas de tráfico sin perder eventos y que desacople la
ingesta del procesamiento.

#### Alternativas evaluadas

**Opción A — Azure Event Hubs (elegida)**
- ✅ Diseñado para ingesta masiva de eventos en tiempo real (millones de eventos/seg escalables)
- ✅ Modelo de consumidor particionado: múltiples instancias de Azure Functions pueden leer en paralelo
- ✅ Retención configurable de eventos (hasta 7 días en Basic tier)
- ✅ Basic tier con 1 Throughput Unit soporta 1 MB/seg de entrada — suficiente para 500 tx/se# PayFlow — Procesamiento de Eventos en Tiempo Real

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

PayFlow procesa en promedio 85.000 transacciones diarias, con picos de hasta 260.000 en
temporada alta, lo que equivale a aproximadamente 500 tx/seg en momentos de alta demanda.
El sistema actual tiene un cuello de botella crítico: el procesador legado solo soporta 40
tx/seg, generando tiempos de respuesta superiores a 8 segundos en picos. Se necesita un
buffer distribuido que absorba ráfagas de tráfico sin perder eventos y que desacople la
ingesta del procesamiento.

#### Alternativas evaluadas

**Opción A — Azure Event Hubs (elegida)**
- ✅ Diseñado para ingesta masiva de eventos en tiempo real (millones de eventos/seg escalables)
- ✅ Modelo de consumidor particionado: múltiples instancias de Azure Functions pueden leer en paralelo
- ✅ Retención configurable de eventos (hasta 7 días en Basic tier)
- ✅ Basic tier con 1 Throughput Unit soporta 1 MB/seg de entrada — suficiente para 500 tx/se# PayFlow — Procesamiento de Eventos en Tiempo Real

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

PayFlow procesa en promedio 85.000 transacciones diarias, con picos de hasta 260.000 en
temporada alta, lo que equivale a aproximadamente 500 tx/seg en momentos de alta demanda.
El sistema actual tiene un cuello de botella crítico: el procesador legado solo soporta 40
tx/seg, generando tiempos de respuesta superiores a 8 segundos en picos. Se necesita un
buffer distribuido que absorba ráfagas de tráfico sin perder eventos y que desacople la
ingesta del procesamiento.

#### Alternativas evaluadas

**Opción A — Azure Event Hubs (elegida)**
- ✅ Diseñado para ingesta masiva de eventos en tiempo real (millones de eventos/seg escalables)
- ✅ Modelo de consumidor particionado: múltiples instancias de Azure Functions pueden leer en paralelo
- ✅ Retención configurable de eventos (hasta 7 días en Basic tier)
- ✅ Basic tier con 1 Throughput Unit soporta 1 MB/seg de entrada — suficiente para 500 tx/se

## Conclusiones

> En construcción — próximo commit
