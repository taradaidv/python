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
		print str(self.path)
		if self.path == '/':
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+'\n'+str(self.headers))
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
		elif self.path == '/ns':
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+str(self.path)+'\n'+str(self.headers))
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
			f_url=root_folder+'/uploads/'+self.path+'/'
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
				#self.send_header('Content-Type', 'text/html; charset=UTF-8')
				self.send_header('Content-type', 'application/zip')
				self.send_header('Content-length',os.path.getsize(f_url+fn))
				#self.send_header('Content-Disposition', 'attachment; filename="'+fn+'"')
				#%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82
				s='привет'
				TEST=s.encode('UTF-8')	
				print (TEST+'ZZZZZZZZZZZZZZZZ')
				self.send_header('Content-Disposition', 'attachment; filename="'+fn+'"; filename*=UTF-8\'\'"'+TEST+'"')
				
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
		path_part=root_folder+'/uploads/'+rand_url
		if name == '':
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
			fdst = open(path_part + '/'+ name + ext, 'wb')
			shutil.copyfileobj(form['file'].file, fdst)
			fdst.close()
			app_log.info('[200] '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+' '+str(self.headers['content-length'])+'\n'+str(self.headers))
			self.wfile.write('Файл <b>'+name+ext+'</b> загружен на сервер и доступен по ссылке <br><a href="'+rand_url+'">'+rand_url+'<a/>')	
		else:
			app_log.info('*DUPL '+self.client_address[0]+' '+str(self.command)+' '+rand_url+' - '+name+ext+'\n'+str(self.headers))
			self.wfile.write('<b>Повторите попытку отправки файла !</b>')
			
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