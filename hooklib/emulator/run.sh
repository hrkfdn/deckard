#!/bin/sh

FRAMEWORK_URL="https://dl-xda.xposed.info/framework/sdk27/x86/xposed-v90-sdk27-x86-beta3.zip"
XPOSED_URL="https://www.apklinker.com/wp-content/uploads/uploaded_apk/5a61a51c53c7c/de.robv.android.xposed.installer_3.1.5_43_MinAPI15_(nodpi)_apklinker.com.apk"

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

if [ ! -f ../libs/x86/libdeckard.so ]
then
    echo "libdeckard.so does not exist, please build it first, e.g. by using hooklib/build.sh."
    exit 1
fi

if [ ! -f framework.zip ]
then
    echo "[+] Downloading Xposed framework"
    curl -qo "$SCRIPTPATH/framework.zip" "$FRAMEWORK_URL"
fi

if [ ! -f xposed.apk ]
then
    echo "[+] Downloading Xposed installer"
    curl -qo "$SCRIPTPATH/xposed.apk" "$XPOSED_URL"
fi

cp ../libs/x86/libdeckard.so ./libdeckard.so

#docker build --no-cache -t deckard/emulator .
docker build -t deckard/emulator .
docker run -it --privileged --rm -p 6080:6080 -p 5554:5554 -p 5555:5555  deckard/emulator
