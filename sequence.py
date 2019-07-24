import serial

port = '/dev/ttyS1'
serial_com = serial.Serial(port, timeout=30)

def wait_response(debug=False,command='OK'):
	global serial_com
	array_res = []
	while True:
		lineData = serial_com.readline()
		lineData = lineData.rstrip('\r\n')
		if debug:
			print "Received: "+ lineData
		if lineData == '':
			continue
		else:
			array_res.append(lineData)
		if lineData.find(command)==0:
			return True,array_res
		elif lineData.find("ERROR")==0:
			return False,array_res

def init_gprs():	
	serial_com.write(bytes('AT+CPIN?\n'))
	print wait_response()
	serial_com.write(bytes('AT+CREG?\n'))	#Network Registration 
	print wait_response()
	serial_com.write(bytes('AT+CGATT?\n'))	#Attach or Detach from GPRS Service 
	print wait_response()
	serial_com.write(bytes('AT+SAPBR=3,1,"CONTYPE","GPRS"\n'))	#Bearer Settings for Applications Based on IP 
	print wait_response()										#3 Set bearer parameters 
	#self.ser.write('AT+SAPBR=3,1,"APN","internet.comcel.com.co"\n'');
	serial_com.write(bytes('AT+SAPBR=3,1,"APN","internet.movistar.com.co"\n'))	#Bearer Settings for Applications Based on IP 
	print wait_response()														#3 Set bearer parameters 
	serial_com.write(bytes('AT+SAPBR=1,1\n'))	#Bearer Settings for Applications Based on IP 
	print wait_response()						#1 Open bearer 
	serial_com.write(bytes('AT+SAPBR=2,1\n'))
	print wait_response()	

def http_get(url):
	serial_com.write(bytes('AT+HTTPINIT\n'))
	print wait_response()
	serial_com.write(bytes('AT+HTTPPARA="CID",1\n'))
	print wait_response()
	serial_com.write(bytes('AT+HTTPPARA="URL","%s"\n' % (url)))
	print wait_response()
	serial_com.write(bytes('AT+HTTPACTION=0\n'))
	print wait_response(False,'+HTTPACTION')
	serial_com.write(bytes('AT+HTTPREAD\n'))
	print wait_response()
	serial_com.write(bytes('AT+HTTPTERM\n'))
	print wait_response()


def http_post(url,data):
	serial_com.write(bytes('AT+HTTPINIT\n'))
	print wait_response()
	serial_com.write(bytes('AT+HTTPPARA="CID",1\n'))
	print wait_response()
	serial_com.write(bytes('AT+HTTPPARA="URL","%s"\n' % (url)))
	print wait_response()
	serial_com.write(bytes('AT+HTTPPARA="CONTENT","application/json"\n'))
	print wait_response()
	serial_com.write(bytes('AT+HTTPDATA=%d,10000\n' % (len(data))))
	print wait_response(False,'DOWNLOAD')
	serial_com.write(bytes(data))
	print wait_response()
	serial_com.write(bytes('AT+HTTPACTION=1\n'))
	print wait_response(False,'+HTTPACTION')
	serial_com.write(bytes('AT+HTTPREAD\n'))
	print wait_response()
	serial_com.write(bytes('AT+HTTPTERM\n'))
	print wait_response()


init_gprs()
http_get('http://agrorealtime.herokuapp.com/tracking?sort=createdAt%20DESC&limit=10')
http_get('http://agrorealtime.herokuapp.com/tracking?sort=createdAt%20DESC&limit=10')
http_get('http://agrorealtime.herokuapp.com/tracking?sort=createdAt%20DESC&limit=10')
data = '{"acc":0.9,"temperatura":"0","date":"2017-08-23T05:41:33.000Z","speed":7.54,"long":-76.463447,"id_device":"1","encendido":"1","lat":3.491068,"rpm":"0"}'
http_post('http://agrorealtime.herokuapp.com/tracking',data)
