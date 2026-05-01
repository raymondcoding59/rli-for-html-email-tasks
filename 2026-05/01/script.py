def pipeline():
    reference_html = load_file(reference_path)
    embeddings = create_embeddings(reference_html)
    images_library = build_image_library(reference_html)
    image_base64 = encode_image(design_path)
    design_specs = extract_design_specs(image_base64)
    
    final_html = build_email(reference_html, embeddings, design_specs, images_library)
    
    return final_html