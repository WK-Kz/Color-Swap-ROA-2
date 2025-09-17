#!/bin/bash

if command -v python3 &>/dev/null; then
  echo "[INFO] - SUCCESS -- Python 3 is installed."
  if command -v wine &>/dev/null; then
    echo "[INFO] - SUCCESS -- Wine has been detected in path."
  else
    echo "[INFO] - WARNING -- Wine is not detected in path, checking flatpak path"
    WINE_PACKAGE=org.winehq.Wine
    flatpak info ${WINE_PACKAGE} >/dev/null 2>&1
    if [ $? -eq 0 ]; then 
      echo "[INFO] Wine has been detected in the user's flatpak directory"
    else
      echo "[INFO] Wine flatpak was not detected on your system, would you like to install it?[y/n]"
      read response

      if [ "$response" == 'y' ]; then
        echo "[INFO] Running command to install wine."
        echo "[INFO] Follow the prompts to install the latest **STABLE** wine"
        sleep 1
        flatpak install flathub org.winehq.Wine
      else
        echo "[Error] - Exiting -- Valid response was not chosen. Please install wine via flatpak or from your package manager."
        sleep 2
        exit
      fi
    fi
  fi
else
  echo "[Error] - Exiting -- Python 3 is not installed"
  sleep 2
  exit
fi

python3 couleur.py
