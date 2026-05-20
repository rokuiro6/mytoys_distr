import bpy

class RenderSettingProperties(bpy.types.PropertyGroup):
    toggle_wirerender : bpy.props.BoolProperty(name = "Toggle WireRender", default=True)
    wire_thickness : bpy.props.FloatProperty(name="Wire Thickenss",default = 1.0)
    wire_color : bpy.props.FloatVectorProperty(name="Wire Color",subtype="COLOR",default = (0.0,0.0,0.0))
    wire_opacity : bpy.props.FloatProperty(name = "Wire Opacity", default = 1.0)
    use_default_material : bpy.props.BoolProperty(name = "Use Default Material",default = True)
    toggle_transparent : bpy.props.BoolProperty(name = "Toggle Transparent back", default = True)