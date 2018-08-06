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
  jobject getPackage(jobject obj);
  jobject callMethod(jobject obj, const std::string& name, const std::string& signature);
  std::string makeString(jstring jstr);
  std::string getName(jobject obj);
private:
  JNIEnv* env;
};

#endif
