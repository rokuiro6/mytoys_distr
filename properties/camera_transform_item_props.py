import bpy

class CameraTransformItemProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name = "Camera Transform Name",default="camera")
    use_render: bpy.props.BoolProperty(name="Use Render",default = True)
    location: bpy.props.FloatVectorProperty(name = "Camera Location", subtype="TRANSLATION", default=(0.0,0.0,0.0))
    rotation: bpy.props.FloatVectorProperty(name = "Camera Rotation", subtype="EULER", default = (0.0,0.0,0.0))
    hide: bpy.props.BoolProperty(name="hide",default=True)