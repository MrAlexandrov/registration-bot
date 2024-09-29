#!/bin/bash

# Прерывать выполнение скрипта при ошибке
set -e

echo "Installing make..."
sudo apt update && sudo apt install -y make python3 pip

echo "Initialising venv..."
python3 -m venv .venv
source .venv/bin/activate

echo "Running make install..."
make install