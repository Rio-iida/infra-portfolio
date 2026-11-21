# Phase 1: Linuxサーバーの作成と初期設定

## 概要

| 項目 | 内容 |
| --- | --- |
| 作業日 | [2026-11-21] |
| 作業端末 | Apple Silicon Mac(macOS [26.6.2（25G83])、Multipass [1.17.0+mac] |
| 作成したサーバー | web01(Ubuntu 24.04 LTS、CPU 2、メモリ 2GB、ディスク 20GB) |
| 結果 | Macから鍵認証でSSHログインでき、パスワード認証とrootログインを禁止し、ファイアウォールでSSH以外の外からの通信を遮断した |

## やったこと

1. MultipassでUbuntu 24.04 LTSの仮想マシン web01 を作成した
2. web01にMacの公開鍵を登録し、秘密鍵でSSHログインできるようにした
3. 初回接続時にホスト鍵を確認し、`~/.ssh/config` で `ssh web01` で接続できるようにした
4. `apt update` と `apt upgrade` で、パッケージを最新版にした
5. タイムゾーンを Asia/Tokyo に設定した
6. パスワード認証を禁止して鍵認証のみにし、rootユーザーでのSSHログインを禁止した
7. ufwでSSH(22番/TCP)を許可してから有効化し、それ以外の外から入ってくる通信を遮断した

## 手順

### 1. 仮想マシンの作成

    multipass launch 24.04 --name web01 --cpus 2 --memory 2G --disk 20G
    multipass list
    multipass info web01

- 実行結果は `Launched: web01 in zone1`。zone1 は、MultipassがクラウドのアベイラビリティゾーンをまねたJ区画(zone1〜zone3)の名前で、指定しなければ自動で割り当てられる。
- 仮想マシンは、Macの中の専用ネットワークからIPアドレスをもらう。Macからは届くが、Macの外(同じWi-FiのiPhoneなど)からは届かない。

### 2. 公開鍵の登録

    pbcopy < ~/.ssh/id_ed25519.pub   # Mac: 公開鍵をコピー
    multipass shell web01            # Mac: 仮想マシンに入る
    nano ~/.ssh/authorized_keys      # web01: 最終行に公開鍵を貼り付けて保存

- `authorized_keys` は「このユーザーにログインしてよい公開鍵の一覧」。
- 既存の行は、Multipassが自分用に使っている鍵なので消さない。
- 秘密鍵(`~/.ssh/id_ed25519`)はMacから出さない。

### 3. SSHログインと接続設定

    ssh ubuntu@<web01のIP>

- 初回は、サーバーのホスト鍵の指紋(fingerprint)が表示され、信用するかを聞かれる。
- web01の中で `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` を実行して指紋が一致することを確かめてから、`yes` と答えた。
- 信用したホスト鍵は、Macの `~/.ssh/known_hosts` に記録され、2回目以降は自動で照合される。

Macの `~/.ssh/config` に次を追加し、`chmod 600 ~/.ssh/config` で自分だけが読み書きできる権限にした。

    Host web01
        HostName <web01のIP>
        User ubuntu
        IdentityFile ~/.ssh/id_ed25519

| 設定 | 意味 |
| --- | --- |
| `Host` | 接続先の呼び名。`ssh web01` で使われる |
| `HostName` | 実際の接続先(IPアドレス) |
| `User` | ログインするユーザー名 |
| `IdentityFile` | 使う秘密鍵の場所 |

- `ssh -G web01` で、設定がどう解釈されるかを確認した。
- この名前は `scp` でも使える。

### 4. パッケージの更新とタイムゾーン

    sudo apt update
    sudo apt upgrade -y
    sudo timedatectl set-timezone Asia/Tokyo
    timedatectl

- `apt update` は、配布元からパッケージの一覧を取ってくるだけで、ソフトは入れ替えない。
- `apt upgrade` は、入っているパッケージを一覧上の最新版に入れ替える。依存のために新しいパッケージを入れることはあるが、削除はしない。
- `/var/run/reboot-required` があれば再起動が必要。

