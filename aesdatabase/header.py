from . import aescrypto
import os
import time
import shutil
import typing
import struct
import pickle


chunkSize = 1024 * 1024
if 'ANDROID_ROOT' in os.environ:
    chunkSize = 1024 * 64
