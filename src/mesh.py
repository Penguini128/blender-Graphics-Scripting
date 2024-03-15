import bpy
import numpy as np
import math
import os
mh = bpy.data.texts["matrix_helper.py"].as_module()
frame = bpy.data.texts["frame.py"].as_module()
materials = bpy.data.texts["materials.py"].as_module()
LOCAL, GLOBAL = frame.Frame.LOCAL, frame.Frame.GLOBAL

####################################################################################################

def mesh_initialize(mesh_class, name):
    mesh_class.mesh_data = bpy.data.meshes.new(f"{name.lower().replace(' ', '_')}_data")
    mesh_class.mesh_data.from_pydata(mesh_class.verts, mesh_class.edges, mesh_class.faces)   
    mesh_class.mesh_object = bpy.data.objects.new(name, mesh_class.mesh_data)
    bpy.context.collection.objects.link(mesh_class.mesh_object)
    
    obj_data = mesh_class.mesh_data
    for vert in obj_data.vertices:
        new_vert = Vertex(vert)
        mesh_class.vert_objects.append(new_vert)

class Vertex:
    def __init__(self, vert):
        self._original_pos = np.array([vert.co[0], vert.co[1], vert.co[2]])
        self._vert = vert

class GenericMesh:
    def __init__(self, name="Mesh"):
        self.verts = []
        self.faces = []
        self.edges = []
        self.vert_objects = []
        self.children = []
        self.parent = None
        self.name = name
        self.buffer_frame = np.identity(4)
        self.local_frame = np.identity(4)
        
    def apply_transform_buffer(self, with_children=True):
        self.local_frame = self.buffer_frame @ self.local_frame
        for vert in self.vert_objects:
            vert_location = mh.translation(vert._vert.co[0],
                                           vert._vert.co[1],
                                           vert._vert.co[2])
            updated_matrix = self.buffer_frame @ vert_location
            updated_co = mh.extract_location(updated_matrix)
            vert._vert.co = updated_co
        self.buffer_frame = np.identity(4)
        if with_children:
            for child in self.children:
                child.apply_transform_buffer()    
    
    def apply_transform(self):
        self.apply_transform_buffer()
        self.buffer_frame = np.identity(4)
        self.local_frame = np.identity(4)
        for vert in self.vert_objects:
            vert._original_pos = np.array(vert._vert.co)
        for child in self.children:
            child.apply_transform()
        
    def global_transform(self, transformation):
        self.buffer_frame = transformation @ self.buffer_frame
        for child in self.children:
            child.global_transform(transformation)
            
    def local_transform(self, transformation, transform_frame=None):
        if transform_frame is None:
            transform_frame = self.buffer_frame @ self.local_frame
        transform_inv = np.linalg.inv(transform_frame)
        self.buffer_frame = transform_frame @ transformation @ transform_inv @ self.buffer_frame
        for child in self.children:
            child.local_transform(transformation, transform_frame)
            
    def add_keyframe(self, anim_frame):
        self.apply_transform_buffer()
        for vert in self.vert_objects:
            vert._vert.keyframe_insert(data_path='co', frame=anim_frame)
            
    def set_smooth(self, state):
        for face in self.mesh_data.polygons:
            face.use_smooth = state
            
    def set_auto_smooth(self, state, angle=45):
        self.mesh_data.use_auto_smooth = state
        self.mesh_data.auto_smooth_angle = angle / 180 * math.pi
        self.set_smooth(state)
        
    def set_subsurf(self, levels=1):
        modifiers_stack = self.mesh_object.modifiers
        if not "Subdivision" in modifiers_stack:
            modifiers_stack.new(name="Subdivision", type="SUBSURF")
        modifiers_stack["Subdivision"].levels = levels
        
    def set_bevel(self, width=0.1, segments=1):
        modifiers_stack = self.mesh_object.modifiers
        if not "Bevel" in modifiers_stack:
            modifiers_stack.new(name="Bevel", type="BEVEL")
        modifiers_stack["Bevel"].width = width
        modifiers_stack["Bevel"].segments = segments
        
    def set_material(self, material):
        name = "Unnamed Material"
        metallic = 0
        roughness = 0.5
        IOR = 1.450
        transmission = 0
        base_color = (1, 1, 1, 1)
        for param in material:
            if param[0] == "METALLIC":
                metallic = param[1]
            elif param[0] == "ROUGHNESS":
                roughness = param[1]
            elif param[0] == "TRANSMISSION":
                transmission = param[1]
            elif param[0] == "IOR":
                IOR = param[1]
            elif param[0] == "BASE_COLOR":
                base_color = param[1]
            elif param[0] == "NAME":
                name = param[1]
        self.mesh_data.materials.append(materials.build_material(
                                        name,
                                        base_color,
                                        roughness,
                                        metallic,
                                        transmission,
                                        IOR
                                        ))
                
    
    def transform(self, transformations):
        for transformation in transformations:
            if transformation[0].value == GLOBAL.value:
                self.global_transform(transformation[1])
            elif transformation[0].value == LOCAL.value:
                self.local_transform(transformation[1])
            
    def set_properties(self, properties):
        for property in properties:
            property_name, property_settings = property[0], property[1:]
            if property_name == "SMOOTH":
                self.set_smooth(property_settings[0])
            elif property_name == "AUTO_SMOOTH":
                if len(property_settings) == 1:
                    self.set_auto_smooth(property_settings[0])
                else:
                    self.set_auto_smooth(property_settings[0],
                                           property_settings[1])
            elif property_name == "BEVEL":
                if len(property_settings) == 1:
                    self.set_bevel(property_settings[0])
                elif len(property_settings) == 2:
                    self.set_bevel(property_settings[0],
                                     property_settings[1])
                else:
                    self.set_bevel(property_settings[0],
                                     property_settings[1],
                                     property_settings[2])
            elif property_name == "SUBSURF":
                self.set_subsurf(property_settings[0])
            elif property_name == "MATERIAL":
                self.set_material(property_settings[0])
            elif property_name == "PARENT":
                parent_object = property_settings[0]
                parent_object.children.append(self)
            
         

