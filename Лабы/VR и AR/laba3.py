"""Кейсы: Blender и программирование для VR на Python (15 кейсов).

Часть 1 (кейсы 1-8) использует Python API Blender (bpy) и работает только
внутри Blender: вкладка Scripting -> Open -> laba3.py -> Run Script, либо
из консоли: blender -b --python laba3.py
Часть 2 (кейсы 9-15) — расчёты на NumPy, работает и в обычном Python
(нужен пакет numpy: pip install numpy; в Blender он уже встроен).
"""
import contextlib
import io
import math
import os
import tempfile

import numpy as np

try:
    import bpy
except ImportError:  # запуск вне Blender — доступна только часть 2
    bpy = None


# ---------------------------------------------------------------------------
# Часть 1. Работа с Blender (Python API bpy)
# ---------------------------------------------------------------------------

def clear_scene():
    """Удалить все объекты, чтобы сцена собиралась с чистого листа."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


# 1
def create_vr_cube():
    """Куб «VR_Cube» на высоте 1 м."""
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    obj = bpy.context.active_object
    obj.name = "VR_Cube"
    return obj


def case_1():
    """Кейс 1: создать куб и вывести имя и число вершин."""
    obj = create_vr_cube()
    print(f"Создан объект: {obj.name}\nВершин: {len(obj.data.vertices)}")


# 2
def add_pbr_material(obj, name, color, roughness):
    """Назначить объекту PBR-материал на узле Principled BSDF."""
    mat = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0):  # в Blender 5 узлы включены всегда
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    obj.data.materials.append(mat)
    return mat


def case_2():
    """Кейс 2: синий PBR-материал с шероховатостью 0.3 для куба."""
    obj = bpy.data.objects["VR_Cube"]
    mat = add_pbr_material(obj, "VR_Material", (0.0, 0.0, 1.0, 1.0), 0.3)
    print(f"Материал назначен: {mat.name}\n"
          f"Материалов на объекте: {len(obj.data.materials)}")


# 3
def setup_stereo_camera(ipd):
    """Камера «VR_Camera» и стереорендер с межзрачковым расстоянием ipd."""
    scene = bpy.context.scene
    # Камера на уровне глаз (1.6 м) смотрит вдоль оси Y на центр сцены
    bpy.ops.object.camera_add(location=(0, -8, 1.6),
                              rotation=(math.radians(90), 0, 0))
    camera = bpy.context.active_object
    camera.name = "VR_Camera"
    scene.camera = camera
    scene.render.use_multiview = True
    scene.render.views_format = "STEREO_3D"
    camera.data.stereo.interocular_distance = ipd
    return camera


def case_3():
    """Кейс 3: включить multiview и задать IPD 65 мм."""
    camera = setup_stereo_camera(0.065)
    # Blender хранит float32, поэтому 0.065 читается как 0.0649999...
    ipd = round(camera.data.stereo.interocular_distance, 3)
    print(f"Стерео включено: {bpy.context.scene.render.use_multiview}\n"
          f"Межзрачковое расстояние, м: {ipd}")


# 4
def triangle_count(obj):
    """Число треугольников меша."""
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def decimate(obj, ratio):
    """Применить к объекту модификатор Decimate с долей ratio."""
    mod = obj.modifiers.new("Decimate", "DECIMATE")
    mod.ratio = ratio
    with bpy.context.temp_override(object=obj, active_object=obj):
        bpy.ops.object.modifier_apply(modifier=mod.name)


def case_4():
    """Кейс 4: упростить икосферу до 25% треугольников."""
    # В Blender subdivisions=1 — это сам икосаэдр (20 граней), поэтому
    # 20 * 4**3 = 1280 треугольников из условия даёт subdivisions=4
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4,
                                          location=(-4, 0, 1))
    sphere = bpy.context.active_object
    sphere.name = "VR_Sphere"
    before, ratio = triangle_count(sphere), 0.25
    decimate(sphere, ratio)
    print(f"Было треугольников: {before}\n"
          f"Целевое число (ratio {ratio}): {int(before * ratio)}")
    return triangle_count(sphere)


# 5
def create_grid(rows, cols, step):
    """Сетка rows x cols кубов Tile_<строка>_<столбец> с шагом step."""
    count = 0
    for r in range(rows):
        for c in range(cols):
            # Сетка стоит справа от куба и сферы, чтобы не пересекаться
            bpy.ops.mesh.primitive_cube_add(
                size=1, location=(4 + c * step, r * step - 4, 0.5))
            bpy.context.active_object.name = f"Tile_{r}_{c}"
            count += 1
    return count


def case_5():
    """Кейс 5: заполнить сцену сеткой 5x5."""
    print(f"Создано объектов: {create_grid(5, 5, 2)}")


# 6
def add_sun(name, energy):
    """Направленный источник света Sun мощностью energy."""
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 10),
                             rotation=(math.radians(45), 0,
                                       math.radians(30)))
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    return light


def case_6():
    """Кейс 6: добавить солнце мощностью 4.0."""
    light = add_sun("VR_Sun", 4.0)
    print(f"Источник света: {light.name}\n"
          f"Тип: {light.data.type} | Мощность: {light.data.energy}")


# 7
def animate_rotation(obj, frame_start, frame_end):
    """Полный оборот вокруг оси Z; возвращает число ключевых кадров."""
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = frame_start, frame_end
    inserted = 0
    for frame, angle in ((frame_start, 0.0), (frame_end, 2 * math.pi)):
        obj.rotation_euler.z = angle
        inserted += obj.keyframe_insert("rotation_euler", index=2,
                                        frame=frame)
    return inserted


def case_7():
    """Кейс 7: анимация вращения куба за 60 кадров."""
    count = animate_rotation(bpy.data.objects["VR_Cube"], 1, 60)
    scene = bpy.context.scene
    print(f"Анимация: кадры {scene.frame_start} - {scene.frame_end}\n"
          f"Ключевых кадров вставлено: {count}")


# 8
def export_glb(path):
    """Экспортировать всю сцену в бинарный glTF (.glb)."""
    # Экспортёр печатает служебный лог — прячем его, чтобы не мешал выводу
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB")
    return path


def case_8():
    """Кейс 8: экспорт сцены в vr_scene.glb."""
    path = os.path.join(tempfile.gettempdir(), "vr_scene.glb")
    print(f"Экспортировано в: {export_glb(path)}")


# ---------------------------------------------------------------------------
# Часть 2. Программирование для VR (расчёты на Python)
# ---------------------------------------------------------------------------

# 9
def eye_positions(head, right, ipd):
    """Позиции левого и правого глаза: смещение на ±IPD/2 вправо."""
    offset = np.asarray(right, dtype=float) * ipd / 2
    head = np.asarray(head, dtype=float)
    return head - offset, head + offset


def case_9():
    """Кейс 9: стереокамеры для головы в (0, -2, 1.6) и IPD 65 мм."""
    left, right = eye_positions([0, -2, 1.6], [1, 0, 0], 0.065)
    print(f"Левый глаз:  {left}\nПравый глаз: {right}\n"
          f"Расстояние между камерами: "
          f"{np.linalg.norm(right - left):.3f} м")


# 10
def visible_width(fov_deg, distance):
    """Ширина видимой области: 2 * distance * tan(FOV / 2)."""
    return 2 * distance * math.tan(math.radians(fov_deg) / 2)


def case_10():
    """Кейс 10: доля кадра для объекта 2 м на расстоянии 5 м."""
    fov, distance, size = 100.0, 5.0, 2.0
    width = visible_width(fov, distance)
    print(f"FOV = {fov} град, расстояние = {distance} м\n"
          f"Ширина видимой области: {width:.2f} м\n"
          f"Объект шириной {size} м занимает {size / width:.1%} "
          "ширины кадра")


# 11
def quaternion_from_axis_angle(axis, angle_deg):
    """Кватернион (w, x, y, z) поворота на угол вокруг оси."""
    half = math.radians(angle_deg) / 2
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    return np.array([math.cos(half), *(axis * math.sin(half))])


def quaternion_to_matrix(q):
    """Матрица поворота 3x3 из единичного кватерниона (w, x, y, z)."""
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ])


def case_11():
    """Кейс 11: поворот взгляда «вперёд» на 90 градусов вокруг Z."""
    q = quaternion_from_axis_angle([0, 0, 1], 90)
    forward = [0, 1, 0]
    rotated = quaternion_to_matrix(q) @ forward
    # + 0.0 превращает -0.0 (погрешность вычислений) в 0.0
    print(f"Кватернион (w,x,y,z): {np.round(q, 3) + 0.0}\n"
          f"Вектор взгляда до поворота: {forward}\n"
          f"После поворота на 90 по Z: {np.round(rotated, 3) + 0.0}")


# 12
def frame_budget(hz):
    """Бюджет кадра в миллисекундах."""
    return 1000 / hz


def case_12():
    """Кейс 12: бюджет кадра для 72, 90 и 120 Гц."""
    for hz in (72, 90, 120):
        print(f"{hz} Гц -> бюджет кадра {frame_budget(hz):.2f} мс")
    render, hz = 9.5, 90
    budget = frame_budget(hz)
    verdict = "успеваем" if render <= budget else "НЕ успеваем"
    print(f"Рендер {render} мс при {hz} Гц ({budget:.2f} мс): {verdict}")


# 13
def select_lod(distance):
    """Уровень детализации по расстоянию до камеры."""
    if distance < 5:
        return "LOD0 (высокая детализация)"
    if distance < 20:
        return "LOD1 (средняя)"
    if distance < 50:
        return "LOD2 (низкая)"
    return "culled (не рендерится)"


def case_13():
    """Кейс 13: LOD для расстояний 2, 10, 35 и 80 м."""
    for d in (2, 10, 35, 80):
        print(f"{d:>3} м -> {select_lod(d)}")


# 14
def polygon_budget(budget, per_object, objects):
    """Максимум объектов, суммарная нагрузка и укладывается ли сцена."""
    load = objects * per_object
    return budget // per_object, load, load <= budget


def case_14():
    """Кейс 14: бюджет 1 000 000 треугольников, сцена из 150 объектов."""
    budget, per_object, objects = 1_000_000, 8_000, 150
    max_objects, load, fits = polygon_budget(budget, per_object, objects)
    verdict = "в бюджете" if fits else "ПРЕВЫШЕН бюджет"
    print(f"Бюджет сцены: {budget:,} тр., на объект: {per_object:,} тр.\n"
          f"Максимум объектов в бюджете: {max_objects}\n"
          f"Сцена из {objects} объектов = {load:,} тр. -> {verdict}")


# 15
def motion_to_photon(stages, threshold=20.0):
    """Суммарная задержка конвейера и комфортна ли она (< threshold)."""
    total = sum(stages.values())
    return total, total < threshold


def case_15():
    """Кейс 15: задержка motion-to-photon."""
    stages = {"Датчик (трекинг)": 2.0, "Обработка": 3.0, "Рендер": 11.0,
              "Вывод на дисплей": 4.0}
    total, comfortable = motion_to_photon(stages)
    for name, ms in stages.items():
        print(f"{name}: {ms} мс")
    print(f"Суммарная задержка motion-to-photon: {total} мс\n"
          f"Комфортно (< 20 мс)? {comfortable}")


# Ожидаемый вывод из файла с заданием
EXPECTED = {
    1: """Создан объект: VR_Cube
