import bpy
import math
import os
from contextlib import contextmanager
from mathutils import Vector, Matrix


class AddCameraTransformItem(bpy.types.Operator):
    bl_idname = "mytoys.camera_transforms_add_item"
    bl_label = "Add Camera Transform Item"

    # 実行される処理はこのメソッドをオーバーライド
    def execute(self,context):
        scene = context.scene
        item = context.scene.camera_transforms.add()
        active_camera = scene.camera
        if active_camera:
            item.location = active_camera.location
            item.rotation = active_camera.rotation_euler
        self.report({'INFO'},"Camera Toransrform Item added")
        return {'FINISHED'}


class DeleteCameraTransformItem(bpy.types.Operator):
    bl_idname = "mytoys.camera_transforms_delete_item"
    bl_label = "Delete Camera Transfrom Item"
    index: bpy.props.IntProperty() 

    def execute(self,context):
        # ボタンが存在すればその要素は存在するので例外を拾わなくても良い
        context.scene.camera_transforms.remove(self.index)
        self.report({'INFO'},"Camera Transform Item deleted")
        return {'FINISHED'}

class CaptureCameraTrans(bpy.types.Operator):
    bl_idname = "mytoys.capture_camera_transform"
    bl_label = "Capture Camera Transform"
    index : bpy.props.IntProperty()
    def execute(self,context):
        scene = context.scene
        camera = scene.camera
        item_camera = scene.camera_transforms[self.index]
        item_camera.location = camera.location.copy()
        item_camera.rotation = camera.rotation_euler.copy()

        self.report({'INFO'},"copied!")
        return {'FINISHED'}
    
class AssignCameraTrans(bpy.types.Operator):
    bl_idname="mytoys.assign_camera_transform"
    bl_label="Assign Camera Transform"
    index: bpy.props.IntProperty()
    def execute(self,context):
        scene = context.scene
        camera = scene.camera
        item_camera = scene.camera_transforms[self.index]
        camera.location = item_camera.location.copy()
        camera.rotation_euler = item_camera.rotation.copy()

        self.report({'INFO'},"assigned!")
        return {'FINISHED'}
    
class AutoGenerateItems(bpy.types.Operator):
    bl_idname = "mytoys.auto_generate_items"
    bl_label = "Auto Generate Items"

    def execute(self, context):
        scene = context.scene
        camera = scene.camera

        if not camera:
            self.report({'WARNING'}, "the scene has not active camera!")
            return {'CANCELLED'}

        if camera.data.type == 'ORTHO':
            self.report({'WARNING'}, "use wide angle perspective camera insetead!")
            return {'CANCELLED'}

        # レンダリング対象を取得
        renderable_objs = [obj for obj in scene.objects if obj.type == 'MESH' and not obj.hide_render]

        if not renderable_objs:
            self.report({'WARNING'}, "renderable object is none! sonnnakotoaru!?")
            return {'CANCELLED'}

        # お片付け用にactive cameraの状態を保存
        original_camera = scene.camera
        original_camera_matrix_world = camera.matrix_world.copy()
        original_camera_ortho_scale = camera.data.ortho_scale

        try:
            depsgraph = context.evaluated_depsgraph_get()

            # camera_fit_coords() に渡す座標
            bbox_points = []
            for obj in renderable_objs:
                eval_obj = obj.evaluated_get(depsgraph)

                for corner in eval_obj.bound_box:
                    world_corner = eval_obj.matrix_world @ Vector(corner)
                    bbox_points.extend((
                        world_corner.x,
                        world_corner.y,
                        world_corner.z,
                    ))
            view_defs = [
                ("front",    (90.0, 0.0,   0.0)),
                ("side",     (90.0, 90.0,  0.0)),
                ("diagonal", (90.0, 45.0,  0.0)),
                ("back",     (90.0, 180.0, 0.0)),
            ]

            for view_name, rot_deg in view_defs:
                rot_matrix = (
                    Matrix.Rotation(math.radians(rot_deg[0]), 4, 'X') @
                    Matrix.Rotation(math.radians(rot_deg[1]), 4, 'Y') @
                    Matrix.Rotation(math.radians(rot_deg[2]), 4, 'Z')
                )

                rot_matrix.translation = original_camera_matrix_world.translation
                camera.matrix_world = rot_matrix

                # Matrixを更新しておく
                context.view_layer.update()

                fit_location, _ = camera.camera_fit_coords(
                    depsgraph,
                    bbox_points
                )

                fitted_matrix = camera.matrix_world.copy()
                fitted_matrix.translation = fit_location
                camera.matrix_world = fitted_matrix

                context.view_layer.update()

                # cameratransformsを追加
                item = scene.camera_transforms.add()
                item.name = view_name
                item.location = camera.location.copy()
                item.rotation = camera.rotation_euler.copy()

            self.report({'INFO'}, "Camera transform items added: front, side, diagonal, back.")

        finally: # お片付け処理
            scene.camera = original_camera
            camera.matrix_world = original_camera_matrix_world
            camera.data.ortho_scale = original_camera_ortho_scale

            context.view_layer.update()

        return {'FINISHED'}
    

    
