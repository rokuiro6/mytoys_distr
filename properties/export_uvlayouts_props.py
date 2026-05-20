import bpy

class ExportUVLayoutsProperties(bpy.types.PropertyGroup):
    # line_thickness : bpy.props.FloatProperty(name = "Line Thickness",default = 1.0)
    resolution : bpy.props.IntProperty(name="Resolution",default = 2048)
    color : bpy.props.FloatVectorProperty(name="Color",subtype='COLOR',default = (1.0,0.0,0.0))
    prefix : bpy.props.StringProperty(name="Prefix",default="UVLayout_")
    fill_opacity : bpy.props.FloatProperty(name="Fill Opacity",default=0.0)
    hide : bpy.props.BoolProperty(name="Hide",default = True)
    #uv_filepath : bpy.props.StringProperty(name="Filepath",subtype='FILE_PATH',default="")