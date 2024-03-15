import bpy
import numpy as np
import math
import time

mesh = bpy.data.texts["mesh.py"].as_module()
cleaner = bpy.data.texts["cleaner.py"].as_module()
mh = bpy.data.texts["matrix_helper.py"].as_module()
materials = bpy.data.texts["materials.py"].as_module()
ah = bpy.data.texts["animation_helper.py"].as_module()
scene_manager = bpy.data.texts["scene_manager.py"].as_module()
frame = bpy.data.texts["frame.py"].as_module()
LOCAL, GLOBAL = frame.Frame.LOCAL, frame.Frame.GLOBAL

glass = (("NAME", "Glass"), 
         ("IOR", 1.5),
         ("TRANSMISSION", 1))
         
shiny_metallic_blue = (("NAME", "Shiny Metallic Blue"),
                       ("BASE_COLOR", (0.007, 0.131, 0.294, 1)),
                       ("METALLIC", 1),
                       ("ROUGHNESS", 0.3))
                       
diffuse_aqua = (("NAME", "Diffuse Aqua"),
                ("BASE_COLOR", (0.0, 0.180, 0.690, 1)),
                ("ROUGHNESS", 0.8))
                
diffuse_black = (("NAME", "Diffuse Black"),
                ("BASE_COLOR", (0.01, 0.01, 0.01, 1)),
                ("ROUGHNESS", 0.8))

magenta_metal = (("NAME", "Magenta Metal"),
                 ("METALLIC", 1),
                 ("BASE_COLOR", (1, 0, 1, 1)),
                 ("ROUGHNESS", 0.15))

####################################################################################################

def multiple_joints_test():
    
    scene = scene_manager.Scene()
    
    suzanne = scene.add(mesh.MeshFromTgifFile('Suzanne', 'funky_monkey.tgif'))
    suzanne.transform([(GLOBAL, mh.translation(0, 0, -0.8)),
                       (GLOBAL, mh.rotation(180, axis='z'))])
    
    arm_1 = scene.add(mesh.Cylinder("Arm1", 0.08, 2, 12))
    arm_1.transform([(GLOBAL, mh.rotation(90, axis='y')),
                     (GLOBAL, mh.translation(1, 0, 0))])
    arm_1.set_properties([("AUTO_SMOOTH", True),
                          ("MATERIAL", glass),
                          ("PARENT", suzanne)])
                                  
    torus = scene.add(mesh.Torus("Torus", 1, 0.12, 32, 20))                                   
    torus.transform([(GLOBAL, mh.translation(3, 0, 0))])
    torus.set_properties([("SMOOTH", True),
                          ("MATERIAL", diffuse_black),
                          ("PARENT", arm_1)])     
    box = scene.add(mesh.Cuboid("Box", 0.3, 0.3, 0.3))
    box.transform([(GLOBAL, mh.translation(4, 0, 0))])
    box.set_properties([("SMOOTH", True),
                        ("BEVEL", 0.02, 3),
                        ("MATERIAL", diffuse_aqua),
                        ("PARENT", torus)])
    
    arm_2 = scene.add(mesh.Cylinder("Arm2", 0.08, 1, 12))
    arm_2.transform([(GLOBAL, mh.rotation(90, axis='y')),
                     (GLOBAL, mh.translation(4.5, 0, 0))])
    arm_2.set_properties([("AUTO_SMOOTH", True),
                          ("MATERIAL", glass),
                          ("PARENT", box)])
                                  
    hammer = scene.add(mesh.Cuboid("Hammer", 0.2, 0.2, 1.5))
    hammer.transform([(GLOBAL, mh.translation(5, 0, 0))])
    hammer.set_properties([("SMOOTH", True),
                           ("BEVEL", 0.02, 3),
                           ("MATERIAL", magenta_metal),
                           ("PARENT", arm_2)])
    
    total_angle = 0
    ANGLE_INCREMENT = 3
    anim_frame = 1
    
    z_rot = mh.rotation(-ANGLE_INCREMENT, axis='z')
    y_rot = mh.rotation(-ANGLE_INCREMENT*2, axis='y')
    x_rot = mh.rotation(-ANGLE_INCREMENT/2, axis='x')
    
    monkey_spin = ah.ease_in_out(-360*7, int(720/ANGLE_INCREMENT),
                                         int(360/ANGLE_INCREMENT),
                                         int(360/ANGLE_INCREMENT))
    while total_angle < 720:
        scene.add_keyframe(anim_frame, all=True)
        x_rot_monkey = mh.rotation(monkey_spin[anim_frame-1], axis='x')
        suzanne.transform([(GLOBAL, z_rot), (LOCAL, x_rot_monkey)])
        box.transform([(LOCAL, y_rot)])
        hammer.transform([(LOCAL, x_rot)])
        total_angle += ANGLE_INCREMENT
        anim_frame += 1

