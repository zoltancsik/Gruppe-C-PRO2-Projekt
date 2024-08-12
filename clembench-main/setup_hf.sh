#!/bin/bash
python3 -m venv venv_hf
source venv_hf/bin/activate
pip3 install -r requirements.txt
pip3 install -r requirements_hf.txt
