# -*- coding:utf-8 -*-
import sys
sys.path.append('.')
__version__ = '0.01a'

"""
For: for Callback api and hub server
e.g: python report_server.py 38080 docker0
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import socket
import mimetypes
import datetime
import logging
import shutil
import urllib
import posixpath
from urllib import parse
import _thread as thread
import urllib
# from urllib.parse import urlsplit
import cgi
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


def _get_ipaddr(iterface=None):
    if len(sys.argv) > 2:
        iterface = sys.argv[2]
    if iterface is None:
        iterface = 'eth0'
    if os.name != 'nt':
        if os.name == 'posix':
            return "127.0.0.1"
        import fcntl
        import struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', iterface[:15]))[20:24])
        return ip
    else:
        try:
            ip = [a for a in os.popen('route print').readlines() if ' 0.0.0.0 ' in a][0].split()[-2]
        except IndexError as msg:
            ip = "127.0.0.1"
        return ip

_today = str(datetime.datetime.now())[:10]
_log_path = '../clog/'
if not os.path.exists(_log_path):
    os.mkdir(_log_path)
_log_filename = _log_path + 'report_server.log.{}'.format(_today)
if not os.path.exists(_log_filename):
    with open(_log_filename, 'w') as f:
        f.flush()


def _logger_die(logger, msg):
    logger.error(msg)
    raise AssertionError(msg)


def note_log(log_filename):
    formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)s][%(thread)d] %(message)s')

    log_autor = logging.getLogger('Helper')
    log_autor.setLevel(logging.DEBUG)
    log_autor.propagate = False

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    log_autor.addHandler(console)

    f = logging.FileHandler(filename=log_filename, mode='a')
    f.setFormatter(formatter)
    f.setLevel(logging.DEBUG)
    log_autor.addHandler(f)

    log_autor.die = lambda msg: _logger_die(log_autor, msg)

    return log_autor

ser_log = note_log(_log_filename)


class ServerViewer(BaseHTTPRequestHandler):
    buffer = 1
    log_file = open(_log_filename, 'a+', buffer)

    def log_message(self, format, *args):
        log_info = ("%s - - [%s] %s\n" %
                            (self.client_address[0],
                             self.log_date_time_string(),
                             format % args))
        if isinstance(log_info, bytes):
            log_info.decode("utf-8")
        self.log_file.write(log_info)
        sys.stderr = self.log_file
        sys.stderr.write(log_info)
        ser_log.info(log_info)

    def _set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

    def translate_path(self, path):
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        # test evn

        return path

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()

        # displaypath = cgi.escape(urllib.parse.unquote(self.path))  # old for python2
        displaypath = cgi.html.escape(urllib.parse.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.parse.quote(linkname), cgi.html.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        try:
            self.send_response(200)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def do_GET(self):
        """Serve a GET request."""
        # client_info = self.rfile.read()
        # print "client_info:", client_info
        f = self.send_head()

        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()

        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        try:
            data = json.loads(self.data_string)
        except:
            ser_log.info("I have get string not json format:{}\n".format(self.data_string))
            data = self.data_string

        ser_log.info("in post method: body {}\n".format(data))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.data_string)
        """form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     }
        )
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %sn ' % str(self.client_address) )
        self.wfile.write('User-agent: %sn' % str(self.headers['user-agent']))
        self.wfile.write('Path: %sn'%self.path)
        self.wfile.write('Form data:n')
        for field in form.keys():
            field_item = form[field]
            filename = field_item.filename
            filevalue  = field_item.value
            filesize = len(filevalue)#文件大小(字节)
            #print len(filevalue)
	    #print (filename)
            with open(filename.decode('utf-8'),'wb') as f:
                f.write(filevalue)
"""
        return

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

curr_dir = os.path.dirname(os.path.realpath(__file__))
report_dir = curr_dir + os.sep + '../../'


def start_report_ser(port=28080):
    from http import server
    os.chdir(report_dir)
    sys.argv.append(port)
    server.test(port=port)


def disRst(isAlive, isDaemon):
    print()
    print('if service running:  %s,' % isAlive)
    print('\n')
    print('if service had ended:  %s,' % isDaemon)
    print('\n')


def run(server_class=HTTPServer, handler_class=ServerViewer, port=8088):
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    server_address = ('', port)
    # os.chdir(report_dir)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd listen 0.0.0.0 on port {}...'.format(port))
    print ("server ip address: {}".format(_get_ipaddr()))
    httpd.serve_forever()

exitFlag = 0
import threading
# import thread


class ModThread(threading.Thread):
    def __init__(self, threadID, name, counter, func):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.func = func

    def run(self):
        self.func()

if __name__ == "__main__":

    # use_age: python report_server.py 38080 docker0
    print("use_age: 'python ViewerServers.py docker0', get argv:{}".format(sys.argv))
    print("report_dir:{}".format(report_dir))
    pidthreads, threads = [], []
    rstdic = {}


    start_report_ser(8088)

    '''
    thread.start_new_thread(start_report_ser(28080), args=('thread_ser_0'))
    th0 = ModThread(1, "to1", 1, start_report_ser(28080))

    # t0 = threading.Thread(start_report_ser(28081), args=('thread_ser_0'))
    # threads.append(t0)
    if len(sys.argv) > 2:
        # t1 = threading.Thread(run(port=int(sys.argv[1])), args=('thread_ser_1'))
        th1 = ModThread(2, "to2", 2, run(port=int(sys.argv[1])))
        # threads.append(t1)
    else:
        # t1 = threading.Thread(run(), args=('thread_ser_1'))
        # threading._start_new_thread(run(), args=('thread_ser_1'))
        # threads.append(t1)
        th1 = ModThread(2, "to2", 2, run(port=28080))
    # start service
    th0.start()
    # th1.start()
    '''

