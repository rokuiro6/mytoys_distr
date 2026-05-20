import bpy

class RendersNamingProperties(bpy.types.PropertyGroup):
    hide: bpy.props.BoolProperty(name = "Hide Naming Convention", default=True)
    subject: bpy.props.StringProperty(name = "File Name Subject", default="")
    posing: bpy.props.StringProperty(name="Pose Name",default="")
    use_posing: bpy.props.BoolProperty(name="Use Pose Name Suffix",default=True)
    shot_type: bpy.props.EnumProperty(
        name="Shot Type",
        items=[
            ('FULL_SHOT',"Full Shot",""),
            ('UP_SHOT',"Up Shot",""),
            ('BUSTSHOT',"Bust Shot",""),
            ('WAIST_SHOT',"Waist Shot",""),
        ],
        default = 'FULL_SHOT'
        ) 
    use_shot_type:bpy.props.BoolProperty(name="Use Shot Type Suffix",default=True)
    use_wire: bpy.props.BoolProperty(name="Use Wireframe Suffix",default=True)

    use_camera_prefix: bpy.props.BoolProperty(name="Use CamTrans Item Nmme Prefix",default = True)