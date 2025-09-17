echo "==================================="
echo "Upgrading pillow-tk from repository"
echo "==================================="

sudo dnf install python3-pillow-tk
if [ $? -eq 0 ]; then 
  echo "[INFO] pillow has been installed successfully"
else
  echo "[ERROR] There was a problem with installing pillow"
fi

sleep 2
