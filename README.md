# innsowl

InnsOwl
======

knowledge site blog

This repository contains knowledge main page and blog


# 建议先参考官方站点操作方法
   https://github.com/pallets/flask/tree/master/examples/tutorial


# 部署linux docker  步骤
                pip3 freeze > test.txt                               #导出环境包列表
                forms.py                                                 #用户资料编辑表单
                views.py                                                 # 管理员资料编辑器
                python3 -m venv venv                           #配置虚拟环境
                . venv/bin/activate                                  #启动虚拟环境
                export FLASK_APP=flasky.py             # 配置App名称
                export FLASK_DEBUG=1                    # 调试模式
                pip3 install -r requirements/dev.txt        # 安装依赖包
                flask test                                                 # 基本结构自测
                flask  db   upgrade                                  # 创建db
                flask    run                                             # 应用运行
                
# Dockerfile
                FROM python:3.6-alpine

                ENV FLASK_APP InnsOwl.py
                ENV FLASK_CONFIG production

                RUN adduser -D  InnsOwl
                USER InnsOwl

                WORKDIR /home/InnsOwl

                COPY requirements requirements
                RUN python3 -m venv venv
                RUN venv/bin/pip install -r requirements/docker.txt

                COPY app app
                COPY migrations migrations
                COPY InnsOwl.py config.py boot.sh ./

                # run-time configuration
                EXPOSE 5000
                ENTRYPOINT ["./boot.sh"]

        docker build -t innsowl:latest .
        docker run --name innsowl -d -p 8089:8089 -e SECRET_KEY=88f6585a8ea1f705bfe4aae3eb45f6dc2 innsowl:latest
                9e85af2d199f9d9d3cc4814da05853304c6dbc62c902879cac8a5acbf117978e
        参考
        https://docs.docker.com/engine/reference/builder/