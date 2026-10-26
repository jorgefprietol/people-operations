# Flujo de operación

![Flujo de operación](diagrams/flow.svg)

[Abrir SVG](diagrams/flow.svg) · [Fuente Mermaid](diagrams/flow.mmd)


El mismo contrato HTTP ofrece tres recorridos: administrar políticas, consultar información y registrar el avance de una incorporación. Una consulta no cambia aprobaciones ni tareas.

<details>
<summary>Versión Mermaid</summary>

```mermaid
flowchart TD
    Request["Solicitud autenticada"] --> Retry{"¿Clave y contenido ya procesados?"}
    Retry -->|Sí| Replay["Devolver respuesta persistida"]
    Retry -->|No| Action{"Tipo de operación"}
    Action -->|Política| ValidatePolicy["Validar texto, ámbito y versión esperada"]
    ValidatePolicy --> Index["Versionar y sustituir fragmentos"]
    Action -->|Consulta| Scope["Filtrar tenant y grupos"]
    Scope --> Rank["Recuperar fuentes por TF-IDF"]
    Rank --> Evidence{"¿Existe sustento suficiente?"}
    Evidence -->|No| Abstain["Abstenerse y devolver fuentes vacías"]
    Evidence -->|Sí| Mode{"¿Ollama configurado?"}
    Mode -->|No| Cite["Construir respuesta con extractos y citas"]
    Mode -->|Sí| Select["Seleccionar y validar identificadores de fuente"]
    Select --> Cite
    Action -->|Expediente| Rules["Validar estado, dependencias y aprobación"]
    Rules --> Case["Registrar transición del expediente"]
    Index --> Commit["Persistir resultado y auditoría"]
    Abstain --> Commit
    Cite --> Commit
    Case --> Commit
    Commit --> Response["Devolver resultado"]
```

</details>

- **Políticas:** `policy_ingest` crea o actualiza una versión; `policy_delete` exige la versión vigente y retira sus fragmentos del índice activo.
- **Consultas:** `query_policy` recibe pregunta, organización y grupos. El ranking se calcula sólo con documentos visibles. El modelo, cuando está configurado, recibe esos fragmentos y no el expediente del empleado.
- **Expedientes:** `create`, `activate`, `approve`, `complete` y `cancel` aplican reglas de estado. La aprobación anticipada no permite omitir dependencias.
- **Errores:** validaciones, fuentes inventadas o fallo del proveedor revierten la transacción. La misma clave puede reintentarse después de una operación fallida.

Las consultas conservadas por idempotencia son evidencia histórica de la respuesta original: cambiar o borrar una política no purga respuestas ya almacenadas. La retención debe definirse con los responsables de datos antes de una operación real.