Вершин: 8""",
    2: """Материал назначен: VR_Material
Материалов на объекте: 1""",
    3: """Стерео включено: True
Межзрачковое расстояние, м: 0.065""",
    4: """Было треугольников: 1280
Целевое число (ratio 0.25): 320""",
    5: "Создано объектов: 25",
    6: """Источник света: VR_Sun
Тип: SUN | Мощность: 4.0""",
    7: """Анимация: кадры 1 - 60
Ключевых кадров вставлено: 2""",
    8: "Экспортировано в: /tmp/vr_scene.glb",
    9: """Левый глаз:  [-0.0325 -2.      1.6   ]
Правый глаз: [ 0.0325 -2.      1.6   ]
Расстояние между камерами: 0.065 м""",
    10: """FOV = 100.0 град, расстояние = 5.0 м
Ширина видимой области: 11.92 м
Объект шириной 2.0 м занимает 16.8% ширины кадра""",
    11: """Кватернион (w,x,y,z): [0.707 0.    0.    0.707]
Вектор взгляда до поворота: [0, 1, 0]
После поворота на 90 по Z: [-1.  0.  0.]""",
    12: """72 Гц -> бюджет кадра 13.89 мс
90 Гц -> бюджет кадра 11.11 мс
120 Гц -> бюджет кадра 8.33 мс
Рендер 9.5 мс при 90 Гц (11.11 мс): успеваем""",
    13: """  2 м -> LOD0 (высокая детализация)
 10 м -> LOD1 (средняя)
 35 м -> LOD2 (низкая)
 80 м -> culled (не рендерится)""",
    14: """Бюджет сцены: 1,000,000 тр., на объект: 8,000 тр.
