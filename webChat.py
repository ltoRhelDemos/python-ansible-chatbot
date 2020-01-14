# -*- coding: utf-8 -*-

try:
	from flask import request
except: 
	print( 'webChat: flask lib not found'   )
	exit(1)

from  sys import exit, path as syspath, argv
from time import sleep
import json
from inspect import stack
import traceback
import ast
import urllib

_homeDir = None
_serverIp = '0.0.0.0'
_totalAppServers = 1

_webPort = 8080
_enginePort = 9095
_home = "/tmp"
_botName = "BOT" 
_title = "General Purpose Chatter Interface" 
_subtitle = "Created by" 
_comment = "Based on"
_questionSentence = "Your quesion?"
_buttonText = "Ask"

_maxRetry = 3

try:
	from serviceProviderLib import socketClient, humanize_duration, dateTime
except: 
	print( 'webChat: serviceProviderLib not found'   )
	exit(1)

from flask import *

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ansibleChatter!!!'

_uptime = dateTime()
_uptime.startTimer()

_stats = {}

refreshTime = 1

###########
##   P   ##
###########
@app.route("/")
def index():

	# ~ returnValue =  socketClient(host=_serverIp,port=_serverPort,command='commands')
	returnValue={}
	
	returnValue["url for interactive chat"] = "http://ip_address/chat"
	returnValue["API url"] = "http://ip_address/api"
	returnValue["Best if viewed with Chrome JSON Viewer extension"] = "Jan 7th, 2020"
	returnValue["Creation Date"] = "Jan 7th, 2020"
	returnValue["WebChat"] = "WebChat is a simple demonstration application for interacting with a chatbot based on AI"
	returnValue["Based On"] = "Python 3 and Flask"
	returnValue["Latam Technology office"] = "It is a Red Hat Specialized Group for emerging technologies"
	return  json.dumps(returnValue)

###########
##   P   ##
###########
@app.route("/api")
def doCommand():
	returnValue = ''
	#page = request.args.get('listSources', default = 1, type = int)
	#filter = request.args.get('filter', default = '*', type = str)
	_command = request.args.get('command', default = 'about', type = str)
	_arguments = ''

	try:
		for argument in request.args: 
			if (argument != "command"):
				_tempArg = urllib.parse.unquote(argument)
				_arguments += ","+argument+"="+request.args[argument].replace(" ","")
	except:
		print(traceback.format_exc())
	
	_command = (_command+" "+_arguments[1:]).encode("utf8")
	
	try:
		socketData = socketClient(host=_serverIp,port=_enginePort,command=_command)
	except:
		print("ERROR")

	# ~ if not 'refused' in socketData[0]:
		# ~ print("(OK) serving from chatServer on Port %s"%_enginePort)

	if len(socketData):
		try:
			returnValue = socketData[0]
		except:
			print(traceback.format_exc())
	else:
		returnValue = '{status:"ERROR", response={"message":"error accesing the chat engine server"}}'

	return  json.dumps(json.loads(returnValue))


###########
##   P   ##
###########
@app.route("/chat", methods=['GET','POST'])
def form():

	returnValue = ""
	chatTemplate = '''
	<html>

	<head>
	<title>Ansible Chatter</title>
	</head>

	<body>
	<h1 style="color:#a10000;line-height:20px">%s</h1>
	<h2 style="color:#a10000;line-height:5px">%s</h2>
	<h6 style="color:#a10000;line-height:3px">%s</h6>
	<hr	>
	
	<form method="POST">
		%s <input type="text" name="question">
		<input type="submit" value="%s">
		
	</form>	
	<hr>

	<h4 style="color:#05157a;line-height:5px">%s Response</h4>
	<h4 style="border:1px solid #05157a;color:#05157a">%s</h4>

	</body>

	</html>
	'''
	
	if request.method == 'POST':
		question = request.form.get('question')
		
		_command = "chat question=%s"%question.replace(" ","_")
		
		socketData = socketClient(host=_serverIp,port=_enginePort,command=_command.encode("utf8"))
		if len(socketData):
			try:
				returnValue = json.loads(socketData[0])["response"]["answer"]
			except:
				returnValue = "Somethig is wirng acceding the chat engine!"
		else:
			returnValue = "Somethig is wirng acceding the chat engine!"

		return chatTemplate%(_title, _subtitle, _comment, _questionSentence, _buttonText, _botName, "###    "+returnValue)
	
	
	return chatTemplate%(_title, _subtitle, _comment, _questionSentence, _buttonText, _botName, "###    "+returnValue)

###########################################
###########################################
###########################################
if __name__ == "__main__":
	
	
	_helpMessage = "webChat.py webPort=browser_port chatbotEnginePort=chatbot_engine_port homedir=path_to_home botName=BOT title=interfaceTitle subtitle=interface_subtitle comment=third_line_in_the_title_header questionSentence=sentence_in_the_question_box buttonText=text_of_the_action_button"

	for arg in argv:
		if 'help' == arg.split('=')[0].lower() or len(arg) == 0:
			print(_helpMessage)
			exit(1)
      
		if 'homedir' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_homeDir = arg.split('=')[1]
			except Exception as pythonError: 
				pass
					
		if 'engineport' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_enginePort = arg.split('=')[1]
			except Exception as pythonError: 
				pass

		if 'webport' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_webPort = arg.split('=')[1]
			except Exception as pythonError: 
				pass

		if 'botname' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_botName = arg.split('=')[1].replace("_"," ")
			except Exception as pythonError: 
				pass

		if 'title' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_title = arg.split('=')[1].replace("_"," ")
			except Exception as pythonError: 
				pass
					
		if 'subtitle' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_subtitle = arg.split('=')[1].replace("_"," ")
			except Exception as pythonError: 
				pass
				
		if 'comment' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_comment = arg.split('=')[1].replace("_"," ")
			except Exception as pythonError: 
				pass
				
		if 'questionsentence' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_questionSentence = arg.split('=')[1].replace("_"," ")
			except Exception as pythonError: 
				pass
				
		if 'buttontext' == arg.split('=')[0].lower():
			try: 
				if arg.split('=')[1]:
					_buttonText = arg.split('=')[1].replace("_"," ")
			except Exception as pythonError: 
				pass

	
	app.run(host='0.0.0.0', port=_webPort, debug=True, threaded=True)
