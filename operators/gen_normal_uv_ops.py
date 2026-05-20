import bpy

class GenNormalUV(bpy.types.Operator):
    bl_idname = "mytoys.gen_normal_uv"
    bl_label = "Pack Custom Normal to UVMap"
    bl_description = "Pack evaluated custom normals into two new UV maps"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(getattr(obj, "type", None) == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        scene = context.scene
        props = scene.gen_normal_uv_names
        
        xy_uv_name = props.normal_xy.strip()
        z0_uv_name = props.normal_z.strip()

        if not xy_uv_name or not z0_uv_name:
            self.report({'ERROR'}, "Both UV names must be set.")
            return {'CANCELLED'}

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        depsgraph = context.evaluated_depsgraph_get()
        processed_count = 0

        for obj in mesh_objects:
            source_mesh = obj.data
            original_active_uv_index = source_mesh.uv_layers.active_index if len(source_mesh.uv_layers) > 0 else -1

            evaluated_obj = obj.evaluated_get(depsgraph)
            evaluated_mesh = evaluated_obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

            if not evaluated_mesh.has_custom_normals:
                evaluated_obj.to_mesh_clear()
                continue

            if len(evaluated_mesh.loops) != len(source_mesh.loops):
                self.report({'WARNING'}, f"Object '{obj.name}' topology changed. Skipped.")
                evaluated_obj.to_mesh_clear()
                continue

            split_normals = self._get_split_normals(evaluated_mesh)
            
            # 既存のUVレイヤーがあれば、それを使う
            xy_uv_layer = source_mesh.uv_layers.get(xy_uv_name) or source_mesh.uv_layers.new(name=xy_uv_name, do_init=False)
            z0_uv_layer = source_mesh.uv_layers.get(z0_uv_name) or source_mesh.uv_layers.new(name=z0_uv_name, do_init=False)

            packed_zero = self._pack_signed_value(0.0)
            
            for loop_index, normal in enumerate(split_normals):
                xy_value = (self._pack_signed_value(normal[0]), self._pack_signed_value(normal[1]))
                z0_value = (self._pack_signed_value(normal[2]), packed_zero)
                
                self._set_uv_value(xy_uv_layer, loop_index, xy_value)
                self._set_uv_value(z0_uv_layer, loop_index, z0_value)

            if original_active_uv_index >= 0:
                source_mesh.uv_layers.active_index = original_active_uv_index

            source_mesh.update()
            evaluated_obj.to_mesh_clear()
            processed_count += 1

        self.report({'INFO'}, f"Packed custom normals into UV maps for {processed_count} object(s).")
        return {'FINISHED'}

    def _get_split_normals(self, mesh):
        if hasattr(mesh, "calc_normals_split"):
            try:
                mesh.calc_normals_split()
            except RuntimeError:
                pass

        corner_normals = getattr(mesh, "corner_normals", None)
        if corner_normals is not None and len(corner_normals) == len(mesh.loops):
            return [(getattr(n, "vector", n)[0], getattr(n, "vector", n)[1], getattr(n, "vector", n)[2]) for n in corner_normals]

        return [tuple(loop.normal) for loop in mesh.loops]

    def _set_uv_value(self, uv_layer, loop_index, value):
        if hasattr(uv_layer, "uv"):
            uv_item = uv_layer.uv[loop_index]
            if hasattr(uv_item, "vector"):
                uv_item.vector = value
                return
        uv_layer.data[loop_index].uv = value

    def _pack_signed_value(self, value):
        return max(0.0, min(1.0, value * 0.5 + 0.5))