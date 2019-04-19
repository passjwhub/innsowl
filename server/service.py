# -*-coding:utf-8 -*-
import sys
sys.path.append('.')

# 从wsgiref模块导入:

from wsgiref.simple_server import make_server

from server.application import application



# 创建服务器
httpde = make_server('', 12581, application)
print("exec Server powered on port 12581")


# 开始监听
httpde.serve_forever()