def ease_test():
    
    scene = scene_manager.Scene()
    
    cube = scene.add(mesh.Cuboid("Cube", 1, 1, 1))
    ease_over = ah.ease_in_out(-8, 50, 20, 20)
    print(ease_over)
    anim_frame = 1
    
    for frame in ease_over:
        scene.add_keyframe(anim_frame, all=True)
        cube.transform([(LOCAL, mh.translation(frame, 0, 0))])
        anim_frame += 1
    scene.add_keyframe(anim_frame, all=True)
        
    ease_back_forth = ah.ease_in(8, 30, 30) + ah.ease_out(-8, 30, 30)
    
    anim_frame = 60
    scene.add_keyframe(anim_frame, all=True)
    for frame in ease_back_forth:
        scene.add_keyframe(anim_frame, all=True)
        cube.transform([(LOCAL, mh.translation(frame, 0, 0))])
        anim_frame += 1
    scene.add_keyframe(anim_frame, all=True)
    
def bounce_test():
    
    scene = scene_manager.Scene()
    
    ball = scene.add(mesh.Sphere("Ball", 0.5))
    ball.transform([(GLOBAL, mh.translation(0, 0, 0.5))])
    ball.apply_transform()
    ball.set_properties([("SMOOTH", True)])
    
    bounce = ah.ease_out(6, 18, 18) + ah.ease_in(-6, 18, 18)
    bounce2 = ah.ease_out(5, 15, 15) + ah.ease_in(-5, 15, 15)
    bounce3 = ah.ease_out(4, 12, 12) + ah.ease_in(-4, 12, 12)
    bounce4 = ah.ease_out(3, 9, 9) + ah.ease_in(-3, 9, 9)
    bounce5 = ah.ease_out(2, 6, 6) + ah.ease_in(-2, 6, 6)
    bounce6 = ah.ease_out(1, 3, 3) + ah.ease_in(-1, 3, 3)
    bounces = bounce + bounce2 + bounce3 + bounce4 + bounce5 + bounce6
    
    anim_frame = 1
    for frame in bounces:
        scene.add_keyframe(anim_frame, all=True)
        ball.transform([(GLOBAL, mh.translation(0, 0, frame))])
        anim_frame += 1
    scene.add_keyframe(anim_frame, all=True)
    
def bounce_test_2():
    
    scene = scene_manager.Scene()
    
    scene.add(mesh.Plane("Plane", 4, 4))
    ball = scene.add(mesh.Sphere("Ball", 0.5))
    ball.transform([(GLOBAL, mh.translation(0, 0, 0.5)),
                             (GLOBAL, mh.scale(1.33, 1.33, 0.358))])
    ball.set_properties([("MATERIAL", materials.shiny_metallic_blue),
                         ("SMOOTH", True)])
    ball.apply_transform()

    squash_factor = 0.71
    strech_factor = 1.1
    bounce = ah.ease_out(6, 18, 18) + ah.ease_in(-6, 18, 18)
    bounces = bounce * 6
    
    squash = [1/squash_factor]*3 + [1]*30 + [squash_factor]*3
    squashes = squash * 6
    
    strech = [1/strech_factor]*3 + [1]*30 + [strech_factor]*3
    streches = strech * 6
    
    anim_frame = 1
    for i in range(len(bounces)):
        scene.add_keyframe(anim_frame, "Ball")
        ball.transform([(GLOBAL, mh.translation(0, 0, bounces[i])),
                        (LOCAL, mh.scale(streches[i], streches[i], squashes[i]))])
        
        anim_frame += 1
    scene.add_keyframe(anim_frame, "Ball")
    