####################################################################################################

class Cuboid(GenericMesh):
    def __init__(self, name, dim_x=1, dim_y=1, dim_z=1):
        super(Cuboid, self).__init__(name)
        
        dim_x = max(0, dim_x)
        dim_y = max(0, dim_y)
        dim_z = max(0, dim_z)
        
        dim_x /= 2
        dim_y /= 2
        dim_z /= 2
        
        self.verts = [(-dim_x, -dim_y, -dim_z),
                      (-dim_x, -dim_y,  dim_z),
                      (-dim_x,  dim_y, -dim_z),
                      (-dim_x,  dim_y,  dim_z),
                      ( dim_x, -dim_y, -dim_z),
                      ( dim_x, -dim_y,  dim_z),
                      ( dim_x,  dim_y, -dim_z),
                      ( dim_x,  dim_y,  dim_z)]
                 
        self.faces = [(0, 1, 3, 2),
                      (4, 5, 1, 0),
                      (6, 7, 5, 4),
                      (2, 3, 7, 6),
                      (3, 1, 5, 7),
                      (0, 2, 6, 4)]
    
        mesh_initialize(self, name)
            
class Cylinder(GenericMesh):
    def __init__(self, name, radius=0.5, height=1, segments=16):
        super(Cylinder, self).__init__(name)
        
        radius = max(0, radius)
        height = max(0, height)
        segments = max(3, segments)
        
        half_height = height / 2
        
        segment_angle = 2 * math.pi / segments
        for i in range(segments):
            cos_dis = math.cos(segment_angle*i)*radius
            sin_dis = math.sin(segment_angle*i)*radius
            self.verts.append((cos_dis, sin_dis, -half_height))
            self.verts.append((cos_dis, sin_dis, half_height))
            
        self.faces.append(tuple([i*2 for i in range(segments)][::-1]))
        self.faces.append(tuple([i*2+1 for i in range(segments)]))
        
        for i in range(segments):
            one = i*2 % (segments*2)
            two = (i*2 + 1) % (segments*2)
            three = (i*2 + 2) % (segments*2)
            four = (i*2 + 3) % (segments*2)
            self.faces.append((one, three, four, two))
        
        mesh_initialize(self, name)
        
        
        
class Sphere(GenericMesh):
    def __init__(self, name, radius=0.5, rings=12, segments=24):
        super(Sphere, self).__init__(name)
        
        radius = max(0, radius)
        rings = max(1, rings)
        segments = max(3, segments)
        
        ring_angle = math.pi / (rings + 1)
        segment_angle = 2 * math.pi / segments
        
        # Create "howest" vertex
        self.verts.append((0, 0, -radius))
        
        # Create "middle" vertices
        for i in range(rings):
            current_ring = ring_angle * (i+1)
            for j in range(segments):
                current_segment = segment_angle * j
                z_pos = -math.cos(current_ring) * radius
                y_pos = math.sin(current_ring) * math.sin(current_segment) * radius
                x_pos = math.sin(current_ring) * math.cos(current_segment) * radius
                self.verts.append((x_pos, y_pos, z_pos))
        
        # Create "highest" vertex
        self.verts.append((0, 0, radius))
                
        # Create "lowest ring" faces  
        for i in range(segments):
            one = 0
            two =  (i+1) % segments + 1
            three = i + 1
            self.faces.append((one, two, three))
        
        # Create "middle ring" faces
        for i in range(rings - 1):
            for j in range(segments):
                one = j + 1 + i * segments
                two = (j+1) % segments + 1 + i * segments
                three = j + 1 + (i + 1) * segments
                four = (j+1) % segments + 1 + (i + 1) * segments
                self.faces.append((one, two, three))
                self.faces.append((two, four, three))
        
        # Create "highest ring" faces
        for i in range(segments):
            one = i + 1 + (rings - 1) * segments
            two = (i+1) % segments + 1 + (rings - 1) * segments
            three = rings * segments + 1
            self.faces.append((one, two, three))
        
        mesh_initialize(self, name)
        
