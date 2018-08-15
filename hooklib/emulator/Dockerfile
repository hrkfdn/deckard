FROM butomo1989/docker-android-x86-8.1

RUN apt-get -qqy update && apt-get -qqy install --no-install-recommends aapt cpio patch

COPY patch_utils.diff /root/patch_utils.diff
COPY patch_ramdisk.sh /root/patch_ramdisk.sh
COPY flash_xposed.sh /root/flash_xposed.sh
COPY generate_modlist.sh /root/generate_modlist.sh
COPY framework.zip /root/xposed_framework.zip
COPY libdeckard.so /root/libdeckard.so

COPY xposed.apk /root/xposed.apk
COPY apks /root/apks

# apply modifications
RUN cd /root && patch -p1 < /root/patch_utils.diff

# patch ramdisk to add dynamic analysis library
RUN cd /root/system-images/android-27/google_apis/x86 && mv ramdisk.img ramdisk.org.img
RUN /root/patch_ramdisk.sh \
    /root/system-images/android-27/google_apis/x86/ramdisk.org.img \
    /root/system-images/android-27/google_apis/x86/ramdisk.img

#RUN echo "disk.ramdisk.path=/root/ramdisk.patched.img" >> /root/android_emulator/config.ini
#CMD /bin/bash
