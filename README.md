Integrantes: Paúl Acuña - Dafne Dasso - Dámaris Villca

Finance Radar: Automatización de Finanzas Personales vía API Middleware
Este proyecto permite la captura y registro automático de movimientos financieros (ingresos y egresos) detectados a través de notificaciones de billeteras virtuales (como Mercado Pago). El sistema utiliza una arquitectura de microservicios y procesamiento de eventos para eliminar la carga manual de datos.

Arquitectura del Sistema
El sistema se basa en un flujo de datos desacoplado en tres capas:

Capa de Captura (Android): Servicio de escucha de notificaciones que actúa como disparador (Trigger) ante eventos financieros.

Capa de Transporte (Ngrok + Flask): Un túnel seguro que expone un endpoint local a internet y un middleware en Python que procesa la información.

Capa de Gestión (Firefly III): Servidor financiero autohospedado en Docker que actúa como núcleo contable y base de datos.

Requisitos Previos
Para desplegar este entorno en sus máquinas, necesitarán:

Docker Desktop: Para correr la instancia de Firefly III.

Python 3.10+: Para ejecutar el middleware de integración.

Ngrok: Para exponer el servidor local de forma segura.

Android con MacroDroid: Para la interceptación de las notificaciones reales.

Instalación y Configuración
1. Servidor Financiero (Docker)
Dentro de la carpeta del proyecto, utilicen el archivo docker-compose.yml proporcionado y ejecuten:

Bash
docker-compose up -d
Accedan a http://localhost:8080 para configurar su usuario y crear sus cuentas de activos (ej. "Mercado Pago").

2. Middleware de Integración (Python)
Instalen las dependencias necesarias:

Bash
pip install flask requests python-dotenv
Configuren el archivo .env con su Personal Access Token de Firefly III y la URL del servidor local.

3. El Túnel (Ngrok)
Inicien el túnel para que su celular pueda hablar con su PC:

Bash
ngrok http 5000
Copien la URL https generada.

Configuración del Dispositivo (Interceptor)
Para que el sistema sea 100% automático, se debe configurar una macro en MacroDroid:

Trigger: Notificación recibida de la app "Mercado Pago".

Action: Solicitud HTTP POST.

URL: [SU_URL_NGROK]/notificacion

Body (JSON): ```json
{
"titulo": "{not_title}",
"texto": "{not_text}"
}




Cómo funciona el "Cerebro" (Procesamiento)
Nuestra API realiza las siguientes tareas de ingeniería:

Sanitización: Recibe el JSON y combina título y cuerpo para evitar pérdida de datos.

Extracción por Regex: Utiliza expresiones regulares para identificar montos monetarios independientemente de su posición en la cadena.

Patrón: \$\s?([\d\.]+,\d{2}|[\d\.]+)

Lógica de Clasificación: Analiza palabras clave (Recibiste, Ingresó, Pagaste) para determinar si la transacción es un depósito o un retiro.

Inyección vía REST API: Envía una petición autenticada a Firefly III para crear el registro de forma permanente.

Pruebas y Demo
Para probar el funcionamiento sin recibir una transferencia real:

Correr firefly_bridge.py.

En MacroDroid, utilizar la opción "Probar acciones".

Verificar en la terminal de Python la extracción del monto y en la interfaz de Firefly III la creación de la transacción.

Notas de Seguridad
El sistema utiliza Personal Access Tokens (PAT) para la autenticación Bearer, asegurando que solo el middleware autorizado pueda escribir en la base de datos financiera.

Se recomienda el uso de un dominio estático en Ngrok para estabilidad en producciones de larga duración.

TP TECNOLOGÍAS EMERGENTES
