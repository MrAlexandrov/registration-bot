#!/bin/bash

# Прерывать выполнение скрипта при ошибке
set -e

echo "Installing make..."
sudo apt update && sudo apt install -y make python3 pip

echo "Running make install..."
make install