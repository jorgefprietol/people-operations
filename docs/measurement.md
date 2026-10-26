# Medición del caso de onboarding

El objetivo es agilizar consultas y solicitudes, reducir tareas manuales y mantener la trazabilidad de cada aprobación. El tiempo completo de incorporación incluye dependencias y esperas humanas; no se deduce de la latencia de una llamada API.

| KPI | Definición | Evidencia necesaria |
| --- | --- | --- |
| Tiempo de solicitud | Mediana y p95 desde recepción hasta resolución | Misma clase de solicitud, marcas de inicio/cierre y periodo antes/después |
| Tiempo de onboarding | Tiempo desde activación hasta completar las tareas requeridas | Eventos del expediente, calendario de trabajo y tiempos de espera externos |
| Productividad | Solicitudes correctas o tareas completadas por hora operativa | Horas registradas y revisión del resultado, con tareas comparables |
| Tasa de errores | Solicitudes que requieren corrección / solicitudes auditadas | Tipología del error, muestra, volumen y revisión humana |
| Calidad de consulta | Respuestas correctas con política y versión válidas / preguntas evaluadas | Preguntas por grupo, fuente esperada, abstenciones y revisión de acceso |

La reducción de tiempo es `(tiempo_base - tiempo_nuevo) / tiempo_base × 100`. Calcula el resultado por tipo de proceso, manteniendo el mismo estadístico, alcance y ventana comparable. Registra también tamaño de muestra y dependencia de sistemas externos. No atribuyas a automatización una reducción obtenida cambiando la complejidad o excluyendo solicitudes pendientes.

La auditoría conserva cambios del flujo. Las consultas documentales no completan tareas ni autorizan accesos. Una respuesta correcta de la API no prueba que una cuenta de un sistema externo se haya provisionado.

`python -m app metrics` expone latencia y transacciones locales únicas. Incluye trabajo de base de datos y llamadas síncronas a proveedores, y excluye transporte HTTP del cliente, fallos y respuestas reutilizadas. Las pruebas usan políticas y expedientes sintéticos; sus resultados no son una medición de productividad empresarial.

Las cifras de proyectos reales requieren sus registros de origen y autorización de uso. Publica únicamente agregados anonimizados; no incorpores expedientes de personal ni datos identificables al repositorio.
