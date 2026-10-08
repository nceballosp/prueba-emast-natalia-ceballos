## Decisiones de Diseño

1. **¿Dónde usó herencia y dónde composición? ¿Por qué eligió cada una en esos casos?**
   - **Herencia:** La usé cuando las clases son de la misma familia. Por ejemplo, una PersonaNatural es un Cliente, y una Empresa es un Cliente. Comparten cosas básicas (como el nombre y el correo), pero cada uno tiene su propia forma de identificarse (cédula vs. NIT). También lo usé en las actividades, Llamada, Reunión y Correo son hijos de Actividad. 

   - **Composición:** Una oportunidad tiene cotizaciones, tiene un cliente y tiene un historial. Una Empresa tiene contactos, esto es mejor porque permite armar y desarmar el sistema fácilmente, si mañana la oportunidad necesita otra pieza nueva, se le puede agregar sin afectar cómo funciona el resto de la oportunidad.


2. **¿Cómo agregaría una política “descuento de temporada: 10 % solo en diciembre” sin modificar la clase Cotización?**
   - Gracias al Patrón Strategy, en lugar de usar código nuevo y un montón de if / else dentro de la Cotizacion para ver en qué mes estamos, la cotización simplemente tiene una ranura vacía para recibir reglas de descuento. Para agregar el descuento de diciembre, solo se tiene que crear una clase llamada DescuentoTemporada. Esta clase tiene por dentro la regla matemática de mirar el calendario y dar el 10% si es diciembre. Luego, se le aplica esta clase a la cotización que lo necesite.


3. **Si mañana cada cliente pudiera configurar sus propias etapas y probabilidades, ¿qué cambiaría en su diseño?**
   - Actualmente, las etapas están escritas manualmente dentro del código (usando un Enum), lo cual es como un semáforo fijo. Para que cada cliente tenga el suyo, cambiaria el enum y  lo pasaría a una base de datos. Crearía un mapa de ruta personalizado para cada cliente. De esta forma, cuando la oportunidad vaya a avanzar de etapa o a calcular el dinero pronosticado, ya no miraría la lista fija del sistema, sino que leería el mapa específico de su cliente para saber cuál es el siguiente paso permitido y qué probabilidad tiene.