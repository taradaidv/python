#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
import os
import urllib
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


listening_ip='0.0.0.0'
listening_port=8443
root_folder=os.path.dirname(os.path.abspath(__file__))


def RND(n=8):
	r = ''
	for i in range(n):
		r += random.choice(string.ascii_lowercase)
	return r

class ThreadingHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def send_headers(self):
		if self.path == '/':
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+' - '+str(self.headers.getheader('User-Agent')))
			self.send_response(200)
			self.send_header('Content-Type', 'text/html; charset=UTF-8')
			self.end_headers()
			i = open(root_folder+'/index.html', 'rb')
			shutil.copyfileobj(i, self.wfile)
			i.close()
		elif self.path == '/upload': #work if JavaScript is disabled
			self.send_response(200)
			self.send_header('Content-Type', 'text/html; charset=UTF-8')
			self.end_headers()
		elif self.path == '/favicon.ico':
			self.send_response(200)
			self.send_header('Content-Type', 'image/x-icon')
			self.end_headers()
			i = open(root_folder+'/favicon.ico', 'rb')
			shutil.copyfileobj(i, self.wfile)
			i.close()
			'''
		elif '.png' in self.path[-4:]:
			if os.path.isfile(root_folder+self.path) and os.access(root_folder+self.path, os.R_OK):
				self.send_response(200)
				self.send_header("Content-Type", "image/png")
				self.end_headers()
				i = open(os.path.dirname(os.path.abspath(__file__))+self.path, "rb")
				shutil.copyfileobj(i, self.wfile)
				i.close()
			else:
				#print self.path+" Either file is missing or is not readable"
				self.send_response(404)
				self.end_headers()
			'''
		elif '/img' in self.path[:4]:
			if os.path.isfile(root_folder+self.path) and os.access(root_folder+self.path, os.R_OK):
				self.send_response(200)
				self.send_header("Content-Type", "image/png")
				self.end_headers()
				i = open(os.path.dirname(os.path.abspath(__file__))+'/img'+self.path[4:], "rb")
				shutil.copyfileobj(i, self.wfile)
				i.close()
			else:
				#print self.path+" Either file is missing or is not readable"
				self.send_response(404)
				self.end_headers()
		elif '/css' in self.path[:4]:
			if os.path.isfile(root_folder+self.path) and os.access(root_folder+self.path, os.R_OK):
				self.send_response(200)
				self.send_header("Content-Type", "text/css; charset=utf-8")
				self.end_headers()
				i = open(os.path.dirname(os.path.abspath(__file__))+'/css'+self.path[4:], "rb")
				shutil.copyfileobj(i, self.wfile)
				i.close()
			else:
				#print self.path+" Either file is missing or is not readable"
				self.send_response(404)
				self.end_headers()
		elif '/jQueryAssets' in self.path[:13]:
			if os.path.isfile(root_folder+self.path) and os.access(root_folder+self.path, os.R_OK):
				self.send_response(200)
				self.send_header("Content-Type", "text/css; charset=utf-8")
				self.end_headers()
				i = open(os.path.dirname(os.path.abspath(__file__))+'/jQueryAssets'+self.path[13:], "rb")
				shutil.copyfileobj(i, self.wfile)
				i.close()
			else:
				self.send_response(404)
				self.end_headers()
		elif '/jQueryAssets/images' in self.path[:20]:
			if os.path.isfile(root_folder+self.path) and os.access(root_folder+self.path, os.R_OK):
				self.send_response(200)
				self.send_header("Content-Type", "image/png")
				self.end_headers()
				i = open(os.path.dirname(os.path.abspath(__file__))+'/jQueryAssets/images'+self.path[20:], "rb")
				shutil.copyfileobj(i, self.wfile)
				i.close()
			else:
				self.send_response(404)
				self.end_headers()
		elif '/images' in self.path[:7]:
			if os.path.isfile(root_folder+self.path) and os.access(root_folder+self.path, os.R_OK):
				self.send_response(200)
				self.send_header("Content-Type", "image/png")
				self.end_headers()
				i = open(os.path.dirname(os.path.abspath(__file__))+'/images'+self.path[7:], "rb")
				shutil.copyfileobj(i, self.wfile)
				i.close()
			else:
				self.send_response(404)
				self.end_headers()
		elif self.path == '/0':
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+' - '+str(self.headers.getheader('User-Agent')))
			self.send_response(200)
			self.send_header('Content-Type', 'text/html; charset=UTF-8')
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
<div><input type='file' name='file'></div>
<br>
<button>Отправить файл</button>	
</form><br>
JavaScript <b>отключен</b>, функционал ресурса доступен в ограниченном режиме.<br>
За более подробной информацией обратитесь к системному администратору.
</body>
</html>
''') 
		else:
			f_url=root_folder+'/uploads/'+self.path+'/file/'
			try:
				sn = os.listdir(f_url)
			except OSError:
				app_log.info('[404] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+' - '+str(self.headers.getheader('User-Agent')))
				self.send_response(404)
				self.end_headers()
			else:
				fn = sn[0]
				app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+' '+str(os.path.getsize(f_url+fn))+' - '+str(self.headers.getheader('User-Agent')))
				self.send_response(200)
				self.send_header('Content-type', 'application/zip')
				self.send_header('Content-length',os.path.getsize(f_url+fn))
				self.send_header('Content-Disposition', "attachment;  filename*=UTF-8''"+urllib.quote(fn))
				self.send_header('Accept-Ranges', 'bytes')
				self.end_headers()
				f = open(f_url+fn, 'rb')
				shutil.copyfileobj(f, self.wfile)
				f.close()			
		return self.path	
	def do_GET(self):
		elements = self.send_headers()
		if elements is None:
			app_log.info('*Dbg1 '+self.client_address[0])
			return
					
	def do_POST(self):
		rand_url=RND()
		elements = self.send_headers()
		if elements is None != '/upload':
			app_log.info('*Dbg2 '+self.client_address[0])
			return
		form = cgi.FieldStorage(
		fp=self.rfile,
		headers=self.headers,
		environ={'REQUEST_METHOD': 'POST'})           
		name, ext = os.path.splitext(form['file'].filename)
		path_part=root_folder+'/uploads/'+rand_url+'/file/'
		if name == '':
			app_log.info('*HACK '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+' - '+name+ext+' - '+str(self.headers.getheader('User-Agent')))
			return
		if '/' in name:
			app_log.info('*HACK '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+' - '+str(self.headers.getheader('User-Agent')))
			return
		if '<' in name:
			app_log.info('*HACK '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+' - '+str(self.headers.getheader('User-Agent')))
			return
		if not os.path.exists(path_part):
			os.makedirs(path_part)
			fdst = open(path_part + name + ext, 'wb')
			shutil.copyfileobj(form['file'].file, fdst)
			fdst.close()
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+' '+str(self.headers['content-length'])+' - '+str(self.headers.getheader('User-Agent')))
			self.wfile.write('<br>Файл <b>'+name+ext+'</b> загружен на сервер и доступен по ссылке:<br><a href="'+rand_url+'">'+'/'.join(self.headers.getheader('Referer').split('/')[0::2])+'/'+rand_url+'<a/>')	#alternative self.headers.getheader('Origin')

		else:
			app_log.info('*DUPL '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+' - '+str(self.headers.getheader('User-Agent')))
			self.wfile.write('<b>Файл загружен частично, повторите отправку !</b>')
			
if __name__ == '__main__':
	log_dir=root_folder+'/logs/'
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
	RequestHandler.server_version = 'Microsoft-IIS/7.5'
	RequestHandler.sys_version = ''
	try:
		httpd = ThreadingHTTPServer((listening_ip, listening_port), RequestHandler)
		app_log.info('*START '+os.path.realpath(__file__)+' LISTEN PORT TCP/'+ str(listening_port) )
		print('Server start & listen port TCP/'+ str(listening_port))
		httpd.socket = ssl.wrap_socket (httpd.socket,keyfile=root_folder+'/crt/key.pem',certfile=root_folder+'/crt/cert.pem', server_side=True)
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