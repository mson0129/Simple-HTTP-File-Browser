# Simple HTTP File Browser

[English](README.md) | 한국어 | [Español](README.es.md) | [日本語](README.ja.md)

별도 패키지 설치 없이 Python 표준 라이브러리만으로 실행되는 단일 파일 웹 파일 브라우저입니다. Synology File Station과 비슷한 SPA 인터페이스에서 폴더를 탐색하고 파일을 관리할 수 있습니다.

## 주요 기능

- 폴더 탐색, 검색 및 이름·크기·수정일 정렬
- 사이드바의 폴더 트리에서 폴더 펼치기, 접기 및 이동
- 파일 다운로드
- 다중 파일 선택 및 드래그 앤 드롭 업로드
- 새 폴더 생성, 이름 변경 및 삭제
- 기본 읽기 전용 모드
- CLI 옵션과 JSON 설정 파일 지원
- 접근 가능 루트 밖으로의 경로 이탈 및 심볼릭 링크 접근 차단
- 모바일 화면을 지원하는 반응형 SPA
- 브라우저 언어에 따른 UI 자동 선택
  - 영어: `en-US` 및 `en-*`
  - 스페인어: `es-ES` 및 `es-*`
  - 일본어: `ja-JP` 및 `ja-*`
  - 한국어: `ko-KR` 및 `ko-*`
  - 지원하지 않는 언어는 영어로 표시

## 요구 사항

- Python 3.9 이상
- 외부 Python 패키지 불필요

## 빠른 시작

프로젝트 폴더에서 다음 명령을 실행합니다.

```bash
python3 simple_http_file_browser.py --root /path/to/files
```

브라우저에서 다음 주소를 엽니다.

```text
http://localhost:8000
```

기본 설정은 모든 네트워크 인터페이스(`0.0.0.0`)에서 수신하며 읽기 전용 모드로 실행됩니다.

### 쓰기 기능 활성화

업로드, 새 폴더 생성, 이름 변경 및 삭제를 허용하려면 `--upload`를 사용합니다.

```bash
python3 simple_http_file_browser.py \
  --root /path/to/files \
  --port 8080 \
  --upload
```

### 다른 기기에서 접속

기본 바인드 주소는 이미 LAN의 다른 기기에서도 접속할 수 있도록 설정되어 있습니다.

```bash
python3 simple_http_file_browser.py \
  --port 8080 \
  --root /path/to/files
```

그런 다음 다른 기기에서 서버 컴퓨터의 IP 주소로 접속합니다.

```text
http://SERVER_IP:8080
```

## CLI 옵션

```text
--config PATH  JSON 설정 파일 경로 (기본값: config.json)
--host HOST    바인드 주소 (기본값: 0.0.0.0)
--port PORT    실행 포트 (기본값: 8000)
--root PATH    브라우저에서 접근할 최상위 폴더 (기본값: 현재 폴더)
--upload       업로드와 파일 관리 기능 활성화
--read-only    쓰기 기능 비활성화
--version      버전 출력
```

전체 도움말은 다음과 같이 확인할 수 있습니다.

```bash
python3 simple_http_file_browser.py --help
```

설정 우선순위는 다음과 같습니다.

1. CLI 옵션
2. JSON 설정 파일
3. 프로그램 기본값

## JSON 설정

제공된 예제 파일을 복사하여 사용할 수 있습니다.

```bash
cp config.example.json config.json
python3 simple_http_file_browser.py
```

예제 설정:

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

| 항목 | 설명 |
|---|---|
| `host` | 서버가 수신할 주소 |
| `port` | 서버 포트 |
| `root` | 접근 가능한 최상위 폴더 |
| `upload` | 쓰기 기능 활성화 여부 |
| `title` | 웹 화면 상단에 표시할 제목 |
| `show_hidden` | 이름이 `.`으로 시작하는 항목 표시 여부 |
| `max_upload_mb` | 한 HTTP 요청의 최대 업로드 크기(MB) |
| `overwrite` | 같은 이름의 기존 파일 덮어쓰기 여부 |

다른 설정 파일을 사용하려면 경로를 지정합니다.

```bash
python3 simple_http_file_browser.py --config /path/to/my-config.json
```

## 파일 삭제 동작

- 파일은 즉시 삭제됩니다.
- 폴더를 삭제하면 내부의 모든 파일과 하위 폴더도 재귀적으로 삭제됩니다.
- 폴더 안의 심볼릭 링크는 링크 대상까지 따라가 삭제하지 않고 링크 자체만 삭제합니다.
- 휴지통이나 복구 기능은 제공하지 않습니다.

## 보안 주의사항

이 서버에는 사용자 인증과 HTTPS가 내장되어 있지 않습니다.

- 기본값인 `0.0.0.0`은 사용 가능한 모든 네트워크 인터페이스에 서버를 공개하므로 신뢰할 수 있는 네트워크에서만 사용하세요.
- 같은 컴퓨터에서만 접속하도록 제한하려면 `--host 127.0.0.1`로 실행하세요.
- 쓰기 권한이 필요할 때만 `upload: true` 또는 `--upload`를 사용하세요.
- 인터넷에 공개해야 한다면 인증과 TLS가 구성된 리버스 프록시 뒤에서 실행하세요.
- 접근할 필요가 없는 상위 폴더를 `root`로 지정하지 마세요.

## 종료

서버를 실행한 터미널에서 `Ctrl+C`를 누릅니다.
