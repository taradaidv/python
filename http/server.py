#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
import os
from SocketServer import ThreadingMixIn
import BaseHTTPServer
import SimpleHTTPServer
import shutil
import cgi
import random
import string
import logging
import datetime
import socket
from logging.handlers import RotatingFileHandler
import ssl

listening_ip="172.16.0.10"
listening_port=8443

def rand_string(n=8):
	res = ""
	for i in range(n):
		res += random.choice(string.ascii_lowercase)
	return res

class ThreadingHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def send_headers(self):
		if self.path == "/":
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+'\n'+str(self.headers))
			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=UTF-8")
			self.end_headers()
			i = open(os.path.dirname(os.path.abspath(__file__))+"/index.html", "rb")
			shutil.copyfileobj(i, self.wfile)
			i.close()
		elif self.path == "/upload":
			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=UTF-8")
			self.end_headers()
		elif self.path == "/ns":
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+'\n'+str(self.headers))
			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=UTF-8")
			self.end_headers()
			self.wfile.write(
'''
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Обмен</title>
</head>
<body>
<form method="POST" action="/upload" enctype="multipart/form-data">
<div><input type="file" name="file"></div>
<br>
<button>Отправить файл</button>	
</form><br>
JavaScript <b>отключен</b>, функционал ресурса доступен в ограниченном режиме.<br>
За более подробной информацией обратитесь к системному администратору.
</body>
</html>
''') 
			
		elif self.path == "/favicon.ico":
			self.send_response(404)
		else:
			f_url=os.path.dirname(os.path.abspath(__file__))+"/uploads/"+self.path+"/"
			try:
				sn = os.listdir(f_url)
			except OSError:
				app_log.info('[404] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+'\n'+str(self.headers))
				self.send_response(404)
				self.end_headers()
			else:
				fn = sn[0]
				app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+' '+str(os.path.getsize(f_url+fn))+'\n'+str(self.headers))
				self.send_response(200)
				self.send_header("Content-type", "application/x-binary")
				self.send_header("Accept-Ranges", "bytes")
				self.send_header('Content-length',os.path.getsize(f_url+fn))
				self.send_header("Content-Disposition", 'form-data; name="file"; filename="'+fn+'"')
				self.end_headers()
				f = open(f_url+fn, "rb")
				shutil.copyfileobj(f, self.wfile)
				f.close()			
		return self.path	
		
	def do_GET(self):
		elements = self.send_headers()
		if elements is None:
			app_log.info('*Dbg1 '+self.client_address[0])
			return
					
	def do_POST(self):
		rand_url=rand_string()
		elements = self.send_headers()
		if elements is None != "/upload":
			app_log.info('*Dbg2 '+self.client_address[0])
			return
		form = cgi.FieldStorage(
		fp=self.rfile,
		headers=self.headers,
		environ={"REQUEST_METHOD": "POST"})           
		name, ext = os.path.splitext(form["file"].filename)
		path_part=os.path.dirname(os.path.abspath(__file__))+"/uploads/"+rand_url
		if name == "":
			app_log.info('*HACK '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+' - '+name+ext+'\n'+str(self.headers))
			return
		if '/' in name:
			app_log.info('*HACK '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+'\n'+str(self.headers))
			return
		if '<' in name:
			app_log.info('*HACK '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+'\n'+str(self.headers))
			return
		if not os.path.exists(path_part):
			os.makedirs(path_part)
			fdst = open(path_part + "/"+ name + ext, "wb")
			shutil.copyfileobj(form["file"].file, fdst)
			fdst.close()
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+' '+str(self.headers['content-length'])+'\n'+str(self.headers))
			self.wfile.write('Файл <b>'+name+ext+'</b> загружен на сервер и доступен для скачивания по ссылке <a href="https://'+str(listening_ip)+':'+str(listening_port)+'/'+rand_url+'">https://'+str(listening_ip)+':'+str(listening_port)+'/'+rand_url+'<a/>')		
		else:
			app_log.info('*DUPL '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+'\n'+str(self.headers))
			self.wfile.write('<b>Повторите попытку отправки файла !</b>')
			
if __name__ == '__main__':
	log_dir=os.path.dirname(os.path.abspath(__file__))+'/logs/'
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	log_formatter = logging.Formatter('%(asctime)s %(message)s','%d/%m/%Y %H:%M:%S')
	logFile = log_dir+'access.log' 
	my_handler = RotatingFileHandler(logFile, maxBytes=10485760, backupCount=50,delay=0)
	my_handler.setFormatter(log_formatter)
	my_handler.setLevel(logging.INFO)
	app_log = logging.getLogger('root')
	app_log.setLevel(logging.INFO)
	app_log.addHandler(my_handler)
	RequestHandler.server_version = "Microsoft-IIS/7.5"
	RequestHandler.sys_version = ""
	try:
		httpd = ThreadingHTTPServer((listening_ip, listening_port), RequestHandler)
		app_log.info('*START '+os.path.realpath(__file__)+' LISTEN PORT TCP/'+ str(listening_port) )
		print('Server start & listen port TCP/'+ str(listening_port))
		httpd.socket = ssl.wrap_socket (httpd.socket,keyfile=os.path.dirname(os.path.abspath(__file__))+'/crt/key.pem',certfile=os.path.dirname(os.path.abspath(__file__))+'/crt/cert.pem', server_side=True)
		httpd.serve_forever()
	except socket.error as e:
		if e.args[0] == 48:
			app_log.info('*ERROR '+os.path.realpath(__file__)+' PORT TCP/'+ str(listening_port)+' already in use' )
			print('Port:',listening_port,'already in use')
		elif e.args[0] == 13:
			app_log.info('*ERROR '+os.path.realpath(__file__)+' PORT TCP/'+ str(listening_port)+' < 1024 & can be opened only by ROOT!' )
			print ('Port: '+str(listening_port)+' < 1024 & can be opened only by ROOT!')			
		else:
			raise 
	except KeyboardInterrupt:
		pass
		httpd.server_close()
		app_log.info('*STOP')
		print('Server stop')