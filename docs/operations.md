# Operación

Revise el expediente antes de activarlo. Complete la verificación de identidad y la aceptación de políticas en sus sistemas responsables; después registre las confirmaciones. No utilice la opción de resumen como evidencia de cumplimiento.

Una tarea bloqueada devuelve un error sin cambiar el estado. Consulte `status`, complete las dependencias y solicite la aprobación que corresponda. Para reintentar una transición por un fallo de red conserve la clave de idempotencia original.

Cancelar un expediente impide nuevas transiciones locales, pero no revoca accesos ya concedidos. Una integración real debe iniciar un flujo separado de revocación, conservar su evidencia y vincularlo al expediente cancelado.

Los indicadores útiles son expedientes abiertos, tareas vencidas, tiempo hasta primera cuenta y tiempo hasta cierre. Las fechas del plan no representan duración efectiva. Para comparar períodos utilice eventos observados de activación y cierre, una misma definición de día laborable y cohortes equivalentes.

Respalde la base y aplique retención al historial. No guarde nombres ni información médica en `actor`, motivos o referencias internas. El proveedor de resumen debe recibir únicamente la proyección prevista en el dominio.

## Corpus de políticas

Publique texto aprobado con `policy_ingest`, un `tenant` y un `access_group`. La creación admite `expected_version:0`; una actualización puede aportar la versión leída para detectar conflictos. La eliminación exige la versión vigente. Use una clave de idempotencia distinta para una modificación nueva y conserve la misma al reintentar una petición incierta.

El servicio admite hasta 500 políticas por organización, 20 000 caracteres por texto y 500 por pregunta. El índice utiliza fragmentos de hasta 600 caracteres y umbrales fijos de relevancia y cobertura. Evalúe preguntas con respuesta conocida y casos sin respuesta antes de ampliar un corpus; no use el porcentaje de similitud como probabilidad de verdad.

`policy_demo` carga únicamente políticas sintéticas bajo `demo-company`. Para probar sin afectar una base de trabajo, ejecute:

```powershell
python -m app run --input data/policy-demo.json --key policy-demo-001 --db var/policy-demo.db
```

Para habilitar selección de citas con modelo configure `MODEL_BACKEND=ollama`, `OLLAMA_MODEL` y `OLLAMA_URL`. No se descarga ningún modelo automáticamente. La prueba del adaptador con dobles no valida la calidad del modelo elegido ni su comportamiento con el corpus real. Un error del proveedor revierte la solicitud completa.

La integración debe obtener `tenant` y `groups` de la identidad, no del texto del usuario. No publique datos personales dentro de políticas. Las preguntas y respuestas se conservan en la tabla de solicitudes por idempotencia; borrar el índice no las purga. Coordine retención y borrado con el responsable de datos.
