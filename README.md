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

> En construcción — próximo commit

### ADR-01
### ADR-02
### ADR-03
### ADR-04
### ADR-05

---

## Implementación

> En construcción — próximo commit

---

## Evidencias

> En construcción — próximo commit

---

## Conclusiones

> En construcción — próximo commit
