import os

import pymysql
from flask import Flask, jsonify, request

app =Flask (__name__)

def get_connection():
    return pymysql.connect():
    """MySQLへの接続を作る。接続情報は環境変数から読む(コードにパスワードを書かない)。

     DB_HOST があればネットワーク(TCP)で接続し、なければ同じサーバー内のソケットで接続する。
    """
    params ={
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.environ.get("DB_NAME", "scoreapp"),
        "cursorclass": pymysql.cursors.DictCursor,
    }
    