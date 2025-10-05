#!/bin/bash

cd /opt
git clone https://HasanMdArik:$GITHUB_KEY@github.com/orbitsix/backend.git
cd ./backend/
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
touch .env
cp service/backend.service /etc/systemd/system
systemctl daemon-reload
systemctl start backend.service
systemctl enable backend.service