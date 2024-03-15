import bpy
mh = bpy.data.texts["matrix_helper.py"].as_module()

def ease_in(total_delta, total_frames, ease_frames):
    total_frames = max(1, total_frames)
    ease_frames = min(ease_frames, total_frames)
    
    post_ease_frames = total_frames - ease_frames
    full_steps = ease_frames / 2 + post_ease_frames
    avg_delta_per_frame = total_delta / full_steps
    ease_delta_fraction = avg_delta_per_frame / (ease_frames + 1)
    
    step_array = []
    
    for i in range(ease_frames):
        step_array.append((i + 1) * ease_delta_fraction)
    for i in range(post_ease_frames - 1):
        step_array.append(avg_delta_per_frame)
    if ease_frames < total_frames:
        step_array.append(total_delta - sum(step_array))
    
    return step_array

def ease_out(total_delta, total_frames, ease_frames):
    total_frames = max(1, total_frames)
    ease_frames = min(ease_frames, total_frames)
    
    pre_ease_frames = total_frames - ease_frames
    full_steps = ease_frames / 2 + pre_ease_frames
    avg_delta_per_frame = total_delta / full_steps
    ease_delta_fraction = avg_delta_per_frame / (ease_frames + 1)
    
    step_array = []
    
    for i in range(pre_ease_frames):
        step_array.append(avg_delta_per_frame)
    for i in range(ease_frames - 1):
        step_array.append((ease_frames - i) * ease_delta_fraction)
    if ease_frames <= total_frames:
        step_array.append(total_delta - sum(step_array))
    
    return step_array

def ease_in_out(total_delta, total_frames, ease_in_frames, ease_out_frames):
    total_frames = max(1, total_frames)
    ease_in_frames = min(ease_in_frames, total_frames)
    ease_out_frames = min(ease_out_frames, total_frames - ease_in_frames)
    
    mid_ease_frames = total_frames - ease_in_frames - ease_out_frames
    full_steps = (ease_in_frames + ease_out_frames) / 2 + mid_ease_frames
    avg_delta_per_frame = total_delta / full_steps
    ease_in_delta_fraction = avg_delta_per_frame / (ease_in_frames + 1)
    ease_out_delta_fraction = avg_delta_per_frame / (ease_out_frames + 1)
    
    step_array = []
    
    for i in range(ease_in_frames):
        step_array.append((i + 1) * ease_in_delta_fraction)
    for i in range(mid_ease_frames):
        step_array.append(avg_delta_per_frame)
    for i in range(ease_out_frames - 1):
        step_array.append((ease_out_frames - i) * ease_out_delta_fraction)
        
    if ease_out_frames <= total_frames - ease_in_frames:
        step_array.append(total_delta - sum(step_array))
    
    return step_array

def constant(total_delta, total_frames):
    return [total_delta/total_frames] * total_frames


def set_animation_sequence(scene, anim_start, anim_end, sequence, additional_actions=[]):
    current_frame = anim_start
    while current_frame < anim_end:
        print(f"Processing frame: {current_frame}", end='\r')
        scene.add_keyframe(current_frame, all=True)
        current_frame += 1
        for curve in sequence:
            object, curve_start, curve_end, delta, transform_space, transform_type, params = curve
            if current_frame >= curve_start and current_frame < curve_end:
                if transform_type == "TRANSLATION":
                    x, y, z = params
                    x *= delta[current_frame - curve_start]
                    y *= delta[current_frame - curve_start]
                    z *= delta[current_frame - curve_start]
                    object.transform([(transform_space, mh.translation(x, y, z))])
                elif transform_type == "ROTATION":
                    axis = params
                    object.transform([(transform_space, mh.rotation(delta[current_frame - curve_start],
                                                                    axis=axis))])
                elif transform_type == "SCALE":
                    x, y, z = params
                    x *= delta[current_frame - curve_start]
                    y *= delta[current_frame - curve_start]
                    z *= delta[current_frame - curve_start]
                    object.transform([(transform_space, mh.scale(x, y, z))])
        for action in additional_actions:
            action_frame, action_type, params = action[0], action[1], action[2:]
            if current_frame != action_frame:
                continue
            if action_type == "PARENT":
                params[1].children.append(params[0])
            elif action_type == "UNPARENT":
                params[1].children.remove(params[0])
    print(f"Processing frame: {anim_end}")
    print(f"Sequence done!")
    scene.add_keyframe(anim_end, all=True)
        
        