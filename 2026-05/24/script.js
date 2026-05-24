rolling_context = {
    var_1 ="xx",
    var_2 = "xx",
    var_3 = "xx",
}

sections = design_specs.get(sections, [])

for section, index in enumerate(sections):
    ...something...
    ...somethinh...
    ...something...

    build_section(
        image_memory
        rolling_context
        global_blueprint
        section
        ...
        )

    ...soemthing...

    rolling_context.append(...)

rolling_context = rolling_context[-2:]