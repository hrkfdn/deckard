#include "jnihelper.h"

jobject JNIHelper::getHookObject(jclass bridgeClass, jobject additionalHookInfo) {
  // get additionalHookInfo.callbacks
  jclass additionalHookInfoClass = env->GetObjectClass(additionalHookInfo);
  jfieldID callbacksId = env->GetFieldID(additionalHookInfoClass, "callbacks", "Lde/robv/android/xposed/XposedBridge$CopyOnWriteSortedSet;");
  jobject callbacks = env->GetObjectField(additionalHookInfo, callbacksId);

  // call callbacks.getSnapshot()
  jobjectArray snapshot = (jobjectArray)this->callMethod(callbacks, "getSnapshot", "()[Ljava/lang/Object;");

  // get callback element, it's always the only callback element because we reset the array
  return env->GetObjectArrayElement(snapshot, 0);
}

jobject JNIHelper::getClass(jobject obj) {
  return this->callMethod(obj, "getClass", "()Ljava/lang/Class;");
}

jobject JNIHelper::getPackage(jobject obj) {
  return this->callMethod(obj, "getPackage", "()Ljava/lang/Package;");
}

std::string JNIHelper::getName(jobject obj) {
  jboolean iscopy;
  jstring ret = (jstring)this->callMethod(obj, "getName", "()Ljava/lang/String;");
  return this->makeString(ret);
}

std::string JNIHelper::makeString(jstring jstr) {
  jboolean iscopy;
  const char* str = env->GetStringUTFChars(jstr, &iscopy);
  std::string s(str);

  // free JNI object
  if(iscopy == JNI_TRUE) {
    env->ReleaseStringUTFChars(jstr, str);
  }

  return s;
}

jobject JNIHelper::callMethod(jobject obj, const std::string& name, const std::string& signature) {
  jclass cls = env->GetObjectClass(obj);
  jmethodID mid = env->GetMethodID(cls, name.c_str(), signature.c_str());
  return env->CallObjectMethod(obj, mid);
}

JNIHelper::JNIHelper(JNIEnv* env) {
  this->env = env;
}