class Cone(GenericMesh):
    def __init__(self, name, radius=0.5, height=1, segments=16):
        super(Cone, self).__init__(name)
        
        radius = max(0, radius)
        height = max(0, height)
        segments = max(3, segments)
        
        segment_angle = 2 * math.pi / segments
        
        self.verts.append((0, 0, height))
        
        for i in range(segments):
            current_cos = math.cos(segment_angle * i)
            current_sin = math.sin(segment_angle * i)
            self.verts.append((current_cos * radius, current_sin * radius, 0))
            
        for i in range(segments):
            one = 0
            two = i + 1
            three = (i + 1) % segments + 1
            self.faces.append((one, two, three))
            
        self.faces.append(tuple([i+1 for i in range(segments)][::-1]))
            
        mesh_initialize(self, name)

class Plane(GenericMesh):
    def __init__(self, name, dim_x=1, dim_y=1):
        super(Plane, self).__init__(name)
        
        dim_x = max(0, dim_x)
        dim_y = max(0, dim_y)
        
        dim_x /= 2
        dim_y /= 2
        
        self.verts = [(-dim_x, -dim_y, 0),
                      (-dim_x,  dim_y, 0),
                      ( dim_x, -dim_y, 0),
                      ( dim_x,  dim_y, 0)]
                      
        self.faces = [(0, 2, 3, 1)]
            
        mesh_initialize(self, name)
        
class Circle(GenericMesh):
    def __init__(self, name, radius=0.5, segments=16):
        super(Circle, self).__init__(name)
        
        radius = max(0, radius)
        segments = max(3, segments)
        
        
        segment_angle = 2 * math.pi / segments
        
        for i in range(segments):
            current_cos = math.cos(segment_angle * i)
            current_sin = math.sin(segment_angle * i)
            self.verts.append((current_cos * radius, current_sin * radius, 0))
                      
        self.faces = [tuple([i for i in range(segments)])]
            
        mesh_initialize(self, name)
        
class Torus(GenericMesh):
    def __init__(self, name, major_radius=0.75, minor_radius=0.25,
                 major_segments=24, minor_segments=12):
        super(Torus, self).__init__(name)
        
        major_radius = max(0, major_radius)
        minor_radius = min(major_radius, minor_radius)
        major_segments = max(3, major_segments)
        minor_segments = max(3, minor_segments)
        
        major_segment_angle = 2 * math.pi / major_segments
        minor_segment_angle = 2 * math.pi / minor_segments
        
        for i in range(major_segments):
            for j in range(minor_segments):
                major_cos = math.cos(major_segment_angle * i)
                minor_cos = math.cos(minor_segment_angle * j)
                major_sin = math.sin(major_segment_angle * i)
                minor_sin = math.sin(minor_segment_angle * j)
                current_x = major_cos * major_radius + minor_cos*major_cos * minor_radius
                current_y = major_sin * major_radius + minor_cos*major_sin * minor_radius
                current_z = minor_sin * minor_radius
                self.verts.append((current_x, current_y, current_z))
                
        for i in range(major_segments):
            for j in range(minor_segments):
                one = j + i*minor_segments
                two = (j + 1) % minor_segments + i*minor_segments
                three = j + (i+1) % major_segments * minor_segments
                four = (j + 1) % minor_segments + (i+1) % major_segments * minor_segments
                self.faces.append((one, three, four, two))
                
        mesh_initialize(self, name)
        

class Empty(GenericMesh):
    def __init__(self, name):
        super(Empty, self).__init__(name)
        mesh_initialize(self, name)
        
