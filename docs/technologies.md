# Tecnologías utilizadas

| Tecnología | Uso concreto | Estado |
| --- | --- | --- |
| Python 3.10+ | Motor de onboarding, API, calendario y validación. | Implementado; biblioteca estándar. |
| SQLite | Expedientes, políticas versionadas, fragmentos, auditoría e idempotencia. | Implementado en modo local. |
| TF-IDF y similitud coseno | Recuperación de políticas sobre el corpus autorizado. | Implementación local; sin embeddings. |
| JSON y REST HTTP | Contrato de solicitudes, transiciones y consultas con citas. | Implementado con `http.server`. |
| Ollama | Selección de citas y redacción opcional del resumen de estado. | Adaptador implementado; modelo e instalación externos. |
| n8n | Webhook y llamada autenticada a `/api/run`. | Workflow JSON incluido; importación y credenciales pendientes por entorno. |
| Docker / Compose | Ejecución aislada del servicio y orquestación opcional. | Archivos incluidos; requiere validar el runtime de despliegue. |
| unittest / GitHub Actions | Regresiones de negocio, acceso, consultas y transacciones. | Pruebas locales y pipeline por repositorio. |
| Mermaid | Diagramas editables de componentes y operación. | Fuentes en la documentación. |

La versión local no conecta un HRIS, directorio corporativo o motor de provisión de cuentas. Registra confirmaciones de esos sistemas mediante API; sus adaptadores e identidad deben configurarse en la integración correspondiente.
