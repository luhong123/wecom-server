# -*- coding: utf-8 -*-
"""
企业微信回调服务器
"""
import os
import hashlib
import base64
import struct
from flask import Flask, request, abort
from Crypto.Cipher import AES

# ========== 配置区 ==========
TOKEN = "sdSLE1Wn8HNJHDD83il1D"
EncodingAESKey = "fS8tP76fJvWfCPQyYrsQUXnqgWR15nSLfc5HqYTnzis"
CorpId = ""  # 企业ID（可选）
# ============================

app = Flask(__name__)


class WeComCrypto:
    """企业微信加解密"""

    def __init__(self, token, encoding_aes_key, corp_id=""):
        self.token = token
        self.corp_id = corp_id
        # AES Key: base64解码，补齐 '='
        aes_key = encoding_aes_key + "=" if len(encoding_aes_key) % 4 else encoding_aes_key
        self.key = base64.b64decode(aes_key)
        self.iv = self.key[:16]

    def verify_signature(self, signature, timestamp, nonce):
        """验证签名"""
        params = [self.token, timestamp, nonce]
        params.sort()
        sha1 = hashlib.sha1("".join(params).encode()).hexdigest()
        return sha1 == signature

    def decrypt(self, echostr):
        """解密 echostr"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted = cipher.decrypt(base64.b64decode(echostr))
        # 去除 PKCS7 补位
        pad = decrypted[-1]
        content = decrypted[16:-pad]
        # 解析: 4字节长度 + 内容 + corp_id
        msg_len = struct.unpack(">I", content[:4])[0]
        msg = content[4:4+msg_len].decode('utf-8')
        return msg


crypto = WeComCrypto(TOKEN, EncodingAESKey, CorpId)


@app.route("/")
def index():
    return "企业微信回调服务运行中"


@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    """企业微信回调接口"""
    signature = request.args.get("msg_signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")

    # GET: 验证URL
    if request.method == "GET":
        if not crypto.verify_signature(signature, timestamp, nonce):
            abort(403)

        echo_str = request.args.get("echostr", "")
        if echo_str:
            try:
                return crypto.decrypt(echo_str)
            except Exception as e:
                print(f"解密失败: {e}")
                abort(500)
        return "ok"

    # POST: 接收消息（暂不处理）
    return "success"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)