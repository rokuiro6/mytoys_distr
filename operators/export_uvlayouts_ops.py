import bpy
import os
from contextlib import contextmanager

# ExportUVLayouts用クリーンアップ
@contextmanager
def SetMaterialSettings(context, active_obj, renderable_objs, renderable_mats):
    original_slot_length = len(active_obj.material_slots)

    try:
        # レンダリング可能なオブジェクトを全て選択する
        bpy.ops.object.select_all(action='DESELECT')
        for obj in renderable_objs:
            obj.select_set(True)

        context.view_layer.objects.active = active_obj

        # レンダリング対象となるマテリアルを集める
        for mat in renderable_mats:
            if mat.name not in active_obj.data.materials:
                active_obj.data.materials.append(mat)

        bpy.ops.object.mode_set(mode='EDIT')
        
        yield

    finally:
        bpy.ops.object.mode_set(mode='OBJECT')

        # 追加したマテリアルを削除
        while len(active_obj.material_slots) > original_slot_length:
            active_obj.data.materials.pop(index=len(active_obj.material_slots) - 1)


class ExportUVLayouts(bpy.types.Operator):
    bl_idname = "mytoys.export_uvlayouts"
    bl_label = "Export UVLayouts"

    directory: bpy.props.StringProperty(name="folderpath", subtype='DIR_PATH')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        target_folder = self.directory

        bpy.ops.object.mode_set(mode='OBJECT') 

        # レンダリング可能なオブジェクトを集める、隠しているオブジェクトも対象にする。
        renderable_objs = [obj for obj in scene.objects if obj.type == 'MESH' and not obj.hide_render and not obj.hide]

        if not renderable_objs:
            self.report({'WARNING'}, "renderable object are none")
            return {'FINISHED'}

        # 重複のないマテリアルリストを抽出
        mats_set = {
            slot.material 
            for obj in renderable_objs 
            for slot in obj.material_slots 
            if slot.material
        }
        renderable_mats = list(mats_set)
 
        active_obj = renderable_objs[0]

        with SetMaterialSettings(context, active_obj, renderable_objs, renderable_mats):
            for index, mat in enumerate(active_obj.data.materials):
                filename = f"UVLayout_{mat.name}.png"   
                filepath = os.path.join(target_folder, filename)

                bpy.ops.mesh.select_all(action='DESELECT')
                
                # 現在の処理対象マテリアルのインデックスをアクティブにする
                active_obj.active_material_index = index     
                # アクティブなスロットのマテリアルを持つ面を選択する
                bpy.ops.object.material_slot_select()

                # UVエクスポートと色付け
                bpy.ops.uv.export_layout(
                    filepath=filepath, 
                    size=(scene.uvlayouts_setting.resolution, scene.uvlayouts_setting.resolution),
                    opacity=scene.uvlayouts_setting.fill_opacity
                )
                self.colorize_image(filepath, scene.uvlayouts_setting.color)

        self.report({'INFO'}, "UVLayouts were exported!")
        return {'FINISHED'}
    

    def colorize_image(self, filepath, color):
        import numpy as np

        img = bpy.data.images.load(filepath)
        
        width = img.size[0]
        height = img.size[1]
        num_pixels = width * height

        pixels = np.empty(num_pixels * 4, dtype=np.float32)

        img.pixels.foreach_get(pixels)
        
        pixels[0::4] = color[0] # R
        pixels[1::4] = color[1] # G
        pixels[2::4] = color[2] # B

        img.pixels.foreach_set(pixels)
        
        img.save()
        bpy.data.images.remove(img)