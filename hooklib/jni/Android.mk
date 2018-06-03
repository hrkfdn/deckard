LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := deckard
LOCAL_SRC_FILES := ../deckard.cpp
LOCAL_ARM_MODE := arm
LOCAL_CFLAGS := -g
LOCAL_LDLIBS := -llog

include $(BUILD_SHARED_LIBRARY)
