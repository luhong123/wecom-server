# 企业微信回调服务器

基于 Flask + wechatpy 的企业微信消息回调服务。

## 功能

- ✅ URL 验证（企业微信配置验证）
- ✅ 消息接收与解密
- ✅ 消息回复与加密

## 服务器部署

### 1. 克隆项目

```bash
git clone https://github.com/luhong123/wecom-server.git
cd wecom-server
```

### 2. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 3. 启动服务

前台运行（调试用）：
```bash
python3 app.py
```

后台运行：
```bash
nohup python3 app.py > wechat.log 2>&1 &
```

查看日志：
```bash
tail -f wechat.log
```

停止服务：
```bash
ps aux | grep app.py
kill <进程ID>
```

### 4. 开放防火墙端口

CentOS/RHEL：
```bash
firewall-cmd --add-port=80/tcp --permanent
firewall-cmd --reload
```

Ubuntu/Debian：
```bash
ufw allow 80
```

## 企业微信配置

登录企业微信管理后台 → 应用管理 → 自建应用 → 接收消息

| 配置项 | 值 |
|--------|-----|
| URL | `http://你的公网IP/wechat` |
| Token | `sdSLE1Wn8HNJHDD83il1D` |
| EncodingAESKey | `fS8tP76fJvWfCPQyYrsQUXnqgWR15nSLfc5HqYTnzis` |

## 配置修改

编辑 `app.py` 文件顶部的配置区：

```python
# ========== 配置区 ==========
TOKEN = "你的Token"
EncodingAESKey = "你的EncodingAESKey"
CorpId = "你的企业ID"  # 可选
# ============================
```

## 项目结构

```
wecom-server/
├── app.py            # 主程序
├── requirements.txt  # Python 依赖
├── start.sh          # 启动脚本
└── README.md         # 说明文档
```

## 常见问题

### Q: 验证 URL 失败？

1. 检查服务是否启动：`curl http://localhost/wechat`
2. 检查防火墙是否开放 80 端口
3. 检查云服务商安全组是否放行 80 端口

### Q: 如何修改端口？

编辑 `app.py` 最后一行：
```python
app.run(host="0.0.0.0", port=8080, debug=False)  # 改为 8080
```

### Q: 如何开机自启？

创建 systemd 服务：
```bash
sudo nano /etc/systemd/system/wecom.service
```

内容：
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

启用：
```bash
sudo systemctl daemon-reload
sudo systemctl enable wecom
sudo systemctl start wecom
```

## License

MIT