class MeshFromPlyFile(GenericMesh):
    def __init__(self, name, filepath):
        if filepath[-4:] != ".ply":
            print(f"ERROR:   Mesh info could not be read from invalid file path \"{filepath}\".")
            super(MeshFromPlyFile, self).__init__("Invalid")
            mesh_initialize(self, "Invalid")
            
        super(MeshFromPlyFile, self).__init__(name)
        
        project_dir = bpy.path.abspath("//")
        full_path = os.path.join(project_dir, filepath)
        
        file = open(full_path)
        header_read = False
        num_vertices = 0
        num_faces = 0
        while not header_read:
            line = file.readline().strip()
            if line == "end_header":
                header_read = True
            else:
                tokens = line.split(" ")
                if tokens[0:2] == ["element", "vertex"]:
                    num_vertices = int(tokens[2])
                elif tokens[0:2] == ["element", "face"]:
                    num_faces = int(tokens[2])
        
        for i in range(num_vertices):
            self.verts.append(tuple([float(x) for x in file.readline().split(" ")]))
        for i in range(num_faces):
            self.faces.append(tuple([int(x) for x in file.readline().split(" ")][1:]))
        
        mesh_initialize(self, name)
        
class MeshFromTgifFile(GenericMesh):
    def __init__(self, name, filepath):
        if filepath[-5:] != ".tgif":
            print(f"ERROR:   Mesh info could not be read from invalid file path \"{filepath}\".")
            super(MeshFromPlyFile, self).__init__("Invalid")
            mesh_initialize(self, "Invalid")
            
        super(MeshFromTgifFile, self).__init__(name)
        
        project_dir = bpy.path.abspath("//")
        full_path = os.path.join(project_dir, filepath)
        
        file = open(full_path)
        
        header_read = False
        num_vertices = 0
        num_faces = 0
        num_materials = 0
        smooth = False
        auto_smooth_angle = -1
        
        temp_modifier_stack = []
        
        while not header_read:
            line = file.readline().strip()
            if line == "end_header":
                header_read = True
            else:
                tokens = line.split(" ")
                if tokens[0:2] == ["element", "vertex"]:
                    num_vertices = int(tokens[2])
                elif tokens[0:2] == ["element", "face"]:
                    num_faces = int(tokens[2])
                elif tokens[0:2] == ["element", "materials"]:
                    num_materials = int(tokens[2])
                elif tokens[0:2] == ["property", "smooth"]:
                    if tokens[2] == "true":
                        smooth = True
                    elif tokens[2] == "auto":
                        smooth = True
                        auto_smooth_angle = float(tokens[3])
                elif tokens[0:2] == ["property", "modifier"]:
                    temp_modifier_stack.append(tokens[2:])
                        
                    
        
        object_materials = []
        materials_read = 0
        current_base_color = (1, 1, 1 ,1)
        current_transmission = 0
        current_roughness = 0.5
        current_metallic = 0
        current_IOR = 1.450
        current_name = "Unnamed Material"
        while materials_read < num_materials:
            line = file.readline().strip()
            if line == "end_material":
                object_materials.append(materials.build_material(
                                        current_name,
                                        current_base_color,
                                        current_roughness,
                                        current_metallic,
                                        current_transmission,
                                        current_IOR
                                        ))
                materials_read += 1
                current_base_color = (1, 1, 1 ,1)
                current_transmission = 0
                current_roughness = 0.5
                current_metallic = 0
                current_IOR = 1.450
                current_name = "Unnamed Material"
            else:
                tokens = line.split(" ")
                if tokens[0] == "base_color":
                    current_base_color = (float(tokens[1]),
                                          float(tokens[2]), 
                                          float(tokens[3]), 
                                          float(tokens[4]))
                elif tokens[0] == "metallic":
                    current_metallic = float(tokens[1])
                elif tokens[0] == "IOR":
                    current_IOR = float(tokens[1])
                elif tokens[0] == "transmission":
                    current_transmission = float(tokens[1])
                elif tokens[0] == "roughness":
                    current_roughness = float(tokens[1])
                elif tokens[0] == "name":
                    current_name = " ".join(tokens[1:])
        
        face_material_indices = []
        for i in range(num_vertices):
            self.verts.append(tuple([float(x) for x in file.readline().split(" ")]))
        for i in range(num_faces):
            tokens = file.readline().split(" ")
            self.faces.append(tuple([int(x) for x in tokens[1:len(tokens)-2]]))
            face_material_indices.append(int(tokens[-1]))
        
        mesh_initialize(self, name)

        faces = self.mesh_data.polygons
        for i in range(len(faces)):
            faces[i].material_index = face_material_indices[i]
        for mat in object_materials:
            self.mesh_data.materials.append(mat)
            
        if auto_smooth_angle != -1:
            self.set_auto_smooth(True, auto_smooth_angle / math.pi * 180)
        elif smooth:
            self.set_smooth(True)
            
        for modifier in temp_modifier_stack:
            if modifier[0] == 'subsurf':
                self.set_subsurf(int(modifier[1]))
            elif modifier[0] == 'bevel':
                self.set_bevel(float(modifier[1]), int(modifier[2]))