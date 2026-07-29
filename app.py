# -*- coding: utf-8 -*-
"""
企业微信回调服务器
"""
import hashlib
import base64
import struct
from flask import Flask, request, abort
from Crypto.Cipher import AES

# ========== 配置区 ==========
TOKEN = "sdSLE1Wn8HNJHDD83il1D"
EncodingAESKey = "fS8tP76fJvWfCPQyYrsQUXnqgWR15nSLfc5HqYTnzis"
# ============================

app = Flask(__name__)

# AES Key
AES_KEY = base64.b64decode(EncodingAESKey + "=")
IV = AES_KEY[:16]


def verify_signature(signature, timestamp, nonce, echostr=""):
    """验证企业微信签名

    企业微信URL验证(GET): sha1(sort(token, timestamp, nonce, echostr))
    企业微信消息回调(POST): sha1(sort(token, timestamp, nonce, encrypt))
    """
    params = [TOKEN, timestamp, nonce, echostr] if echostr else [TOKEN, timestamp, nonce]
    params.sort()
    sorted_str = "".join(params)
    calc = hashlib.sha1(sorted_str.encode()).hexdigest()
    print(f"Token: {TOKEN}")
    print(f"排序后字符串: {sorted_str}")
    print(f"签名验证: 计算={calc}, 接收={signature}")
    return calc == signature


def decrypt_echostr(echostr):
    """解密 echostr"""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, IV)
    decrypted = cipher.decrypt(base64.b64decode(echostr))
    # 去除 PKCS7 补位
    pad = decrypted[-1]
    content = decrypted[16:-pad]
    # 解析: 4字节长度 + 内容
    msg_len = struct.unpack(">I", content[:4])[0]
    return content[4:4+msg_len].decode('utf-8')


@app.route("/")
def index():
    return "企业微信回调服务运行中"


@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    """企业微信回调接口"""
    signature = request.args.get("msg_signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")

    print(f"收到请求: path={request.path}, signature={signature}, timestamp={timestamp}, nonce={nonce}")

    if request.method == "GET":
        # 验证签名（URL验证时需包含echostr）
        if not verify_signature(signature, timestamp, nonce, echostr):
            print("签名验证失败!")
            abort(403)

        # 解密并返回
        if echostr:
            try:
                result = decrypt_echostr(echostr)
                print(f"解密成功: {result}")
                return result
            except Exception as e:
                print(f"解密失败: {e}")
                abort(500)
        return "ok"

    # POST: 接收消息
    return "success"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=87, debug=True)