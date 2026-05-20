import bpy

# import Classes
from .properties.camera_transform_item_props import CameraTransformItemProperties
from .properties.renders_naming_props import RendersNamingProperties
from .properties.render_setting_props import RenderSettingProperties
from .properties.export_uvlayouts_props import ExportUVLayoutsProperties
from .properties.fbx_exporter_substance_props import FBXExporterSubstanceProperties
from .properties.gen_normal_uv_props import GenNormalUVProperties

from .operators.camera_transforms_ops import (
    AddCameraTransformItem,
    DeleteCameraTransformItem,
    RenderSelectedItems,
    CaptureCameraTrans,
    AssignCameraTrans,
    AutoGenerateItems
    )
from .operators.export_uvlayouts_ops import ExportUVLayouts
from .operators.fbx_exporter_substance_ops import FbxExporterSubstance
from .operators.gen_normal_uv_ops import GenNormalUV
from .ui.panel_view3d import PanelView3D

# bpy.typesを継承しているクラスは全て初期化される必要がある。
classes = [
    CameraTransformItemProperties,
    RendersNamingProperties,
    RenderSettingProperties,
    ExportUVLayoutsProperties,
    FBXExporterSubstanceProperties,
    GenNormalUVProperties,

    AddCameraTransformItem,
    DeleteCameraTransformItem,
    CaptureCameraTrans,
    AssignCameraTrans,
    AutoGenerateItems,
    RenderSelectedItems,
    ExportUVLayouts,
    FbxExporterSubstance,
    GenNormalUV,

    PanelView3D,
    ]

# register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # register scene properties
    bpy.types.Scene.uvlayouts_setting = bpy.props.PointerProperty(type=ExportUVLayoutsProperties)
    bpy.types.Scene.camera_transforms = bpy.props.CollectionProperty(type=CameraTransformItemProperties)
    bpy.types.Scene.renders_naming = bpy.props.PointerProperty(type=RendersNamingProperties)
    bpy.types.Scene.render_setting = bpy.props.PointerProperty(type=RenderSettingProperties)
    bpy.types.Scene.fbx_exporter_substance_setting = bpy.props.PointerProperty(type=FBXExporterSubstanceProperties)
    bpy.types.Scene.gen_normal_uv_names = bpy.props.PointerProperty(type = GenNormalUVProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.camera_transforms


# trigger run script
if __name__ == "__main__":
    register()