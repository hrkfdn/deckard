#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

#include <jni.h>
#include <android/log.h>

//#include "xposed_shared.h"

void _log(const char* fmt, ...) {
  char* abuf;
  va_list ap;

  va_start(ap, fmt);
  if(vasprintf(&abuf, fmt, ap) == -1) {
    va_end(ap);
    return;
  }

  FILE *f = fopen("/data/local/tmp/deckard.log", "a");
  fprintf(f, "%s", abuf);
  fclose(f);

  printf("%s", abuf);
  __android_log_print(ANDROID_LOG_DEBUG, "Deckard", "%s", abuf);
}

/*
void XposedBridge_hookMethodNative(JNIEnv* env, jclass clazz, jobject
                                   javaReflectedMethod, jobject declaredClass,
                                   jint slot, jobject javaAdditionalInfo) {
  _log("hookMethodNative\n");
}
*/

/*
typedef bool (*xposedInitLib_t)(xposed::XposedShared* XposedShared);
xposedInitLib_t _xposedInitLib = 0;
bool newxposedInitLib(struct* XposedShared* shared) {
  if(!_xposedInitLib) {
    _xposedInitLib = (xposedInitLib_t)dlsym(RTLD_NEXT, "xposedInitLib");
  }
  _log("xposedInitLib");
  return _xposedInitLib(shared);
}
*/

extern "C"
__attribute__((__weak__, visibility("default")))
void* __loader_dlsym(void* handle, const char* symbol, const void* caller_addr);

void *dlsym(void *handle, const char *symbol) {
  const void* caller_addr = __builtin_return_address(0);
  _log("dlsym(0x%X, \"%s\")\n", handle, symbol);
  return __loader_dlsym(handle, symbol, caller_addr);
}

__attribute((constructor))
void onload() {
  _log("Deckard loaded\n");
}
