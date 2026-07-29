// ========== 配置区 ==========
const TOKEN = "sdSLE1Wn8HNJHDD83il1D";
const EncodingAESKey = "fS8tP76fJvWfCPQyYrsQUXnqgWR15nSLfc5HqYTnzis";
// ============================

// AES Key: base64解码得到32字节密钥，IV取前16字节
const AES_KEY = base64ToBytes(EncodingAESKey + "=");
const IV = AES_KEY.slice(0, 16);

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === "/") {
      return new Response("企业微信回调服务运行中");
    }

    if (url.pathname === "/wechat") {
      const signature = url.searchParams.get("msg_signature") || "";
      const timestamp = url.searchParams.get("timestamp") || "";
      const nonce = url.searchParams.get("nonce") || "";
      const echostr = url.searchParams.get("echostr") || "";

      if (request.method === "GET") {
        // 验证签名: sha1(sort([token, timestamp, nonce, echostr]))
        const params = [TOKEN, timestamp, nonce, echostr].sort().join("");
        const hashBuf = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(params));
        const calcSig = bytesToHex(new Uint8Array(hashBuf));

        if (calcSig !== signature) {
          return new Response("Forbidden", { status: 403 });
        }

        // 解密 echostr 并返回明文
        if (echostr) {
          try {
            const result = await decryptEchostr(echostr);
            return new Response(result);
          } catch (e) {
            return new Response("Decrypt Error: " + e.message, { status: 500 });
          }
        }
        return new Response("ok");
      }

      // POST: 接收消息
      return new Response("success");
    }

    return new Response("Not Found", { status: 404 });
  },
};

/**
 * 解密 echostr
 * 企业微信加密格式: [16字节随机] [4字节大端长度] [消息内容] [CorpID]
 * Web Crypto 的 AES-CBC 自动处理 PKCS7 去补位
 */
async function decryptEchostr(echostr) {
  const key = await crypto.subtle.importKey(
    "raw", AES_KEY, { name: "AES-CBC" }, false, ["decrypt"]
  );
  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-CBC", iv: IV }, key, base64ToBytes(echostr)
  );
  const view = new DataView(decrypted);
  const msgLen = view.getUint32(16, false); // big-endian
  const msgBytes = new Uint8Array(decrypted, 20, msgLen);
  return new TextDecoder().decode(msgBytes);
}

function base64ToBytes(str) {
  const bin = atob(str);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

function bytesToHex(bytes) {
  return [...bytes].map((b) => b.toString(16).padStart(2, "0")).join("");
}
