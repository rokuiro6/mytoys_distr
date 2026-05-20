import bpy

class FBXExporterSubstanceProperties(bpy.types.PropertyGroup):
    modified:bpy.props.BoolProperty(name="Modified",default=False)
    apply_gns:bpy.props.BoolProperty(name="Apply GNs",default=False)
    mat_prefix:bpy.props.StringProperty(name="Material prefix",default="MAT_")
    tex_prefix:bpy.props.StringProperty(name="Texture Prefix",default = "TEX_")
    hide:bpy.props.BoolProperty(name="Hide",default=True)