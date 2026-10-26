# Decisiones de diseño

1. **Datos mínimos.** Se rechazan campos adicionales en la creación. La relación entre referencia y persona permanece en el sistema de RR. HH.
2. **Dependencias explícitas.** Las tareas se definen en código, con precondiciones verificables. El modelo de lenguaje no decide acceso ni modifica el grafo.
3. **Aprobación separada de ejecución.** Un permiso aprobado no prueba que la cuenta exista. El sistema registra la finalización como un paso distinto.
4. **Identidad externa.** El token autentica al cliente de la API. El campo `actor` es un identificador declarado, no una firma ni un mecanismo de autorización por usuario. La integración debe obtenerlo del proveedor de identidad, filtrar las acciones por rol e impedir suplantación.
5. **Calendario acotado.** Los plazos se expresan en días de lunes a viernes. Agregar feriados requiere una fuente de calendario y pruebas por país.
6. **Resumen sin efectos.** La redacción opcional utiliza una proyección del estado y no habilita herramientas empresariales.
7. **Recuperación con acceso previo.** El índice de políticas filtra organización y grupos antes de calcular TF-IDF. Las políticas ocultas no afectan el ranking de las visibles. El modelo sólo puede seleccionar fuentes que ya atravesaron ese filtro.
8. **Extractos como respuesta verificable.** La salida informativa conserva el texto exacto y la versión de sus fuentes. Se prioriza trazabilidad sobre paráfrasis libre; el proveedor no recibe herramientas de onboarding ni devuelve una decisión de acceso.
9. **Versiones y retención.** Un cambio retira los fragmentos activos anteriores de la política. Las respuestas persistidas por idempotencia siguen representando la evidencia original y requieren su propia política de retención. El índice no pretende ser un registro documental histórico completo.
10. **Alcance de organización explícito.** Las políticas admiten múltiples ámbitos de consulta. El flujo de expedientes permanece en una organización operadora y no se expone como un sistema multiusuario con permisos propios.
