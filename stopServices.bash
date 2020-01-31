#!/usr/bin/bash

echo -n "Stopping Engine : "
systemctl stop ansibleChatbotEngine.service 2>/dev/null 
echo `systemctl is-active ansibleChatbotEngine.service`
echo -n "Stopping web app : "
systemctl stop ansibleChatbotWebInterface.service 2>/dev/null
echo `systemctl is-active ansibleChatbotWebInterface.service`

