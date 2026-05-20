import bpy

class GenNormalUVProperties(bpy.types.PropertyGroup):
    normal_xy : bpy.props.StringProperty(name = "Custom Normal xy",default = "cNrm_xy")
    normal_z:bpy.props.StringProperty(name="Custom Normal z",default="cNrm_z")
    hide:bpy.props.BoolProperty(name="hide",default=True)