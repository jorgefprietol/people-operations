# People Operations

Servicio de onboarding con expedientes mínimos, dependencias entre tareas y aprobaciones explícitas para accesos. Permite comprobar qué bloquea una incorporación y quién registró cada paso sin almacenar nombres, documentos o correos personales.

## Contexto y confidencialidad

Este caso de uso forma parte de mi experiencia en soluciones implementadas en producción durante trabajos de consultoría. La versión pública es una implementación independiente con datos sintéticos que permite revisar la arquitectura, los flujos y los controles. Por confidencialidad, no se incluyen la identidad del cliente, su código ni sus registros operativos.

Incluye consultas RAG sobre políticas versionadas, con filtro de acceso, citas y abstención. Un modelo configurado puede seleccionar las fuentes; la respuesta conserva extractos verificables y nunca sustituye una aprobación.

[Arquitectura diagramada](docs/architecture.md) · [Flujo diagramado](docs/flow.md) · [Tecnologías utilizadas](docs/technologies.md)

## Ejecutar

Requiere Python 3.10 o posterior; la demo utiliza datos sintéticos y una base temporal.

```powershell
python -m app demo
python -m unittest discover -s tests -v
$env:SERVICE_TOKEN = 'un-token-local-de-al-menos-24-caracteres'
python -m app serve
```

La interfaz está en `http://127.0.0.1:8080`. `POST /api/run` exige `Authorization: Bearer <SERVICE_TOKEN>` e `Idempotency-Key`. Utilice otra clave para cada transición del expediente.

## Flujo

```json
{"action":"create","employee_ref":"EMP-DEMO-042","role":"engineering","start_date":"2026-10-26"}
```

Guarde el `case_id` recibido. Los roles admitidos son `engineering`, `operations` y `sales`. La creación deja el expediente en `planned`; `activate` abre las tareas y `cancel` exige un motivo. Todas las tareas completadas cierran el expediente como `completed`.

```json
{"action":"activate","case_id":"ID_RECIBIDO"}
```

| Tarea | Dependencias | Aprobación |
| --- | --- | --- |
| `policy_acknowledged` | Ninguna | No |
| `identity_verified` | Ninguna | No |
| `account_provisioned` | Política e identidad | Sí |
| `workspace_ready` | Cuenta | No |
| `repository_access` | Cuenta; solo engineering | Sí |

`complete` registra un paso realizado; no crea cuentas ni concede permisos en sistemas externos. Para tareas sensibles, primero use `approve`, y después registre `complete` cuando el adaptador o responsable haya confirmado su ejecución.

```json
{"action":"approve","case_id":"ID_RECIBIDO","task_id":"account_provisioned","actor":"manager-01"}
```

```json
{"action":"complete","case_id":"ID_RECIBIDO","task_id":"account_provisioned","actor":"it-01"}
```

`status` devuelve tareas, fechas y progreso. `summary` resume exclusivamente ese estado; con el proveedor configurado puede redactarlo mediante un modelo. El estado estructurado acompaña siempre al resumen y conserva la autoridad sobre el texto generado.

## Consultas de políticas

El índice recibe texto por API: no abre rutas de archivos enviadas por clientes. Cada política pertenece a una organización y un grupo de acceso. La misma política sin cambios conserva su versión; un cambio sustituye los fragmentos del índice activo y genera nuevas citas.

```json
{"action":"policy_ingest","tenant":"demo-company","policy_id":"access-policy","title":"Alta de cuentas","access_group":"employees","expected_version":0,"content":"La provisión de cuentas requiere verificar la identidad y obtener aprobación del responsable."}
```

```json
{"action":"query_policy","tenant":"demo-company","groups":["employees"],"query":"provisión cuentas identidad aprobación"}
```

La respuesta incluye `answer`, `sources`, `abstained` y `method`. Cada fuente contiene `policy_id`, `version`, `chunk_id` y `excerpt`. El motor aplica TF-IDF y similitud coseno sólo sobre fuentes autorizadas; devuelve hasta tres fragmentos con puntuación y cobertura suficientes. No usa una base vectorial externa. `policy_delete` exige `expected_version` para retirar una política y sus fragmentos actuales.

Con `MODEL_BACKEND=ollama`, el modelo selecciona identificadores de esos fragmentos. El servicio rechaza identificadores ajenos, campos extra y duplicados; la respuesta final sigue siendo extractiva. Un fallo del proveedor revierte la solicitud, sin modificar el onboarding.

Para una demo de consulta con corpus sintético:

```powershell
python -m app run --input data/policy-demo.json --key policy-demo-001
```

`data/policy-ingest.json` y `data/policy-query.json` muestran los recorridos separados. La política de ejemplo explica los requisitos de provisión de cuentas; su consulta no completa tareas ni concede permisos.

## Evidencia y alcance

Las pruebas verifican dependencias, aprobación, reintentos, cancelación, cierre, fechas laborables y rechazo de datos personales adicionales. Los vencimientos excluyen sábados y domingos; no consideran feriados nacionales. La API usa autenticación de servicio; `actor` sirve de referencia de auditoría y requiere asociación a identidad y permisos en una integración corporativa.

Las consultas verifican además aislamiento de políticas por organización y grupo, versiones, eliminación, falta de evidencia, rollback y selección de fuentes mediante el proveedor. `tenant` y `groups` son atributos confiados a la integración autenticada; deben derivarse de una identidad corporativa. El flujo de expedientes conserva el alcance de una sola organización operadora. Borrar una política del índice no elimina las respuestas históricas persistidas por idempotencia.

`/api/metrics` mide solicitudes locales. El progreso se calcula como tareas completadas sobre tareas del expediente. Para medir tiempo de onboarding en una operación real deben registrarse eventos de inicio y cierre con su calendario de trabajo. Este repositorio no incluye selección, ranking de candidatos ni decisiones laborales automatizadas.

Consulte [arquitectura](docs/architecture.md), [flujo](docs/flow.md), [tecnologías](docs/technologies.md), [decisiones](docs/decisions.md), [operación](docs/operations.md) y [referencias](docs/references.md).
