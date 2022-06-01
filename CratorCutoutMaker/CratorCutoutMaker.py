import bpy
import bmesh
from math import radians
from bpy.props import *
from mathutils import Color

class CratorCutoutMaker(bpy.types.Operator):
    bl_idname = "object.my_operator"
    bl_label = "CratorCutoutMaker"
    bl_options = {'REGISTER', 'UNDO'}
    
    #create properties
        
    decimate_ratio : FloatProperty(
        name = "Decimate Ratio",
        default = .08,
        min = 0.0,
        max = 1.0    
    )
    
    depth : FloatProperty(
        name = "Depth",
        description = "How deep the crater",
        default = .18,
        min = 0.0    
    )
    
    size : FloatProperty(
        name = "Width of rim",
        description = "Width of the crater rim",
        default = 5,
        min = 0.0    
    )
    
    bottomsize : FloatProperty(
        name = "Scale of bottom",
        description = "Width of the crater",
        default = 1,
        min = 0.0    
    )
    
    bottomoffsetX : FloatProperty(
        name = "Move X",
        description = "Move the bottom x offset",
        default = 0  
    )
    
    bottomoffsetY : FloatProperty(
        name = "Y",
        description = "Move the bottom y offset",
        default = 0  
    )
    
    
    def pol(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        #set name to walls
        bpy.context.active_object.name = "Walls"
        walls = bpy.context.active_object
        
        #set location
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = 0

        #set Scale
        bpy.context.object.scale[0] = self.size
        bpy.context.object.scale[1] = self.size

    
    
        #Create Mesh
        bpy.ops.object.convert(target='MESH')

        #Decemate Vertex .08
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.decimate(ratio=self.decimate_ratio)
        

        #Create New Vertex Group for top selection
        group = bpy.context.object.vertex_groups.new()
        group.name = ("TopVertices")


        #Save Top Selcted Vertices
        topVerts = []
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
        for v in selectedVerts:
            topVerts.append(v.index)

        #extrude
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={
        "use_normal_flip":False, "mirror":False},
         TRANSFORM_OT_translate={"value":(self.bottomoffsetX, self.bottomoffsetY, -self.depth),
          "orient_type":'NORMAL', "orient_matrix":((-0.685739, -0.727848, 0), (0.727848, -0.685739, 0), (0, 0, 1)),
          "orient_matrix_type":'NORMAL',
          "constraint_axis":(False, False, True), "mirror":False,
          "use_proportional_edit":False,
          "proportional_edit_falloff":'SMOOTH',
          "proportional_size":1,
          "use_proportional_connected":False,
          "use_proportional_projected":False,
          "snap":False, "snap_target":'CLOSEST',
          "snap_point":(0, 0, 0), "snap_align":False,
          "snap_normal":(0, 0, 0), "gpencil_strokes":False,
          "cursor_transform":False, "texture_space":False,
          "remove_on_cancel":False, "release_confirm":False,
          "use_accurate":False
        })
        
        #scale bottom
        
        bpy.ops.transform.resize(
            value=(self.bottomsize, self.bottomsize, self.bottomsize),
            orient_type='GLOBAL',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type='GLOBAL',
            mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
            proportional_size=1,
            use_proportional_connected=False,
            use_proportional_projected=False
        )

        #seaperate bottom and rename
        scn = bpy.context.scene
        names = [ obj.name for obj in scn.objects]

        bpy.ops.mesh.separate(type="SELECTED")

        new_objs = [ obj for obj in scn.objects if not obj.name in names]
        
        new_objs[0].name = "Bottom"
        
        bot = new_objs[0]
        
        
        #select top 
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        group.add(topVerts, 1.0, 'ADD')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.vertex_group_select()
        
        #Seaperate and rename Top
        scn = bpy.context.scene
        names = [ obj.name for obj in scn.objects]

        bpy.ops.mesh.separate(type="SELECTED")

        new_objs = [ obj for obj in scn.objects if not obj.name in names]
        
        new_objs[0].name = "Top"
        
        top = new_objs[0]
        
        
        #apply scale
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        print(top.name)
        print(walls.name)
        print(bot.name)
        
        #set the materials - top
        mat = bpy.data.materials.get("Top")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="Top")

        # Assign it to object
        if top.data.materials:
            # assign to 1st material slot
            top.data.materials[0] = mat
        else:
            # no slots
            top.data.materials.append(mat)
            
        #set the materials - walls
        mat = bpy.data.materials.get("Walls")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="Walls")

        # Assign it to object
        if walls.data.materials:
            # assign to 1st material slot
            walls.data.materials[0] = mat
        else:
            # no slots
            walls.data.materials.append(mat) 
            
        #set the materials - Bottom
        mat = bpy.data.materials.get("Bottom")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="Bottom")

        # Assign it to object
        if bot.data.materials:
            # assign to 1st material slot
            bot.data.materials[0] = mat
        else:
            # no slots
            bot.data.materials.append(mat)      
        
                
        #Flip the normals of the top
        bpy.ops.object.select_all(action='DESELECT')        
        top.select_set(state = 1)
        bpy.context.view_layer.objects.active = top
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Uv Unrap the walls
        bpy.ops.object.select_all(action='DESELECT')        
        walls.select_set(state = 1)
        bpy.context.view_layer.objects.active = walls
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.cylinder_project(direction='ALIGN_TO_OBJECT', clip_to_bounds=True, scale_to_bounds=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Uv unwrap the floor
        bpy.ops.object.select_all(action='DESELECT')        
        bot.select_set(state = 1)
        bpy.context.view_layer.objects.active = bot
        
       # bot.select_set(state = 1)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CratorCutoutMaker)


def unregister():
    bpy.utils.unregister_class(CratorCutoutMaker)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.my_operator()