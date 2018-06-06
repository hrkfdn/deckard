#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>

#include <jni.h>
#include <android/log.h>

#include "xposed_shared.h"
#include "jnihelper.h"

void _log(const char* fmt, ...) {
  char* abuf;
  va_list ap;

  va_start(ap, fmt);
  if(vasprintf(&abuf, fmt, ap) == -1) {
    va_end(ap);
    return;
  }

  printf("%s", abuf);
  __android_log_print(ANDROID_LOG_DEBUG, "Deckard", "%s", abuf);
}

// Java declaration: void hookMethodNative(Member method, Class<?>
// declaringClass, int slot, Object additionalInfo);
typedef void (*hookMethodNative_t)(JNIEnv*, jclass, jobject, jobject, jint, jobject);
hookMethodNative_t _hookMethodNative = 0;
void hookMethodNative(JNIEnv* env, jclass clazz, jobject
                      javaReflectedMethod, jobject declaringClass,
                      jint slot, jobject javaAdditionalInfo) {

  _log("hookMethodNative called!");

  JNIHelper helper(env);

  std::string methodName = helper.getName(javaReflectedMethod);
  std::string className = helper.getName(declaringClass);

  _log("hookMethodNative(%s, %s)", className.c_str(), methodName.c_str());

  _hookMethodNative(env, clazz, javaReflectedMethod, declaringClass, slot, javaAdditionalInfo);
}

typedef jint (*RegisterNatives_t)(JNIEnv*, jclass, const JNINativeMethod*, jint);
RegisterNatives_t _RegisterNatives = 0;
jint RegisterNatives(JNIEnv* env, jclass clazz, const JNINativeMethod* methods, jint nMethods) {
  _log("RegisterNatives:");

  JNINativeMethod hookedMethods[nMethods];
  memcpy(&hookedMethods, methods, sizeof(JNINativeMethod)*nMethods);

  for(int i = 0; i < nMethods; i++) {
    _log("\tMethod %s(%s) = 0x%X", hookedMethods[i].name, hookedMethods[i].signature, hookedMethods[i].fnPtr);
    if(!strcmp(methods[i].name, "hookMethodNative")) {
      _log("\t->Intercepting hookMethodNative!");
      _hookMethodNative = (hookMethodNative_t)hookedMethods[i].fnPtr;
      hookedMethods[i].fnPtr = (void*)&hookMethodNative;
    }
  }

  // call original with our manipulated list of native methods
  return _RegisterNatives(env, clazz, hookedMethods, nMethods);
}

typedef void (*onVmCreated_t)(JNIEnv*);
onVmCreated_t _onVmCreated = 0;
void onVmCreated(JNIEnv *env) {
  _log("onVmCreated(0x%x)", env);

  /* Create a temporary copy of the JNI interface on the heap, this is
     necessary because the structure is const and seems to have write
     protection flags.  We are replacing the RegisterNatives function
     pointer with the address of our function. As we only need this
     hook during Xposed library calls, restore the original interface
     struct pointer after executing onVmCreated. */
  const struct JNINativeInterface* oldni = env->functions;
  _RegisterNatives = (RegisterNatives_t)env->functions->RegisterNatives;
  struct JNINativeInterface ni;
  memcpy(&ni, env->functions, sizeof(struct JNINativeInterface));

  // Save original function pointer and apply hook
  ni.RegisterNatives = &RegisterNatives;
  env->functions = &ni;

  _onVmCreated(env);

  // Restore old JNI interface as it applies to the whole JVM
  env->functions = oldni;
}

typedef bool (*xposedInitLib_t)(xposed::XposedShared* XposedShared);
xposedInitLib_t _xposedInitLib = 0;
bool xposedInitLib(xposed::XposedShared* shared) {
  _log("xposedInitLib: %d %d %d", shared->zygote, shared->startSystemServer, shared->xposedVersionInt);

  // original xposedInitLib needs to be called first so that
  // XposedShared is initialized
  bool retval = _xposedInitLib(shared);

  // hook onVmCreated
  _onVmCreated = (onVmCreated_t)shared->onVmCreated;
  shared->onVmCreated = &onVmCreated;

  return retval;
}


extern "C"
__attribute__((__weak__, visibility("default")))
void* __loader_dlsym(void* handle, const char* symbol, const void* caller_addr);

void *dlsym(void *handle, const char *symbol) {
  const void* caller_addr = __builtin_return_address(0);
  void *retval = __loader_dlsym(handle, symbol, caller_addr);

  if(!strcmp(symbol, "xposedInitLib")) {
    _xposedInitLib = (xposedInitLib_t)retval;
    return (void*)&xposedInitLib;
  }

  return retval;
}

__attribute((constructor))
void onload() {
  _log("Deckard loaded\n");
}
