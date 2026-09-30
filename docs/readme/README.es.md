# Simple HTTP File Browser

[English](../../README.md) | [한국어](README.ko.md) | Español | [日本語](README.ja.md)

Con escritura habilitada, arrastra una fila de archivo o carpeta a una carpeta de la lista o del árbol lateral para moverla. Los clics en nombres conservan su comportamiento. No se pueden mover contenidos de archivos comprimidos ni sobrescribir elementos existentes.

Un explorador de archivos web en un único archivo, sin dependencias externas y creado completamente con la biblioteca estándar de Python. Ofrece una SPA adaptable inspirada en Synology File Station para explorar y administrar archivos.

## Funciones

- Exploración de carpetas con navegación Atrás del navegador, búsqueda y ordenación por nombre, tamaño o fecha de modificación
- Expandir, contraer y navegar por las carpetas mediante el árbol de la barra lateral
- Explorar archivos ZIP y TAR como carpetas de solo lectura, sin extraerlos al disco
- Descargar carpetas como ZIP sin compresión (`ZIP_STORED`) en streaming, incluyendo subcarpetas y carpetas vacías
- Vista previa de imágenes, audio y vídeo compatibles con el navegador, texto sin formato y Markdown con enlaces y tablas; descarga de cualquier archivo
- Búsqueda dentro de audio y vídeo mediante rangos de bytes HTTP y aviso claro si falla la reproducción
- Carga múltiple mediante selector de archivos o arrastrar y soltar
- Progreso individual por archivo con tamaño transferido y estado de finalización
- Carga en streaming al disco sin almacenar archivos completos en memoria
- Creación de carpetas, cambio de nombre y eliminación recursiva
- Modo de solo lectura de forma predeterminada
- Opciones de línea de comandos y configuración JSON
- Protección contra recorridos de ruta y escapes mediante enlaces simbólicos
- Interfaz adaptable para escritorio y dispositivos móviles
- Selección automática del idioma según las preferencias del navegador: inglés, español, japonés y coreano; los demás idiomas usan inglés

## Exploración de archivos comprimidos

Haz clic en el nombre para explorar un archivo comprimido o usa Descargar para obtener el archivo original. Formatos compatibles: `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz`, `.tbz2`, `.tar.xz` y `.txz`.

Los contenidos permiten descargas, vistas previas, navegación por el árbol y el historial del navegador. Siempre son de solo lectura, incluso si las cargas están habilitadas: no se pueden subir, renombrar, eliminar ni editar archivos dentro del archivo comprimido.

El botón Descargar de una carpeta crea un ZIP sin compresión, también para carpetas dentro de un archivo comprimido. Los datos se envían directamente al navegador sin crear un ZIP temporal. Las entradas ocultas respetan `show_hidden` y se omiten los enlaces simbólicos del sistema de archivos.

No se pueden abrir miembros ZIP cifrados. Se excluyen rutas inseguras y enlaces. Los archivos comprimidos anidados se pueden descargar, pero no explorar como carpetas adicionales. Los archivos grandes pueden tardar más en explorarse o buscarse; los métodos de compresión disponibles dependen de Python. RAR y 7z no son compatibles.

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
