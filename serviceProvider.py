#https://www.python.org/dev/peps/pep-0263/t

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
import os, sys, signal
from time import sleep, time
import traceback
import threading
from serviceProviderLib import socketServer, socketClient
from serviceProviderLib import dateTime, runInBack
from serviceProviderLib import shellCommand, humanize_duration
from chatbotLib import ltoChatbot
import json
from datetime import datetime
from inspect import stack

################################################################################################################         
## class for creating a service provider using sockets - tested on Ubuntu, Raspbian                           ##         
## Alejandro Dirgan - 2017                                                                                    ##
################################################################################################################         
class serviceProvider():
	HOMEPATH = '/tmp'
	PORT = 9095
	SERVICENAME_VERSION = '0.1'

#HISTORY OF CHANGES
#  0.1    creation
#  0.1.1  add serverName, check existance of homedir, better error habdle at main, change default port to 3533
#  0.1.2  change naming from tcpserver to serviceProvider (generic)

#-------------------------------------------------------------------------------------------------------------------
	def __init__(self, host='0.0.0.0', port=None, bufferSize=10*1024, homePath=None, serviceName='tcpServer', dbServer = ('0.0.0.0',7075), appServersInfo = [('0.0.0.0',7080),('0.0.0.0',7081),('0.0.0.0',7082),('0.0.0.0',7083),('0.0.0.0',7084)], verbose = False, debug=False):
#-------------------------------------------------------------------------------------------------------------------
      
		self.pid = os.getpid()
		self.errorMessage = ''
		self.errorCode = 0
		self.error = False
		self.serviceName = serviceName
		self.defaultUser = self.serviceName
		self.home = os.path.abspath(homePath)
		self.initFile = self.home+'/'+self.serviceName+'.pid'
		self.finishFile = self.home+'/'+self.serviceName+'.stop'
		self.verbose = verbose
		self.spaceSeparator = '_'
		self.debug=debug
		self.header = False
		self.time2saveContext = 10
		self.module = self.serviceName
      
		self.adminEmail = 'alejandro.dirgan@gmail.com'

		self.lockTcpServer = threading.Lock()
			
		self.uptime = dateTime()
		self.uptime.startTimer()
		self.host=host

		self.pageSize = 20

		self.somethingToWrite = False

		self.avoidCharsArray = ["'","(",")","[","]","{","}","<",">",",",".","?","^","%","$","#","@","!","|",":",";","~"," -",'"']

		if os.path.isfile(self.finishFile): 
			shellCommand('rm %s'%(self.finishFile)).run()
      
		# ~ for i in shellCommand('ps -ef | grep %s.py | grep -v grep  | grep -v %s | wc -l'%(self.serviceName, self.serviceName)).run():
			# ~ processCount = int(i)

		# ~ if processCount > 2: 
			# ~ print('(init) there is another instance of %s running... exiting'%(self.serviceName))
			# ~ exit(1)
         
		if port == None:
			self.port = self.PORT
		else:
			if port < 1000 or port > 9999:   
				self.errorMessage = 'port number have to be in range of 1000 - 9999'
				self.errorCode = 1004
				self.error = True
				print(self.errorMessage)
				exit(1)
			else:
				self.port = port   
      
		self.version = self.serviceName + ' ' + self.SERVICENAME_VERSION
   
		if not os.path.isdir(self.home): 
			self.errorMessage = 'home directory %s does not exists'%self.home
			self.errorCode = 1001
			self.error = True
			print(self.errorMessage)
			exit(1)
			
		print(not os.path.isfile(self.initFile))
		print(self.initFile)	

		shellCommand('echo %s > %s'%(self.pid,self.initFile)).run()
      
		print( '(init) starting %s!'%self.serviceName)
		print( '(init) home directory is %s'%(self.home))


		if '(OK)' in socketClient(host=self.host,port=self.port,command='about')[0]:
			print( '(init) there is another instance of %s running... exiting'%(self.serviceName))
			shellCommand('rm %s'%self.initFile).run()
			exit(1)
         
		self.bufferSize = bufferSize
		self.loopDelay = .7
		self.tcpServerExit = False
				   
		self.defineMessages()

		print( '(init) listening on port %s'%self.port)
		print( '(init) this process is identified by: %s'%self.pid)

		self.socketServer = socketServer(host=self.host, port=self.port) 
		self.socketServer.setBehavior(self.tcpServer).start(inBackground=True)

		self.returnStats = {
			"host":host,
			"port":port,
		}
		
		self.chatBot = ltoChatbot(corpusFile="Ansible_Corpus.json", forceTraining=False, levels=2, iterations = 300)

