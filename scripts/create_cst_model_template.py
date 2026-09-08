"""Starter template for generating CST Microwave Studio models.

Copy this script into a project and replace the parameter dictionary and VBA
blocks with the requested geometry, material, port, and solver setup.
"""

from __future__ import annotations

import win32com.client


def send_vba_to_cst(mws, history_name: str, vba_code: str) -> None:
    """Send a VBA block to CST history using win32com late binding."""
    mws._FlagAsMethod("AddToHistory")
    mws.AddToHistory(history_name, vba_code.strip())


def create_new_mws():
    cst = win32com.client.Dispatch("CSTStudio.Application")
    return cst.NewMWS()


def store_parameters(mws, parameters: dict[str, str]) -> None:
    for name, value in parameters.items():
        send_vba_to_cst(mws, f"Define Parameter {name}", f'StoreParameter "{name}", "{value}"')


def build_model() -> None:
    mws = create_new_mws()

    parameters = {
        "block_x": "100",
        "block_y": "300",
        "block_z": "100",
        "hole_d": "50",
    }
    store_parameters(mws, parameters)

    vba_geometry = """
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
    send_vba_to_cst(mws, "Create geometry", vba_geometry)


if __name__ == "__main__":
    build_model()

