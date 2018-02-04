#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from socketserver import ThreadingMixIn
import http.server
import sys
import shutil
import cgi
import random
import string
import logging
import datetime
import socket
import time
import errno

listening_ip="0.0.0.0"
listening_port=8000

now = datetime.datetime.now()

def RS(n=8):
	r = ""
	for i in range(n):
		r += random.choice(string.ascii_lowercase)
	return r
	
def f_str(arg):

	try:
		files = os.listdir(arg)
	except OSError as e:
		if e.errno != 2:
			f_res =files[0]
		else:
			f_res="xxx"
			
		return f_res

class ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
	pass

class RequestHandler(http.server.SimpleHTTPRequestHandler):
	def do_HEAD(self):
		self.send_headers()
	def send_headers(self):
		npath = os.path.normpath(self.path)
		npath = npath[1:]
		path_elements = npath.split('/')
		if path_elements[0] == "":
			self.send_response(200)
			self.end_headers()
			date='''
<!DOCTYPE HTML>
<html>
	<head>
	<meta charset="utf-8">
	<title>Send</title>
	</head>
<body> 
	<center>
	<form method="POST" action='/upload' enctype="multipart/form-data">
		<input type="file" name="file"><br>
		<button><img src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pgo8IS0tIEdlbmVyYXRvcjogQWRvYmUgSWxsdXN0cmF0b3IgMTkuMi4wLCBTVkcgRXhwb3J0IFBsdWctSW4gLiBTVkcgVmVyc2lvbjogNi4wMCBCdWlsZCAwKSAgLS0+CjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgdmVyc2lvbj0iMS4xIiBpZD0iTGF5ZXJfMSIgeD0iMHB4IiB5PSIwcHgiIHZpZXdCb3g9IjAgMCA0MCA0MCIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNDAgNDA7IiB4bWw6c3BhY2U9InByZXNlcnZlIj4KPGc+Cgk8cG9seWdvbiBzdHlsZT0iZmlsbDojRkZGRkZGOyIgcG9pbnRzPSI2LjUsMzcuNSA2LjUsMi41IDI0Ljc5MywyLjUgMzMuNSwxMS4yMDcgMzMuNSwzNy41ICAiLz4KCTxnPgoJCTxwYXRoIHN0eWxlPSJmaWxsOiM0Nzg4Qzc7IiBkPSJNMjQuNTg2LDNMMzMsMTEuNDE0VjM3SDdWM0gyNC41ODYgTTI1LDJINnYzNmgyOFYxMUwyNSwyTDI1LDJ6Ii8+Cgk8L2c+CjwvZz4KPGc+Cgk8cG9seWdvbiBzdHlsZT0iZmlsbDojREZGMEZFOyIgcG9pbnRzPSIyNC41LDExLjUgMjQuNSwyLjUgMjQuNzkzLDIuNSAzMy41LDExLjIwNyAzMy41LDExLjUgICIvPgoJPGc+CgkJPHBhdGggc3R5bGU9ImZpbGw6IzQ3ODhDNzsiIGQ9Ik0yNSwzLjQxNEwzMi41ODYsMTFIMjVWMy40MTQgTTI1LDJoLTF2MTBoMTB2LTFMMjUsMkwyNSwyeiIvPgoJPC9nPgo8L2c+CjxnPgoJPHBvbHlnb24gc3R5bGU9ImZpbGw6Izk4Q0NGRDsiIHBvaW50cz0iMjMsMjEgMTAsMjEgMTAsMjUgMjMsMjUgMjMsMjkgMzAsMjMgMjMsMTcgICIvPgo8L2c+Cjwvc3ZnPgo=' width="189" height="255" style="vertical-align: middle"/> Отправить файл</button>
	</form>
 </body>
</html>
''' 
			self.wfile.write(date.encode("utf-8"))
		elif path_elements[0] == "upload":
			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=utf-8")
			self.end_headers()
            #logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
		else:
			f_url=os.path.dirname(os.path.abspath(__file__))+"/uploads/"+path_elements[0]+"/"
			f_name=f_str(f_url)
			self.send_response(200)
			self.send_header("Content-type", "application/x-binary")
			self.send_header("Content-Disposition", 'form-data; name="file"; filename="'+f_name+'"')
			self.end_headers()
			f = open(f_url+f_name, "rb")
			shutil.copyfileobj(f, self.wfile)
			f.close()
        	#logging.info("GET Download t,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
		return path_elements

	def do_GET(self):
		elements = self.send_headers()
		logging.info(now.strftime(" |%Y.%m.%d %H:%M:%S.%f")+"|IP:%s|DNS:%s|%s|URL:%s\n%s",str(format(self.client_address[0])),str(self.address_string()),str(self.command), str(self.path),str(self.headers))      
		if elements is None:
			return
			
	def do_POST(self):
		rand_url=RS()
		elements = self.send_headers()
		if elements is None or elements[0] != "upload":
			return
		
		form = cgi.FieldStorage(
		fp=self.rfile,
		headers=self.headers,
		environ={"REQUEST_METHOD": "POST"})           
		name, ext = os.path.splitext(form["file"].filename)
		path_part=os.path.dirname(os.path.abspath(__file__))+"/uploads/"+rand_url
		
		try:
			os.makedirs(path_part)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
				
		if name[0] ==".":
			name="_"
			#Hack?!
		else:
			fdst = open(path_part + "/"+ name + ext, "wb")
			shutil.copyfileobj(form["file"].file, fdst)
			fdst.close()
			#logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",str(self.path), str(self.headers), name+ext )
			logging.info(now.strftime(" |%Y.%m.%d %H:%M:%S.%f")+"|IP:%s|DNS:%s|%s|URL:%s/%s|File [%s]\n%s",str(format(self.client_address[0])),str(self.address_string()),str(self.command), str(self.path),rand_url,name+ext,str(self.headers))
			
		#Result URL OUT
			self.end_headers()
			date='<a href="http://'+self.address_string()+':'+str(listening_port)+'/'+rand_url+'">http://'+self.address_string()+':'+str(listening_port)+'/'+rand_url+'</a>'
			self.wfile.write(date.encode("utf-8"))
			
if __name__ == '__main__':
	logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__))+'/logs/'+now.strftime('%Y.%m.%d_%H-%M-%S')+'_logs.txt',level=logging.INFO)
	Handler = RequestHandler
	try:
		httpd = ThreadingHTTPServer((listening_ip, listening_port), Handler)
		logging.info('1... - start')
		print(time.asctime(), 'Server Starts at port',listening_port )
		httpd.serve_forever()
	except socket.error as e:
		if e.args[0] == 48:
			logging.info('Port: already in use')
			print('Port:',listening_port,'already in use')
		elif e.args[0] == 13:
			logging.info('below 1024 can be opened only by root. You must be root to do that !')
			print ('Port:',listening_port,'below 1024 can be opened only by root. You must be root to do that !')			
		else:
			raise 
	except KeyboardInterrupt:
		pass
		httpd.server_close()
		logging.info('3...- stop')
		print(time.asctime(), 'Server stop' )