#------------------------------------------------   
	def start(self):
#------------------------------------------------   
		self.eventLoop()      

#-------------------------------------------------------------------------------------------------------------------
	def _logError(self, message):
#-------------------------------------------------------------------------------------------------------------------
		self.errorLog.logMessage(message)

#-------------------------------------------------------------------------------------------------------------------
	def _logMessage(self, message, user = None, verbose = False):
#-------------------------------------------------------------------------------------------------------------------
		if verbose:
			if user != None:
				message += ', executed by %s'%user

#-------------------------------------------------------------------------------------------------------------------
	def defineMessages(self):
#-------------------------------------------------------------------------------------------------------------------
		self.helpMessage = {
		'chat'                              : 'USAGE: chat question=sentence [help]\n',
		'about'                             : 'USAGE: about [help]\n',
		'uptime'                            : 'USAGE: uptime [help]\n',
		'getpid'                            : 'USAGE: getPid token=secret | [help]\n',
		'commands'                          : 'USAGE: commands [filter=word] [help]\n',
		'help'                              : 'USAGE: help [filter=word] [help]\n',
		'stop'                              : 'USAGE: stop [help]\n',
		'getstats'                          : 'USAGE: getStats [help]\n',
		}
      
		self.severity  = { 'ok': '(OK)',
		'info': '(INFO)',
		'warning': '(WARNING)',
		'error': '(ERROR)',
		'panic': '(PANIC)',
		}
      
#-------------------------------------------------------------------------------------------------------------------
	def getError(self):
#-------------------------------------------------------------------------------------------------------------------
		returnValue = {'error':self.error,
		'errorCode': self.errorCode,
		'errorMessage': self.errorMessage
		}

		return returnValue

#-------------------------------------------------------------------------------------------------------------------
	def check4ExitFile(self):
#-------------------------------------------------------------------------------------------------------------------
		if os.path.exists(self.finishFile):
			self.tcpServerExit = True
			shellCommand('rm %s'%self.finishFile).run()
			self.stopServer(0,0)

#-------------------------------------------------------------------------------------------------------------------
	def eventLoop(self):
#-------------------------------------------------------------------------------------------------------------------
		self.updateDB = True
		print( '(eventLoop) entering event loop!')

		self.countSongs = 1

		songPercent = 0         

		self.artist = ''

		#~ self.timers.startTimer(timerId='commitUserDB')
      
		while not self.tcpServerExit:
			self.lockTcpServer.acquire()
			try:         
				pass
			
			#~ if self.timers.trigger(timerId='checkDBServer'):
				#~ runInBack(self.checkDBServer).start()
				#~ self.timers.startTimer(timerId='checkDBServer')
          
			except Exception as pythonError: 
				print( "(eventLoop) Error:")
				if self.debug: print( traceback.format_exc())
			finally:
				self.lockTcpServer.release()
         
			sleep(self.loopDelay)   

		#*** END OF Eventloop

		print( '(eventLoop) %s has been stopped gracefully!'%self.serviceName)
      
#-------------------------------------------------------------------------------------------------------------------
	def Jsonize(self, _status, _response):
#-------------------------------------------------------------------------------------------------------------------
		rvalue = {'status':_status,'response':_response}
		return json.dumps(rvalue)+'\n'

#-------------------------------------------------------------------------------------------------------------------
	def doStopServer(self):
#-------------------------------------------------------------------------------------------------------------------
		self.stopServer(0,0)

#-------------------------------------------------------------------------------------------------------------------
	def stopServer(self, signum, frame):
