# -*- coding: cp1252 -*-
import os
import time
import re
import cx_Oracle

class Exec:
	debug = True
	
	@staticmethod
	def cmd(cmd_string):
		if Exec.debug:
			print("# " + cmd_string)
		else:
			os.system(cmd_string)

class Connection:
	slash = "\\"
	dump_root_path = "E:" + slash + "dumps"

	def __init__(self, client, username, password, tns, zs3_username, zs3_password, zs3_tns):
		self.client = client
		self.username = username
		self.password = password
		self.tns = tns
		self.zs3_username = zs3_username
		self.zs3_password = zs3_password		
		self.zs3_tns = zs3_tns

	def get_client_path(self):
		return dump_root_path + slash + self.client

	def get_today_path(self):
		return self.get_client_path() + slash + time.strftime("%Y%m%d")

	def get_filename(self):
		return self.get_today_path() + slash + self.username.lower() + "@" + self.tns.lower() + "." + time.strftime("%Y%m%d") + "." + time.strftime("%H") + ("30" if time.strftime("%M") >= "30" else "00")
	
	def get_zs3_filename(self):
		return self.get_today_path() + slash + self.zs3_username.lower() + "@" + self.zs3_tns.lower() + "." + time.strftime("%Y%m%d") + "." + time.strftime("%H") + ("30" if time.strftime("%M") >= "30" else "00")
	
	def get_dump_filename(self):
		return self.get_filename() + ".dmp"

	def get_exp_logname(self):
		return self.get_filename() + ".exp.log"
	
	def get_imp_logname(self):
		return self.get_zs3_filename() + ".imp.log"

	def get_exp_cmd(self):
		return "exp " + self.username + "/" + self.password + "@" + self.tns +\
			" file=" + self.get_dump_filename() +\
			" log=" + self.get_exp_logname() +\
			" rows=yes"

	def get_imp_cmd(self):
		return "imp " + self.zs3_username + "/" + self.zs3_password + "@" + self.zs3_tns +\
			" file=" + self.get_dump_filename() +\
			" log=" + self.get_imp_logname() +\
			" fromuser=" + self.username +\
			" touser=" + self.zs3_username +\
			" rows=yes"
	
	def is_prot(self):
		return re.search("prot", conn.username + conn.zs3_username, re.I)

gisa_connections = [
	# as conns com from e to, preciso fazer o refactor dos nomes e tal...
	Connection("cliente", "from_user", "from_pass", "from_tns", "to_user", "to_pass", "to_tns")
]

slash = "\\"
dump_root_path = "E:" + slash + "dumps"


for conn in gisa_connections:
	# se necessario, cria a pasta do cliente
	
	print "current running for " + conn.client + "." + conn.username

	if not os.path.exists(conn.get_client_path()):
		os.system("mkdir \"" + conn.get_client_path() + "\"")
	
	if not os.path.exists(conn.get_today_path()):
		os.system("mkdir \"" + conn.get_today_path() + "\"")

	if not os.path.exists(conn.get_dump_filename()):
		Exec.cmd(conn.get_exp_cmd())
	else:	
		print " . . dump already exists"

	if os.path.exists(conn.get_dump_filename()) and not os.path.exists(conn.get_imp_logname()) or Exec.debug:
		Exec.cmd(conn.get_imp_cmd())
	else:	
		print " . . dump file not found or imp.log already exists"
	
	# parei aqui, vou fazer os updates que rolam apenas nas bases "prots" (são nosso controle de licenças lol
	if conn.is_prot():
		print " SOU PROT SOU PROT! "