# -*- coding: utf-8 -*-
"""
企业微信回调服务器
"""
import os
from flask import Flask, request, abort
from wechatpy.work.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.work.exceptions import InvalidCorpIdException
from wechatpy.work import parse_message, create_reply

# ========== 配置区 ==========
TOKEN = "sdSLE1Wn8HNJHDD83il1D"
EncodingAESKey = "fS8tP76fJvWfCPQyYrsQUXnqgWR15nSLfc5HqYTnzis"
CorpId = ""  # 填入你的企业ID（可选，消息解密验证用）
# ============================

app = Flask(__name__)


@app.route("/")
def index():
    return "企业微信回调服务运行中"


@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    """企业微信回调接口"""
    signature = request.args.get("msg_signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")

    crypto = WeChatCrypto(TOKEN, EncodingAESKey, CorpId)

    # GET: 验证URL
    if request.method == "GET":
        echo_str = request.args.get("echostr", "")
        try:
            echo_str = crypto.check_signature(signature, timestamp, nonce, echo_str)
        except InvalidSignatureException:
            abort(403)
        return echo_str

    # POST: 接收消息
    try:
        msg = crypto.decrypt_message(request.data, signature, timestamp, nonce)
    except (InvalidSignatureException, InvalidCorpIdException):
        abort(403)

    msg = parse_message(msg)

    # 处理消息
    if msg.type == "text":
        reply = create_reply(f"收到：{msg.content}", msg).render()
    else:
        reply = create_reply("暂只支持文本消息", msg).render()

    res = crypto.encrypt_message(reply, nonce, timestamp)
    return res


if __name__ == "__main__":
    # 监听所有网卡，端口80
    app.run(host="0.0.0.0", port=80, debug=False)