#-------------------------------------------------------------------------------------------------------------------
		print( '(stopServer) stopping %s after %s'%(self.serviceName,humanize_duration(self.uptime.timeLapsed())))

		self.socketServer.stop()
      
		if os.path.isfile(self.initFile): #or forceStart:
			shellCommand('rm %s'%self.initFile).run()
		else:
			print( '(init) control file %s was not found'%(self.serviceName,self.initFile))
			exit(1)

		self.tcpServerExit = True

#-------------------------------------------------------------------------------------------------------------------
	def normalizeParameters(self, fpars,p1024,ars):
#-------------------------------------------------------------------------------------------------------------------
		for key in pars:
			try: 
				fpars[key] = pars[key].replace('#',' ')
			except Exception as pythonError: 
				if self.debug: self.errorLog(traceback.format_exc())
				fpars[key] = ''

#-------------------------------------------------------------------------------------------------------------------
	def tcpServer(self, command):
#-------------------------------------------------------------------------------------------------------------------
		#print( stack()[1][3])
		returnValue = ''
		#rules: p1=value,p2=value,..,pn=value
		#rules: no spaces beetwen parameters
		#rules: if strings are needed as value of parameter replace spaces by self.spaceSeparator
		#rules: p1="do this thing" must be specified as p1=do_this_thing
		self.lockTcpServer.acquire()
		try:
			try:
				if self.debug:
					print( '(tcpServer) processing requirement')

				command_decoded = command.decode("utf-8")
				
				parameters = {}
				
				if len(command_decoded.split(' ')) == 1:
					cmd = command_decoded             
				else:   
					# ~ cmd = command_decoded.replace('\'', '').split(' ')
					cmd = command_decoded.split(' ')
					prmts=cmd[1]
					cmd = cmd[0].strip()
					
					# ~ for dupla in prmts.replace('\'', '').split(','):
					for dupla in prmts.split(','):
						p1=''
						p2=''
						parameter = dupla.split('=')
						p1=parameter[0].strip().lower()
						try:
							p2=parameter[1]
						except Exception as err: 
							p2=None             
						
						parameters[p1]=p2   
			 
				if self.debug:
					print( '(tcpServer) command: %s'%cmd)
					print( '(tcpServer) parameters %s'%parameters)


				returnValue = self.executeCommandProcedure(cmd,parameters)
						
			except Exception as err: 
				print( '(tcpServer) command error: %s\n'%err)
				returnValue = '%s command not executed\n'%(self.severity['error'])
		except Exception as err:
			print( '(tcpServer) command error: %s\n'%err)
			

		finally:
			self.lockTcpServer.release()

		return returnValue
      
#-------------------------------------------------------------------------------------------------------------------
	def executeCommandProcedure(self, command, parameters):