def robot_arm():
    
    scene = scene_manager.Scene()
    
    floor = mesh.MeshFromTgifFile("Floor", "fancy_floor.tgif")
    
    suzanne = scene.add(mesh.MeshFromTgifFile("Monkey Idol", 'monkey_idol.tgif'))
    suzanne.transform([(GLOBAL, mh.translation(-.2, -.1, 0)),
                       (LOCAL, mh.rotation(30, axis='z'))])
    
    robot_base = scene.add(mesh.MeshFromTgifFile("Robot Base", 'robot_base.tgif'))
    
    robot_z_swivel = scene.add(mesh.MeshFromTgifFile("Robot Z Swivel", 'robot_z_swivel.tgif'))
    robot_z_swivel.set_properties([("PARENT", robot_base)])
    
    robot_arm_1 = scene.add(mesh.MeshFromTgifFile("Robot Arm 1", 'robot_arm_1.tgif'))
    robot_arm_1.local_transform(mh.translation(0.0035, 0, 0.1715))
    robot_arm_1.apply_transform_buffer()
    robot_arm_1.set_properties([("PARENT", robot_z_swivel)])
    
    robot_arm_2 = scene.add(mesh.MeshFromTgifFile("Robot Arm 2", 'robot_arm_2.tgif'))
    robot_arm_2.local_transform(mh.translation(0.0035, 0, 0.1715 + 0.221))
    robot_arm_2.apply_transform_buffer()
    robot_arm_2.set_properties([("PARENT", robot_arm_1)])
    
    robot_end = scene.add(mesh.MeshFromTgifFile("Robot End", 'robot_end.tgif'))
    robot_end.local_transform(mh.translation(-0.0305 + .0035, 0, 0.1715 + 0.221 + .235))
    robot_end.apply_transform_buffer()
    robot_end.set_properties([("PARENT", robot_arm_2)])
    
    robot_base.local_transform(mh.translation(0.1, 0.1, 0))
    
    robot_z_swivel.local_transform(mh.rotation(-20, axis='z'))
    robot_arm_1.local_transform(mh.rotation(25, axis='y'))
    robot_arm_2.local_transform(mh.rotation(25, axis='y'))
    
    #robot_z_swivel.local_transform(mh.rotation(-125, axis='z'))
    #robot_arm_1.local_transform(mh.rotation(37, axis='y'))
    #robot_arm_2.local_transform(mh.rotation(54, axis='y'))
    #robot_end.local_transform(mh.rotation(45, axis='y'))
    
    
    
    scene.apply_all_transform_buffers()
    
    swivel_to_monkey = ah.ease_in_out(-125, 45, 22, 23)
    arm1_to_monkey = ah.ease_in_out(20, 30, 15, 15)
    end_double_spin = ah.ease_in_out(-720, 30, 15, 15)
    arm1_slow = ah.ease_in_out(17, 75, 15, 15)
    arm2_slow = ah.ease_in_out(54, 75, 15, 15)
    end_slow = ah.ease_out(45, 75, 15)
    
    swivel_360 = ah.ease_in_out(360, 60, 30, 30)
    arm1_raise = ah.ease_in_out(-62, 60, 30, 30)
    arm2_raise = ah.ease_in_out(-79, 60, 30, 30)
    end_raise = ah.ease_in_out(-45, 60, 30, 30)
    
    arm1_lower = ah.ease_in_out(62, 100, 20, 80)
    arm2_lower = ah.ease_in_out(79, 100, 20, 80)
    end_lower = ah.ease_in_out(45, 100, 20, 80)
    
    swivel_look = ah.ease_in_out(75, 45, 22, 23)
    arm1_look = ah.ease_in_out(-20, 45, 22, 23)
    arm2_look = ah.ease_in_out(-45, 45, 22, 23)
    end_look = ah.ease_in_out(-45, 60, 30, 30)
    
    nod_start = ah.ease_in_out(-20, 7, 4, 3)
    nod_down =  ah.ease_in_out(40, 7, 4, 3)
    nod_up =  ah.ease_in_out(-40, 7, 4, 3)
    
    swivel_to_start = ah.ease_in_out(-310, 50, 25, 25)
    arm1_to_start = ah.ease_in_out(-17, 50, 25, 25)
    arm2_to_start = ah.ease_in_out(-9, 50, 25, 25)
    
    ah.set_animation_sequence(scene, 0, 190, 
                              [(robot_z_swivel, 0, 45, swivel_to_monkey, LOCAL, "ROTATION", 'z'),
                               (robot_arm_1, 20, 50, arm1_to_monkey, LOCAL, "ROTATION", 'y'),
                               (robot_end, 55, 85, end_double_spin, LOCAL, "ROTATION", 'y'),
                               (robot_arm_1, 100, 175, arm1_slow, LOCAL, "ROTATION", 'y'),
                               (robot_arm_2, 100, 175, arm2_slow, LOCAL, "ROTATION", 'y'),
                               (robot_end, 100, 175, end_slow, LOCAL, "ROTATION", 'y')])
    suzanne.set_properties([("PARENT", robot_end)])
    
    ah.set_animation_sequence(scene, 190, 380, 
                              [(robot_z_swivel, 190, 250, swivel_360, LOCAL, "ROTATION", 'z'),
                               (robot_arm_1, 190, 250, arm1_raise, LOCAL, "ROTATION", 'y'),
                               (robot_arm_2, 190, 250, arm2_raise, LOCAL, "ROTATION", 'y'),
                               (robot_end, 190, 250, end_raise, LOCAL, "ROTATION", 'y'),
                               (robot_arm_1, 265, 365, arm1_lower, LOCAL, "ROTATION", 'y'),
                               (robot_arm_2, 265, 365, arm2_lower, LOCAL, "ROTATION", 'y'),
                               (robot_end, 265, 365, end_lower, LOCAL, "ROTATION", 'y')])
                               
    robot_end.children.remove(suzanne)
    
    ah.set_animation_sequence(scene, 380, 550, 
                              [(robot_arm_1, 380, 425, arm1_look, LOCAL, "ROTATION", 'y'),
                               (robot_arm_2, 380, 425, arm2_look, LOCAL, "ROTATION", 'y'),
                               (robot_z_swivel, 380, 425, swivel_look, LOCAL, "ROTATION", 'z'),
                               (robot_end, 380, 425, end_look, LOCAL, "ROTATION", 'y'),
                               (robot_end, 430, 437, nod_start, LOCAL, "ROTATION", 'y'),
                               (robot_end, 437, 444, nod_down, LOCAL, "ROTATION", 'y'),
                               (robot_end, 444, 451, nod_up, LOCAL, "ROTATION", 'y'),
                               (robot_end, 451, 458, nod_down, LOCAL, "ROTATION", 'y'),
                               (robot_end, 458, 465, nod_up, LOCAL, "ROTATION", 'y'),
                               (robot_end, 465, 472, nod_down, LOCAL, "ROTATION", 'y'),
                               (robot_end, 472, 479, nod_start, LOCAL, "ROTATION", 'y'),
                               (robot_arm_1, 485, 535, arm1_to_start, LOCAL, "ROTATION", 'y'),
                               (robot_arm_2, 485, 535, arm2_to_start, LOCAL, "ROTATION", 'y'),
                               (robot_z_swivel, 485, 535, swivel_to_start, LOCAL, "ROTATION", 'z')])    
    return
        
