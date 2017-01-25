#Libreria Modulo de GPS-GPRS SIM808
#Actualizacion: 20 Enero 2017
#Actualizo: Juan Jurado

import threading
import math
import time

import serial
import requests
import json

from datetime import datetime

from time import time , sleep





class sim808Class:

	def __init__(self,url='THE_URL',port='/dev/ttyS1'):
		#Variables de GPS
		self.ser = serial.Serial(port)
		self.url=url

		self.date = None
		self.latitude = None
		self.longitude = None
		self.speed = None
		self.acc = None
		self.leerGPS = True
		self.lecturaGps = False
		self.connGps = False
		self.reconnGps = 0
		self.connGprs = False
		self.reconnGprs = 0
		self.timeRate = 1
		self.timeOut = 60
		
		


	def writeSerial(self,msg):
		#print "Sended: "+msg
		self.ser.write(bytes(msg))

	def WhilePower(self,debug=False):
		while True:
			lineData = self.ser.readline()
			if debug:
				print "Received WhilePower: "+lineData
			if lineData.find("SMS Ready")==0:
				return lineData
				break

	def WhileOk(self,debug=False):
		while True:
			lineData = self.ser.readline()
			if debug:
				print "Received WhileOk: "+lineData
			if lineData.find("OK")==0:
				return lineData
				break
			elif lineData.find("ERROR")==0:
				return False
				break

	def WhileRead(self,debug=False):
		response = ''
		while True:
			lineData = self.ser.readline()
			if debug:
				print "Received WhileOk: "+lineData
			if lineData.startswith("{") or lineData.startswith("["):
				print 'Encontro Response'
				response = response+lineData
			elif lineData.find("OK")==0:
				return response
				break
			elif lineData.find("ERROR")==0:
				return False
				break

	def WhileIp(self,debug=False):
		while True:
			lineData = self.ser.readline()
			if debug:
				print "Received WhileIp: "+lineData
			if lineData.find("+SAPBR: 1,0,")==0:	#1-Bearer profile identifier,0-Bearer is connecting 
				return False
				break
			elif lineData.find("+SAPBR: 1,1,")==0:	#1-Bearer profile identifier,1-Bearer is connected 
				return lineData
				break
			elif lineData.find("+SAPBR: 1,2,")==0:	#1-Bearer profile identifier,2-Bearer is closing
				return False
				break
			elif lineData.find("+SAPBR: 1,3,")==0:	#1-Bearer profile identifier,3-Bearer is closed
				return False
				break

	def WhileDownload(self,debug=False):
		while True:
			lineData = self.ser.readline()
			if debug:
				print "Received WhileDownload: "+lineData
			if lineData.find("DOWNLOAD")==0:
				break

	def WhileAction(self,debug=False):
		while True:
			lineData = self.ser.readline()
			if debug:
				print "Received WhileAction: "+lineData
			#if lineData.find("+HTTPACTION:")==0:
				#break
			if lineData.find("+HTTPACTION: 1,200")==0:		#OK-Cuando envia bien
				return True
				break
			elif lineData.find("+HTTPACTION: 1,202")==0:	#Accepted-Cuando envia bien
				return True
				break
			elif lineData.find("+HTTPACTION: 1,400")==0:	#Bad Request-Cuando esta mal JSON
				return True
				break
			elif lineData.find("+HTTPACTION: 1,408")==0:	#Request Timeout
				return True
				break
			elif lineData.find("+HTTPACTION: 1,307")==0:	#Temporary Redirect-Cuando no tiene datos
				return True
				break	
			elif lineData.find("+HTTPACTION: 1,601")==0:	#Network Error-Cuando se desconecta antena GPRS
				return False
				break
			elif lineData.find("+HTTPACTION: 1,603")==0:	#DNS Error-Cuando se desconecta antena GPRS
				return False
				break
			elif lineData.find("+HTTPACTION:")==0:
				print "response action"+lineData
				return True
				break

	

	def Power(self,OnOff):
		self.leerGPS = False
		if OnOff == True:
			self.writeSerial('AT+CPOWD=1\n')	#Power off # 1- Normal power off (Will send out NORMAL POWER DOWN) 
			self.WhilePower()
			print "power on"
		elif OnOff ==False:
			self.writeSerial('AT+CPOWD=0\n')	#Power off # 0-Power off urgently (Will not send out NORMAL POWER DOWN) 
			self.WhilePower()
			print "power off"
		self.leerGPS = True

	def Echo(self,OnOff):
		if OnOff == True:
			self.writeSerial('ATE1\n')
			res = self.WhileOk()
		elif OnOff ==False:
			self.writeSerial('ATE0\n')
			res = self.WhileOk()
		return res

	def verifyStatusSIMCARD(self):
		self.writeSerial('AT+CPIN?\n')
		res = self.WhileOk()
		return res

	def EnableGPS(self,OnOff):
		if OnOff == True:
			self.writeSerial('AT+CGNSPWR=1\n')	#1 Turn on GNSS power supply
			res = self.WhileOk()
		elif OnOff ==False:
			self.writeSerial('AT+CGNSPWR=0\n')	#0 Turn off GNSS power supply
			res = self.WhileOk(True)

		self.writeSerial('AT+CGNSSEQ="RMC"\n')	#Define the last NMEA sentence that parsed
		res = self.WhileOk()					#RMC Time, date, position, course and speed data 
		return res

	def EnableGprsHttp(self):
		print "EnableGprsHttp"
		self.writeSerial('AT+CREG?\n')	#Network Registration 
		self.WhileOk()
		self.writeSerial('AT+CGATT?\n')	#Attach or Detach from GPRS Service 
		self.WhileOk()
		self.writeSerial('AT+SAPBR=3,1,"CONTYPE","GPRS"\n')	#Bearer Settings for Applications Based on IP 
		self.WhileOk()										#3 Set bearer parameters 
		#self.ser.write("AT+SAPBR=3,1,\"APN\",\"internet.comcel.com.co\"");
		self.writeSerial('AT+SAPBR=3,1,"APN","internet.movistar.com.co"\n')	#Bearer Settings for Applications Based on IP 
		self.WhileOk()														#3 Set bearer parameters 
		self.writeSerial('AT+SAPBR=1,1\n')	#Bearer Settings for Applications Based on IP 
		self.WhileOk()						#1 Open bearer 
		self.writeSerial('AT+SAPBR=2,1\n')	#Bearer Settings for Applications Based on IP 
		res = self.WhileIp(True)			#2 Query bearer 
		return res

	def DisableGprsHttp(self):
		print "DisableGprsHttp"
		self.writeSerial('AT+HTTPTERM\n')	#Terminate HTTP service 
		self.WhileOk(True)
		self.writeSerial('AT+SAPBR=0,1\n')	#Bearer Settings for Applications Based on IP #To close a GPRS context. 
		self.WhileOk(True)					#0 Close bearer  
		
	def RequestGps(self):
		self.writeSerial('AT+CGNSINF\n')	#GNSS navigation information parsed from NMEA sentences 
		self.ser.readline()
		lineData = self.ser.readline()
		#print "GPS: "+lineData
		self.WhileOk()
		if lineData.find("+CGNSINF")==0:
			data = lineData.split(",")
			return data

	def SendJsonPostHttp(self,url,date,latitude,longitude,acc,speed,temperature):

		payload = {'date': date ,'lat': latitude ,'long': longitude ,'acc': acc ,'speed': speed ,'temperatura': temperature}
		payload = json.dumps(payload)
		return self.PostHttp(url,len(payload),payload)

	def SendJsonPostHttp2(self,dateJson,url=None):
		self.leerGPS = False
		#print ("Se detiene el Hilo de lecturaGps",self.leerGPS)
		while self.lecturaGps:
			#print ("Entro While espera que termine leer Gps",self.lecturaGps)
			self.lecturaGps
		response = self.PostHttp(len(dateJson),dateJson,url)
		self.leerGPS = True
		return response
		#print ("Se activa el Hilo de lecturaGps",self.leerGPS)

	def PostHttp(self,tamano,dato,url=None):
		self.writeSerial('AT+SAPBR=2,1\n')
		res = self.WhileIp(True)
		if res != False:
			self.connGprs = True
			self.writeSerial('AT+HTTPINIT\n')
			self.WhileOk()
			self.writeSerial('AT+HTTPPARA="CID",1\n')
			self.WhileOk()
			url_req = self.url
			if url != None:
				url_req = url
			print url_req
			self.writeSerial('AT+HTTPPARA="URL","'+url_req+'"\n')
			#self.writeSerial('AT+HTTPPARA="URL",'url'\n')
			self.WhileOk()
			self.writeSerial('AT+HTTPPARA="CONTENT","application/json"\n')
			self.WhileOk()
			data = "AT+HTTPDATA=%d,10000\n" % (tamano)
			#print "Data:"data
			self.writeSerial(data)
			self.WhileDownload()
			#print dato	
			self.writeSerial(dato)
			self.WhileOk()	
			self.writeSerial('AT+HTTPACTION=1\n')
			res = self.WhileAction(True)
			if res == True:
				self.connGprs = True
				self.reconnGprs = 0
				self.writeSerial('AT+HTTPREAD\n')
				response = self.WhileRead(True)
				print('Response:  ')
				#log = "{value:"+log+"}"
				#log = {'value':log}
				#self.DB.save_data('medicion/log',log)
				self.writeSerial('AT+HTTPTERM\n')
				self.WhileOk(True)
				return response
			else:
				self.connGprs = False
				self.reconnGprs += 1
				self.DisableGprsHttp()
				self.EnableGprsHttp()
		else:
			self.connGprs = False
			self.reconnGprs += 1
			self.DisableGprsHttp()
			self.EnableGprsHttp()




	def HiloSim808(self):
	
		tiempoInicioGprs=0
		tiempoFinalGprs=0
		tiempoTotalGprs=0
		#print ("Hilo de lecturaGps",self.leerGPS)
		while True:
			if self.leerGPS:
				try:
					self.lecturaGps = True
					#print ("Hilo de lecturaGps",self.lecturaGps)
					dataGPS = self.RequestGps()
					#print dataGPS
					#gpio.IndicadorGPS(0.1, True)
					if dataGPS != None:
						if len(dataGPS) > 6 and dataGPS[3] != '': 
							#gpio.IndicadorGPS(0.1, True)
							self.connGps = True
							self.reconnGps = 0
							tiempoFinalGprs= time()
							datelocal = dataGPS[2]
							self.date = datetime.strptime(datelocal,"%Y%m%d%H%M%S.%f").isoformat()
							self.latitude = float(dataGPS[3])
							self.longitude = float(dataGPS[4])
							self.speed = float(dataGPS[6])
							self.acc = dataGPS[10]
							#print("Data GPS",date,latitude,longitude,speed,acc)
							#sim808.SendJsonPostHttp(urlPost,date,latitude,longitude,acc,speed,dataADC1)
							#sleep(timePost)
							
							#tiempoTotalGprs = tiempoFinalGprs - tiempoInicioGprs
							#if tiempoTotalGprs >= 20:
								#gpio.IndicadorGPRS(0.1, True)
							#	tiempoInicioGprs = time()
							#	self.SendJsonPostHttp(self.urlPost,self.date,self.latitude,self.longitude,self.acc,self.speed,self.dataADC1)
							
						else:
							self.connGps = False
							self.reconnGps += 1
							self.date = None
							self.latitude = None
							self.longitude = None
							self.speed = None
							self.acc = None
							sleep(0.1)
							#print("Data GPS",date,latitude,longitude,speed,acc)
							#gpio.IndicadorGPS(0.1, False)
							#gpio.IndicadorGPRS(0.1, False)
						self.lecturaGps = False
				except Exception, e:
					print("Error GetDataGps", str(e))
			sleep(self.timeRate)

	def Inicializar(self):
		try:
			self.Power(True)
			sleep(10)
			self.Echo(True)
			self.verifyStatusSIMCARD()
			self.EnableGPS(True)
			self.EnableGprsHttp()
			
			SIM808 = threading.Thread(target=self.HiloSim808, name='HiloSim808')
			SIM808.start()
			return True
		except Exception, e:
			print("Error Inicializar SIM808", str(e))
			return False

	def read(self):
		return {
			"date":self.date,
			"latitude":self.latitude,
			"longitude":self.longitude,
			"speed":self.speed,
			"acc":self.acc,
			"connGprs":self.connGprs,
			"reconnGprs":self.reconnGprs,
			"connGps":self.connGps,
			"reconnGps":self.reconnGps,
		}