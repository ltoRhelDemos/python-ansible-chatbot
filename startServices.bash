#!/usr/bin/bash

cd /home/chatbot

cp *.service /etc/systemd/system/.

echo -n "Starting Engine : "
systemctl start ansibleChatbotEngine.service 2>/dev/null 
echo `systemctl is-active ansibleChatbotEngine.service`
echo -n "Starting web app : "
systemctl start ansibleChatbotWebInterface.service 2>/dev/null
echo `systemctl is-active ansibleChatbotWebInterface.service`

