#!/usr/bin/bash

echo -n "Chatbot Engine : "
echo `systemctl is-active ansibleChatbotEngine.service`
echo -n "Chatbot web app: "
echo `systemctl is-active ansibleChatbotWebInterface.service`

