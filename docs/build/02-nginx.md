# Phase 2: Webサーバー(Nginx)の構築

## 概要

| 項目 | 内容 |
| --- | --- |
| 作業日 | [2026-11-21] |
| 対象 | web01(Ubuntu 24.04 LTS、Multipassの仮想マシン) |
| 導入したもの | Nginx [バージョン] |
| 結果 | Macのブラウザ(Safari)から、自作のトップページ「Score API」を表示できた |

## やったこと

1. Nginxをインストールし、起動していることを確認した
2. ufwで外からのHTTP(80番/TCP)を許可した
3. 自作のトップページ(index.html)を `/var/www/scoreapp/` に置いた
4. サイト設定ファイルを作り、Nginxの初期サイト(default)と入れ替えた
5. 設定を検査(`nginx -t`)してから読み直し(`reload`)、ブラウザとアクセスログで動作を確認した

## 手順

### 1. Nginxの導入と確認

    sudo apt install -y nginx
    systemctl status nginx       # active (running) を確認
    curl -I http://localhost     # HTTP/1.1 200 OK を確認
    sudo ufw allow 'Nginx HTTP'  # 80番/TCPを許可

- `Nginx HTTP` は、Nginxのインストール時に追加されるufwの設定名で、中身は 80/tcp の許可。
- Phase 1でufwを有効にし、SSH以外の外からの通信を遮断しているため、HTTPは明示的に許可する必要がある。

### 2. トップページを置く

    sudo mkdir -p /var/www/scoreapp
    echo '<h1>Score API</h1><p>/api/health, /api/scores</p>' | sudo tee /var/www/scoreapp/index.html

- `tee` を使うのは、`sudo echo ... > ファイル` と書くと、書き込み(`>`)がsudoの外の一般ユーザー権限で行われ、失敗するため。

### 3. サイト設定ファイル

`/etc/nginx/sites-available/scoreapp`:

    server {
        listen 80 default_server;
        server_name _;

        root /var/www/scoreapp;
        index index.html;

        location / {
            try_files $uri $uri/ =404;
        }

        access_log /var/log/nginx/scoreapp_access.log;
        error_log  /var/log/nginx/scoreapp_error.log;
    }

| 設定 | 意味 |
| --- | --- |
| `listen 80 default_server;` | 80番ポートで待ち受ける。ほかに該当するサイトがないときは、このサイトで応答する |
| `server_name _;` | どのホスト名で来ても、この設定で受け付ける(`_` は特定の名前に一致させないための慣習的な書き方) |
| `root /var/www/scoreapp;` | 公開するファイルの置き場所 |
| `index index.html;` | フォルダが指定されたとき(例: `/`)に返すファイル名 |
| `location / { ... }` | `/` で始まるすべてのリクエストに適用するルール |
| `try_files $uri $uri/ =404;` | リクエストされたファイル → 同名のフォルダの順に探し、どちらもなければ404を返す |
| `access_log` / `error_log` | このサイト専用のアクセスログとエラーログの保存先 |

### 4. 有効化と反映

    sudo ln -s /etc/nginx/sites-available/scoreapp /etc/nginx/sites-enabled/scoreapp
    sudo rm /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl reload nginx

- `sites-available` は設定の置き場所、`sites-enabled` は有効にする設定へのリンク(シンボリックリンク)の置き場所。Nginxが読み込むのは `sites-enabled` 側。
- `rm` で消したのは初期サイトへのリンクだけで、設定本体(`sites-available/default`)は残っている。
- `nginx -t` で設定の誤りを検査してから `reload` する。`reload` は接続を切らずに設定を読み直す。

## Nginxの動き

1. クライアント(ブラウザ)が、web01の80番ポートにHTTPリクエスト(`GET /`)を送る
2. Nginxが受け取り、設定ファイルのルール(`listen`、`location`)から使う設定を決める
3. `root` とURLを組み合わせて、`/var/www/scoreapp/index.html` を探す
4. ファイルがあれば、その中身をステータスコード200とともにHTTPレスポンスとして返す。なければ404を返す
5. やり取りをアクセスログに記録する

設定ファイルは「どのファイルを、どう返すか」のルールで、ページの中身(HTML)は `index.html` に入っている。

## 動作確認

| 確認内容 | 方法 | 結果 |
| --- | --- | --- |
| サーバー内からの応答 | `curl -v http://localhost/` | `HTTP/1.1 200 OK` と index.html の中身が返った |
| Macのブラウザからの表示 | Safariで `http://<web01のIP>` を開く | 「Score API」が表示された |
| アクセスの記録 | `sudo tail -3 /var/log/nginx/scoreapp_access.log` | 自分のアクセスが記録されていた |

アクセスログの読み方(例):

    <接続元IP> - - [日時] "GET / HTTP/1.1" 200 50 "-" "<ブラウザの情報>"

左から、接続元のIP、日時、リクエスト(メソッド・URL・HTTPのバージョン)、ステータスコード、返したデータのサイズ(バイト)、参照元、クライアントのソフトの情報。

## 理解チェック

**`sites-available` と `sites-enabled` を分ける利点は何か**
設定ファイルを消さずに、リンクの作成・削除だけでサイトの有効・無効を切り替えられる。設定を残したまま一時的に止めたり、元に戻したりしやすい。

**`nginx -t` をせずに `reload` して、設定が間違っていたらどうなるか**
誤りのある設定は読み込まれず、反映に失敗する。`restart` の場合は、Nginxが止まったまま起動できず、サイト全体が見られなくなるおそれがある。反映前に `nginx -t` で検査すれば、動いている状態を壊さずに誤りに気づける。

**アクセスログの1行から何が読み取れるか**
誰が(接続元IP)、いつ(日時)、何を(メソッドとURL)要求し、結果がどうだったか(ステータスコードと返したサイズ)、何を使ってアクセスしたか(クライアントの情報)。

## つまずいた点

MacのChromeから `ERR_ADDRESS_UNREACHABLE` でアクセスできなかった。サーバー側から順に切り分けた結果、サーバーは正常で、macOSのローカルネットワーク制限によるChrome側の問題と判明した。詳細は障害報告書を参照。

- [docs/incidents/[ファイル名].md](../incidents/[ファイル名].md)

以降の動作確認は、Safariとターミナルの `curl` で行う。

## スクリーンショット

- [Safariで「Score API」が表示された画面](./images/[ファイル名].png)

画像にIPアドレスが写っている場合は、隠してから載せる。
