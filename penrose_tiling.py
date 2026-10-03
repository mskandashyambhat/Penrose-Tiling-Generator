"""Interactive Penrose triangle tiling generator.

The generator uses Robinson triangle subdivision. Coordinates are represented
as complex numbers, which makes rotation and interpolation compact and clear.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from penrose_core import PHI, Triangle, generate


class PenroseApp:
    """Small desktop studio for exploring the algorithm."""

    BG = "#10161c"
    PANEL = "#18232b"
    INK = "#e8e2d4"
    MUTED = "#8da0a9"
    GOLD = "#e4aa50"
    TEAL = "#4da5a0"
    GRID = "#273740"
    PALETTES = {
        "Sunset Glass": {
            "background": "#10161c",
            "edge": "#10161c",
            "tiles": ["#f06c5b", "#f4b860", "#5bc0be", "#f8e16c", "#c084fc"],
        },
        "Mineral Bloom": {
            "background": "#111827",
            "edge": "#111827",
            "tiles": ["#e76f51", "#f4a261", "#e9c46a", "#2a9d8f", "#457b9d"],
        },
        "Nordic Ice": {
            "background": "#12212b",
            "edge": "#12212b",
            "tiles": ["#ff6b6b", "#ffd166", "#06d6a0", "#4cc9f0", "#c77dff"],
        },
        "Botanical": {
            "background": "#132018",
            "edge": "#132018",
            "tiles": ["#e9c46a", "#90be6d", "#43aa8b", "#577590", "#f9844a"],
        },
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PENROSE / Aperiodic Geometry Studio")
        self.root.geometry("1120x760")
        self.root.minsize(820, 600)
        self.triangles: list[Triangle] = []
        self._build_style()
        self._build_ui()
        self._bind_events()
        self.render()

    def _build_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure("App.TFrame", background=self.BG)
        style.configure("Heading.TLabel", background=self.BG, foreground=self.INK,
                        font=("Helvetica", 22, "bold"))
        style.configure("Subheading.TLabel", background=self.BG, foreground=self.MUTED,
                        font=("Helvetica", 10))
        style.configure("Panel.TLabel", background=self.PANEL, foreground=self.INK,
                        font=("Helvetica", 10))
        style.configure("Value.TLabel", background=self.PANEL, foreground=self.GOLD,
                        font=("Menlo", 11, "bold"))
        style.configure("Action.TButton", background=self.GOLD, foreground="#10161c",
                        font=("Helvetica", 10, "bold"), padding=(14, 8), borderwidth=0)
        style.map("Action.TButton", background=[("active", "#f2c477")])
        style.configure("Secondary.TButton", background=self.GRID, foreground=self.INK,
                        font=("Helvetica", 10), padding=(12, 8), borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#38505b")])
        style.configure("TScale", background=self.PANEL, troughcolor=self.GRID)

    def _build_ui(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame", padding=24)
        shell.pack(fill="both", expand=True)
        header = ttk.Frame(shell, style="App.TFrame")
        header.pack(fill="x", pady=(0, 18))
        ttk.Label(header, text="PENROSE", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(header, text="APERIODIC GEOMETRY STUDIO  /  ROBINSON TRIANGLES",
                  style="Subheading.TLabel").pack(anchor="w", pady=(2, 0))

        content = ttk.Frame(shell, style="App.TFrame")
        content.pack(fill="both", expand=True)
        panel = ttk.Frame(content, style="Panel.TFrame", padding=20)
        panel.pack(side="left", fill="y", padx=(0, 18))
        canvas_frame = ttk.Frame(content, style="App.TFrame")
        canvas_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(panel, text="CONTROL DECK", style="Panel.TLabel",
                  font=("Helvetica", 10, "bold")).pack(anchor="w")
        ttk.Separator(panel).pack(fill="x", pady=(10, 22))
        self.depth = tk.IntVar(value=4)
        self.scale = tk.DoubleVar(value=260)
        self.rotation = tk.DoubleVar(value=0)
        self.print_size = tk.DoubleVar(value=180)
        self.thickness = tk.DoubleVar(value=3)
        self.palette_name = tk.StringVar(value="Sunset Glass")
        self._add_slider(panel, "RECURSION DEPTH", self.depth, 0, 7, 1, "depth_value")
        self._add_slider(panel, "SCALE", self.scale, 120, 420, 10, "scale_value")
        self._add_slider(panel, "ROTATION", self.rotation, -180, 180, 1, "rotation_value")
        ttk.Label(panel, text="COLOR LANGUAGE", style="Panel.TLabel").pack(anchor="w", pady=(0, 7))
        palette_picker = ttk.Combobox(panel, textvariable=self.palette_name,
                          values=list(self.PALETTES), state="readonly",
                          width=21)
        palette_picker.pack(fill="x", pady=(0, 19))
        palette_picker.bind("<<ComboboxSelected>>", lambda _event: self.draw())
        ttk.Separator(panel).pack(fill="x", pady=24)
        ttk.Label(panel, text="3D PRINT / MILLIMETRES", style="Panel.TLabel",
              font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 14))
        self._add_slider(panel, "PRINT SIZE", self.print_size, 80, 240, 10, "print_size_value")
        self._add_slider(panel, "THICKNESS", self.thickness, 0.8, 8, 0.2, "thickness_value")
        ttk.Separator(panel).pack(fill="x", pady=(4, 20))
        self.count_value = ttk.Label(panel, style="Value.TLabel")
        self.count_value.pack(anchor="w")
        ttk.Label(panel, text="visible triangles", style="Panel.TLabel").pack(anchor="w")
        ttk.Label(panel, text="The golden ratio drives every cut.\nEach generation replaces a tile\nwith two or three smaller tiles.",
                  style="Subheading.TLabel", justify="left").pack(anchor="w", pady=(22, 0))
        ttk.Button(panel, text="REGENERATE", style="Action.TButton",
                   command=self.render).pack(fill="x", pady=(28, 8))
        ttk.Button(panel, text="EXPORT SVG", style="Secondary.TButton",
               command=self.export_svg).pack(fill="x", pady=(0, 8))
        ttk.Button(panel, text="EXPORT STL FOR 3D PRINT", style="Secondary.TButton",
               command=self.export_stl).pack(fill="x")
        self.canvas = tk.Canvas(canvas_frame, background=self.BG, highlightthickness=1,
                                highlightbackground=self.GRID)
        self.canvas.pack(fill="both", expand=True)
        self.status = ttk.Label(shell, text="READY  /  10-fold seed", style="Subheading.TLabel")
        self.status.pack(anchor="w", pady=(14, 0))

    def _add_slider(self, parent: ttk.Frame, label: str, variable: tk.Variable,
                    start: float, end: float, resolution: float, value_name: str) -> None:
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(0, 20))
        top = ttk.Frame(row, style="Panel.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text=label, style="Panel.TLabel").pack(side="left")
        value_label = ttk.Label(top, style="Value.TLabel")
        value_label.pack(side="right")
        setattr(self, value_name, value_label)
        ttk.Scale(row, from_=start, to=end, variable=variable,
                  command=lambda _value: self._update_value_labels()).pack(fill="x", pady=(9, 0))

    def _bind_events(self) -> None:
        for variable in (self.depth, self.scale, self.rotation, self.print_size, self.thickness):
            variable.trace_add("write", lambda *_args: self._update_value_labels())
        self.canvas.bind("<Configure>", lambda _event: self.draw())

    def _update_value_labels(self) -> None:
        self.depth_value.configure(text=f"{self.depth.get():02d}")
        self.scale_value.configure(text=f"{self.scale.get():.0f}")
        self.rotation_value.configure(text=f"{self.rotation.get():.0f}°")
        self.print_size_value.configure(text=f"{self.print_size.get():.0f} mm")
        self.thickness_value.configure(text=f"{self.thickness.get():.1f} mm")

    def render(self) -> None:
        depth = self.depth.get()
        self.triangles = generate(depth, self.scale.get(), self.rotation.get())
        self._update_value_labels()
        self.count_value.configure(text=f"{len(self.triangles):,}")
        self.status.configure(text=f"GENERATED  /  DEPTH {depth}  /  PHI = {PHI:.6f}")
        self.draw()

    def draw(self) -> None:
        if not self.triangles:
            return
        palette = self.PALETTES[self.palette_name.get()]
        self.canvas.configure(background=palette["background"])
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        center_x, center_y = width / 2, height / 2
        padding = 30
        points = [point for triangle in self.triangles for point in (triangle.a, triangle.b, triangle.c)]
        max_extent = max(max(abs(point.real) for point in points), max(abs(point.imag) for point in points), 1)
        factor = min((width - padding * 2) / (2 * max_extent),
                     (height - padding * 2) / (2 * max_extent))

        for index, triangle in enumerate(self.triangles):
            coords = []
            for point in (triangle.a, triangle.b, triangle.c):
                coords.extend((center_x + point.real * factor, center_y - point.imag * factor))
            fill = palette["tiles"][(index + triangle.kind * 2) % len(palette["tiles"])]
            self.canvas.create_polygon(*coords, fill=fill, outline=palette["edge"], width=1)

        self.canvas.create_oval(center_x - 2, center_y - 2, center_x + 2, center_y + 2,
                                fill=palette["tiles"][0], outline="")

    def export_svg(self) -> None:
        if not self.triangles:
            return
        path = filedialog.asksaveasfilename(
            title="Export Penrose tiling", defaultextension=".svg",
            filetypes=[("SVG vector", "*.svg")], initialfile="penrose_tiling.svg")
        if not path:
            return
        width = max(self.canvas.winfo_width(), 800)
        height = max(self.canvas.winfo_height(), 600)
        points = [point for triangle in self.triangles for point in (triangle.a, triangle.b, triangle.c)]
        max_extent = max(max(abs(point.real) for point in points), max(abs(point.imag) for point in points), 1)
        factor = min((width - 60) / (2 * max_extent), (height - 60) / (2 * max_extent))
        palette = self.PALETTES[self.palette_name.get()]
        polygons = []
        for index, triangle in enumerate(self.triangles):
            coords = []
            for point in (triangle.a, triangle.b, triangle.c):
                coords.append(f"{width / 2 + point.real * factor:.2f},{height / 2 - point.imag * factor:.2f}")
            color = palette["tiles"][(index + triangle.kind * 2) % len(palette["tiles"])]
            polygons.append(f'  <polygon points="{" ".join(coords)}" fill="{color}" stroke="{palette["edge"]}" stroke-width="1"/>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
               f'viewBox="0 0 {width} {height}">\n<rect width="100%" height="100%" fill="{palette["background"]}"/>\n'
               + "\n".join(polygons) + "\n</svg>\n")
        Path(path).write_text(svg, encoding="utf-8")
        self.status.configure(text=f"EXPORTED  /  {Path(path).name}")

    def export_stl(self) -> None:
        """Export each 2D tile as a closed extruded solid for slicing."""
        if not self.triangles:
            return
        path = filedialog.asksaveasfilename(
            title="Export printable Penrose design", defaultextension=".stl",
            filetypes=[("STL 3D model", "*.stl")], initialfile="penrose_tiling.stl")
        if not path:
            return
        points = [point for triangle in self.triangles for point in (triangle.a, triangle.b, triangle.c)]
        max_extent = max(max(abs(point.real) for point in points), max(abs(point.imag) for point in points), 1)
        factor = self.print_size.get() / (2 * max_extent)
        height = self.thickness.get()

        def vertex(point: complex, z: float) -> tuple[float, float, float]:
            return (self.print_size.get() / 2 + point.real * factor,
                    self.print_size.get() / 2 + point.imag * factor, z)

        def facet(normal: tuple[int, int, int], first: tuple[float, float, float],
                  second: tuple[float, float, float], third: tuple[float, float, float]) -> str:
            values = " ".join(f"{value:.5f}" for value in (*first, *second, *third))
            return (f"  facet normal {' '.join(str(value) for value in normal)}\n"
                    f"    outer loop\n      vertex {values.split()[0]} {values.split()[1]} {values.split()[2]}\n"
                    f"      vertex {values.split()[3]} {values.split()[4]} {values.split()[5]}\n"
                    f"      vertex {values.split()[6]} {values.split()[7]} {values.split()[8]}\n"
                    f"    endloop\n  endfacet\n")

        facets: list[str] = []
        for triangle in self.triangles:
            bottom = [vertex(point, 0) for point in (triangle.a, triangle.b, triangle.c)]
            top = [vertex(point, height) for point in (triangle.a, triangle.b, triangle.c)]
            facets.append(facet((0, 0, 1), top[0], top[1], top[2]))
            facets.append(facet((0, 0, -1), bottom[2], bottom[1], bottom[0]))
            for index in range(3):
                next_index = (index + 1) % 3
                facets.append(facet((0, 0, 0), bottom[index], bottom[next_index], top[next_index]))
                facets.append(facet((0, 0, 0), bottom[index], top[next_index], top[index]))
        Path(path).write_text("solid penrose_tiling\n" + "".join(facets) + "endsolid penrose_tiling\n", encoding="ascii")
        self.status.configure(text=f"EXPORTED STL  /  {Path(path).name}  /  {len(facets):,} facets")


def main() -> None:
    root = tk.Tk()
    PenroseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
