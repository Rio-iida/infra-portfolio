2026/11/21

multipass launch 24.04 --name web01 --cpus 2 --memory 2G --disk 20G
仮想マシンを右の設定内容で作成する(名前はweb01)
multipass list
仮想マシンのリストとステータスを確認する
multipass shell web01
ターミナルから作成したweb01という仮想マシンに入る(Multipassの機能)
nano ~/.ssh/authorized_keys  
この仮想マシンにログインできる公開鍵の一覧情報を編集して、自分の作成したSSHの公開鍵を載せる
※この設定以降はweb01のIPアドレスでSSHログインが可能になる

sudo ufw status verbose
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp (OpenSSH)           ALLOW IN    Anywhere                  
22/tcp (OpenSSH (v6))      ALLOW IN    Anywhere (v6)          
