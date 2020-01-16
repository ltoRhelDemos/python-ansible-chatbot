#https://www.python.org/dev/peps/pep-0263/

# -*- coding: utf-8 -*-
#
#  chatbot.py
#  
#  Copyright 2020 Dirgan <Dirgan@DESKTOP-RJGI65M>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


try:
	from subprocess import STDOUT, PIPE, Popen
except: 
	print( 'subprocess lib not found')
	exit(1)
try:
	from sys import exit
except: 
	print( 'serviceProviderLib: sys lib not found')
	exit(1)
try:
	from time import strftime, time
except: 
	print( 'serviceProviderLib: time lib not found')
	exit(1)
try:
	import os
except: 
	print( 'serviceProviderLib: os lib not found')
	exit(1)
try:
	from datetime import datetime
except: 
	print( 'serviceProviderLib: datetime lib not found')
	exit(1)
try:
	import socket
except: 
	print( 'serviceProviderLib: socket lib not found')
	exit(1)
try:
	from threading import Thread
except: 
	print( 'serviceProviderLib: Thread lib not found')
	exit(1)
try:
	import _thread as thread
except: 
	print( 'serviceProviderLib: thread lib not found')
	exit(1)
try:
	import json
except: 
	print( 'serviceProviderLib: json lib not found'   )
	exit(1)
try:
	import traceback
except: 
	print( 'serviceProviderLib: traceback lib not found'   )
	exit(1)

###########
##   C   ##
###########
def humanize_duration(amount, units='s'):
	INTERVALS = [(lambda mlsec:divmod(mlsec, 1000), 'ms'),
		(lambda seconds:divmod(seconds, 60), 's'),
		(lambda minutes:divmod(minutes, 60), 'm'),
		(lambda hours:divmod(hours, 24), 'h'),
		(lambda days:divmod(days, 7), 'D'),
		(lambda weeks:divmod(weeks, 4), 'W'),
		(lambda years:divmod(years, 12), 'M'),
		(lambda decades:divmod(decades, 10), 'Y')]

	for index_start, (interval, unit) in enumerate(INTERVALS):
		if unit == units:
			break

	amount_abrev = []
	last_index = 0
	amount_temp = amount
	for index, (formula, abrev) in enumerate(INTERVALS[index_start: len(INTERVALS)]):
		divmod_result = formula(amount_temp)
		amount_temp = divmod_result[0]
		amount_abrev.append((divmod_result[1], abrev))
		if divmod_result[1] > 0:
			last_index = index

	amount_abrev_partial = amount_abrev[0: last_index + 1]
	amount_abrev_partial.reverse()

	final_string = ''
	for amount, abrev in amount_abrev_partial:
		final_string += str(amount) + abrev + ' '

	return final_string

###########
##   C   ##
###########
class shellCommand():

	RETURNCODE = 0
	OUTPUT = 1
	NOERROR = 0

#-------------------------------------------------------------------------------------------------------------------
	def __init__(self, command):
#-------------------------------------------------------------------------------------------------------------------
		self.returnCode = 0
		self.commandLine = command
      
#crear run para comandos de background      
#-------------------------------------------------------------------------------------------------------------------
	def run(self, sortedOutput=False):
#-------------------------------------------------------------------------------------------------------------------
		returnOutput=list()
		p = Popen(self.commandLine, shell=True, stdout=PIPE, stderr=STDOUT)
		for i in iter(p.stdout.readline, b''):
			returnOutput.append(str(i, encoding = 'utf-8').strip())
		self.returnCode = p.wait() 

		if sortedOutput:
			commandOutput = sorted(returnOutput)
		else:
			commandOutput = (returnOutput)

		return iter(commandOutput)

#-------------------------------------------------------------------------------------------------------------------
	def runBackground(self):
#-------------------------------------------------------------------------------------------------------------------
		p = Popen(self.commandLine, shell=True, stdout=PIPE, stderr=STDOUT)

		return p

#-------------------------------------------------------------------------------------------------------------------
	def replaceCommand(self, command):
#-------------------------------------------------------------------------------------------------------------------
		self.commandLine = command

		return self
           
#-------------------------------------------------------------------------------------------------------------------
	def status(self):
#-------------------------------------------------------------------------------------------------------------------
		return self.returnCode

        
###########
##   C   ##
###########
class dateTime():
    
#-------------------------------------------------------------------------------------------------------------------
	def __init__(self): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		self.refresh()      
		self.start = datetime.now()
		self.stop  = self.start
		self.elapsed=0
		self.timerStarted = False

		self.refresh()

#-------------------------------------------------------------------------------------------------------------------
	def humanizeElapsed(self): 
#-------------------------------------------------------------------------------------------------------------------
		return humanize_duration(self.elapsed)
       
#-------------------------------------------------------------------------------------------------------------------
	def refresh(self): 
