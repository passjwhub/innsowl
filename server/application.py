# -*- coding:utf-8 -*-
import sys
import subprocess
import threading
import time
import datetime
import os
import re
# import commands
import subprocess
import json
from server.gene_temp import Generater, generate_execute, generate_complete
from server.service_log import ServiceLog


dataUrl = "../"
_date = str(datetime.datetime.now())[:10]
print('dataUrl', dataUrl)
reporturl = dataUrl + '/report'
tmpPath = "../"
service_ip = "127.0.0.1"
user_email = "test_analysis.txt@foxmail.com"
g_logger = ServiceLog("service_app").logger_writer(_date)
backCase = ['testKill', 'testStop', 'testInternetError', 'testRestart']

runCase = ['Get.GetTest', 'PostTest.PostTest']
python_version = 'python'
# (status, ip) = commands.getstatusoutput('hostname -i')
p0 = subprocess.Popen("hostname -i", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
(ip, status) = p0.communicate()
# sys.exc_traceback



def check_ip(str):
    Rst = 'True'
    cheIP = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    if not re.findall(cheIP, str):
        Rst = 'False'
    else:
        IPs = list(str.split('.'))
        # g_logger.info( 'IPs is ', IPs, len(IPs)
        for i in range(len(IPs)):
            try:
                if int(IPs[i]) > 255:
                    g_logger.info('bigger than 255 %s' % IPs[i])
                    Rst = 'False'
                else:
                    pass
            except ValueError as Emsg:
                g_logger.info(Emsg)
    return Rst, str


if 'True' not in check_ip(ip):
    run_host = '127.0.0.1'
else:
    run_host = ip


def exec_fo(threadname, rstlis, case=None):
    print("enter exec_cmd :%s" % threadname)
    if case in backCase:
        print("will exec failover case %s " % case)
        cmd = '%s -m unittest failover.FailoverTest.FailoverTest.%s &' % (python_version, case)
    else:
        print("will exec all fo_case")
        cmd = '%s -m  failover.testFO_suite &'% (python_version)

    pid = ''
    logFile = tmpPath + os.sep + 'foTmp.txt'
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=open(logFile, 'w'), stderr=subprocess.PIPE)
        (stderrS, out) = p.communicate()

        print('stderr', stderrS)
        if stderrS:
            rstlis.append('stderr:' + stderrS)
        else:
            print('call rest pid:', p.pid)
            pid = p.pid
            rstlis.append(pid)
            print('rstlis', rstlis)
    except OSError as msg:
        print("OSError,msg: %s" % msg)
        raise(AssertionError(msg))
    return pid


def exec_run(threadname, rstlis, case=None):
    print("enter exec_cmd  :%s" % threadname)
    if case in runCase:
        print("will exec runCase %s" % case)
        cmd = '%s -m unittest runner.%s &' % (python_version, case)
    else:
        cmd = '%s  -m  runner.run_suite &' % (python_version)
    x = 0
    pid = ''

    print(time.time())
    fileName = 'runTmp' + '.txt'
    runFile = tmpPath + os.sep + fileName
    print('runfile: ', runFile)
    p = subprocess.Popen(cmd, shell=True, stdout=open(runFile, 'w'), stderr=subprocess.PIPE)
    (stderrS, out) = p.communicate()

    print('stderr', stderrS)
    if stderrS:
        rstlis.append('stderr:' + stderrS)
    else:
        x += 1
        print('call rest pid:', p.pid)
        pid = p.pid
        rstlis.append(pid)
        print('rstlis', rstlis)
    return pid


def disRst(isAlive, isDaemon):
    print()
    print('是否运行中:  %s,' % isAlive)
    print('\n')
    print('是否被动结束:  %s,' % isDaemon)
    print('\n')


def choose(path):
    if path:
        if 'run' in path:
            return runCase[0]
        else:
            return backCase[0]
    else:
        return 'NoPath'


def report_url(url):
    get_url = '<div><a href="%s" target="_blank">%s</a></div>' % (url, url)
    return get_url


