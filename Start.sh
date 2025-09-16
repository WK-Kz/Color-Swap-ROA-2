#!/bin/bash

if command -v python3 &>/dev/null; then
  echo "Python 3 is installed."
else
  echo "Python 3 is not installed"
  echo "Exiting"
  exit
fi

python3 couleur.py
