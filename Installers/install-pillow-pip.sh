echo "==================================="
echo "Upgrading pip and installing pillow"
echo "==================================="

python3 -m pip install --upgrade pip
if [ $? -eq 0 ]; then 
  echo "[INFO] pip has been upgraded successfully"
else
  echo "[ERROR] There was a problem with installing/upgrading pip"
fi

python3 -m pip install --upgrade Pillow
if [ $? -eq 0 ]; then 
  echo "[INFO] pillow has been installed and upgraded successfully"
else
  echo "[ERROR] There was a problem with installing/upgrading pillow"
fi

sleep 2

