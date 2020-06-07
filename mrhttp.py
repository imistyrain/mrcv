#!/usr/bin/env python
#coding=utf-8
#modifyDate: 20200529
#author:imistyrain
#add support for python3
#add support for automatelly get host ip address

"""
    简介：这是一个 python 写的轻量级的文件共享服务器（基于内置的SimpleHTTPServer模块），
    支持文件上传下载，只要你安装了python（建议版本2.6~2.7，不支持3.x），
    然后去到想要共享的目录下，执行：
        python mvhttp.py [8901]
    其中8901为你指定的端口号，如不写，默认为 8901
    然后访问 http://hostip:8901即可
    hostip为执行脚本输出的地址，将整行输入浏览器打开即可
"""

__version__ = "1.0"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "imistyrain"
__home_page__ = "https://github.com/imistyrain"

import os
import sys
import platform
import posixpath
if sys.version_info.major == 2:
    import BaseHTTPServer
    from BaseHTTPServer import BaseHTTPRequestHandler
    from SocketServer import ThreadingMixIn
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
    from io import StringIO
    import urllib.parse
import threading
import urllib
import cgi
import shutil
import mimetypes
import re
import time

#获取主机IP地址，详见https://blog.csdn.net/weixin_40539892/article/details/79103254 
def get_host_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    finally:
        s.close()
    return ip

try:
   port = int(sys.argv[1])
except Exception as e:
   port = 8901

