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
        adjcency_
        best_chunks
        ...
        )

    ...soemthing...

    rolling_context["previous_sections"].append(
        {
                ...
            }
        )

    rolling_context["previous_sections"] = rolling_context["previous_sections"][-2:]