import bpy
from bpy_extras.io_utils import ExportHelper
from contextlib import contextmanager

# FbxExporterSubstance用クリーンアップ
@contextmanager
def SetOriginalSetting():
    disabled_gns = []
    renamed_mats = {}
    try:
        yield disabled_gns, renamed_mats

    finally:        
        #  ジオメトリノードの表示状態を復元
        for mod in disabled_gns:
            mod.show_viewport = True

        # マテリアル名を元に戻す
        for mat, original_name in renamed_mats.items():
            mat.name = original_name


class FbxExporterSubstance(bpy.types.Operator, ExportHelper):
    bl_idname = "mytoys.fbx_exporter_substance"
    bl_label = "FBX Exporter for Substance"

    filename_ext = ".fbx"
    filter_glob: bpy.props.StringProperty(
        default="*.fbx",
        options={"HIDDEN"},
    )

    def execute(self, context):
        scene = context.scene
        target_path = self.filepath

        selected_obs = context.selected_objects
        if not selected_obs:
            self.report({'WARNING'}, "select object")
            return {'FINISHED'}
        
        with SetOriginalSetting() as (disabled_gns, renamed_mats):            
            # ジオメトリノード系の前処理
            if not scene.fbx_exporter_substance_setting.apply_gns:
                for obj in selected_obs:
                    if obj.type == "MESH":
                        for mod in obj.modifiers:
                            # GNsでかつ表示されている場合、それを非表示にする
                            if mod.type == "NODES" and mod.show_viewport:
                                disabled_gns.append(mod)
                                mod.show_viewport = False

            # 名前置換処理
            for obj in selected_obs:
                for slot in obj.material_slots:
                    if slot.material:
                        mat = slot.material
                        if mat.name.startswith(scene.fbx_exporter_substance_setting.mat_prefix):
                            original_name = mat.name
                            if mat not in renamed_mats:
                                renamed_mats[mat] = original_name
                                # 新しい名前を適用
                                new_suffix = original_name[len(scene.fbx_exporter_substance_setting.mat_prefix):]
                                mat.name = scene.fbx_exporter_substance_setting.tex_prefix + new_suffix

            # FBXエクスポート実行
            bpy.ops.export_scene.fbx(
                filepath=target_path,
                use_selection=True,
                use_visible=True,
                object_types={'MESH'},
                bake_space_transform=True,
                bake_anim=False,
                use_mesh_modifiers=scene.fbx_exporter_substance_setting.modified
            )
        
        self.report({'INFO'}, "FBX exported for Substance!")
        return {'FINISHED'}