#!/bin/bash
# 启动供应商付款查询系统
cd /home/ubuntu/supplier-payment-query
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy
fuser -k 15723/tcp 2>/dev/null
nohup /usr/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 15723 > /tmp/payment-query.log 2>&1 &
echo "✅ 项目已启动 (PID: $!)"
echo "   访问地址: http://0.0.0.0:15723"
echo "   日志文件: /tmp/payment-query.log"
