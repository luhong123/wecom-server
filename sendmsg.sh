#!/bin/bash
# 企业微信消息发送脚本
# 使用方式: ./sendmsg.sh "消息内容"

user="@all"
corpid="ww87931xx"
corpsecret="LHlFk1GiLaz0lcLEB1R-TuQKWxxxxxxxxxxxxxxx"
agentld=1000002
msg=$1

A=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=$corpid&corpsecret=$corpsecret")
token=$(echo $A | jq -c '.access_token')
token=${token%*\"}

URL="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=$token"

for I in $user; do
    JSON="{\"touser\": \"$I\",\"msgtype\": \"text\",\"agentid\": \"$agentld\",\"text\": {\"content\": \"$msg\"},\"safe\":0 }"
    curl -d "$JSON" "$URL"
done

exit 0