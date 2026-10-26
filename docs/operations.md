# Operación

Revise el expediente antes de activarlo. Complete la verificación de identidad y la aceptación de políticas en sus sistemas responsables; después registre las confirmaciones. No utilice la opción de resumen como evidencia de cumplimiento.

Una tarea bloqueada devuelve un error sin cambiar el estado. Consulte `status`, complete las dependencias y solicite la aprobación que corresponda. Para reintentar una transición por un fallo de red conserve la clave de idempotencia original.

Cancelar un expediente impide nuevas transiciones locales, pero no revoca accesos ya concedidos. Una integración real debe iniciar un flujo separado de revocación, conservar su evidencia y vincularlo al expediente cancelado.

Los indicadores útiles son expedientes abiertos, tareas vencidas, tiempo hasta primera cuenta y tiempo hasta cierre. Las fechas del plan no representan duración efectiva. Para comparar períodos utilice eventos observados de activación y cierre, una misma definición de día laborable y cohortes equivalentes.

Respalde la base y aplique retención al historial. No guarde nombres ni información médica en `actor`, motivos o referencias internas. El proveedor de resumen debe recibir únicamente la proyección prevista en el dominio.
