from OpenGL import *
from OpenGL.GL import *
from OpenGL.EGL import *
import numpy as np
from math import sin, cos
from PIL import Image

def initialize_egl_context():
    # EGL 디스플레이 연결 초기화
    egl_display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
    if egl_display == EGL_NO_DISPLAY:
        raise RuntimeError("Unable to get EGL display")
    else:
        print("EGL display OK")

    if not eglInitialize(egl_display, None, None):
        raise RuntimeError("Unable to initialize EGL")
    else:
        print("EGL initialized OK")

    # 적절한 EGL 설정 선택
    config_attribs = [
        EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
        EGL_BLUE_SIZE, 8,
        EGL_GREEN_SIZE, 8,
        EGL_RED_SIZE, 8,
        EGL_DEPTH_SIZE, 8,
        EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
        EGL_NONE
    ]
    num_configs = EGLint()
    egl_config = EGLConfig()
    if not eglChooseConfig(egl_display, config_attribs, egl_config, 1, num_configs):
        raise RuntimeError("Unable to choose EGL config")

    # EGL 서피스와 컨텍스트 생성
    egl_surface = eglCreatePbufferSurface(egl_display, egl_config, None)
    egl_context = eglCreateContext(egl_display, egl_config, EGL_NO_CONTEXT, None)
    if egl_context == EGL_NO_CONTEXT:
        raise RuntimeError("Unable to create EGL context")

    # 생성된 컨텍스트를 현재 스레드에 바인딩
    if not eglMakeCurrent(egl_display, egl_surface, egl_surface, egl_context):
        raise RuntimeError("Unable to make EGL context current")

    return egl_display, egl_surface, egl_context

# egl_display, egl_surface, egl_context = initialize_egl_context()
egl_display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
if egl_display == EGL_NO_DISPLAY:
    raise RuntimeError("Unable to get EGL display")
else:
    print("EGL display OK")

if not eglInitialize(egl_display, None, None):
    raise RuntimeError("Unable to initialize EGL")
else:
    print("EGL initialized OK")

# 적절한 EGL 설정 선택
config_attribs = [
    EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
    EGL_BLUE_SIZE, 8,
    EGL_GREEN_SIZE, 8,
    EGL_RED_SIZE, 8,
    EGL_DEPTH_SIZE, 8,
    EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
    EGL_NONE
]
num_configs = EGLint()
egl_config = EGLConfig()
if not eglChooseConfig(egl_display, config_attribs, egl_config, 1, num_configs):
    raise RuntimeError("Unable to choose EGL config")

# EGL 서피스와 컨텍스트 생성
egl_surface = eglCreatePbufferSurface(egl_display, egl_config, None)
egl_context = eglCreateContext(egl_display, egl_config, EGL_NO_CONTEXT, None)
if egl_context == EGL_NO_CONTEXT:
    raise RuntimeError("Unable to create EGL context")

# 생성된 컨텍스트를 현재 스레드에 바인딩
if not eglMakeCurrent(egl_display, egl_surface, egl_surface, egl_context):
    raise RuntimeError("Unable to make EGL context current")

#### OpenGL ####


vertices = [-0.5, -0.5, 0.0,
             0.5, -0.5, 0.0,
             0.0,  0.5, 0.0]

colors = [1.0, 0.0, 0.0,
          0.0, 1.0, 0.0,
          0.0, 0.0, 1.0]

vertices = np.array(vertices, dtype=np.float32)
colors = np.array(colors, dtype=np.float32)

# Initialize the library

# glEnableClientState(GL_VERTEX_ARRAY)
# glVertexPointer(3, GL_FLOAT, 0, vertices)

# glEnableClientState(GL_COLOR_ARRAY)
# glColorPointer(3, GL_FLOAT, 0, colors)

# glClearColor(0, 0.1, 0.1, 1)


# glClear(GL_COLOR_BUFFER_BIT)


# glLoadIdentity()
# glScale(abs(sin(ct)), abs(sin(ct)), 1)
# glRotatef(sin(ct) * 45, 0, 0, 1)
# glTranslatef(sin(ct), cos(ct), 0)

# glDrawArrays(GL_TRIANGLES, 0, 3)


#### Destroy OpenGL ####
eglDestroyContext(egl_display, egl_context)
eglDestroySurface(egl_display, egl_surface)
eglTerminate(egl_display)