def build_email(reference_html, embeddings, design_spec, images_library):
    
    shell = extract_reference_shell(reference_html)
    
    final_parts = [shell["head_part"], shell["body_part"]]
    global_blueprint = design_spec.get("global_blueprint", {})
    preheader_html = update_preheader_html(shell["preheader_html"], global_blueprint.get("preheader_html", ""))
    ...
    
    
    
    return final_html