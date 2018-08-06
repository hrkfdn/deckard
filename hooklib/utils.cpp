#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <android/log.h>

void _log(const char* fmt, ...) {
  char* abuf;
  va_list ap;

  va_start(ap, fmt);
  if(vasprintf(&abuf, fmt, ap) == -1) {
    va_end(ap);
    return;
  }

  __android_log_print(ANDROID_LOG_DEBUG, "Deckard", "%s", abuf);
  free(abuf);
}
