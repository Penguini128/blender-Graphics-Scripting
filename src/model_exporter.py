import bpy
import os

def export_selected_to_tgif():
    
    print("\nMake sure an object is selected!")
    filepath = input("Input exported file name: ")
    
    if filepath[-5:] != ".tgif":
        filepath += ".tgif"
    
    project_dir = bpy.path.abspath("//")
    full_path = os.path.join(project_dir, filepath)
    
    selected_object = bpy.context.active_object
    
    
    
    mesh_data = selected_object.data
    vertices = mesh_data.vertices
    faces = mesh_data.polygons
    material_slots = selected_object.material_slots
    
    output = open(full_path, "w")
    output.write("tgif\n")
    output.write("comment Tommy Galletta's Instance Format\n")
    output.write(f"element materials {len(material_slots)}\n")
    output.write(f"element vertex {len(vertices)}\n")
    output.write(f"element face {len(faces)}\n")
    
    if mesh_data.use_auto_smooth:
        output.write(f"property smooth auto {mesh_data.auto_smooth_angle}\n")
    elif mesh_data.polygons[0].use_smooth:
        output.write(f"property smooth true\n")
    else:
        output.write(f"property smooth false\n")
        
    for modifier in selected_object.modifiers:
        if modifier.type == 'SUBSURF':
            output.write(f"property modifier subsurf {modifier.levels}\n")
        elif modifier.type == 'BEVEL':
            output.write(f"property modifier bevel {modifier.width} {modifier.segments}\n")
    
    output.write("end_header\n")
    for slot in material_slots:            
        material = slot.material
        
        if material.use_nodes:
            principled = material.node_tree.nodes["Principled BSDF"].inputs
            base_color = principled[0].default_value[:]
            metallic = principled[1].default_value
            roughness = principled[2].default_value
            IOR = principled[3].default_value
            transmission = principled[17].default_value
        else:
            base_color = material.diffuse_color[:]
            roughness = material.roughness
            metallic = material.metallic
            IOR = 1.450
            transmission = 1
        output.write(f"name {material.name}\n")
        output.write(f"base_color {base_color[0]} {base_color[1]} {base_color[2]} {base_color[3]}\n")
        output.write(f"metallic {metallic}\n")
        output.write(f"roughness {roughness}\n")
        output.write(f"IOR {IOR}\n")
        output.write(f"transmission {transmission}\n")
        output.write(f"end_material\n")
    for vertex in vertices:
        output.write(f"{vertex.co[0]} {vertex.co[1]} {vertex.co[2]}\n")
    for face in faces:
        face_verts = face.vertices
        index_string = ""
        for vert in face_verts:
            index_string += f"{vert} "
        output.write(f"{len(face_verts)} {index_string}m {face.material_index}\n")
    
    output.close()
    print(f"Exported model \"{filepath}\" saved to:\n{full_path}")

########################################################################
# YOU MUST HAVE THE BLENDER CONSOLE OPEN IN ORDER TO RUN THIS PROPERLY #
########################################################################
export_selected_to_tgif()