if not 1024 < port < 65535:  port = 8901
serveraddr = ('', port)
print('-------->> You can visit the URL:   '+get_host_ip()+':' + str(port))
print('----------------------------------------------------------------------->> ')

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def modification_date(filename):
    # t = os.path.getmtime(filename)
    # return datetime.datetime.fromtimestamp(t)
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getmtime(filename)))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET/HEAD/POST commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.

    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "SimpleHTTPWithUpload/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        # print "....................", threading.currentThread().getName()
        f = self.send_head()
        if f:
            if sys.version_info.major == 2:
                self.copyfile(f, self.wfile)
                f.close()
            else:
                self.wfile.write(f)

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        #print r, info, "by: ", self.client_address
        if sys.version_info.major == 2:
            r, info = self.deal_post_data_2()
            f = StringIO()
            f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
            f.write("<html>\n<title>Upload Result Page</title>\n")
            f.write("<body>\n<h2>Upload Result Page</h2>\n")
            f.write("<hr>\n")
            if r:
                f.write("<strong>Success:</strong>")
            else:
                f.write("<strong>Failed:</strong>")
            f.write(info)
            f.write("<br><a href=\"%s\">back</a>" % self.headers['referer'])
            f.write("<hr><small>Powered By: bones7456, check new version at ")
            f.write("<a href=\"http://li2z.cn/?s=SimpleHTTPServerWithUpload\">")
            f.write("here</a>.</small></body>\n</html>\n")
            length = f.tell()
            f.seek(0)
        else:
            r, info = self.deal_post_data_3()
            info = info.replace('\n', '<br>')
            f = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">') +\
                ('<html><head>') +\
                ('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">') +\
                ('<title>Upload Result Page</title>') +\
                ('</head><body>') +\
                ('<h1>Upload Result Page</h1>') +\
                ('<hr>')
            if r:
                f = f + ('<strong>Success:<strong><br/>') + info
            else:
                f = f + ('<strong>Failed:<strong>') + info
            f = f + '<br><a href="%s">back</a>' % self.headers['referer'] +\
                '</body></html>'

            f = f.encode('utf-8')
            length = len(f)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            if sys.version_info.major == 2:
                self.copyfile(f, self.wfile)
                f.close()
            else:
                self.wfile.write(f)

    def deal_post_data_2(self):
        boundary = self.headers.plisttext.split("=")[1]
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        osType = platform.system()
        try:
            if osType == "Linux":
                fn = os.path.join(path, fn[0].decode('gbk').encode('utf-8'))
            else:
                fn = os.path.join(path, fn[0])
        except Exception as e:
            return (False, "文件名请不要用中文，或者使用IE上传中文名的文件。")
        while os.path.exists(fn):
            fn += "_"
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith('\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")
       
    def deal_post_data_3(self):
        boundary = self.headers["Content-Type"].split("=")[1]

        boundary_begin = ('--' + boundary + '\r\n').encode('utf-8')
        boundary_end = ('--' + boundary + '--\r\n').encode('utf-8')

        return_status = True
        return_info = '\n'
        outer = 1
        inner = 2
        leave = 3
        loop_info = outer # 1: outer loop, 2: inner_loop, 3: leave and return

        # first line
        # b'------WebKitFormBoundaryLVlRNkjiiJLtNYQE'
        line = self.rfile.readline()

        while loop_info == outer:
            # print(line)
            line = line
            if line != boundary_begin:
                return_status = False
                return_info += "Content NOT begin with boundary\n"
                break

            # get filename
            # b'Content-Disposition: form-data; name="file"; filename="file1.txt"'
            line = self.rfile.readline().decode('utf-8').rstrip('\r\n')
            # print(line)
            filename = re.findall(r'filename="(.*)"', line)[0]
            # print(filename)
            if not filename:
                return_status = False
                return_info += "Can't find out file name...\n"
                loop_info = leave
                break
            path = self.translate_path(self.path)
            filename = os.path.join(path, filename)
            # if filename alread exists
            if os.path.exists(filename):
                filename += "_copy"

            # second line
            # b'Content-Type: text/plain'
            line = self.rfile.readline()
            # print(line)

            # blank line
            line = self.rfile.readline()
            # print(line)

            loop_info = inner
            # POST data
            try:
                buf = b''
                with open(filename, 'wb') as f:
                    while loop_info == inner:
                        line = self.rfile.readline()
                        if line == boundary_begin:
                            loop_info = outer
                            f.write(buf[:-2])
                            break
                        elif line == boundary_end:
                            loop_info = leave
                            # post 数据的实际内容, 在 boundary_end 之前那一行就已经结束了
                            # 而这一行数据后面紧跟的 '\r\n' 只是为了区分接下来的 boundary_end
                            # 因此在把数据写如文件的时候, 要把这个多余的 '\r\n' 去掉
                            f.write(buf[:-2])
                            break
                        else:
                            if len(buf) > 1024:
                                f.write(buf)
                                buf = b''
                            buf += line
            except Exception as e:
                loop_info = leave
                return_status = False
                return_info += 'Exception!\n'
            return_info += filename + '\n'
        return (return_status, return_info) 
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                if sys.version_info.major == 2:
                    return self.list_directory_2(path)
                else:
                    return self.list_directory_3(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        if sys.version_info.major == 2:
            return f
        else:
            data = f.read()
            f.close()
            return data

    def list_directory_2(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n")
        f.write("<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write("<input name=\"file\" type=\"file\"/>")
        f.write("<input type=\"submit\" value=\"upload\"/>")
        f.write("&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp")
        f.write("<input type=\"button\" value=\"HomePage\" onClick=\"location='/'\">")
        f.write("</form>\n")
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            colorName = displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                colorName = '<span style="background-color: #CEFFCE;">' + name + '/</span>'
                displayname = name
                linkname = name + "/"
            if os.path.islink(fullname):
                colorName = '<span style="background-color: #FFBFFF;">' + name + '@</span>'
                displayname = name
                # Note: a link to a directory displays with @ and links with /
            filename = os.getcwd() + '/' + displaypath + displayname
            f.write('<table><tr><td width="60%%"><a href="%s">%s</a></td><td width="20%%">%s</td><td width="20%%">%s</td></tr>\n'
                    % (urllib.quote(linkname), colorName,
                        sizeof_fmt(os.path.getsize(filename)), modification_date(filename)))
        f.write("</table>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def list_directory_3(self, path):
        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        displaypath = cgi.escape(urllib.parse.unquote(self.path))

        f = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">') +\
            ('<html><head>') +\
            ('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">') +\
            ('<title>Directory listing for %s</title>' % displaypath) +\
            ('</head><body>') +\
            ('<h1>Directory listing for %s</h1>' % displaypath) +\
            ('<form ENCTYPE="multipart/form-data" method="post">') +\
            ('<input name="file" type="file" multiple="multiple"/>') +\
            ('<input type="submit" value="upload"/></form>') +\
            ('<hr><ul>')

        for name in list:
            fullname = os.path.join(path, name)
            colorName = displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
                colorName = '<span style="background-color: #CEFFCE;">' + name + '/</span>'
            if os.path.islink(fullname):
                displayname = name
                colorName = '<span style="background-color: #FFBFFF;">' + name + '@</span>'
                # Note: a link to a directory displays with @ and links with /
            #f = f + ('<li><a href="%s">%s</a>' % (urllib.parse.quote(linkname), cgi.escape(displayname)))
            filename = os.getcwd() + '/' + displaypath + displayname
            f = f+'<table><tr><td width="60%%"><a href="%s">%s</a></td><td width="20%%">%s</td><td width="20%%">%s</td></tr>\n'% (urllib.parse.quote(linkname), colorName,sizeof_fmt(os.path.getsize(filename)), modification_date(filename))
        f = f + ("</table><hr></body></html>")

        f = f.encode('utf-8')
        length = len(f)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        if sys.version_info.major == 2:
            path = posixpath.normpath(urllib.unquote(path))
        else:
            path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
    '': 'application/octet-stream', # Default
    '.py': 'text/plain',
    '.h': 'text/plain',
    '.hpp': 'text/plain',
    '.c': 'text/plain',
    '.cc': 'text/plain',
    '.cpp': 'text/plain',
    '.cu': 'text/plain',
    '.md': 'text/plain',
    '.log': 'text/plain',
    '.ini': 'text/plain',
    '.htm': 'text/plain',
    '.yml': 'text/plain',
    '.yaml': 'text/plain',
    '.sh': 'text/plain',
    '.cfg': 'text/plain',
    '.bat': 'text/plain',
    '.rc': 'text/plain',
    '.prototxt': 'text/plain',
    })

if sys.version_info.major == 2:
    class ThreadingServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
        pass

    def test(HandlerClass = SimpleHTTPRequestHandler,
        ServerClass = BaseHTTPServer.HTTPServer):
        BaseHTTPServer.test(HandlerClass, ServerClass)
else:
    class ThreadingServer(ThreadingMixIn, HTTPServer):
        pass

if __name__ == '__main__':
    #单线程
    # srvr = BaseHTTPServer.HTTPServer(serveraddr, SimpleHTTPRequestHandler)
    #多线程
    srvr = ThreadingServer(serveraddr, SimpleHTTPRequestHandler)
    srvr.serve_forever()
