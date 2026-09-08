# CST Python/VBA Generation Reference

Use this reference when generating a CST Studio Suite model from natural language.

## Preferred Automation Patterns

This workspace already uses two CST automation styles:

- `win32com.client.Dispatch("CSTStudio.Application")`, `cst.NewMWS()`, and `mws.AddToHistory(...)`
- `cst.interface.DesignEnvironment()`, `de.new_mws()`, and `model3d._execute_vba_code(...)`

Prefer the style already present in the target script or project. For new standalone scripts, `win32com.client` is usually easier to run from ordinary Python environments; `cst.interface` is useful when the CST Python package is configured.

## Python COM Helper

```python
import win32com.client


def send_vba_to_cst(mws, history_name, vba_code):
    mws._FlagAsMethod("AddToHistory")
    mws.AddToHistory(history_name, vba_code.strip())


def new_mws():
    cst = win32com.client.Dispatch("CSTStudio.Application")
    return cst.NewMWS()
```

## Units And Parameters

CST geometry in this workspace should default to millimeters. Store dimensions as CST parameters when the model should remain editable:

```vb
StoreParameter "W_sub", "60"
StoreParameter "L_sub", "60"
StoreParameter "h", "1.6"
```

When generating Python scripts, keep numeric values in one `parameters` dictionary and send each as `StoreParameter`.

## Common Geometry Snippets

Brick:

```vb
With Brick
     .Reset
     .Name "Block"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "-50", "50"
     .Yrange "-150", "150"
     .Zrange "0", "100"
     .Create
End With
```

Cylinder:

```vb
With Cylinder
     .Reset
     .Name "HoleTool"
     .Component "tools"
     .Material "Vacuum"
     .Axis "z"
     .Xcenter "0"
     .Ycenter "0"
     .Zrange "-1", "101"
     .OuterRadius "25"
     .InnerRadius "0"
     .Segments "0"
     .Create
End With
```

Boolean subtraction:

```vb
Solid.Subtract "component1:Block", "tools:HoleTool"
```

## RF Setup Snippets

Frequency range:

```vb
Solver.FrequencyRange "4", "7"
```

Discrete port:

```vb
With DiscretePort
     .Reset
     .PortNumber "1"
     .Type "SParameter"
     .Impedance "50"
     .Voltage "1.0"
     .Current "1.0"
     .Monitor "True"
     .Point1 "xp", "yp", "0"
     .Point2 "xp", "yp", "h"
     .InvertDirection "False"
     .LocalCoordinates "False"
     .Create
End With
```

Lossy FR-4 material:

```vb
With Material
     .Reset
     .Name "FR-4 (lossy)"
     .Type "Normal"
     .Epsilon "4.3"
     .TanD "0.025"
     .TanDFreq "10.0"
     .TanDGiven "True"
     .TanDModel "ConstTanD"
     .Create
End With
```

## Complete Example: 10 x 30 x 10 cm Block With 5 cm Hole

The dimensions below are in millimeters: 10 cm = 100 mm, 30 cm = 300 mm, hole diameter 5 cm = 50 mm.

```python
import win32com.client


def send_vba_to_cst(mws, history_name, vba_code):
    mws._FlagAsMethod("AddToHistory")
    mws.AddToHistory(history_name, vba_code.strip())


def create_block_with_hole():
    cst = win32com.client.Dispatch("CSTStudio.Application")
    mws = cst.NewMWS()

    parameters = {
        "block_x": "100",
        "block_y": "300",
        "block_z": "100",
        "hole_d": "50",
    }

    for name, value in parameters.items():
        send_vba_to_cst(mws, f"Define Parameter {name}", f'StoreParameter "{name}", "{value}"')

    vba = """
With Brick
     .Reset
     .Name "Block_10x30x10cm"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "-block_x/2", "block_x/2"
     .Yrange "-block_y/2", "block_y/2"
     .Zrange "0", "block_z"
     .Create
End With
With Cylinder
     .Reset
     .Name "HoleTool_D5cm"
     .Component "tools"
     .Material "Vacuum"
     .Axis "z"
     .Xcenter "0"
     .Ycenter "0"
     .Zrange "-1", "block_z+1"
     .OuterRadius "hole_d/2"
     .InnerRadius "0"
     .Segments "0"
     .Create
End With
Solid.Subtract "component1:Block_10x30x10cm", "tools:HoleTool_D5cm"
"""
    send_vba_to_cst(mws, "Create block with centered through hole", vba)


if __name__ == "__main__":
    create_block_with_hole()
```

## Response Pattern

When delivering CST generation work, include:

- Units and key parameters.
- Whether the model was actually sent to CST or only generated as a script.
- The output path for the script or `.cst` project if saved.
- Any assumptions about material, solver, port, frequency range, or boundary conditions.

