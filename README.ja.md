# Simple HTTP File Browser

[English](README.md) | [한국어](README.ko.md) | [Español](README.es.md) | 日本語

Python標準ライブラリだけで動作する、外部依存のない単一ファイルのWebファイルブラウザーです。Synology File StationをイメージしたレスポンシブなSPAで、ファイルを閲覧・管理できます。

## 主な機能

- フォルダーの閲覧、検索、名前・サイズ・更新日時による並べ替え
- ファイルのダウンロード
- ファイル選択またはドラッグ＆ドロップによる複数ファイルのアップロード
- フォルダー作成、名前変更、ファイルとフォルダーの再帰削除
- デフォルトは読み取り専用モード
- CLIオプションとJSON設定
- ルート外へのパストラバーサルおよびシンボリックリンクによる脱出を防止
- デスクトップとモバイルに対応したレスポンシブUI
- ブラウザー設定に応じて英語、スペイン語、日本語、韓国語を自動選択。未対応言語は英語を使用

## 動作要件

- Python 3.9以降
- サードパーティーパッケージ不要

## クイックスタート

プロジェクトフォルダーで次のコマンドを実行します。

```bash
python3 simple_http_file_browser.py --root /path/to/files
```

ブラウザーで次のURLを開きます。

```text
http://127.0.0.1:8000
```

デフォルトではローカル接続のみを受け付け、読み取り専用で動作します。

### 書き込み操作を有効にする

```bash
python3 simple_http_file_browser.py \
  --root /path/to/files \
  --port 8080 \
  --upload
```

### 別の端末からアクセスする

```bash
python3 simple_http_file_browser.py \
  --host 0.0.0.0 \
  --port 8080 \
  --root /path/to/files
```

別の端末から `http://SERVER_IP:8080` を開きます。

## CLIオプション

```text
--config PATH  JSON設定ファイル（デフォルト: config.json）
--host HOST    バインドアドレス（デフォルト: 127.0.0.1）
--port PORT    サーバーポート（デフォルト: 8000）
--root PATH    アクセス可能な最上位フォルダー（デフォルト: 現在のフォルダー）
--upload       アップロードとファイル管理を有効化
--read-only    書き込み操作を無効化
--version      バージョンを表示
```

設定の優先順位は、CLIオプション、JSON設定ファイル、プログラムのデフォルト値です。

## JSON設定

```bash
cp config.example.json config.json
python3 simple_http_file_browser.py
```

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

| 項目 | 説明 |
|---|---|
| `host` | サーバーが待ち受けるアドレス |
| `port` | サーバーポート |
| `root` | ブラウザーからアクセスできる最上位フォルダー |
| `upload` | 書き込み操作を有効にするかどうか |
| `title` | Web画面に表示するタイトル |
| `show_hidden` | `.` で始まる名前を表示するかどうか |
| `max_upload_mb` | HTTPリクエストごとの最大アップロードサイズ（MB） |
| `overwrite` | 同名の既存ファイルを上書きするかどうか |

別の設定ファイルを使う場合は `python3 simple_http_file_browser.py --config /path/to/config.json` を実行します。

## 削除動作

- ファイルは即座に削除されます。
- フォルダーを削除すると、中のファイルとサブフォルダーも再帰的に削除されます。
- シンボリックリンクはリンク先をたどらず、リンク自体だけを削除します。
- ごみ箱や復元機能はありません。

## セキュリティ

このサーバーにはユーザー認証やHTTPSは組み込まれていません。`0.0.0.0`や書き込み操作は信頼できるネットワークだけで使用してください。インターネットに公開する場合は、認証とTLSを設定したリバースプロキシの背後で実行してください。`root`には必要最小限のフォルダーを指定してください。

## サーバーの停止

実行中のターミナルで `Ctrl+C` を押します。

