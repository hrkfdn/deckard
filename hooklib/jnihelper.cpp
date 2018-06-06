#include "jnihelper.h"

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
