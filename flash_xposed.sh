#!/bin/sh

if [ -z $1 ];
then
    echo "usage: $0 /path/to/xposed_framework.zip"
    exit
fi

XPOSED_TMP="/tmp/xposed"
XPOSED_ZIP=$1

rm -rf $XPOSED_TMP
mkdir -p $XPOSED_TMP
unzip -d /tmp/xposed/ $XPOSED_ZIP META-INF/com/google/android/update-binary

# Adapted from Xposed build.pl
# https://github.com/rovo89/XposedTools/blob/78173acfbf7fe2ef46e4ee4d0dcbad15bb45b05f/build.pl#L402
mkdir -p $XPOSED_TMP
adb push $XPOSED_ZIP /data/local/tmp/xposed.zip
adb push $XPOSED_TMP/META-INF/com/google/android/update-binary /data/local/tmp/update-binary
adb shell 'chmod 700 /data/local/tmp/update-binary'
adb shell '/data/local/tmp/update-binary 2 1 /data/local/tmp/xposed.zip'
adb shell sh -c 'stop'
sleep 2
adb shell sh -c 'start'
