# Deckard

Deckard is a static/dynamic analysis tool for Xposed modules written
in Python 3. The main executable is located in `src/deckard.py`.

## Usage

```
$ ./deckard.sh
usage: src/deckard.py <static|dynamic|show> <path_to.apk|path_to.report>
```

## Requirements

In order to use Deckard, required third party Python modules can be
installed to a virtual environment using `setup.sh`.

A wrapper `deckard.sh` is provided to execute Deckard within this
virtual environment.

### Dynamic Analysis Setup

If you'd like to perform dynamic analysis, additional setup steps are
required:

- The Android SDK and NDK need to be installed
- The native library in `hooklib/`needs to be compiled using
  `ndk-build`
  - If you have a working installation of Docker, you can use
    `hooklib/build.sh` to compile the native library in a prepared
    environment
- An emulator or real device with root privileges and write access to
  the system partition is required:
  - When using the Android emulator, enable persistent system
    partition writes and set SELinux to permissive mode by supplying
    the `-writable-system -selinux permissive` commandline parameters.
  - Xposed needs to be installed on the device. The script
    `flash_xposed.sh` can be used to install Xposed on emulated
    devices.
  - The `libdeckard.so` binary that was previously compiled in
    `hooklib/libs/$ARCH/libdeckard.so` needs to be installed on the
    target device, e.g. to `/system/lib/libdeckard.so`
  - `libdeckard.so` needs to be preloaded before Zygote, e.g. by
    setting the environment variable in the Zygote service
    configuration. On an Android emulator device `echo " setenv
    LD_PRELOAD /system/lib/libdeckard.so" >> /init.zygote32.rc` can be
    executed in an *adb shell* running as root.
