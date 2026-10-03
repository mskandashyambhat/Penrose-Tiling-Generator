# Penrose Tiling Generator

This is a small Python application for exploring Penrose tilings. It uses the golden ratio and recursive Robinson triangle subdivision to produce a non-periodic pattern.

The desktop interface lets you change the recursion depth, scale, rotation, palette, print size, and extrusion thickness. The current design can be exported as SVG or as an ASCII STL model for a 3D printer.

## Running it

The project uses only the Python standard library. It needs a Python installation with Tk support.

```bash
python3 penrose_tiling.py
```

In VS Code, the same program can be started with the `Run Penrose Tiling` launch configuration in `.vscode/launch.json`.

On macOS with Homebrew Python, install Tk separately if needed:

```bash
brew install python-tk@3.14
```

## Exporting a model

Set the print size and thickness in the control panel, then choose `EXPORT STL FOR 3D PRINT`. The resulting file can be opened in a slicer such as Cura, PrusaSlicer, or Bambu Studio.

For a first print, a size between 120 and 180 mm, a thickness of 2 to 4 mm, and recursion depth 3 or 4 are reasonable starting values.

## The construction

The generator uses

```text
phi = (1 + sqrt(5)) / 2
```

New points are placed at a `1 / phi` fraction along the edges of each triangle. Thin Robinson triangles are replaced by two children, while thick triangles are replaced by three. Repeating those substitutions creates the aperiodic pattern.
