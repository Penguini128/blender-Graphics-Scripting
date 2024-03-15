# Animating in Python - Robot Arm

## Renders
Animation renders are contained within the ```renders``` folder. I couldn't figure out how to embed them into this README, so they will have to be downloaded in order to view them.

## What is a .tgif file?
When working in blender, I wanted a way to model an object, apply materials to it, then export that model with the material information embedded. Unfortunately, with the way I was importing models (ingesting .ply files and interpreting their contents via a python script) there was no way for me to easily preserve the material information. Therefore, I created a script that exports a modified version of .ply that contains additional information about the materials used on the model as well as the material applied to each face.

TGIF stands for "Tommy Galletta's Instance Format", not "Thank Goodness It's Friday".

Unfortunately, these models cannot be loaded by any means other than the script I wrote to import the models back into blender. There are not models in the repository that are not displayed within one of the rendered animations.

## Where is the Python code?
The code I wrote is contained within the ```src``` folder, however unless you have blender you will not be able to run it. The code makes use of the bpy package which is a package built into blender. However, if you just wish to simply see everything I wrote, the code is there. ```graphics.blend``` also contains an internal version of each script.

## What are ```robot_arm.blend``` and ```graphics.blend```?

```robot_arm.blend``` contains all of the models I made. It is the file where I modeled each part of the robot and each additional miscellaneous item before exporting them to the .tgif format.

```graphics.blend``` contains all of the Python scripting I used to create my animations. A lot of time went into the "infrastructure" of the animation, creating systems that allowed me to easily move elements around at different times.


### And that's it! Enjoy!