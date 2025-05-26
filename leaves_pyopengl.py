# Code adapted from John Parker circle animation:
# https://github.com/johnaparker/blog/tree/master/circle_animation
#
# Converted to Python from C++ and simplified

import glfw
import glm

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL import EGL

from ctypes import sizeof, c_float, c_void_p

import numpy as np

from time import time
from PIL import Image

VAO = None
VBO = None
EBO = None
transformVBO = None
colorVBO = None


# Global variables
width = 1000


def make_window():
    if not glfw.init():
        raise Exception("GLFW can not be initialized")

    window = glfw.create_window(width, width, "", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window can not be created")

    glfw.make_context_current(window)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def bind_vertices():
    global VAO, VBO, EBO
    vertices = np.array([
        1.0,  1.0, 0.0,
        1.0, -1.0, 0.0,
        -1.0, -1.0, 0.0,
        -1.0,  1.0, 0.0
    ], dtype=np.float32)
    indices = np.array([
        0, 1, 3,
        1, 2, 3
    ], dtype=np.uint32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)


def bind_attributes():
    global transformVBO, colorVBO
    transformVBO = glGenBuffers(1)
    colorVBO = glGenBuffers(1)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)

    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, transformVBO)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 16 * sizeof(c_float), None)
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 16 * sizeof(c_float), c_void_p(1 * 4 * sizeof(c_float)))
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, 16 * sizeof(c_float), c_void_p(2 * 4 * sizeof(c_float)))
    glEnableVertexAttribArray(4)
    glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, 16 * sizeof(c_float), c_void_p(3 * 4 * sizeof(c_float)))

    glVertexAttribDivisor(1, 1)
    glVertexAttribDivisor(2, 1)
    glVertexAttribDivisor(3, 1)
    glVertexAttribDivisor(4, 1)

    glEnableVertexAttribArray(5)
    glBindBuffer(GL_ARRAY_BUFFER, colorVBO)
    glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, 4 * sizeof(c_float), None)
    glVertexAttribDivisor(5, 1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)


def close_window():
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [EBO])
    glDeleteBuffers(1, [transformVBO])
    glDeleteBuffers(1, [colorVBO])
    glfw.terminate()


def dead_leaves(n_images=100):
    """Because the setup is costly, we are going to create new images here
    """
    # Radius parameter
    alpha = 3.0
    r_min = 4
    r_max = 2000

    vamin = 1/(r_max**(alpha-1))
    vamax = 1/(r_min**(alpha-1))

    # Number of disks
    N = 10000

    # Read shaders
    with open("vertex_shader.glsl") as f:
        vshader = f.read()

    with open("fragment_shader.glsl") as f:
        fshader = f.read()

    make_window()
    bind_vertices()
    bind_attributes()

    shader = compileProgram(compileShader(vshader, GL_VERTEX_SHADER), compileShader(fshader, GL_FRAGMENT_SHADER))
    glUseProgram(shader)

    # Projection matrix
    projection = glm.ortho(0.0, 1.0, 0.0, 1.0, -0.1, 0.1)
    glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

    # rendering to a framebuffer
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, width, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)
    glViewport(0, 0, width, width)


    start_time = time()

    for k in range(n_images):
        pos = np.random.rand(N, 2).astype(np.float32)
        radii = vamin + (vamax - vamin) * np.random.rand(N).astype(np.float32)
        radii = np.ceil(1/(radii**(1./(alpha-1)))) / (width // 2)
        colors = np.random.rand(N, 3).astype(np.float32)

        # Directly write the matrix in transposed form
        circleTransforms = np.tile(np.eye(4, dtype=np.float32), (N, 1, 1))
        circleTransforms[:,0,0] = radii
        circleTransforms[:,1,1] = radii
        circleTransforms[:,3,0] = pos[:,0]
        circleTransforms[:,3,1] = pos[:,1]

        circleColors = np.concatenate((colors, np.ones((N, 1), dtype=np.float32)), axis=-1)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glBindBuffer(GL_ARRAY_BUFFER, transformVBO)
        glBufferData(GL_ARRAY_BUFFER, circleTransforms.nbytes, circleTransforms, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, colorVBO)
        glBufferData(GL_ARRAY_BUFFER, circleColors.nbytes, circleColors, GL_STATIC_DRAW)

        glBindVertexArray(VAO)
        glDrawElementsInstanced(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None, N)

        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, width, width, GL_RGB, GL_UNSIGNED_BYTE)
        img = Image.frombytes("RGB", (width, width), data)

        img.save(f"{k:03d}.png")

    print(time() - start_time)
    close_window()


if __name__ == "__main__":
    dead_leaves()
