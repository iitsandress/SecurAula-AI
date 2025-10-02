Ética, privacidad y auditoría (EduMon)

Principios
- Consentimiento explícito: el agente no inicia sin aceptación expresa en el equipo del alumno/a.
- Transparencia: indicador visual permanente mientras dura la sesión; botón para detener en cualquier momento.
- Minimización de datos: solo CPU %, RAM %, uptime, nombre de host, usuario y un ID de dispositivo. Nada más.
- Lista blanca estricta: el agente solo realiza register, heartbeat y unregister.
- Auditoría integral: todas las interacciones (servidor y agente) se registran como eventos JSON con fecha/hora, actor, acción y detalles.
- Seguridad y acceso: la API exige X-API-Key. Limite el acceso a la red local del aula y rote claves periódicamente.
- Retención y borrado: defina políticas claras de retención (p. ej., 7–30 días) y mecanismos de borrado seguro.
- Cumplimiento normativo: adecúe el uso a la legislación local (p. ej., RGPD/LOPDGDD) y a las políticas del centro educativo.

Prácticas recomendadas
- Presentar una hoja informativa a estudiantes y familias, incluyendo finalidades, datos tratados y contacto de soporte.
- Usar nombres o identificadores de equipo en lugar de datos personales cuando sea posible.
- Revisar periódicamente los logs para detectar accesos indebidos.
- Aislar el servidor (segmentación de red) y aplicar parches/actualizaciones.
- Evitar ampliar el alcance del agente sin revaluación ética y legal.
