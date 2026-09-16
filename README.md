# Simple HTTP File Browser

English | [한국어](README.ko.md) | [Español](README.es.md) | [日本語](README.ja.md)

A dependency-free, single-file web file browser built entirely with the Python standard library. It provides a responsive, Synology File Station-inspired SPA for browsing and managing files.

## Features

- Browse folders and search or sort by name, size, and modification date
- Download files
- Upload multiple files using the file picker or drag and drop
- Create folders, rename items, and recursively delete files and folders
- Read-only mode by default
- CLI options and JSON configuration
- Protection against path traversal and symbolic-link escapes outside the configured root
- Responsive interface for desktop and mobile browsers
- Automatic UI language selection based on browser preferences:
  - English: `en-US` and `en-*`
  - Spanish: `es-ES` and `es-*`
  - Japanese: `ja-JP` and `ja-*`
  - Korean: `ko-KR` and `ko-*`
  - Unsupported languages fall back to English

## Requirements

- Python 3.9 or later
- No third-party Python packages

## Quick start

Run the following command from the project directory:

```bash
python3 simple_http_file_browser.py --root /path/to/files
```

Open this address in your browser:

```text
http://127.0.0.1:8000
```

The default configuration accepts local connections only and runs in read-only mode.

### Enable write operations

Use `--upload` to allow uploads, folder creation, renaming, and deletion:

```bash
python3 simple_http_file_browser.py \
  --root /path/to/files \
  --port 8080 \
  --upload
```

### Access from another device

Bind to all network interfaces to allow connections from other devices on your LAN:

```bash
python3 simple_http_file_browser.py \
  --host 0.0.0.0 \
  --port 8080 \
  --root /path/to/files
```

Then open the server computer's IP address from the other device:

```text
http://SERVER_IP:8080
```

## CLI options

```text
--config PATH  JSON configuration file (default: config.json)
--host HOST    Bind address (default: 127.0.0.1)
--port PORT    Server port (default: 8000)
--root PATH    Top-level accessible folder (default: current directory)
--upload       Enable uploads and file-management operations
--read-only    Disable write operations
--version      Print the version
```

Display the complete help output with:

```bash
python3 simple_http_file_browser.py --help
```

Configuration precedence is:

1. CLI options
2. JSON configuration file
3. Program defaults

## JSON configuration

Copy the supplied example configuration:

```bash
cp config.example.json config.json
python3 simple_http_file_browser.py
```

Example:

```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "root": ".",
  "upload": false,
  "title": "My File Station",
  "show_hidden": false,
  "max_upload_mb": 512,
  "overwrite": false
}
```

| Option | Description |
|---|---|
| `host` | Address on which the server listens |
| `port` | Server port |
| `root` | Top-level folder accessible through the browser |
| `upload` | Whether write operations are enabled |
| `title` | Title displayed in the web interface |
| `show_hidden` | Whether names beginning with `.` are shown |
| `max_upload_mb` | Maximum upload size per HTTP request, in MB |
| `overwrite` | Whether uploads replace an existing file with the same name |

Specify a different configuration file with:

```bash
python3 simple_http_file_browser.py --config /path/to/my-config.json
```

## Deletion behavior

- Files are deleted immediately.
- Deleting a folder recursively deletes all files and subfolders inside it.
- Symbolic links inside a deleted folder are removed without following their targets.
- There is no trash or recovery feature.

## Security

This server does not include user authentication or HTTPS.

- Prefer the default `127.0.0.1` address and read-only mode.
- Use `--host 0.0.0.0` or `upload: true` only on a trusted network.
- If internet exposure is required, place the server behind a reverse proxy configured with authentication and TLS.
- Do not select a broader `root` folder than necessary.

## Stopping the server

Press `Ctrl+C` in the terminal running the server.