### 5. SSHの設定強化

`/etc/ssh/sshd_config.d/00-hardening.conf`:

    # rootでのSSHログインを禁止する
    PermitRootLogin no
    # パスワード認証を禁止し、鍵認証だけにする
    PasswordAuthentication no

    sudo sshd -t
    sudo systemctl restart ssh
    sudo sshd -T | grep -E '^(permitrootlogin|passwordauthentication) '

- `sshd_config.d` の設定は名前順に読まれ、同じ項目は最初に読んだ値が使われる。`00-` で始めて、ほかの設定より先に読ませた。
- 反映後は、今のログインを切らずに、別のターミナルから新しくログインできることを確かめた。

### 6. ファイアウォール(ufw)

    sudo ufw allow OpenSSH
    sudo ufw enable
    sudo ufw status verbose

- `OpenSSH` は、ufwの設定名で、中身は 22/tcp の許可。
- ufwの初期設定は、外から入ってくる通信を `DROP`(捨てる)、外へ出ていく通信を `ACCEPT`(通す)。有効にしたことで、SSH以外の外からの通信がすべて遮断された。
- 必ずSSHを許可してから有効化する。

## 動作確認

| 確認内容 | 方法 | 結果 |
| --- | --- | --- |
| 鍵認証でのログイン | `ssh web01` | パスワードを聞かれずにログインできた |
| SSHの設定 | `sudo sshd -T` | `permitrootlogin no`、`passwordauthentication no` |
| タイムゾーン | `timedatectl` | `Asia/Tokyo` |
| ファイアウォール | `sudo ufw status verbose` | 有効。22/tcp のみ許可 |

## 理解チェック

**`apt update` と `apt upgrade` の違いは何か**
`update` は、配布元からパッケージの一覧を取ってくるだけ。`upgrade` は、その一覧をもとに、入っているパッケージを最新版に入れ替える。一覧が古いままだと最新版を見つけられないので、`update` → `upgrade` の順に実行する。

**パスワード認証を禁止すると、どんな攻撃を防げるか**
総当たり攻撃、よく使われるパスワードを試す辞書攻撃、他のサービスから漏れたパスワードの使い回しなど、パスワードを当てて侵入する攻撃を防げる。ログインには秘密鍵が必須になり、秘密鍵はMacから出ずネットワークにも流れないため、パスワードをいくら試しても侵入できない。rootログインの禁止は、どのLinuxにもある「root」という名前を狙われることと、侵入時にいきなり最高権限を取られることを防ぐ。

**ufwで、SSHの許可より先に有効化すると何が起きるか**
初期設定で外から入る通信は捨てられるため、新しいSSH接続がすべて拒否される。確立済みの通信は通すルールがあるので、今のログインは残るが、ログアウトすると入れなくなる。`multipass shell` も内部でSSHを使うため、同様に入れなくなる。その場合は仮想マシンを作り直す。

**`sshd -t` を再起動の前に実行するのはなぜか**
`sshd -t` は、SSHを止めずに設定ファイルの誤りだけを検査する。Ubuntuの `ssh.service` は起動前にも同じ検査を行うため、設定が壊れたまま `restart` すると、今のSSHが止まった後に新しいSSHが起動できず、新しい接続が一切できなくなる。先に検査すれば、動いている状態を壊す前に誤りに気づける。

## 学んだこと

- SSHの鍵は両方向にある。自分の鍵(公開鍵をサーバーに登録)は自分が本人であることを、サーバーのホスト鍵(known_hostsに記録)はサーバーが本物であることを証明する。
- 仮想マシンを作り直すとホスト鍵が変わり、`REMOTE HOST IDENTIFICATION HAS CHANGED!` の警告が出る。原因が自分の作り直しだと分かっている場合に限り、`ssh-keygen -R <IP>` で古い記録を消す。
- 設定変更は「検査してから反映」と「今の接続を切らずに、新しい接続で確認」を守る。
