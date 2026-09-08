---
name: cst-generator
description: Generate CST Studio Suite models and automate native Array Tasks and Full Array projects, geometry, parameters, ports, materials, solver setup, and exports using Python-driven VBA or CST COM scripts.
---

# CST Generator

Use this skill when the user asks to generate or automate a CST Studio Suite model, especially Microwave Studio antenna, RF, waveguide, enclosure, block, cylinder, boolean, port, boundary, monitor, or solver setup work.

## Workflow

- Convert the request into CST parameters first: units, dimensions, materials, components, coordinate ranges, frequency range, boundaries, ports, excitations, monitors, mesh, and expected outputs.
- Prefer Python that sends CST VBA through `cst.interface` or `win32com.client`, matching the user's existing project style. Use plain CST VBA only when the user asks for a macro.
- Use CST model units deliberately. In this workspace, default geometry dimensions are millimeters unless the user specifies otherwise.
- Create geometry with CST primitives such as `Brick`, `Cylinder`, `Sphere`, `Curve`, and Boolean operations like `Solid.Subtract`; name every important object and component.
- For RF models, do not stop at geometry when the request implies simulation: define materials, frequency range, ports, boundaries, monitors, and solver settings when enough information is available.
- Ask a short question only when a missing value changes the electromagnetic intent, such as substrate material, port type, frequency band, boundary condition, or feed location. Otherwise choose conservative defaults and state them in comments.
- Do not overwrite existing `.cst` projects, run long simulations, or delete model objects unless the user explicitly asks.
- If CST is installed and interactive execution is appropriate, run the script and report whether CST accepted the model history. If CST cannot be launched, leave a runnable script and explain the remaining in-CST validation.

## References

- For native Array Task / Full Array automation, optimized-element preservation, shared reflectors, excitation setup, and verification, read [references/cst-array-task-workflow.md](references/cst-array-task-workflow.md). Use this route when the user asks for an Array Task; creating copied geometry alone does not fulfill a native Array Task request.

- For Python/VBA patterns, geometry snippets, Boolean subtraction, parameters, ports, and a complete block-with-hole example, read [references/cst-python-vba-generation.md](references/cst-python-vba-generation.md).
- For a reusable Python starter script, use [scripts/create_cst_model_template.py](scripts/create_cst_model_template.py).