# RenderSelectedItems用クリーンアップ
@contextmanager    
def SetRenderSettings(context):
    scene = context.scene
    camera = scene.camera
    original = {
        "location": camera.location.copy(),
        "rotation": camera.rotation_euler.copy(),
        "filepath": scene.render.filepath,
        "film_transparent": scene.render.film_transparent,
        "use_freestyle": scene.render.use_freestyle,
        "line_thickness": scene.render.line_thickness,
        "linestyles_color":bpy.data.linestyles["LineStyle"].color,
        "material_override":scene.view_layers["ViewLayer"].material_override,
        "mode": context.mode,
    }

    try:
        yield original
    finally:
        camera.location = original['location']
        camera.rotation_euler = original['rotation']
        scene.render.filepath = original['filepath']
        scene.render.film_transparent = original['film_transparent']
        scene.render.use_freestyle = original['use_freestyle']
        scene.render.line_thickness = original['line_thickness']
        bpy.data.linestyles["LineStyle"].color = original['linestyles_color']
        scene.view_layers["ViewLayer"].material_override = original["material_override"]


        bpy.ops.mesh.mark_freestyle_edge(clear = True)
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # 全ての選択を解除する
        for obj in context.view_layer.objects:
            obj.select_set(False)
            

    
class RenderSelectedItems(bpy.types.Operator):
    bl_idname = "mytoys.camera_transforms_render_items"
    bl_label = "Render Selected Items"

    def execute(self,context):
        scene = context.scene
        camera = scene.camera

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # レンダリング可能なオブジェクトを集める
        renderable_objs = [obj for obj in scene.objects if obj.type == 'MESH' and not obj.hide_render]

        if not renderable_objs:
            self.report({'WARNING'},"renderable object are not found!")

        # カメラがなければ焦点距離等調整されていないため、強制終了させてしまう
        if not camera:
            self.report({'WARNING'},"scene dont have any camera")
            return {'CANCELLED'}
        
        with SetRenderSettings(context) as original:
            for item in scene.camera_transforms:
                if item.use_render:
                    camera.location = item.location.copy()
                    camera.rotation_euler = item.rotation.copy()

                    suffix_list = [scene.renders_naming.subject]
                    if scene.renders_naming.use_posing: suffix_list.append(scene.renders_naming.posing)
                    if scene.renders_naming.use_shot_type: suffix_list.append(scene.renders_naming.shot_type)
                    if scene.renders_naming.use_wire | scene.render_setting.toggle_wirerender : suffix_list.append("std")
                    if scene.renders_naming.use_camera_prefix : suffix_list.append(item.name)

                    filename = "_".join(filter(None,suffix_list))

                    # ファイルパスの結合ならosの方を使うと、/や\,エスケープシーケンスの違いを吸収できる
                    scene.render.filepath = os.path.join(original['filepath'], filename)
                    bpy.ops.render.render(write_still = True) # write_stillで静止画レンダリング

            #ワイヤーレンダー
            if scene.render_setting.toggle_wirerender :
                # 全ての辺をマークする

                bpy.ops.object.select_all(action='DESELECT')

                for obj in renderable_objs:
                    obj.select_set(True)
                active_obj = renderable_objs[0]
                context.view_layer.objects.active = active_obj

                bpy.ops.object.mode_set(mode = 'EDIT') # この段階では、ツール使用時に選択されていた(またはその直前)オブジェクトの編集モードである
                bpy.ops.mesh.select_mode(type = 'EDGE')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.mark_freestyle_edge(clear = False)

                # フリースタイルラインの設定
                scene.render.line_thickness = original['line_thickness']
                bpy.data.linestyles["LineStyle"].color = scene.render_setting.wire_color

                # マテリアルオーバーライドの設定
                if scene.render_setting.use_default_material : scene.view_layers["ViewLayer"].material_override = bpy.data.materials.new(name = "MAT_OVERRIDE")

                scene.render.use_freestyle = True

                # クリース辺180度を拾わせると三角面化されたメッシュを基にラインを作ってしまったため却下。
                # backup_crease_angle = context.view_layer.freestyle_settings.crease_angle
                # context.view_layer.freestyle_settings.crease_angle = math.pi これだと、三角面化された結果まで拾ってしまう

                for item in scene.camera_transforms:
                    if item.use_render:
                        camera.location = item.location.copy()
                        camera.rotation_euler = item.rotation.copy()

                        suffix_list = [scene.renders_naming.subject]
                        if scene.renders_naming.use_posing: suffix_list.append(scene.renders_naming.posing)
                        if scene.renders_naming.use_shot_type: suffix_list.append(scene.renders_naming.shot_type)
                        suffix_list.append("_wire")
                        if scene.renders_naming.use_camera_prefix : suffix_list.append(item.name)
                        filename = "_".join(suffix_list)

                        scene.render.filepath = os.path.join(original['filepath'], filename)

                        bpy.ops.render.render(write_still = True)

                context.view_layer.objects.active = active_obj #レンダー系のops系はアクティブ状態をリセットする可能がある
            
        self.report({'INFO'},"completed render!")
        return {'FINISHED'}