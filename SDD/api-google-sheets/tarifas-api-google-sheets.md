Límites de uso



La API de Google Sheets es un servicio compartido, por lo que aplicamos cuotas y limitaciones para proteger el rendimiento general del sistema de Google Workspace para todos los usuarios.

Límites de cuota
Si bien la API de Sheets no tiene límites de tamaño estrictos para una solicitud a la API, es posible que los usuarios experimenten límites de diferentes componentes de procesamiento que no controla Hojas de cálculo de Google. Para acelerar las solicitudes, recomendamos una carga útil máxima de 2 MB.

La API de Sheets tiene cuotas por minuto, y estas se restablecen cada minuto. Por ejemplo, hay un límite de 300 solicitudes de lectura por minuto y por proyecto. Si tu app envía 350 solicitudes en un minuto, las 50 solicitudes adicionales superan la cuota y generan una respuesta con el código de estado HTTP 429: Too many requests. Si esto sucede, debes usar un algoritmo de retirada exponencial. Después de 1 minuto, podrás volver a ejecutar solicitudes.

En la siguiente tabla, se detallan los límites de solicitudes:

Cuotas
Leer solicitudes	
Por minuto, por proyecto	300
Por minuto, por usuario y por proyecto	60
Escribir solicitudes	
Por minuto, por proyecto	300
Por minuto, por usuario y por proyecto	60
Para obtener detalles sobre los límites de archivos, consulta Archivos que se pueden guardar en Google Drive.

Comportamiento y limitaciones
Cuando trabajes con ((sheets_api_short)), ten en cuenta el siguiente comportamiento y las limitaciones que afectan tus cuotas:

Las solicitudes de lectura son llamadas a cualquier método que recupera datos de una hoja de cálculo, como get o search. Las solicitudes de escritura son llamadas a cualquier método que cambie una hoja de cálculo, como update, clear o copyTo.

Los usuarios pueden enviar varias solicitudes al mismo tiempo, siempre y cuando no superen el límite de la cuota. Cada solicitud por lotes, incluida cualquier subsolicitud, se considera como una solicitud a la API para tu límite de uso.

Todas las solicitudes de Hojas de cálculo se aplican de forma atómica. Es decir, si alguna solicitud no es válida, toda la actualización no se realizará correctamente y no se aplicará ninguno de los cambios (que podrían ser dependientes).

Existe un límite de tiempo máximo para procesar una solicitud a la API. Cuando Hojas de cálculo procesa una solicitud durante más de 180 segundos, la solicitud devuelve un error de tiempo de espera agotado.

Siempre y cuando te mantengas dentro de las cuotas por minuto, no hay límite en la cantidad de solicitudes que puedes realizar por día.

Cómo resolver errores de cuota basados en el tiempo
Para todos los errores basados en el tiempo (máximo de N solicitudes por X minutos), te recomendamos que tu código detecte la excepción y use una retirada exponencial truncada para asegurarte de que tus dispositivos no generen una carga excesiva.

La retirada exponencial es una estrategia estándar de manejo de errores para aplicaciones de red. Un algoritmo de retirada exponencial reintenta las solicitudes con tiempos de espera que aumentan de forma exponencial entre las solicitudes, hasta un tiempo de retirada máximo. Si las solicitudes siguen sin tener éxito, es importante que los retrasos entre las solicitudes aumenten con el tiempo hasta que la solicitud se realice correctamente.

Algoritmo de ejemplo
Un algoritmo de retirada exponencial vuelve a intentar las solicitudes de forma exponencial, lo que aumenta el tiempo de espera entre los reintentos hasta un tiempo de retirada máximo. Por ejemplo:

Realiza una solicitud a la API de Google Sheets.
Si la solicitud falla, espera 1 + random_number_milliseconds y vuelve a intentarla.
Si la solicitud falla, espera 2 + random_number_milliseconds segundos y vuelve a intentarla.
Si la solicitud falla, espera 4 + random_number_milliseconds y vuelve a intentarla.
Y así sucesivamente, hasta un tiempo de maximum_backoff.
Continúa con la espera y los reintentos hasta un número máximo de reintentos, pero no aumentes el período de espera entre los reintentos.
Donde:

El tiempo de espera es min(((2^n)+random_number_milliseconds), maximum_backoff), con n incrementado en 1 para cada iteración (solicitud).
random_number_milliseconds es un número aleatorio de milisegundos menor o igual que 1,000. Esto ayuda a evitar los casos en los que muchos clientes se sincronizan por alguna situación y todos realizan el reintento a la vez, lo que hace que se envíen solicitudes en oleadas sincronizadas. El valor de random_number_milliseconds se vuelve a calcular después de cada reintento de solicitud.
maximum_backoff suele ser de 32 o 64 segundos. El valor apropiado depende del caso de uso.
El cliente puede seguir reintentando después de que alcanza el tiempo maximum_backoff. Después de este punto, los reintentos no necesitan continuar con el aumento del tiempo de retirada. Por ejemplo, si un cliente usa un tiempo maximum_backoff de 64 segundos, luego de alcanzar este valor, el cliente puede volver a intentarlo cada 64 segundos. En algún momento, se debe evitar que los clientes vuelvan a intentarlo de forma ilimitada.

El tiempo de espera entre los reintentos y la cantidad de reintentos dependen del caso práctico y las condiciones de la red.

Precios