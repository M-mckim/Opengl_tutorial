import numpy as np
from OpenGL.GL import *

ES_PI = 3.14159265358979323846

class Sphere:
    def __init__(self, radius=1.0, sliceCount=200):
        print("SPHERE INIT")

        sliceCount = 200
        radius = 1.0
        self.vertexCount = (sliceCount // 2 + 1) * (sliceCount + 1)
        self.vertices, self.texCoords, self.indices = self.esGenSphere(sliceCount, radius)
        self.indexCount = len(self.indices)

    def esGenSphere(self, numSlices, radius):
        numParallels = numSlices // 2
        numVertices = (numParallels + 1) * (numSlices + 1)
        numIndices = numParallels * numSlices * 6
        angleStep = (2.0 * ES_PI) / numSlices

        vertices = np.zeros((numVertices, 3), dtype=np.float32)
        texCoords = np.zeros((numVertices, 2), dtype=np.float32)
        indices = []

        for i in range(numParallels + 1):
            for j in range(numSlices + 1):
                vertex = (i * (numSlices + 1) + j) * 3

                x = radius * np.sin(angleStep * i) * np.cos(angleStep * j)
                y = radius * np.cos(angleStep * i)
                z = radius * np.sin(angleStep * i) * np.sin(angleStep * j)

                vertices[i * (numSlices + 1) + j] = [x, y, z]

                texX = j / numSlices
                texY = i / numParallels
                texCoords[i * (numSlices + 1) + j] = [texX, texY]

        for i in range(numParallels):
            for j in range(numSlices):
                indices.append(i * (numSlices + 1) + j)
                indices.append((i + 1) * (numSlices + 1) + j)
                indices.append((i + 1) * (numSlices + 1) + (j + 1))
                indices.append(i * (numSlices + 1) + j)
                indices.append((i + 1) * (numSlices + 1) + (j + 1))
                indices.append(i * (numSlices + 1) + (j + 1))

        return vertices, texCoords, np.array(indices, dtype=np.ushort)

# Sphere 객체 생성
# sphere = Sphere()