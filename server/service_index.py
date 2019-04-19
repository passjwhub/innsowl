# -*- coding:utf-8 -*-
import sys
from builtins import len, int
sys.path.append('.')

# 从wsgiref模块导入:

from ViewerServers import run
from gene_temp import page_index, service_ip


def start_index():
    # 开启首页
    # sys.argv.append('12588')
    # print "Web Server powered on port 12588"
    # SimpleHTTPServer.test()
    print("use_age: 'python report_server.py 38080 docker0', get argv:{}".format(sys.argv))
    if len(sys.argv) > 2:
        run(port=int(sys.argv[1]))
    else:
        run(port=8088)


if __name__ == '__main__':
    user_email = ['test_analysis.txt@foxmail.com']
    page_index({'service_ip': service_ip, 'user_email': user_email[0]})
    # generate_execute({'service_ip': service_ip, 'case_name': 'runtest', 'user_email': user_email})
    # with futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     executor.submit(start_index)
    start_index()
    # 开启web 服务 8088

