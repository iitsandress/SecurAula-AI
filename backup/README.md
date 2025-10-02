# EduMon v2.0 - Sistema Educativo de Monitoreo

## Configuración con ngrok

### 1. ¿Qué es ngrok?

ngrok es una herramienta que crea un túnel seguro desde un punto final público a un servicio web que se ejecuta localmente. Esto le permite exponer su servidor local a Internet para que el agente pueda conectarse a él desde cualquier lugar.

### 2. Instalar ngrok

1.  Vaya a la [página de descargas de ngrok](https://ngrok.com/download) y descargue la versión para su sistema operativo.
2.  Descomprima el archivo descargado.
3.  (Opcional) Mueva el ejecutable de ngrok a una carpeta que esté en el PATH de su sistema para poder ejecutarlo desde cualquier lugar.

### 3. Iniciar el servidor y ngrok

1.  Inicie el servidor local ejecutando el siguiente comando en la raíz del proyecto:

    ```bash
    python server.py
    ```

2.  En otra terminal, inicie ngrok para exponer el puerto 8000:

    ```bash
    ngrok http 8000
    ```

3.  ngrok le proporcionará una URL pública (por ejemplo, `https://<random-string>.ngrok.io`). Esta es la URL que utilizará para configurar el agente.

### 4. Configurar el agente

1.  Ejecute el asistente de configuración del agente:

    ```bash
    python edumon/agent/main.py --config-wizard
    ```

2.  Cuando se le solicite la URL del servidor, introduzca la URL pública de ngrok que obtuvo en el paso anterior.
3.  Complete el resto de los pasos de configuración.

### 5. Iniciar el agente

Una vez que el agente esté configurado, puede iniciarlo ejecutando el siguiente comando:

```bash
python edumon/agent/main.py
```

El agente se conectará a su servidor local a través del túnel de ngrok.