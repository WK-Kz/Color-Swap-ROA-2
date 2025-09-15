#!/bin/sh
if [ $# -ne 0 ]; then
  # echo "Error"
  exit
fi

pushd .
echo $1/*.* "../../../*.*" > filelist.txt
./UnrealPak $1.pak -create=filelist.txt -compress
popd

exit
