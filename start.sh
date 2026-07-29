#!/bin/bash
# 启动脚本

# 安装依赖
pip3 install -r requirements.txt

# 启动服务（后台运行）
nohup python3 app.py > wechat.log 2>&1 &

echo "服务已启动，查看日志: tail -f wechat.log"