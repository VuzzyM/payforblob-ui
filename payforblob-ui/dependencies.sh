#!/bin/bash

# Install Python
if ! command -v python3 &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3
fi

# Install Flask & other dependencies
sudo apt-get install -y python3-pip
pip3 install flask requests
