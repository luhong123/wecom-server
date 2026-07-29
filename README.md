# 企业微信消息推送 + 回调服务

企业微信消息推送脚本 + 消息回调接收服务。

## 场景说明

```
只主动推送消息 → 不需要回调服务，只用 sendmsg.sh 即可
需要接收用户回复 → 回调地址必须一直运行
```

---

## 一、只推送消息（不需要回调）

如果只需要给用户发消息，**不需要配置回调地址**，直接用 `sendmsg.sh` 即可。

### 使用方式

```bash
bash sendmsg.sh "你好，这是一条测试消息"
```

### 脚本配置

编辑 `sendmsg.sh` 修改以下参数：

| 参数 | 说明 | 获取方式 |
|------|------|----------|
| `corpid` | 企业ID | 企业微信后台 → 我的企业 |
| `corpsecret` | 应用Secret | 应用管理 → 应用 → 查看Secret |
| `agentld` | 应用AgentId | 应用管理 → 应用 → AgentId |
| `user` | 接收成员 | `@all` 为所有人，或指定 UserID |

### 依赖

```bash
# 需要 jq 命令解析 JSON
apt install jq -y      # Ubuntu/Debian
yum install jq -y      # CentOS
```

---

## 二、需要接收用户回复（需要回调服务）

如果需要在应用里接收用户发送的消息，必须部署回调服务。

### 回调服务部署

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 启动服务（前台测试）
python3 app.py

# 3. 后台运行
nohup python3 app.py > wechat.log 2>&1 &
```

### 防火墙

```bash
# Ubuntu/Debian
ufw allow 87

# CentOS
firewall-cmd --add-port=87/tcp --permanent
firewall-cmd --reload
```

### 企业微信配置

登录后台 → 应用管理 → 自建应用 → 接收消息

| 配置项 | 值 |
|--------|-----|
| URL | `http://你的公网IP:87/wechat` |
| Token | `sdSLE1Wn8HNJHDD83il1D` |
| EncodingAESKey | `fS8tP76fJvWfCPQyYrsQUXnqgWR15nSLfc5HqYTnzis` |

> 示例：`http://10.0.1.x:87/wechat`

### 配置修改

编辑 `app.py` 顶部配置区：

```python
TOKEN = "你的Token"
EncodingAESKey = "你的EncodingAESKey"
```

---

## 项目结构

```
wecom-server/
├── app.py            # 回调服务（接收用户消息）
├── sendmsg.sh        # 消息推送脚本（主动发消息）
├── requirements.txt  # Python 依赖
└── README.md         # 说明文档
```

## 常见问题

### 验证 URL 失败？

1. 检查服务是否启动：`curl http://localhost:87/wechat`
2. 检查防火墙是否开放端口
3. 检查云服务商安全组是否放行

### 如何开机自启？

```bash
sudo nano /etc/systemd/system/wecom.service
```

```ini
[Unit]
Description=WeChat Work Callback Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/wecom-server
ExecStart=/usr/bin/python3 /root/wecom-server/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable wecom
sudo systemctl start wecom
```

## License

MIT