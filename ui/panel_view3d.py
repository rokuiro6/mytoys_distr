import bpy

class PanelView3D(bpy.types.Panel):
     bl_label = "MyToys"
     bl_idname = "MyToys_Panel_View3D"
     bl_space_type = 'VIEW_3D' # 3DViewに表示させることを明示
     bl_region_type = 'UI'
     bl_category = "MyToys_distr" #サイドバーのタブ名
     
     def draw(self,context):
        layout = self.layout
        scene = context.scene

        layout.operator("mytoys.auto_generate_items",text="Auto Generate 3 Sided Items")
        layout.operator("mytoys.camera_transforms_add_item", text="Add Camera Transform", icon='ADD')
        layout.separator() 

        for i, item in enumerate(scene.camera_transforms):
            box_cam_item=layout.box()
            box_cam_ops = box_cam_item.row()
            box_cam_ops.prop(item,"name",text="")
            delete_button = box_cam_ops.operator("mytoys.camera_transforms_delete_item",text="",icon='TRASH')
            delete_button.index = i
            capture_button = box_cam_ops.operator("mytoys.capture_camera_transform",text="",icon="FILE_TICK")
            capture_button.index = i
            assign_button = box_cam_ops.operator("mytoys.assign_camera_transform",text="",icon="VIEW_CAMERA")
            assign_button.index = i
            box_cam_trans = box_cam_item.column()
            box_cam_trans.prop(item,"use_render",text = "Use Render")
            box_cam_trans.prop(item,"hide",icon="TRIA_DOWN" if item.hide else "TRIA_RIGHT",text="Tranform",emboss=False)
            if not item.hide:
                box_cam_trans = box_cam_item.column()
                box_cam_trans.prop(item, "location",text = "Location")
                box_cam_trans.prop(item,"rotation",text = "Rotation")

        # レンダリング画像の名前解決の設定をここにまとめる
        # プルダウン化、実際にはhideの値でアイコンの表示を変え、描画するかしないかを分岐しているだけである。embossはボタンっぽい見た目にするか
        box_item_naming = layout.box()
        box_item_naming.prop(scene.renders_naming,"hide",icon="TRIA_DOWN" if scene.renders_naming.hide else "TRIA_RIGHT", text="Render Naming Convention", emboss=False)
        if not scene.renders_naming.hide:
            column_subject = box_item_naming.column(align = True)
            column_subject.prop(scene.renders_naming,"subject",text="Subject")

            column_posing = layout.row(align = True)
            column_posing.prop(scene.renders_naming,"use_posing",text="Posing")
            column_posing.prop(scene.renders_naming,"posing",text="")

            column_shot_type = layout.row(align = True)
            column_shot_type.prop(scene.renders_naming,"use_shot_type",text="Shot Type")
            column_shot_type.prop(scene.renders_naming,"shot_type",text = "")

            layout.prop(scene.renders_naming,"use_wire",text="Use WireRender Suffix")
            layout.prop(scene.renders_naming,"use_camera_prefix",text = "Use CamTrans Item Name")

        layout.prop(scene.render_setting,"toggle_transparent",text = "Is World background Transparent")
        layout.prop(scene.render_setting,"toggle_wirerender",text="Render Wireframe")
        if scene.render_setting.toggle_wirerender:
            layout.prop(scene.render_setting, "wire_color",text = "Wire Color")
            layout.prop(scene.render_setting,"wire_opacity", text = "Wire Opacity")
            layout.prop(scene.render_setting,"use_default_material",text="Use Default Material")

        layout.operator("mytoys.camera_transforms_render_items", text="Render Selected Items",icon='RENDER_STILL')

        layout.separator()
        box_uv = layout.box()
        box_uv.prop(scene.uvlayouts_setting,"hide",icon = "TRIA_DOWN" if scene.uvlayouts_setting.hide else "TRIA_RIGHT",text = "Export UV Layouts",emboss=False)
        if not scene.uvlayouts_setting.hide:
            box_uv.prop(scene.uvlayouts_setting,"prefix",text="Prefix")
            box_uv.prop(scene.uvlayouts_setting,"resolution",text="Resolution")
            box_uv.prop(scene.uvlayouts_setting,"fill_opacity",text = "Fill Opacity")
            box_uv.prop(scene.uvlayouts_setting,"color",text = "color")
            # StringPropertyのSubtypeにFILE_PATHを追加することで入力欄の横に自動でフォルダのUIが付けられる
            # ただし、今回はwindowmanagerから起動した方が使いやすいため、コメントアウト
            #row.prop(scene.uvlayouts_setting,"uv_filepath",text="Filepath")
            box_uv.operator("mytoys.export_uvlayouts",text="Export UVLayout",icon = 'UV_DATA')

        box_fbx = layout.box()
        box_fbx.prop(scene.fbx_exporter_substance_setting,"hide",text="Export FBX for Substance",icon="TRIA_DOWN" if scene.fbx_exporter_substance_setting.hide else "TRIA_RIGHT",emboss=False)
        if not scene.fbx_exporter_substance_setting.hide:
            box_fbx.prop(scene.fbx_exporter_substance_setting,"modified",text = "Modified")
            box_fbx.prop(scene.fbx_exporter_substance_setting,"apply_gns",text = "Apply GNs")
            box_fbx.prop(scene.fbx_exporter_substance_setting,"mat_prefix",text = "Material Prefix")
            box_fbx.prop(scene.fbx_exporter_substance_setting,"tex_prefix",text="Texture Prefix")
            box_fbx.operator("mytoys.fbx_exporter_substance",text = "Export FBX for Substance",icon="EXPORT")

        box_custom_normal = layout.box()
        box_custom_normal.prop(scene.gen_normal_uv_names,"hide",text = "Generate Custom Normal UV",icon="TRIA_DOWN" if scene.gen_normal_uv_names.hide else "TRIA_RIGHT",emboss=False)
        if not scene.gen_normal_uv_names.hide:
            box_custom_normal.prop(scene.gen_normal_uv_names,"normal_xy", text = "uv: xy")
            box_custom_normal.prop(scene.gen_normal_uv_names,"normal_z",text = "uv: z")
            box_custom_normal.operator("mytoys.gen_normal_uv",text = "Pack Custom Normal to UVMap",icon="MOD_NORMALEDIT")