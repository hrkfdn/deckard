#include "jnihelper.h"

jobject JNIHelper::getHookObject(jclass bridgeClass, jobject additionalHookInfo) {
  // get additionalHookInfo.callbacks
  jclass additionalHookInfoClass = env->GetObjectClass(additionalHookInfo);
  jfieldID callbacksId = env->GetFieldID(additionalHookInfoClass, "callbacks", "Lde/robv/android/xposed/XposedBridge$CopyOnWriteSortedSet;");
  jobject callbacks = env->GetObjectField(additionalHookInfo, callbacksId);

  // call callbacks.getSnapshot()
  jclass snapshotClass = env->GetObjectClass(callbacks);
  jmethodID getSnapshotId = env->GetMethodID(snapshotClass, "getSnapshot", "()[Ljava/lang/Object;");
  jobjectArray snapshot = (jobjectArray)env->CallObjectMethod(callbacks, getSnapshotId);

  // get callback element, it's always the only callback element because we reset the array
  return env->GetObjectArrayElement(snapshot, 0);
}

jobject JNIHelper::getClass(jobject obj) {
  jclass cls = env->GetObjectClass(obj);
  jmethodID mid = env->GetMethodID(cls, "getClass", "()Ljava/lang/Class;");
  return env->CallObjectMethod(obj, mid);
}

std::string JNIHelper::getName(jobject obj) {
  jboolean iscopy;
  jclass cls = env->GetObjectClass(obj);
  jmethodID getNameMethod = env->GetMethodID(cls, "getName", "()Ljava/lang/String;");
  jstring ret = (jstring)env->CallObjectMethod(obj, getNameMethod, 0);

  const char* str = env->GetStringUTFChars(ret, &iscopy);
  std::string s(str);

  // free JNI object
  if(iscopy == JNI_TRUE) {
    env->ReleaseStringUTFChars(ret, str);
  }

  return s;
}

JNIHelper::JNIHelper(JNIEnv* env) {
  this->env = env;
}
