**2026/11/21**

multipass 1.17.0+mac
git version 2.50.1 (Apple Git-155)

**0.初期設定**

Multipassのインストール
SSH鍵の作成

**1.Githubとの連携**

GithubとのSSH接続設定
cloneでローカルにGithubのリポジトリをコピーして、必要なフォルダとファイルを作成してGithubに反映

<つまづいた点>
Macのターミナルで使用するコマンドに慣れていなかったので、主要コマンドとその操作内容を一通り調べて実行した。

ターミナルのログを記録する方法
作業開始時に以下のコマンドを入力
script ~/Documents/TerminalLogs/$(date '+%Y-%m-%d_%H-%M-%S')-session.log
作業終了時にexitを入力

**2.仮想サーバーの作成**

MultipassでUbuntu 24.04 LTSの仮想マシン web01(CPU 2、メモリ 2GB、ディスク 20GB)を作成
web01の ubuntu ユーザーの ~/.ssh/authorized_keys に、Macの公開鍵を登録
初回接続時にホスト鍵を確認し、Macの known_hosts に記録した
~/.ssh/config に設定を書き、ssh web01 で接続できるようにした
apt update でパッケージ一覧を更新し、apt upgrade で入っているパッケージを最新版にした
タイムゾーンを Asia/Tokyo(日本時間)に設定した
パスワード認証を禁止して鍵認証のみにし、rootユーザーでのSSHログインを禁止した
ufwでSSH(22番/TCP)を許可してから有効化し、それ以外の外から入ってくる通信を遮断した