#-------------------------------------------------------------------------------------------------------------------
		#this is the behavior section of the service provider
		#in this section we can add functionality
		#  first, create an elif command subsection
		#  elif command == "command_name": where command_name must be in lowercase

		command = command.replace("'",'').lower().strip()
		
		returnValue = ''
		executeCommandError = False
		executeCommandString = ''
		executeCommand = True
		activeVars = {}   
		pythonError = ''

		header=self.header
		
		try:
			if parameters['headeron']==None: 
				header = True
		except Exception as pythonError:
			pass
			##if self.debug: print((traceback.format_exc()) )

		try: 
			if parameters['help'] == None: 
				try: 
					returnValue = self.helpMessage[command]
				except Exception as pythonError:
					if self.debug: self.errorLog(traceback.format_exc())
					returnValue = self.Jsonize(self.severity['error'],'help not available for <command> %s'%command)

			return returnValue
		except Exception as pythonError: 
			pass
			#if self.debug: print((traceback.format_exc()) )
         
		################################# 
		################################# Help Commands
		#################################
		########################################################################################
		
		if command == 'chat': 
			_result = {}

			try: 
				_question = parameters['question'].replace("_"," ")
			except Exception as pythonError: 
				_question=''

			if not executeCommandError and executeCommand:
				returnValue = self.Jsonize(self.severity['ok'],self.chatBot.askBot(question=_question, accuracy=.8))

		########################################################################################
		
		elif command == 'about': 
			if not executeCommandError and executeCommand:
				returnValue = self.Jsonize(self.severity['ok'],self.version)

		########################################################################################
		elif command == 'uptime': 
			if not executeCommandError and executeCommand:
				returnValue = self.Jsonize(self.severity['ok'],humanize_duration(self.uptime.timeLapsed()))

		########################################################################################
		elif command == 'stop': 

			if not executeCommandError and executeCommand:
				self.stopServer(0,0)
				returnValue = '%s\n'%self.severity['ok']

		########################################################################################
		elif command == 'getstats': 
			self.returnStats["uptime"] = humanize_duration(self.uptime.timeLapsed())   
			if not executeCommandError and executeCommand:
				try:
					returnValue = self.Jsonize(self.severity['ok'],{'stats':self.returnStats})
				except:
					print( traceback.format_exc())

		########################################################################################
		elif command == '': 
			if not executeCommandError and executeCommand:
				returnValue = self.Jsonize(self.severity['ok'],'OK')
         
		########################################################################################
		elif command == 'commands': 
			_result = {}
			commandName = ''
			commandParameters = []

			try: 
				_filter = parameters['filter']
			except Exception as pythonError: 
				_filter=''
         
			for key in sorted(self.helpMessage): 
				if _filter in key:
					commandName = self.helpMessage[key].split('USAGE: ')[1].split()[0]
					commandParameters = self.helpMessage[key].split('USAGE: ')[1].replace("\n","")
					_result[commandName] = commandParameters
               
			returnValue = self.Jsonize(self.severity['ok'],{"commands":_result})
   
      ########################################################################################
		elif command == 'getpid': 

			if not executeCommandError and executeCommand:
				returnValue = self.Jsonize(self.severity['ok'],self.pid)

			########################################################################################
			#elif command == 'new_behavior_command':
			#   -- This first section is for parse parameters of the command. If no partameter are needed
			#   -- remove this section. If params are needed parse them. Each parameter is added to the list parameters
			#   -- so we can determine its values.
			#   -- activeVars list is just a list that can be used instead of volatile variables to store the paramater
			#   -- and the use it.
			#   -- you can use volatile variables instead to handle the parameters, ie. param_1
			#   -- parameters with spaces has to be replaced with "_", so for example.
			#   -- command: nameLight name=thomas_edison
			#   -- the command is  nameLight and the parameter is name which value is thomas_edison. 
			#   -- .replace(self.spaceSeparator,' ') change "_" for a space to have "thomas Edison" as the real value
			#   try: 
			#      activeVars['parameter_name_1'] = parameters['parameter_name_1'].replace(self.spaceSeparator,' ') #or
			#      #param_1 = parameters['parameter_name_1'].replace(self.spaceSeparator,' ')
			#   except Exception as pythonError: 
			#      activeVars['parameter_name_1'] = None OR executeCommand=False

			#   try: 
			#      activeVars['parameter_name_n'] = parameters['parameter_name_n'].replace(self.spaceSeparator,' ')
			#   except Exception as pythonError: 
			#      activeVars['parameter_name_n'] = None OR executeCommand=False

			#   try:
			#      -- parameters are in activeVars list or volatile variables
			#      if not executeCommandError and executeCommand:
			#         --- execution of actions for this behavior
			#         returnValue = '%s message of no error\n'%(self.severity['ok'],) 
			#      else:
			#         returnValue = '%s message of error\n'%(self.severity['error'],) 

			#   except Exception as pythonError:
			#      if self.debug: print((traceback.format_exc()) )
			#      executeCommandError = True  
			#      returnValue = '%s <%s> not executed\n'%(self.severity['error'], command)
			########################################################################################
		else: 
			executeCommandError = True  
			executeCommandString = '(tcpServer) unknown command <%s>'%command
			returnValue = self.Jsonize(self.severity['error'],'unknown command')
      
		if self.verbose and executeCommandError: 
			if executeCommandString == '':
				executeCommandString = '(tcpServer) <%s> command error:\n\n %s'%(command,pythonError)  


      
		return returnValue

