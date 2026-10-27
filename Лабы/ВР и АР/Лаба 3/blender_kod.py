# Кейс 1
import bpy

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "VR_Cube"
print(f"Создан объект: {cube.name}")
print(f"Вершин: {len(cube.data.vertices)}")


# Кейс 2
import bpy

cube = bpy.data.objects.get("VR_Cube")
if cube is None:
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    cube = bpy.context.active_object
    cube.name = "VR_Cube"

mat = (bpy.data.materials.get("VR_Material")
       or bpy.data.materials.new("VR_Material"))
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
mat.diffuse_color = (0.0, 0.0, 1.0, 1.0)
cube.data.materials.clear()
cube.data.materials.append(mat)
print(f"Материал назначен: {mat.name}")
print(f"Материалов на объекте: {len(cube.data.materials)}")


# Кейс 3
import bpy
import math

scene = bpy.context.scene
bpy.ops.object.camera_add(location=(0, -8, 1.6),
                          rotation=(math.radians(90), 0, 0))
camera = bpy.context.active_object
camera.name = "VR_Camera"
scene.camera = camera
scene.render.use_multiview = True
scene.render.views_format = "STEREO_3D"
camera.data.stereo.interocular_distance = 0.065
print(f"Стерео включено: {scene.render.use_multiview}")
print(f"Межзрачковое расстояние, м: "
      f"{round(camera.data.stereo.interocular_distance, 3)}")


# Кейс 4
import bpy

bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, location=(-4, 0, 1))
sphere = bpy.context.active_object
sphere.name = "VR_Sphere"
before = sum(len(p.vertices) - 2 for p in sphere.data.polygons)
ratio = 0.25
mod = sphere.modifiers.new("Decimate", "DECIMATE")
mod.ratio = ratio
with bpy.context.temp_override(object=sphere, active_object=sphere):
    bpy.ops.object.modifier_apply(modifier=mod.name)

print(f"Было треугольников: {before}")
print(f"Целевое число (ratio {ratio}): {int(before * ratio)}")


# Кейс 5
import bpy

count = 0
for r in range(5):
    for c in range(5):
        bpy.ops.mesh.primitive_cube_add(size=1,
                                        location=(4 + c * 2, r * 2 - 4, 0.5))
        bpy.context.active_object.name = f"Tile_{r}_{c}"
        count += 1

print(f"Создано объектов: {count}")


# Кейс 6
import bpy
import math

bpy.ops.object.light_add(type="SUN", location=(0, 0, 10),
                         rotation=(math.radians(45), 0, math.radians(30)))
light = bpy.context.active_object
light.name = "VR_Sun"
light.data.energy = 4.0
print(f"Источник света: {light.name}")
print(f"Тип: {light.data.type} | Мощность: {light.data.energy}")


# Кейс 7
import bpy
import math

cube = bpy.data.objects.get("VR_Cube")
if cube is None:
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    cube = bpy.context.active_object
    cube.name = "VR_Cube"

scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 60
count = 0
for frame, angle in ((1, 0.0), (60, 2 * math.pi)):
    cube.rotation_euler.z = angle
    count += cube.keyframe_insert("rotation_euler", index=2, frame=frame)

print(f"Анимация: кадры {scene.frame_start} - {scene.frame_end}")
print(f"Ключевых кадров вставлено: {count}")


# Кейс 8
import bpy

path = "/tmp/vr_scene.glb"
bpy.ops.export_scene.gltf(filepath=path, export_format="GLB")
print(f"Экспортировано в: {path}")


# Кейс 9
import numpy as np

head = np.array([0, -2, 1.6])
right_dir = np.array([1, 0, 0])
ipd = 0.065
left = head - right_dir * ipd / 2
right = head + right_dir * ipd / 2
print(f"Левый глаз:  {left}")
print(f"Правый глаз: {right}")
print(f"Расстояние между камерами: {np.linalg.norm(right - left):.3f} м")


# Кейс 10
import math

fov, distance, size = 100.0, 5.0, 2.0
width = 2 * distance * math.tan(math.radians(fov) / 2)
print(f"FOV = {fov} град, расстояние = {distance} м")
print(f"Ширина видимой области: {width:.2f} м")
print(f"Объект шириной {size} м занимает {size / width:.1%} ширины кадра")


# Кейс 11
import math
import numpy as np

half = math.radians(90) / 2
axis = np.array([0, 0, 1])
q = np.array([math.cos(half), *(axis * math.sin(half))])
w, x, y, z = q
matrix = np.array([
    [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
    [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
    [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
])
forward = [0, 1, 0]
rotated = matrix @ forward
print(f"Кватернион (w,x,y,z): {np.round(q, 3) + 0.0}")
print(f"Вектор взгляда до поворота: {forward}")
print(f"После поворота на 90 по Z: {np.round(rotated, 3) + 0.0}")


# Кейс 12
for hz in (72, 90, 120):
    print(f"{hz} Гц -> бюджет кадра {1000 / hz:.2f} мс")

render, hz = 9.5, 90
budget = 1000 / hz
verdict = "успеваем" if render <= budget else "НЕ успеваем"
print(f"Рендер {render} мс при {hz} Гц ({budget:.2f} мс): {verdict}")


# Кейс 13
for d in (2, 10, 35, 80):
    if d < 5:
        lod = "LOD0 (высокая детализация)"
    elif d < 20:
        lod = "LOD1 (средняя)"
    elif d < 50:
        lod = "LOD2 (низкая)"
    else:
        lod = "culled (не рендерится)"
    print(f"{d:>3} м -> {lod}")


# Кейс 14
budget, per_object, objects = 1_000_000, 8_000, 150
max_objects = budget // per_object
load = objects * per_object
verdict = "в бюджете" if load <= budget else "ПРЕВЫШЕН бюджет"
print(f"Бюджет сцены: {budget:,} тр., на объект: {per_object:,} тр.")
print(f"Максимум объектов в бюджете: {max_objects}")
print(f"Сцена из {objects} объектов = {load:,} тр. -> {verdict}")


# Кейс 15
stages = {"Датчик (трекинг)": 2.0, "Обработка": 3.0, "Рендер": 11.0,
          "Вывод на дисплей": 4.0}
total = sum(stages.values())
for name, ms in stages.items():
    print(f"{name}: {ms} мс")

print(f"Суммарная задержка motion-to-photon: {total} мс")
print(f"Комфортно (< 20 мс)? {total < 20}")
