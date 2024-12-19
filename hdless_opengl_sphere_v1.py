import os
os.environ['PYOPENGL_PLATFORM'] = 'egl'
from OpenGL import EGL
from OpenGL.GLES3 import *
import ctypes
import numpy as np
from PIL import Image
import pyrr
import cv2 as cv

from sphere import Sphere


#### 왜 PIL로 읽어온 이미지가 더 좋지? ####
#### opencv resize inter_linear, area 둘다 PIL보다 안좋은거 같음 ####
cv_image = cv.imread("first_frame.png")
cv_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
cv_image = cv.flip(cv_image, 0)
cv_image = cv.resize(cv_image, (1000, 500), interpolation=cv.INTER_AREA)
cv_image = cv_image.tobytes()

pil_image = Image.open("first_frame.png")
pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)
pil_image = pil_image.convert("RGB")
pil_image = pil_image.resize((1000, 500))
pil_image = pil_image.tobytes()

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    success = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not success:
        infoLog = glGetShaderInfoLog(shader)
        print(f"Shader compile error: {infoLog}")
    
    return shader

def create_program(vertex_src, fragment_src):
    vertex_shader = compile_shader(vertex_src, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_src, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

def create_opengl_context():
    # 컨텍스트 생성 및 바인딩
    config_attribs = [
        EGL.EGL_SURFACE_TYPE, EGL.EGL_PBUFFER_BIT, 
        EGL.EGL_BLUE_SIZE, 8, 
        EGL.EGL_GREEN_SIZE, 8, 
        EGL.EGL_RED_SIZE, 8, 
        EGL.EGL_ALPHA_SIZE, 8,
        EGL.EGL_RENDERABLE_TYPE, EGL.EGL_OPENGL_ES3_BIT, 
        EGL.EGL_NONE
    ]
    context_attribs = [
        EGL.EGL_CONTEXT_CLIENT_VERSION, 3, 
        EGL.EGL_NONE
    ]
    # EGL 컨텍스트 설정 및 초기화
    display = EGL.eglGetDisplay(EGL.EGL_DEFAULT_DISPLAY)
    EGL.eglInitialize(display, None, None)
    EGL.eglBindAPI(EGL.EGL_OPENGL_ES_API)
    num_configs = EGL.EGLint()
    config = EGL.EGLConfig()
    EGL.eglChooseConfig(display, config_attribs, config, 1, num_configs)
    egl_context = EGL.eglCreateContext(display, config, EGL.EGL_NO_CONTEXT, context_attribs)
    EGL.eglMakeCurrent(display, EGL.EGL_NO_SURFACE, EGL.EGL_NO_SURFACE, egl_context)
    return display, egl_context

def on_view_changed():
    pass

def init_viewport(width, height):
    global program
    glViewport(0, 0, width, height)
    
    projection = pyrr.matrix44.create_perspective_projection_matrix(90, width / height, 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_FALSE, projection)

    view = pyrr.matrix44.create_look_at(
        pyrr.Vector3([0.0, 0.0, 0.0]), 
        pyrr.Vector3([0.0, 0.0, -1.0]), 
        pyrr.Vector3([0.0, 1.0, 0.0])
    )
    glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_FALSE, view)

    # glm::mat4(1.0f)
    model = pyrr.matrix44.create_identity(dtype=np.float32)
    # scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([30.0, 30.0, 30.0]))
    # model = pyrr.matrix44.multiply(model, scale)
    glUniformMatrix4fv(glGetUniformLocation(program, "model"), 1, GL_FALSE, model)


def destroy_opengl_context(display, egl_context):
    EGL.eglDestroyContext(display, egl_context)
    EGL.eglTerminate(display)

def opengl_init():
    global program, width, height, VAO
    
    vertex_src = """
    attribute vec4 a_position;
    attribute vec2 a_texCoord;

    varying vec2 v_texCoord;

    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    
    void main() {
        gl_Position = projection * view * model * a_position;
        v_texCoord = a_texCoord;
    }
    """

    fragment_src = """
    precision mediump float;
    varying vec2 v_texCoord;
    uniform sampler2D texture;
    void main() {
       gl_FragColor = texture2D(texture, v_texCoord);
    }
    """

    program = create_program(vertex_src, fragment_src)
    glUseProgram(program)

    width, height = 1000, 500

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, sphere.vertices.nbytes, sphere.vertices, GL_STATIC_DRAW)

    posotion_loc = glGetAttribLocation(program, "a_position")
    glEnableVertexAttribArray(posotion_loc)
    glVertexAttribPointer(posotion_loc, 3, GL_FLOAT, GL_FALSE, sphere.vertices.itemsize * 3, ctypes.c_void_p(0))

    texCoodBuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, texCoodBuffer)
    glBufferData(GL_ARRAY_BUFFER, sphere.texCoords.nbytes, sphere.texCoords, GL_STATIC_DRAW)

    texCoord_loc = glGetAttribLocation(program, "a_texCoord")
    glEnableVertexAttribArray(texCoord_loc)
    glVertexAttribPointer(texCoord_loc, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    
    EVO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EVO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sphere.indexCount*8, sphere.indices, GL_STATIC_DRAW)

    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    renderbuffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, renderbuffer)

    # 렌더버퍼 생성 및 프레임버퍼에 연결
    fbo_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, fbo_texture)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, fbo_texture, 0);  
    # 렌더버퍼 생성 및 프레임버퍼에 연결
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, renderbuffer)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")
        exit()
    else:
        print("Framebuffer is complete!")

if __name__ == "__main__":
    # create opengl context
    display, egl_context = create_opengl_context()
    # create sphere
    sphere = Sphere()
    # init opengl
    opengl_init()
        
    glUseProgram(program)
    glClearColor(0., 0.25, 0.25, 1)
    
    # view init
    init_viewport(width, height)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glBindVertexArray(VAO)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pil_image)
    glUniform1i(glGetUniformLocation(program, "texture"), 0)
    
    glDrawElements(GL_TRIANGLES, sphere.indexCount, GL_UNSIGNED_SHORT, None)
        
    image_data = np.zeros((height, width, 3), dtype=np.uint8)
    glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, image_data)

    image_data = cv.cvtColor(image_data, cv.COLOR_RGB2BGR)
    cv.imwrite("test_sphere_view_000.png", image_data)
    # cv.imwrite("test_sphere_view_001.png", image_data)
    # cv.imwrite("test_sphere_view_002.png", image_data)
    # cv.imwrite("test_sphere_view_003.png", image_data)
    # cv.imwrite("test_sphere_view_004.png", image_data)
    # cv.imwrite("test_sphere_view_005.png", image_data)
    # image = Image.frombytes("RGBA", (width, height), image_data)
    # image = image.transpose(Image.FLIP_TOP_BOTTOM)
    # image.save("test_sphere.png")
    print("image saved")

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindVertexArray(0)
    
    # destroy opengl context
    destroy_opengl_context(display, egl_context)

    
    