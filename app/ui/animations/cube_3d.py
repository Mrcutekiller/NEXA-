# app/ui/animations/cube_3d.py
"""
Pure Python 3D rotating cube animation generator.
Renders a 3D wireframe cube to an ASCII/ANSI canvas.
"""

import math
from typing import List, Tuple

# 3D vertices of a cube
CUBE_VERTICES = [
    [-1.0, -1.0, -1.0],
    [ 1.0, -1.0, -1.0],
    [ 1.0,  1.0, -1.0],
    [-1.0,  1.0, -1.0],
    [-1.0, -1.0,  1.0],
    [ 1.0, -1.0,  1.0],
    [ 1.0,  1.0,  1.0],
    [-1.0,  1.0,  1.0]
]

# 12 edges connecting the vertices
CUBE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0), # Front face
    (4, 5), (5, 6), (6, 7), (7, 4), # Back face
    (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting edges
]

def rotate_x(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return x, y * cos_a - z * sin_a, y * sin_a + z * cos_a

def rotate_y(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a

def rotate_z(x: float, y: float, z: float, angle_rad: float) -> Tuple[float, float, float]:
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a, z

def project(x: float, y: float, z: float, width: int, height: int, fov: float = 20.0, distance: float = 3.5) -> Tuple[int, int]:
    # Project 3D onto 2D viewport
    factor = fov / (z + distance)
    # Multiply X by 2.2 to compensate for terminal character cell aspect ratio
    x_proj = int(width / 2 + x * factor * 2.2)
    y_proj = int(height / 2 + y * factor)
    return x_proj, y_proj

def draw_line_bresenham(x0: int, y0: int, x1: int, y1: int, canvas: List[List[str]], char: str = "*"):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    h = len(canvas)
    w = len(canvas[0]) if h > 0 else 0
    
    while True:
        if 0 <= x0 < w and 0 <= y0 < h:
            canvas[y0][x0] = char
            
        if x0 == x1 and y0 == y1:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

class Cube3DAnimator:
    def __init__(self, width: int = 40, height: int = 15):
        self.width = width
        self.height = height
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0

    def next_frame(self, color_ansi: str = "\033[38;5;51m", char: str = "#") -> str:
        """
        Calculates the next rotated state of the cube and draws it.
        Returns a colored ANSI string.
        """
        # Increment angles for rotation
        self.angle_x += 0.04
        self.angle_y += 0.03
        self.angle_z += 0.02
        
        # Initialize empty canvas
        canvas = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Project all rotated vertices
        projected_vertices = []
        for vertex in CUBE_VERTICES:
            # Rotate
            rx, ry, rz = rotate_x(*vertex, self.angle_x)
            rx, ry, rz = rotate_y(rx, ry, rz, self.angle_y)
            rx, ry, rz = rotate_z(rx, ry, rz, self.angle_z)
            
            # Project
            px, py = project(rx, ry, rz, self.width, self.height)
            projected_vertices.append((px, py))
            
        # Draw edges
        for edge in CUBE_EDGES:
            p1 = projected_vertices[edge[0]]
            p2 = projected_vertices[edge[1]]
            draw_line_bresenham(p1[0], p1[1], p2[0], p2[1], canvas, char)
            
        # Compile canvas to single string with color codes
        lines = []
        for row in canvas:
            line = "".join(row)
            # Wrap non-space characters in color
            colored_line = ""
            for char_in_line in line:
                if char_in_line != " ":
                    colored_line += f"{color_ansi}{char_in_line}\033[0m"
                else:
                    colored_line += " "
            lines.append(colored_line)
            
        return "\n".join(lines)
