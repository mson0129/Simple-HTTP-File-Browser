# Simple HTTP File Browser

[English](README.md) | [한국어](README.ko.md) | Español | [日本語](README.ja.md)

Un explorador de archivos web en un único archivo, sin dependencias externas y creado completamente con la biblioteca estándar de Python. Ofrece una SPA adaptable inspirada en Synology File Station para explorar y administrar archivos.

## Funciones

- Exploración de carpetas, búsqueda y ordenación por nombre, tamaño o fecha de modificación
- Expandir, contraer y navegar por las carpetas mediante el árbol de la barra lateral
- Descarga de archivos
- Carga múltiple mediante selector de archivos o arrastrar y soltar
- Creación de carpetas, cambio de nombre y eliminación recursiva
- Modo de solo lectura de forma predeterminada
- Opciones de línea de comandos y configuración JSON
- Protección contra recorridos de ruta y escapes mediante enlaces simbólicos
- Interfaz adaptable para escritorio y dispositivos móviles
- Selección automática del idioma según las preferencias del navegador: inglés, español, japonés y coreano; los demás idiomas usan inglés

## Requisitos

- Python 3.9 o posterior
- No requiere paquetes de terceros

## Inicio rápido

Ejecuta el siguiente comando desde la carpeta del proyecto:

```bash
python3 simple_http_file_browser.py --root /ruta/a/archivos
```

Abre esta dirección en el navegador:

```text
http://localhost:8000
```

De forma predeterminada, el servidor escucha en todas las interfaces de red (`0.0.0.0`) y funciona en modo de solo lectura.

### Activar operaciones de escritura

Usa `--upload` para permitir cargas, creación de carpetas, cambios de nombre y eliminaciones:

```bash
python3 simple_http_file_browser.py \
  --root /ruta/a/archivos \
  --port 8080 \
  --upload
```

### Acceso desde otro dispositivo

```bash
python3 simple_http_file_browser.py \
  --port 8080 \
  --root /ruta/a/archivos
```

Después, abre `http://IP_DEL_SERVIDOR:8080` desde el otro dispositivo.

## Opciones de CLI

```text
--config PATH  Archivo de configuración JSON (predeterminado: config.json)
--host HOST    Dirección de escucha (predeterminada: 0.0.0.0)
--port PORT    Puerto del servidor (predeterminado: 8000)
--root PATH    Carpeta superior accesible (predeterminada: carpeta actual)
--upload       Activar cargas y administración de archivos
--read-only    Desactivar operaciones de escritura
--version      Mostrar la versión
```

La prioridad de configuración es: opciones de CLI, archivo JSON y valores predeterminados.

## Configuración JSON

```bash
cp config.example.json config.json
python3 simple_http_file_browser.py
```

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "root": ".",
  "upload": false,
  "title": "My File Station",
  "show_hidden": false,
  "max_upload_mb": 512,
  "overwrite": false
}
```

| Opción | Descripción |
|---|---|
| `host` | Dirección en la que escucha el servidor |
| `port` | Puerto del servidor |
| `root` | Carpeta superior accesible desde el navegador |
| `upload` | Activa o desactiva las operaciones de escritura |
| `title` | Título de la interfaz web |
| `show_hidden` | Muestra nombres que comienzan por `.` |
| `max_upload_mb` | Tamaño máximo por solicitud, en MB |
| `overwrite` | Reemplaza archivos existentes con el mismo nombre |

Para usar otro archivo: `python3 simple_http_file_browser.py --config /ruta/a/config.json`.

## Eliminación

- Los archivos se eliminan inmediatamente.
- Al eliminar una carpeta también se eliminan recursivamente sus archivos y subcarpetas.
- Los enlaces simbólicos se eliminan sin seguir sus destinos.
- No existe papelera ni función de recuperación.

## Seguridad

El servidor no incluye autenticación de usuarios ni HTTPS. La dirección predeterminada `0.0.0.0` publica el servidor en todas las interfaces de red disponibles, por lo que debe utilizarse solo en redes de confianza. Para limitar el acceso al mismo equipo, usa `--host 127.0.0.1`. Activa las operaciones de escritura solo cuando sean necesarias. Para publicarlo en internet, colócalo detrás de un proxy inverso con autenticación y TLS. Limita `root` a la carpeta estrictamente necesaria.

## Detener el servidor

Pulsa `Ctrl+C` en el terminal donde se ejecuta.