def four_arms():
    scene = scene_manager.Scene()
    
    bot_radius = 0.6
    
    floor = scene.add(mesh.MeshFromTgifFile("Floor", 'circle_floor.tgif'))
    floor.local_transform(mh.scale(bot_radius + 0.2, bot_radius + 0.2, 1))
    floor.set_properties([("SUBSURF", 2)])
    
    ball = scene.add(mesh.MeshFromTgifFile("Ball", 'shiny_glass_ball.tgif'))
    ball_scale = 0.255
    ball.local_transform(mh.scale(ball_scale, ball_scale, ball_scale))
    ball.apply_transform()
    ball.global_transform(mh.translation(.3, 0, 0.4))
    ball.global_transform(mh.rotation(60, axis='z'))
    
    robot_1_base = scene.add(mesh.MeshFromTgifFile("Robot 1 Base", 'robot_base.tgif'))
    robot_1_base.set_properties([("PARENT", floor)])
    
    robot_1_z_swivel = scene.add(mesh.MeshFromTgifFile("Robot 1 Z Swivel", 'robot_z_swivel.tgif'))
    robot_1_z_swivel.set_properties([("PARENT", robot_1_base)])
    
    robot_1_arm_1 = scene.add(mesh.MeshFromTgifFile("Robot 1 Arm 1", 'robot_arm_1.tgif'))
    robot_1_arm_1.local_transform(mh.translation(0.0035, 0, 0.1715))
    robot_1_arm_1.apply_transform_buffer()
    robot_1_arm_1.set_properties([("PARENT", robot_1_z_swivel)])
    
    robot_1_arm_2 = scene.add(mesh.MeshFromTgifFile("Robot 1 Arm 2", 'robot_arm_2.tgif'))
    robot_1_arm_2.local_transform(mh.translation(0.0035, 0, 0.1715 + 0.221))
    robot_1_arm_2.apply_transform_buffer()
    robot_1_arm_2.set_properties([("PARENT", robot_1_arm_1)])
    
    robot_1_end = scene.add(mesh.MeshFromTgifFile("Robot 1 End", 'robot_end.tgif'))
    robot_1_end.local_transform(mh.translation(-0.0305 + .0035, 0, 0.1715 + 0.221 + .235))
    robot_1_end.apply_transform_buffer()
    robot_1_end.set_properties([("PARENT", robot_1_arm_2)])
    
    robot_1_base.local_transform(mh.rotation(180, axis='z'))
    robot_1_base.local_transform(mh.translation(-bot_radius, 0, 0))
    
    robot_2_base = scene.add(mesh.MeshFromTgifFile("Robot 2 Base", 'robot_base.tgif'))
    robot_2_base.set_properties([("PARENT", floor)])
    
    robot_2_z_swivel = scene.add(mesh.MeshFromTgifFile("Robot 2 Z Swivel", 'robot_z_swivel.tgif'))
    robot_2_z_swivel.set_properties([("PARENT", robot_2_base)])
    
    robot_2_arm_1 = scene.add(mesh.MeshFromTgifFile("Robot 2 Arm 1", 'robot_arm_1.tgif'))
    robot_2_arm_1.local_transform(mh.translation(0.0035, 0, 0.1715))
    robot_2_arm_1.apply_transform_buffer()
    robot_2_arm_1.set_properties([("PARENT", robot_2_z_swivel)])
    
    robot_2_arm_2 = scene.add(mesh.MeshFromTgifFile("Robot 2 Arm 2", 'robot_arm_2.tgif'))
    robot_2_arm_2.local_transform(mh.translation(0.0035, 0, 0.1715 + 0.221))
    robot_2_arm_2.apply_transform_buffer()
    robot_2_arm_2.set_properties([("PARENT", robot_2_arm_1)])
    
    robot_2_end = scene.add(mesh.MeshFromTgifFile("Robot 2 End", 'robot_end.tgif'))
    robot_2_end.local_transform(mh.translation(-0.0305 + .0035, 0, 0.1715 + 0.221 + .235))
    robot_2_end.apply_transform_buffer()
    robot_2_end.set_properties([("PARENT", robot_2_arm_2)])
    
    robot_2_base.local_transform(mh.rotation(180, axis='z'))
    robot_2_base.local_transform(mh.translation(-bot_radius, 0, 0))
    robot_2_base.global_transform(mh.rotation(120, axis='z'))
    
    robot_3_base = scene.add(mesh.MeshFromTgifFile("Robot 3 Base", 'robot_base.tgif'))
    robot_3_base.set_properties([("PARENT", floor)])
    
    robot_3_z_swivel = scene.add(mesh.MeshFromTgifFile("Robot 3 Z Swivel", 'robot_z_swivel.tgif'))
    robot_3_z_swivel.set_properties([("PARENT", robot_3_base)])
    
    robot_3_arm_1 = scene.add(mesh.MeshFromTgifFile("Robot 3 Arm 1", 'robot_arm_1.tgif'))
    robot_3_arm_1.local_transform(mh.translation(0.0035, 0, 0.1715))
    robot_3_arm_1.apply_transform_buffer()
    robot_3_arm_1.set_properties([("PARENT", robot_3_z_swivel)])
    
    robot_3_arm_2 = scene.add(mesh.MeshFromTgifFile("Robot 3 Arm 2", 'robot_arm_2.tgif'))
    robot_3_arm_2.local_transform(mh.translation(0.0035, 0, 0.1715 + 0.221))
    robot_3_arm_2.apply_transform_buffer()
    robot_3_arm_2.set_properties([("PARENT", robot_3_arm_1)])
    
    robot_3_end = scene.add(mesh.MeshFromTgifFile("Robot 3 End", 'robot_end.tgif'))
    robot_3_end.local_transform(mh.translation(-0.0305 + .0035, 0, 0.1715 + 0.221 + .235))
    robot_3_end.apply_transform_buffer()
    robot_3_end.set_properties([("PARENT", robot_3_arm_2)])
    
    robot_3_base.local_transform(mh.rotation(180, axis='z'))
    robot_3_base.local_transform(mh.translation(-bot_radius, 0, 0))
    robot_3_base.global_transform(mh.rotation(240, axis='z'))
    
    robot_1_z_swivel.local_transform(mh.rotation(-30, axis='z'))
    robot_1_arm_1.local_transform(mh.rotation(45, axis='y'))
    robot_1_arm_2.local_transform(mh.rotation(33, axis='y'))
    robot_1_end.local_transform(mh.rotation(20, axis='y'))
    
    robot_2_z_swivel.local_transform(mh.rotation(30, axis='z'))
    robot_2_arm_1.local_transform(mh.rotation(45, axis='y'))
    robot_2_arm_2.local_transform(mh.rotation(33, axis='y'))
    robot_2_end.local_transform(mh.rotation(20, axis='y'))
    
    robot_3_arm_1.local_transform(mh.rotation(45, axis='y'))
    robot_3_arm_2.local_transform(mh.rotation(33, axis='y'))
    robot_3_end.local_transform(mh.rotation(20, axis='y'))
    
    ball.set_properties([("PARENT", robot_2_end)])
    
    scene.apply_all_transform_buffers()
    
    anim_length = 150
    ease_left = ah.ease_in_out(60, anim_length*2//3, anim_length//3, anim_length//3)
    ease_right = ah.ease_in_out(-60, anim_length//3, anim_length//6, anim_length//6)
    ease_s_half_left = ah.ease_out(30, anim_length//3, anim_length//3)
    ease_e_half_left = ah.ease_in(30, anim_length//3, anim_length//3)
    
    fun_spin = ah.constant(-360, anim_length)
    
    ah.set_animation_sequence(scene, 0, anim_length, 
                              [(floor, 0, anim_length, fun_spin, LOCAL, "ROTATION", 'z'),
                               (robot_1_z_swivel, 0, anim_length*2//3, ease_left, LOCAL, "ROTATION", 'z'),
                               (robot_2_z_swivel, 0, anim_length//3, ease_right, LOCAL, "ROTATION", 'z'),
                               (robot_3_z_swivel, 0, anim_length//3, ease_s_half_left, LOCAL, "ROTATION", 'z'),
                               (robot_3_z_swivel, anim_length//3, anim_length*2//3, ease_right, LOCAL, "ROTATION", 'z'),
                               (robot_1_z_swivel, anim_length*2//3, anim_length, ease_right, LOCAL, "ROTATION", 'z'),
                               (robot_2_z_swivel, anim_length//3, anim_length, ease_left, LOCAL, "ROTATION", 'z'),
                               (robot_3_z_swivel, anim_length*2//3, anim_length, ease_e_half_left, LOCAL, "ROTATION", 'z')],
                               [(anim_length//3, "UNPARENT", ball, robot_2_end),
                                (anim_length//3, "PARENT", ball, robot_3_end),
                                (anim_length*2//3, "UNPARENT", ball, robot_3_end),
                                (anim_length*2//3, "PARENT", ball, robot_1_end),
                                (anim_length, "UNPARENT", ball, robot_1_end),
                                (anim_length, "PARENT", ball, robot_2_end)])
    
    

cleaner.clean_scene() 
four_arms()