Максимум объектов в бюджете: 125
Сцена из 150 объектов = 1,200,000 тр. -> ПРЕВЫШЕН бюджет""",
    15: """Датчик (трекинг): 2.0 мс
Обработка: 3.0 мс
Рендер: 11.0 мс
Вывод на дисплей: 4.0 мс
Суммарная задержка motion-to-photon: 20.0 мс
Комфортно (< 20 мс)? False""",
}


def main():
    """Выполнить все кейсы и сравнить вывод с ожидаемым."""
    if bpy is None:
        print("Blender (bpy) не найден: кейсы 1-8 пропущены, их нужно "
              "запускать в Blender.\n")
    else:
        clear_scene()
    for number, expected in EXPECTED.items():
        if number <= 8 and bpy is None:
            continue
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            globals()[f"case_{number}"]()
        result = output.getvalue().rstrip()
        status = "OK" if result == expected else "ОТЛИЧАЕТСЯ"
        print(f"{'=' * 60}\nКейс {number}  [{status}]\n"
              f"--- ожидается:\n{expected}\n--- получено:\n{result}\n")
    if bpy is not None:
        print("* Кейс 8: в условии путь /tmp (Linux); на Windows файл "
              "сохраняется\n  во временную папку системы.")


if __name__ == "__main__":
    main()
