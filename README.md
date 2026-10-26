# People Operations

Servicio de onboarding con expedientes mínimos, dependencias entre tareas y aprobaciones explícitas para accesos. Permite comprobar qué bloquea una incorporación y quién registró cada paso sin almacenar nombres, documentos o correos personales.

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

## Evidencia y alcance

Las pruebas verifican dependencias, aprobación, reintentos, cancelación, cierre, fechas laborables y rechazo de datos personales adicionales. Los vencimientos excluyen sábados y domingos; no consideran feriados nacionales. La API usa autenticación de servicio; `actor` sirve de referencia de auditoría y requiere asociación a identidad y permisos en una integración corporativa.

`/api/metrics` mide solicitudes locales. El progreso se calcula como tareas completadas sobre tareas del expediente. Para medir tiempo de onboarding en una operación real deben registrarse eventos de inicio y cierre con su calendario de trabajo. Este repositorio no incluye selección, ranking de candidatos ni decisiones laborales automatizadas.

Consulte [arquitectura](docs/architecture.md), [decisiones](docs/decisions.md), [operación](docs/operations.md) y [referencias](docs/references.md).
