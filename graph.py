import math
import random
import tkinter as tk
from typing import List, Tuple

Coord = Tuple[float, float]
Matrix = List[List[int]]

VARIANT = 4104
PANEL_SIZE = 600
PANEL_GAP = 40
OUTER_RADIUS = 0.40 * PANEL_SIZE
NODE_RADIUS = 22
EDGE_WIDTH = 3

def generate_directed_matrix(size: int, seed: int, n3: int, n4: int) -> Matrix:
    random.seed(seed)
    k = 1.0 - n3 * 0.02 - n4 * 0.005 - 0.25
    return [[1 if random.uniform(0, 2) * k >= 1 else 0 for _ in range(size)] for _ in range(size)]

def to_undirected(matrix: Matrix) -> Matrix:
    n = len(matrix)
    return [[1 if matrix[i][j] or matrix[j][i] else 0 for j in range(n)] for i in range(n)]

def node_positions_triangle(count: int, offset_x: int) -> List[Coord]:
    cx, cy, r = offset_x + PANEL_SIZE / 2, PANEL_SIZE / 2, OUTER_RADIUS
    angles = [math.pi/2 + i * 2*math.pi/3 for i in range(3)]
    verts = [(cx + r * math.cos(a), cy - r * math.sin(a)) for a in angles]
    base, extra = divmod(count, 3)

    def points_on_edge(p1, p2, n):
        return [(p1[0] + (p2[0]-p1[0]) * i / n, p1[1] + (p2[1]-p1[1]) * i / n) for i in range(n)]

    points = []
    for i in range(3):
        n_nodes = base + (1 if i < extra else 0)
        points += points_on_edge(verts[i], verts[(i+1)%3], n_nodes)
    return points[:count]

class GraphRenderer:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas

    def shift(self, p: Coord, q: Coord, d: float) -> Coord:
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return p
        return (p[0] + dx * d / length, p[1] + dy * d / length)

    def draw_node(self, x: float, y: float, label: str):
        self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill="green", outline="black", width=2)
        self.canvas.create_text(x, y, text=label, font=("Arial", 12, "bold"))

    def draw_edge(self, p1: Coord, p2: Coord, directed: bool):
        a = self.shift(p1, p2, NODE_RADIUS)
        b = self.shift(p2, p1, NODE_RADIUS * (1.25 if directed else 1))
        self.canvas.create_line(*a, *b, width=EDGE_WIDTH, fill="black", arrow=tk.LAST if directed else tk.NONE, arrowshape=(12,14,6), capstyle=tk.ROUND)

    def draw_loop(self, x: float, y: float, directed: bool):
        pass

    def render_matrix(self, matrix: Matrix, origin: Coord):
        pass

def draw_graph(canvas: tk.Canvas, positions: List[Coord], matrix: Matrix, offset_x: int, directed: bool):
    renderer = GraphRenderer(canvas)
    drawn_edges = set()
    n = len(matrix)

    for row in matrix:
        if len(row) != n:
            raise ValueError("Matrix is not square!")

    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 0:
                continue
            if i == j:
                continue
            else:
                if directed:
                    if (i, j) not in drawn_edges:
                        renderer.draw_edge(positions[i], positions[j], True)
                        drawn_edges.add((i, j))
                else:
                    if (j, i) in drawn_edges or (i, j) in drawn_edges:
                        continue
                    renderer.draw_edge(positions[i], positions[j], False)
                    drawn_edges.add((i, j))
    for idx, (x, y) in enumerate(positions):
        renderer.draw_node(x, y, str(idx + 1))
    caption = "Directed" if directed else "Undirected"
    canvas.create_text(offset_x + PANEL_SIZE / 2, PANEL_SIZE - 15, text=caption, font=("Arial", 17, "bold"))
    renderer.render_matrix(matrix, (offset_x + PANEL_SIZE / 4, PANEL_SIZE + 10))

def print_matrix(matrix: Matrix, title: str):
    print(f"\n{title}:")
    for row in matrix:
        print(" ".join(str(v) for v in row))

if __name__ == "__main__":
    n1, n2, n3, n4 = map(int, str(VARIANT).zfill(4))
    vertex_count = 10 + n3

    directed_mx = generate_directed_matrix(vertex_count, VARIANT, n3, n4)
    undirected_mx = to_undirected(directed_mx)

    print_matrix(directed_mx, "Directed adjacency matrix")
    print_matrix(undirected_mx, "Undirected adjacency matrix")

    canvas_width = 2 * PANEL_SIZE + PANEL_GAP
    root = tk.Tk()
    root.title(f"Lab 3 · Variant {VARIANT}")
    canvas = tk.Canvas(root, width=canvas_width, height=PANEL_SIZE + 330, bg="white")
    canvas.pack()

    pos_directed = node_positions_triangle(vertex_count, offset_x=0)
    pos_undirected = node_positions_triangle(vertex_count, offset_x=PANEL_SIZE + PANEL_GAP)

    draw_graph(canvas, pos_directed, directed_mx, offset_x=0, directed=True)
    draw_graph(canvas, pos_undirected, undirected_mx, offset_x=PANEL_SIZE + PANEL_GAP, directed=False)

    root.mainloop()