###########
##   P   ##
###########
#-------------------------------------------------------------------------------------------------------------------
def stopServerHandler(signum, frame):
#-------------------------------------------------------------------------------------------------------------------
	print( 'Stopping the service by an external signal!')
	stop()


##########################################################
### BEGIN MAIN          ##################################
##########################################################
##########################################################
#--------------------------------------------------------      
def printBanner():
	print( '''
  _____          _   _    _       _   
 |  __ \        | | | |  | |     | |  
 | |__) |___  __| | | |__| | __ _| |_ 
 |  _  // _ \/ _` | |  __  |/ _` | __|
 | | \ \  __/ (_| | | |  | | (_| | |_ 
 |_|  \_\___|\__,_| |_|  |_|\__,_|\__|

  Ansible AI Chatbot Demo
  Alejandro Dirgan 2019  
  Latam Technology Office
                
	''')
   
#--------------------------------------------------------      
if __name__ == '__main__':
#--------------------------------------------------------      
	_homeDir = None
	_port = None
	_serviceName = None
	_verbose = False

	_defaultPort = 9095
	_defaultHome = '/tmp'
	_defaultServiceName = 'serviceProvider'
   
	for arg in sys.argv:
		if 'help' in arg.lower():
			print( 'serviceProvider.py [port=%s] [homedir=%s] serviceName=%s] [verbose=True]'%(_defaultPort, _defaultHome, _defaultServiceName))
			exit(1)

		if 'verbose' in arg.lower():
			try: 
				if arg.split('=')[1] == 'True':
					_verbose = True
				elif arg.split('=')[1] == 'False':
					_verbose = False
				else:
					_verbose = False
			except Exception as pythonError: 
				pass
         
      
		if 'homedir' in arg.lower():
			try: 
				if arg.split('=')[1]:
					_homeDir = os.path.abspath(arg.split('=')[1])
					print( '(OK) HOME directory was supplied as homeDir=%s'%_homeDir)
			except Exception as pythonError: 
				pass
      
		if 'port' in arg.lower():
			try: 
				if arg.split('=')[1]:
					_port = int(arg.split('=')[1])
					print( '(OK) PORT was supplied as port=%d'%_port)
			except Exception as pythonError: 
				pass

		if 'servicename' in arg.lower():
			try: 
				if arg.split('=')[1]:
					_serviceName = arg.split('=')[1]
					print( '(OK) SERVICENAME was supplied as %s'%_serviceName)
			except Exception as pythonError: 
				pass
            
	print( '--------------------------------------------------------------------------')
	printBanner()        

	if _homeDir == None:
		_homeDir = _defaultHome

	if _port == None:
		_port=_defaultPort

	if _serviceName == None:
		_serviceName=_defaultServiceName

	if not os.path.isdir(_homeDir): 
		print( "(ERROR) homeDir=%s does not exists"%_homeDir)
		exit(1)   
        
	try:
		print( '--------------------------------------------------------------------------')
		print( 'HELP:')
		print( '--------------------------------------------------------------------------')
		print( 'to start server using other than default values use it with the paramaters:')
		print( '   serviceProvider.py [port=%s] [homedir=%s] [serviceName=%s] [verbose=True]'%(_port,_homeDir, _serviceName))
		print()
		print( 'to stop the server:')
		print( '   touch %s/%s.stop'%(_homeDir, _serviceName))
		print()
		print( 'to send command to server via command line where 0.0.0.0 is the ip (localhost)')
		print( '   echo about | nc 0.0.0.0 %s'%_port)
		print()
		print( '--------------------------------------------------------------------------')
		print( 'INFO:')
		print( '--------------------------------------------------------------------------')
		server = serviceProvider(port=_port, homePath=_homeDir, serviceName=_serviceName, verbose=_verbose, debug=False)

		global stop
		stop = server.doStopServer
		signal.signal(signal.SIGINT, stopServerHandler)
		signal.signal(signal.SIGTERM, stopServerHandler)

		server.start()

	except Exception as pythonError: 
		print((traceback.format_exc()))


