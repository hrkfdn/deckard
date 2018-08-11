#!/bin/sh

if [ $# -ne 2 ];
then
    echo "usage: $0 <ramdisk.img> <patched.img>"
    exit 1
fi

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
TEMPDIR=$(mktemp -d -p $SCRIPTPATH)

# if we don't do this, cpio will assume the root directory is meant to
# have 700, causing a bootloop in the emulator
chmod 777 $TEMPDIR

echo "[+] Extracting ramdisk ($1)"
(cd $TEMPDIR && gunzip -c $1 | cpio -id)

echo "[+] Adding libdeckard.so to Zygote LD_PRELOAD"
echo "    setenv LD_PRELOAD /system/lib/libdeckard.so" >> $TEMPDIR/init.zygote32.rc

echo "[+] Packing new ramdisk ($2)"
(cd $TEMPDIR && find . | cpio -coR "root:root") > $2

echo "[+] Deleting temporary files"
#rm -rf $TEMPDIR
