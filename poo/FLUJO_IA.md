Como vi que me estaba quedando sin tiempo decidi mandarle a Gemini toda la Seccion 2A con su respectivo contexto. Ya despues revise que haya respondido bien a todos los requisitos y que todo estuviera correcto. La seccion de Decisiones si la conteste yo. 

Prompt:

Estoy haciendo una entrevista tecnica donde la primera parte era hacer unos ejercicios de logica, entre estos hay una funcion que se llama calcular_dv que se puede reutilizar para crear la siguiente aplicacion en Python:

Una empresa stá construyendo para un cliente un sistema de gestión comercial (CRM). Usted debe
implementar el modelo de dominio en memoria: clases, reglas de negocio y un servicio de
consulta. Se evaluará especialmente el uso correcto de encapsulamiento, herencia,
polimorfismo, abstracción, composición y el manejo de errores de negocio. Puede usar IA como
apoyo para generar código (ver política).

R1. Clientes
• Todo cliente tiene id, nombre (obligatorio), email (formato válido básico) y fecha de creación. No
debe ser posible crear un “cliente genérico”: solo existen dos tipos concretos.
• Persona natural: tiene número de documento (solo dígitos).
• Empresa: tiene NIT (calcule y valide el DV — puede reutilizar el ejercicio 1.1; si el NIT se recibe
con DV y este no coincide, es un error) y una lista de contactos (nombre, cargo, email). Una
empresa tiene como máximo un contacto principal. La lista de contactos no debe poder
modificarse desde fuera de la clase sin pasar por sus métodos.
• Todo cliente responde identificacion(): "CC 1144123456" para persona natural y "NIT
900373913-4" para empresa.

R2. Oportunidades de venta
Una oportunidad tiene id, cliente, asesor, título, valor estimado (debe ser > 0), fecha de creación y
etapa. Cada etapa tiene una probabilidad de cierre:

Prospecto Calificada Propuesta Negociación Ganada Perdida
10 % 25 % 50 % 75 % 100 % 0 %

• Toda oportunidad nueva inicia en Prospecto.
• avanzar(): pasa solo a la siguiente etapa: Prospecto → Calificada → Propuesta → Negociación.
Desde Negociación no se puede “avanzar”, solo ganar o perder.
• ganar(): solo desde Negociación y solo si la oportunidad tiene una cotización en estado
Aceptada. Al ganar, el valor de la oportunidad pasa a ser el valor antes de IVA de esa
cotización.
• perder(motivo): desde cualquier etapa abierta; el motivo es obligatorio (no vacío).
• Una oportunidad cerrada (Ganada o Perdida) no admite cambios de etapa, ni nuevas
actividades, ni nuevas cotizaciones.
• Cada cambio de etapa queda en un historial (etapa anterior, etapa nueva, fecha y hora) que se
puede consultar pero no alterar desde fuera.
• Toda operación inválida debe producir un error de dominio propio (por ejemplo
TransicionInvalidaError) con un mensaje claro.

R3. Actividades
Sobre una oportunidad se registran actividades. Toda actividad tiene fecha, asesor y descripción, y
sabe responder resumen() (texto de una línea) y minutos_invertidos():

Tipo Datos propios Minutos invertidos
Llamada duración en minutos, si el cliente contestó la duración

Tipo Datos propios Minutos invertidos
Reunión duración, lista de asistentes (al menos uno),
presencial o virtual
duración + 30 min de desplazamiento si
es presencial
Correo asunto, enviado o recibido 5 minutos fijos

R4. Cotizaciones
• Una cotización tiene líneas (descripción, cantidad > 0, precio unitario ≥ 0) y calcula: subtotal,
descuento, base = subtotal − descuento, IVA = 19 % de la base, y total = base + IVA.
Redondee a 2 decimales.
• El descuento lo define una política de descuento intercambiable:
– Sin descuento.
– Porcentual: un porcentaje mayor que 0 y hasta 15 %; un valor fuera de ese rango es un error.
– Por volumen: 8 % si el subtotal es ≥ $50.000.000; 5 % si es ≥ $20.000.000; 0 % en otro caso.
• Debe poder agregarse una nueva política en el futuro sin modificar la clase de la cotización.
• Estados: Borrador → Enviada → Aceptada o Rechazada. Las líneas y la política solo se modifican
en Borrador; no se puede enviar una cotización sin líneas.

R5. Servicio de pipeline
Una clase de servicio que agrupa oportunidades y ofrece:
• pronostico_ponderado(asesor): suma de valor × probabilidad de la etapa, solo de las
oportunidades abiertas del asesor.
• oportunidades_estancadas(dias, hoy): oportunidades abiertas cuya última actividad (o su
fecha de creación, si no tiene actividades) sea anterior a hoy − dias.
• resumen_por_etapa(): cantidad de oportunidades y valor total por cada etapa.

R6. Demostración obligatoria
Mediante pruebas unitarias (preferido) o un programa principal, ejecute el siguiente escenario y
muestre los resultados. Agregue pruebas para al menos 4 reglas que deban fallar con error de
dominio.
1. Cree la empresa Logística Andina SAS, NIT 900373913, con un contacto principal; y la persona
natural Mariana López, CC 1144123456.
2. Cree la oportunidad “Implementación CRM” para Logística Andina, asesora Laura, valor
estimado $30.000.000. Registre una llamada de 20 min (contestó) y una reunión presencial de 60
min con 3 asistentes.
3. Avance la oportunidad hasta Negociación. Cree una cotización con descuento por volumen y
las líneas: “Licencias (10 usuarios)” 10 × $1.200.000 e “Implementación” 1 × $18.000.000.
Envíela, acéptela y gane la oportunidad.
4. Muestre: identificación del cliente, subtotal, descuento, base, IVA y total de la cotización, valor
final y historial de la oportunidad, y total de minutos invertidos en sus actividades.
5. Cree la oportunidad “Soporte anual” para Mariana López (asesora Laura, $8.000.000), avánzela
a Calificada y muestre el pronóstico ponderado de Laura.
6. Demuestre que intentar perder() la oportunidad ganada produce un error de dominio