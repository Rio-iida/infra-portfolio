# 03. データベースの構築(MySQL)

作業日: [2026-11-24]
対象サーバー: web01(Ubuntu 24.04 LTS / Multipass VM)

## 目的

アプリ(Phase 4で作るスコアAPI)のデータを保存するため、web01にMySQLを構築する。
アプリ専用のデータベース、ユーザー、テーブルを作り、アプリ用ユーザーには必要最小限の権限だけを与える。

## 構成

```
web01(Ubuntu 24.04)
  ├─ Nginx ……… 80/tcp で外部(Mac)から受け付ける(Phase 2)
  └─ MySQL 8.0 … 127.0.0.1:3306 と Unixソケットで、web01の中からだけ受け付ける
       ├─ ユーザー
       │    ├─ root     : auth_socket 認証(OSのroot権限を持つ場合のみログイン可)
       │    └─ scoreapp : パスワード認証、接続元は localhost のみ
       └─ データベース scoreapp
            └─ テーブル scores(scoreapp ユーザーは SELECT と INSERT のみ)
```

NginxとMySQLは、同じOSの上で動く別々のサービス。CPU・メモリ・ディスクは共有している。

## 手順

### 1. MySQLのインストールと起動確認

```bash
sudo apt install -y mysql-server
systemctl status mysql          # active (running) を確認
sudo ss -lntp | grep 3306       # 待ち受けアドレスを確認
```

| コマンド | 意味 |
| --- | --- |
| `apt install -y mysql-server` | MySQLサーバーをインストールする。`-y` で確認に自動で Yes と答える |
| `systemctl status mysql` | サービスの状態を表示する |
| `ss -lntp` | 待ち受け中(`-l`)のTCP(`-t`)ポートを、数字表記(`-n`)とプロセス名(`-p`)付きで表示する |

結果:

```
[ss の出力を貼る。例: LISTEN ... 127.0.0.1:3306 ... users:(("mysqld",...))]
```

- MySQLのバージョン: Ver 8.0.46-0ubuntu0.24.04.5 for Linux on aarch64 ((Ubuntu))
- 3306番は `127.0.0.1` だけで待ち受けており、外部からは接続できないことを確認した(設定は `/etc/mysql/mysql.conf.d/mysqld.cnf` の `bind-address`)

### 2. 管理者ユーザー(root)の認証方式の確認

```bash
sudo mysql
```

```sql
SELECT user, host, plugin FROM mysql.user WHERE user = 'root';
```

結果:

```
+------+-----------+-------------+
| user | host      | plugin      |
+------+-----------+-------------+
| root | localhost | auth_socket |
+------+-----------+-------------+
```

- `sudo mysql` では、パスワードを聞かれずにログインできた
- UbuntuのMySQLのrootは `auth_socket` 認証で、OSのroot権限で実行しているかを確かめる方式になっている
- `sudo` を付けない `mysql -u root` は拒否される

### 3. データベース・ユーザー・テーブルの作成

アプリ用のパスワードを生成し、パスワード管理アプリに保存した。

```bash
openssl rand -base64 24         # ランダムな24バイトを Base64(32文字)で表示する
```

```sql
-- アプリ用のDB(文字コードは絵文字も扱える utf8mb4)
CREATE DATABASE scoreapp CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- アプリ専用ユーザー(web01の中からの接続だけ許可)
CREATE USER 'scoreapp'@'localhost' IDENTIFIED BY '<パスワード>';

-- 読む(SELECT)と追加(INSERT)だけを許可する
GRANT SELECT, INSERT ON
