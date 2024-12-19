import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import PIL.Image as Image
import ctypes


sample_image = Image.open("torch_result.png")
sample_image = sample_image.transpose(Image.FLIP_TOP_BOTTOM)
sample_image = sample_image.convert("RGBA")
sample_image = sample_image.resize((30, 30))
sample_image = sample_image.tobytes()

vertex_src = """
attribute vec4 a_position;
attribute vec4 a_color;

varying vec4 v_color;

void main()
{
    gl_Position = a_position;
    v_color = a_color;
}
"""

fragment_src = """
precision mediump float;
varying vec4 v_color;

void main()
{
    gl_FragColor = v_color;
}
"""

def window_resize(window, width, height):
    glViewport(0, 0, width, height)

# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, 400, 200)

# set the callback function for window resize
glfw.set_window_size_callback(window, window_resize)

# make the context current
glfw.make_context_current(window)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

width, height = 30, 30

vertices = [-0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
            -0.5,  0.5, 0.0, 0.0, 0.0, 1.0,
             0.5,  0.5, 0.0, 1.0, 1.0, 1.0]

vertices = np.array(vertices, dtype=np.float32)

VAO = glGenVertexArrays(1)
glBindVertexArray(VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

posotion_loc = glGetAttribLocation(shader, "a_position")
glEnableVertexAttribArray(posotion_loc)
glVertexAttribPointer(posotion_loc, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

color_loc = glGetAttribLocation(shader, "a_color")
glEnableVertexAttribArray(color_loc)
glVertexAttribPointer(color_loc, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

framebuffer = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

renderbuffer = glGenRenderbuffers(1)
glBindRenderbuffer(GL_RENDERBUFFER, renderbuffer)

fbo_texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, fbo_texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, fbo_texture, 0);  
# 렌더버퍼 생성 및 프레임버퍼에 연결
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, renderbuffer)

if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")
    exit()
else:
    print("Framebuffer is complete!")
    
glUseProgram(shader)
glClearColor(0., 0.25, 0.25, 1)

# the main application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, sample_image)

    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    
    image_data = np.zeros((height, width, 4), dtype=np.uint8)
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    image = Image.frombytes("RGBA", (width, height), image_data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save("test.png")
    print("Image saved!")
    
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glfw.swap_buffers(window)

# terminate glfw, free up allocated resources
glfw.terminate()