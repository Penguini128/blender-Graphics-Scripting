import bpy

def build_material(mat_name, base_color, roughness, metallic, transmission, IOR):
    material_name = mat_name
    new_mat = False
    if material_name not in bpy.data.materials:
        new_mat = True
        bpy.data.materials.new(name=material_name)
        
    material = bpy.data.materials[material_name]
    
    if new_mat:
        material.use_nodes = True
        # Color
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = base_color
        # Metallic
        material.node_tree.nodes["Principled BSDF"].inputs[1].default_value = metallic
        # Transmission
        material.node_tree.nodes["Principled BSDF"].inputs[17].default_value = transmission
        # IOR
        material.node_tree.nodes["Principled BSDF"].inputs[3].default_value = IOR
        # Roughness
        material.node_tree.nodes["Principled BSDF"].inputs[2].default_value = roughness
        
    return material



