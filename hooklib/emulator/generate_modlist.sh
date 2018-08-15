#!/bin/sh

MODULES=""

for apk in apks/*.apk
do
    PKG=$(aapt dump badging "$apk" | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g)
    MODULES="$MODULES $PKG"
done

for mod in $MODULES
do
    adb shell "mkdir /data/user_de/0/de.robv.android.xposed.installer/conf/"
    adb shell "echo \"$mod\" >> /data/user_de/0/de.robv.android.xposed.installer/conf/enabled_modules.list"
    APK=$(adb shell "pm path $mod" | cut -d ":" -f2)
    adb shell "echo \"$APK\" >> /data/user_de/0/de.robv.android.xposed.installer/conf/modules.list"
    adb shell "chmod -R 777 /data/user_de/0/de.robv.android.xposed.installer/conf/"
done

exit 0

echo "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>"
echo "<map>"
for mod in $MODULES
do
    echo -n "    <int name=\""
    echo -n $mod
    echo "\" value=\"1\" />"
done
echo "</map>"
