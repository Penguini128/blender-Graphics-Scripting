import bpy
import numpy as np

frame = bpy.data.texts["frame.py"].as_module()
LOCAL, GLOBAL = frame.Frame.LOCAL, frame.Frame.GLOBAL

####################################################################################################


class Scene:
    def __init__(self):
        self.obj_dict = {}
        
    def add(self, mesh_object):
        self.obj_dict[mesh_object.name] = mesh_object
        return mesh_object
    def get(self, name):
        if not name in self.obj_dict.keys():
            return None
        return self.obj_dict.get(name)
            
    def apply_all_transform_buffers(self):
        for key in self.obj_dict:
            self.obj_dict[key].apply_transform_buffer()   
    
    def apply_transform_buffer(self, name):
        object = self.get(name)
        if object is None:
            return
        object.apply_transform_buffer()
        
    def transform(self, name, transformations):
        object = self.get(name)
        if object is None:
            return
        for transformation in transformations:
            if transformation[0].value == GLOBAL.value:
                object.global_transform(transformation[1])
            elif transformation[0].value == LOCAL.value:
                object.local_transform(transformation[1])
            
    def set_properties(self, name, properties):
        object = self.get(name)
        if object is None:
            return
        for property in properties:
            property_name, property_settings = property[0], property[1:]
            if property_name == "SMOOTH":
                object.set_smooth(property_settings[0])
            elif property_name == "AUTO_SMOOTH":
                if len(property_settings) == 1:
                    object.set_auto_smooth(property_settings[0])
                else:
                    object.set_auto_smooth(property_settings[0],
                                           property_settings[1])
            elif property_name == "BEVEL":
                if len(property_settings) == 1:
                    object.set_bevel(property_settings[0])
                elif len(property_settings) == 2:
                    object.set_bevel(property_settings[0],
                                     property_settings[1])
                else:
                    object.set_bevel(property_settings[0],
                                     property_settings[1],
                                     property_settings[2])
            elif property_name == "SUBSURF":
                object.set_subsurf(property_settings[0])
            elif property_name == "MATERIAL":
                object.set_material(property_settings[0])
            elif property_name == "PARENT":
                parent_object = property_settings[0]
                if parent_object is None:
                    print(f"ERROR:   Parent object {property_settings[0]} not found.")
                    return
                parent_object.children.append(object)
                
    def add_keyframe(self, anim_frame, name="", all=False):
        if all == True:
            self.apply_all_transform_buffers()
            for key in self.obj_dict:
                self.obj_dict[key].add_keyframe(anim_frame)
        else:
            object = self.get(name)
            if object is None:
                return
            object.add_keyframe(anim_frame)