# Deckard

Deckard is a static/dynamic analysis tool for Xposed modules written
in Python 3. The main executable is located in `src/deckard.py`.

## Usage

```
$ ./deckard.sh
usage: src/deckard.py <static|dynamic|show> <path_to.apk|path_to.report>
```

- `static` will perform static analysis on a supplied Xposed module
  APK and write a report.
- `dynamic` will perform dynamic analysis and write a
  report. Additional setup is required, see below for further
  instructions.
- `show` opens a report file in the web GUI.

## Requirements

In order to use Deckard, required third party Python modules can be
installed to a virtual environment using `setup.sh`.

A wrapper `deckard.sh` is provided to execute Deckard within this
virtual environment.

### Dynamic Analysis using the Android Emulator (recommended)

A Dockerfile is provided to boot up a container running the Android
emulator. It will also patch the emulator images to preload the
dynamic analysis library.

1. Build the dynamic analysis helper library (hooklib), e.g. by using
   `hooklib/build.sh`
2. Place the Xposed module to analyze in `hooklib/emulator/apks`. If
   you are aware of external applications targeted by the module,
   place them in the same folder.
3. Run the emulator and pipe the device's logcat to the Deckard
   application, like so: `./hooklib/emulator/run.sh | ./deckard.sh
   dynamic hooklib/emulator/apks/xposed_module.apk`.
4. If the module needs additional stimulation, for instance launching
   a specific application, you can use the VNC viewer provided at
   http://localhost:6080 (replace localhost if Docker is on a
   different host).
   
The first boot take a few minutes. Initial setup also requires a
reboot that will be performed automatically. Deckard will print
incoming hook messages. Once you are finished with capture, hit CTRL-C
to stop the container and save the report.

### Dynamic Analysis using a real device/custom emulator

If you'd like to perform dynamic analysis on a real device other with
custom emulator setups, additional setup steps are required:

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
- Reboot the device and pipe the logcat output to Deckard.
