#!/bin/bash
if [ $# -eq 0 ]; then
  echo "Error"
  exit
fi

pushd .
echo "Pushing directory"
cd Upack_Linux
./UnrealPak $1.pak -create=filelist.txt -compress
popd

exit
