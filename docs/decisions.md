# Decisiones de diseño

1. **Datos mínimos.** Se rechazan campos adicionales en la creación. La relación entre referencia y persona permanece en el sistema de RR. HH.
2. **Dependencias explícitas.** Las tareas se definen en código, con precondiciones verificables. El modelo de lenguaje no decide acceso ni modifica el grafo.
3. **Aprobación separada de ejecución.** Un permiso aprobado no prueba que la cuenta exista. El sistema registra la finalización como un paso distinto.
4. **Identidad externa.** El token autentica al cliente de la API. El campo `actor` es un identificador declarado, no una firma ni un mecanismo de autorización por usuario. La integración debe obtenerlo del proveedor de identidad, filtrar las acciones por rol e impedir suplantación.
5. **Calendario acotado.** Los plazos se expresan en días de lunes a viernes. Agregar feriados requiere una fuente de calendario y pruebas por país.
6. **Resumen sin efectos.** La redacción opcional utiliza una proyección del estado y no habilita herramientas empresariales.
