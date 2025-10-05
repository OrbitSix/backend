#!/bin/bash

cd /opt
git clone https://HasanMdArik:$GITHUB_KEY@github.com/orbitsix/backend.git
cd ./backend/
python3 -m venv venv
source venv/bin/activate