def application(environ, start_fn):
    start_fn('200 ok', [('Conten-type', 'text/plain')])
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    if path == '/cfavicon.ico':
        return ['cfavicon.ico'.encode('utf-8')]

    case = environ.get('QUERY_STRING')
    print('case', case)
    print('path info', path, method)
    g_logger.info('environ:{}, path info:{}, method:{}'.format(environ, path, method))
    if method == 'POST':
        g_logger.info('environ:{}'.format(environ))

    resp, threads, folis, runlis, pidthreads = [], [], [], [], []
    rstdic = {}

    if path == '/':
        threads = []

    if path == '/back':
        body = generate_execute({'run_host': run_host, 'case_name': 'backtest', 'user_email': user_email})
        print(body)
        return [body]
    if path == '/run':
        body = generate_execute({'run_host': run_host, 'case_name': 'runtest', 'user_email': user_email})
        print(body)
        return [body]

    if path == '/backtest':
        if case:
            t0 = threading.Thread(target=exec_fo, args=('thread_back_0', folis, case))
            g_logger.info('load fo case %s' % case)
        else:
            t0 = threading.Thread(target=exec_fo, args=('thread_back_0', folis))
            g_logger.info('load fo all case')
        threads.append(t0)
    if path == '/runtest':
        if case:
            g_logger.info('load run case %s' % case)
            t1 = threading.Thread(target=exec_run, args=('thread_run_1', runlis, case))
        else:
            t1 = threading.Thread(target=exec_run, args=('thread_run_1', runlis))
            g_logger.info('load run all case ')
        threads.append(t1)
    g_logger.info('threads:%s' % threads)
    if not threads:
        g_logger.info('not threads:%s' % threads)
        resp = str(environ['PATH_INFO'][1:])
        body = generate_execute({'run_host': run_host, 'case_name': 'runtest', 'user_email': user_email})
    else:
        err_msg = 'pid Stderr,subprocess execute error'
        for thread_obj in threads:
            thread_obj.daemon = False
            thread_obj.start()
            # p = subprocess.Popen(thread_obj.start(), shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            # (code, out) = p.communicate()
            # print 'stdin, stdout:', code, out
            obj = threading.current_thread()
            pidthreads.append(obj)
            rstdic[thread_obj.name] = (thread_obj.isAlive())
            disRst(thread_obj.isAlive(), thread_obj.isDaemon())

        for thread_obj in threads:
            thread_obj.join()
            print('thread_obj.isAlive()', thread_obj.isAlive())
            if thread_obj.isAlive():
                print('kill this thread_obj %s' % thread_obj)
                # thread_obj._Thread__stop()
                # thread_obj.()
            print("Exiting Main Thread", rstdic)
        resp.append(str(path) + ',exec status:' + ' ' + str(rstdic) + '')
        pids = []

        if folis and runlis:
            if 'stderr' in folis:
                pids = ['backlis' + err_msg, str(folis)]
            else:
                pids = ['back_pid:' + str(folis) + 'run_pid:' + str(runlis)]
        if not folis:
            if 'stderr' in runlis:
                pids = ['runlis' + err_msg, str(runlis)]
            else:
                pids = ['run_pid:' + str(runlis) + str(pidthreads)]
        if not runlis:
            if 'stderr' in folis:
                pids = ['folis' + err_msg, str(folis)]
            else:
                pids = ['fo_pid:' + str(folis) + str(pidthreads)]
        reportDiv = report_url(reporturl)
        picDiv = report_url(dataUrl + '/Ocean')
        tmpLog = report_url(reporturl + '/')
        complete_page = generate_complete(
            {'resp': resp, 'pids': pids, 'reportDiv': reportDiv, 'picDiv': picDiv, 'time_now': ('time:' + str(datetime.datetime.now())[:-7]),
             'tmpLog': tmpLog, 'run_host': run_host, 'path': path, 'ocean_ip': service_ip})
        body = complete_page
    print(resp)
    print(body)
    return [body]


def test(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    case = environ.get('QUERY_STRING')
    if environ['PATH_INFO'] == '/cfavicon.ico':
        return ["cfavicon.ico".encode('utf-8')]
    resp = environ['PATH_INFO'][1:]
    # 接收到的是字符串对象
    print(type(resp))
    print(type(json.dumps(resp)), json.dumps(resp, indent=2))
    # 转化为python对象
    dicResp = eval(resp)
    print("dicResp", type(dicResp), dicResp)
    jsonRsp = json.dumps(dicResp, indent=2)
    print(type(jsonRsp), jsonRsp)
    # jsonRsp现在是json对象
    print(type(json.loads(jsonRsp)), json.loads(jsonRsp))
    print('case', case)
    body = '<h1>Hello, %s!</h1>' % (case or 'web')
    return [body.encode('utf-8')]


if __name__ == "__main__":
    pass