#-------------------------------------------------------------------------------------------------------------------
		dateTime = datetime.now()
		self.dateString = dateTime.strftime('%b %d,%Y')
		self.classicDate = dateTime.strftime('%d/%m/%y')
		self.classicStime = dateTime.strftime('%H:%M:%S')
		self.timeString = dateTime.strftime('%H:%M%P')

		return self

#-------------------------------------------------------------------------------------------------------------------
	def startTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		self.elapsed=0
		self.timerStarted = True
		self.start = datetime.now()

		return self       

#-------------------------------------------------------------------------------------------------------------------
	def stopTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		self.timerStarted = False
		self.stop = datetime.now()

		return self       

#-------------------------------------------------------------------------------------------------------------------
	def timeLapsed(self, p=6, timerId = 'timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0

		if self.timerStarted: 
			self.elapsed = (datetime.now()-self.start).total_seconds()
		else: 
			self.elapsed = (self.stop - self.start).total_seconds()

		return float(self.elapsed)


###########
##   C   ##
###########
class timer():
    
#-------------------------------------------------------------------------------------------------------------------
	def __init__(self): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		self.atTriggered = False
		self.windowError = 5
		self.timers = {}
		self.timers['timer1'] = { 'timerId': 'timer1', 
								'forceTrigger':False,  
								'timeout': 60,
								'at':(),
								'start': 0,
								'stop': 0,
								'started': False,
								'diff': 0,
								'seconds': 0,
								'days': 0,
								'microseconds': 0 }
                                
#-------------------------------------------------------------------------------------------------------------------
	def forceTrigger(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		self.timers[timerId]["forceTrigger"] = True
       
#-------------------------------------------------------------------------------------------------------------------
	def setTimer(self, timerId='timer1', timeoutinseconds=60, startNow=False): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		try: 
			self.timers[timerId] = { 'timerId': timerId, 
									'timeout': timeoutinseconds,
									'at':(),
									'start': 0,
									'stop': 0,
									'started': False,
									'diff': 0,
									'seconds': 0,
									'days': 0,
									'microseconds': 0 }
			returnValue = timerId                         
		except: 
			self.error = -1
          
		if startNow: self.startTimer(timerId=timerId)   

		return self 
       
#-------------------------------------------------------------------------------------------------------------------
	def setTimerEvery(self, timerId='timer1', timeoutinseconds=60, startNow=False): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		try: 
			self.timers[timerId] = { 'timerId': timerId, 
			'timeout': timeoutinseconds,
			'at':(),
			'start': 0,
			'stop': 0,
			'started': False,
			'diff': 0,
			'seconds': 0,
			'days': 0,
			'microseconds': 0 }
			returnValue = timerId                         
		except: 
			self.error = -1

		if startNow: self.startTimer(timerId=timerId)   

		return self 

#-------------------------------------------------------------------------------------------------------------------
	def setTimeout(self, timerId='timer1', timeoutinseconds=60): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0     
		try: 
			self.timers[timerId]['timeout'] = timeoutinseconds
			returnValue = timeoutinseconds 
		except: 
			self.error = -1

		return self
       
#-------------------------------------------------------------------------------------------------------------------
	def trigger(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		returnValue = False
       
		if not (self.timers[timerId]['forceTrigger']):        
			if (self.timers[timerId]['started']): 
				try: 
					if self.timeLapsed(timerId=timerId) > self.timers[timerId]['timeout']: 
						returnValue = True
				except: 
					self.error = -1
			else:
				self.startTimer(timerId=timerId)
				returnValue=True
		else:
			self.startTimer(timerId=timerId)
			self.timers[timerId]['forceTrigger'] = False
			returnValue=True

		return returnValue
             
#-------------------------------------------------------------------------------------------------------------------
	def startTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		try: 
			self.timers[timerId]['started'] = True
		except: 
			self.error = -1
		try: 
			self.timers[timerId]['start'] = datetime.now()
		except: 
			self.error = -1

		return self       

#-------------------------------------------------------------------------------------------------------------------
	def stopTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		try: 
			self.timers[timerId]['started'] = False
		except: 
			self.error = -1
		try: 
			self.timers[timerId]['stop'] = datetime.now()
		except: 
			self.error = -1

		self.timeDifference(timerId=timerId)

		return self       

#-------------------------------------------------------------------------------------------------------------------
	def timeLapsed(self, p=6, timerId = 'timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		precisionTimeElapsed = 0.0
		try: 
			if self.timers[timerId]['started']: 
				precisionTimeElapsed=(datetime.now() - self.timers[timerId]['start']).total_seconds()
			else: 
				precisionTimeElapsed=self.timers[timerId]['diff']
		except: 
			self.error = -1

		return precisionTimeElapsed

#-------------------------------------------------------------------------------------------------------------------
	def isStarted(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		return self.timers[timerId]['started']

#-------------------------------------------------------------------------------------------------------------------
	def timeDifference(self, p=6, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		try: 
			self.timers[timerId]['diff'] = (self.timers[timerId]['stop'] - self.timers[timerId]['start']).total_seconds()
			returnValue = self.timers[timerId]['diff']
			self.timers[timerId]['seconds'] = self.timers[timerId]['diff'].total_seconds()
			self.timers[timerId]['days'] = self.timers[timerId]['diff'].days
			self.timers[timerId]['microseconds'] = self.timers[timerId]['diff'].microseconds
		except: 
			self.error = -1

		return self

#-------------------------------------------------------------------------------------------------------------------
	def setCron(self, cronId='timer1', at=(0,)): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0

		#define at as an array in format hh.mm, or mm

		_at=[]
		for _minute in at:
			_m = int(_minute)
			_at.append(_m if _m in range(0,60) else 0)
       
		try: 
			self.timers[cronId] = { 'timerId': cronId, 
									'timeout': 0,
									'at':set(_at),
									'atTriggered':False,
									'start': 0,
									'stop': 0,
									'started': True,
									'diff': 0,
									'seconds': 0,
									'days': 0,
									'microseconds': 0 }
			returnValue = self                         

		except Exception as error:
			print(error)
			self.error = -1
          
		return self 

#-------------------------------------------------------------------------------------------------------------------
	def setCron1(self, cronId='timer1', at=(0,)): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0

		#define at as an array in format hh.mm, or mm

		_at=[]
		for _minute in at:
			_m = int(_minute)
			_at.append(_m if _m in range(0,60) else 0)
       
		try: 
			self.timers[cronId] = { 'timerId': cronId, 
									'timeout': 0,
									'at':set(_at),
									'atTriggered':False,
									'start': 0,
									'stop': 0,
									'started': True,
									'diff': 0,
									'seconds': 0,
									'days': 0,
									'microseconds': 0 }
			returnValue = self                         

		except Exception as error: 
			print(error)
			self.error = -1

		return self 

#-------------------------------------------------------------------------------------------------------------------
	def triggerCron(self, cronId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		returnValue = False

		try:
			tId = self.timers[cronId]['timerId']

			hour = int(datetime.now().strftime('%H'))
			minute = int(datetime.now().strftime('%M'))
			second  = int(datetime.now().strftime('%S'))

			#at = (0,5,59)
			for _minute in self.timers[cronId]['at']:
				if minute == _minute and (second >= 0 and second <= self.windowError): #this is a window second window to trigger
					if not self.atTriggered:
						self.atTriggered = True
						returnValue = True
						break
				elif second > self.windowError:
					self.atTriggered = False          
		except Exception as error:
			self.setCron(cronId = cronId)
			print(error)

		return returnValue

#-------------------------------------------------------------------------------------------------------------------
	def triggerCron1(self, cronId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
		self.error = 0
		returnValue = False
		try:
			tId = self.timers[cronId]['timerId']

			hour = int(datetime.now().strftime('%H'))
			minute = int(datetime.now().strftime('%M'))
			second  = int(datetime.now().strftime('%S'))

			#at = (0,5,59)
			for _minute in self.timers[cronId]['at']:
				#~ print( "checking entry %d (now is %d:%d)"%(_minute, minute, second)
				if type(_minute) == float:
					_hour = int(_minute)
					_minutes = int((_minute - int(_minute))*100)
				else:
					_hour = -1
					_minutes = _minute

				print( _hour)
				print( _minutes   )

				if minute == _minute and (second >= 0 and second <= self.windowError): #this is a window second window to trigger
					if not self.atTriggered:
						self.atTriggered = True
						returnValue = True
						break
				elif second > self.windowError:
					self.atTriggered = False          
		except Exception as error:
			self.setCron(cronId = cronId)
			print(error)

		return returnValue



###########
##   P   ##
###########
#-------------------------------------------------------------------------------------------------------------------
def socketClient(host='localhost', port=6600, command=''):
#-------------------------------------------------------------------------------------------------------------------
	RECV_SIZE = (2**20)*10 #10 megabytes
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	returnData = []

	try:
		s.connect((host, int(port)))
		if command: s.send(command)
		s.shutdown(socket.SHUT_WR)

		tempData = ''
		while True:
			data = s.recv(RECV_SIZE)
			if data: tempData += data.decode("utf-8")
			if not data:
				break
		s.close()    
		
		returnData = ''.join(tempData).splitlines() 

	except Exception as error: 
		returnData.append(str(error)) 


	return returnData
	
	
###########
##   C   ##
###########
class socketServer():
	STOPLISTENING = False
#-------------------------------------------------------------------------------------------------------------------
	def __init__(self, host='0.0.0.0', port=6768, bufferSize=50*1024, verbose = False):
#-------------------------------------------------------------------------------------------------------------------
		self.resetError()
		self.verbose =  verbose
		self.STOPLISTENING = False
		self.host=host
		self.port=port
		self.function = None
		self.handlerProc = None
		self.bufferSize=bufferSize
		self.socket = None

		try: 
			self.ADDR = (self.host, self.port)
			self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.serversock.bind(self.ADDR)
			self.serversock.listen(5)
		except Exception as err:
			self.errorMessage = err
			self.error = True 

#-------------------------------------------------------------------------------------------------------------------
	def resetError(self):
#-------------------------------------------------------------------------------------------------------------------
		self.error = False
		self.errorMessage = ''

#-------------------------------------------------------------------------------------------------------------------
	def getError(self):
#-------------------------------------------------------------------------------------------------------------------
		returnValue = { 'gotError' : self.error, 'message':self.errorMessage }

		return returnValue
      
#-------------------------------------------------------------------------------------------------------------------
	def setHost(self, host):
#-------------------------------------------------------------------------------------------------------------------
		self.host = host
		return self

#-------------------------------------------------------------------------------------------------------------------
	def setPort(self, port):
#-------------------------------------------------------------------------------------------------------------------
		self.port = port
		return self

#-------------------------------------------------------------------------------------------------------------------
	def setBufSize(self, sizeInBytes):
#-------------------------------------------------------------------------------------------------------------------
		self.bufferSize = sizeInBytes
		return self

#-------------------------------------------------------------------------------------------------------------------
	def start(self, inBackground=False):
#-------------------------------------------------------------------------------------------------------------------
		if not self.error:
			if inBackground: 
				thread.start_new_thread(self.listen,())
			else: 
				self.listen()

#-------------------------------------------------------------------------------------------------------------------
	def closeSocket(self):
#-------------------------------------------------------------------------------------------------------------------
		try:
			self.socket.close()
		except:
			pass      
            
#-------------------------------------------------------------------------------------------------------------------
	def listen(self):
#-------------------------------------------------------------------------------------------------------------------
		if self.error: return

		while not self.STOPLISTENING:
			if self.verbose: print( 'waiting for connection... listening on port', self.port)
			(clientsock, addr) = self.serversock.accept()
			if not self.STOPLISTENING: 
				thread.start_new_thread(self.handler, (clientsock, addr))

#-------------------------------------------------------------------------------------------------------------------
	def handler(self,clientsock,addr):
#-------------------------------------------------------------------------------------------------------------------
		if self.error: return
		self.socket = clientsock
		while True:
			try: 
				data = clientsock.recv(self.bufferSize)
			except Exception as err: 
				self.error = True
				self.errorMessage = err
				print(err)
				break

			if not data: break
			if self.verbose: print( repr(addr) + ' recv:' + repr(data))
			

			try:
				if self.handlerProc != None: 
					clientsock.send(bytearray(self.handlerProc(data),"utf-8"))
				else: 	
					clientsock.send(data)

			except Exception as err: 
				print("4:",err)
				print( traceback.format_exc())
				self.error = True
				self.errorMessage = err
				break
               
			break


		try:  
			clientsock.close()
			if self.verbose: print( 'closing socket')
		except Exception as err: 
			self.error = True
			self.errorMessage = err

		if self.verbose: print( addr, '- closed connection on port %s'%self.port)

#-------------------------------------------------------------------------------------------------------------------
	def stop(self):
#-------------------------------------------------------------------------------------------------------------------
		if not self.error:
			socketClient(port=self.port, command='stopServer67680512')

#-------------------------------------------------------------------------------------------------------------------
	def setBehavior(self, func):
#-------------------------------------------------------------------------------------------------------------------
		self.handlerProc = func
		return self

###########
##   C   ##
###########
#------------------------------------------------   
class runInBack():
#------------------------------------------------   

#------------------------------------------------
	def __init__(self, _process, _args=()):
#------------------------------------------------
		self.process = _process
		self.args = _args
		self.process = Thread(target=_process, args=_args)
		self.process.deamon = True
		self.lastError = ''
		self.finished = False
      
#------------------------------------------------
	def start(self):
#------------------------------------------------
		try:
			self.process.start()
		except:
			self.lastError = "Error: unable to start thread"
			print( self.lastError)
  
#------------------------------------------------
	def isAlive(self):
#------------------------------------------------
		return self.process.isAlive()

#------------------------------------------------
	def join(self):
#------------------------------------------------
		return self.process.join()
         
#------------------------------------------------
	def stop(self):
#------------------------------------------------
		try:
			self.process._Thread__stop()
			self.process.join()
			self.finished = True     
		except:
			self.lastError = str(self.getName()) + ' could not be terminated'
			print((self.lastError))

############################################
############################################
############################################
if __name__ == "__main__":
	pass
