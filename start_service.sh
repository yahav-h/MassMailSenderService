#!/usr/bin/env bash
source ./venv/bin/activate
./venv/bin/python3.9 -m pip install -r ./requirements.txt
sudo nohup ./venv/bin/python3.9 mass_mail_sender_service_main.py &