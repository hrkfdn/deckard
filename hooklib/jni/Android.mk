LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := deckard
LOCAL_SRC_FILES := ../deckard.c
LOCAL_ARM_MODE := arm
LOCAL_CFLAGS := -g

include $(BUILD_SHARED_LIBRARY)
