#ifndef _JNIXPOSED_H
#define _JNIXPOSED_H

#include <vector>
#include <string>
#include <jni.h>

class JNIHelper {
public:
  JNIHelper(JNIEnv* env);
  jobject getHookObject(jclass bridgeClass, jobject additionalHookInfo);
  jobject getClass(jobject obj);
  std::string getName(jobject obj);
private:
  JNIEnv* env;
};

#endif
