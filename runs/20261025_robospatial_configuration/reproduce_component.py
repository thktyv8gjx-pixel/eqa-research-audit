"""Offline RoboSpatial configuration component, not a trained-VLM reproduction.

Original numerical functions are loaded unchanged from pinned private sources.
Only Open3D's OBB container is replaced by an explicit NumPy boundary adapter.
No model calls, new questions, meshes, sampling, or source patches are used.
"""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import platform
import time
from pathlib import Path

import numpy as np
from matplotlib.path import Path as PixelPath
from scipy.spatial.transform import Rotation

COMMIT = "7a1b901cd86ad980ff6d14c0c1fc9d556ccabb19"
PREFIX = f"https://raw.githubusercontent.com/NVlabs/RoboSpatial/{COMMIT}/"
SOURCES = {
    "configuration.py": ("robospatial/spatial_analysis/configuration/configuration.py", ""),
    "configuration_utils.py": ("robospatial/spatial_analysis/configuration/configuration_utils.py", "933f28258ceafb0fde5f14216790a8c7f6bc221a"),
    "relationship_utils.py": ("robospatial/spatial_analysis/relationship_utils.py", ""),
    "example_input.json": ("example_data/annotations/example_input.json", "4bc5c709df5e43077a3edde3de82362226b1cb3b"),
    "example_image.jpg": ("example_data/images/example_dataset/example_scene/example_image.jpg", "2b8bf7f8bdeb7d9e55cd9c68be1cf27c51b2067a"),
}


class NumpyOBB:
    """Open3D-compatible center/R/extents/corner order; this is an adaptation.

    Rotation order and corner order follow Open3D v0.19.0 Geometry3D.cpp and
    BoundingVolume.cpp. Native Open3D execution is not claimed.
    """
    def __init__(self, values, shift):
        values = np.asarray(values, dtype=float)
        self.center = values[:3] + shift
        self.extent = values[3:6]
        self.R = Rotation.from_euler("ZXY", values[6:]).as_matrix()

    def get_center(self):
        return self.center

    def get_box_points(self):
        signs = np.array([[-1,-1,-1], [1,-1,-1], [-1,1,-1], [-1,-1,1],
                          [1,1,1], [-1,1,1], [1,-1,1], [1,1,-1]])
        return (signs * self.extent / 2) @ self.R.T + self.center


def load_functions(source, names, namespace):
    tree = ast.parse(source.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    # Exclude module imports and unrelated Open3D constructors, not function code.
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)


def projected_points(box, extrinsic, intrinsic):
    points = np.c_[box.get_box_points(), np.ones(8)]
    camera = points @ np.linalg.inv(extrinsic).T
    pixels = camera @ intrinsic.T
    return pixels[:, :2] / pixels[:, 2:3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    src, out = args.source_dir.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    source_index = {}
    for filename, (relative, expected) in SOURCES.items():
        data = (src / filename).read_bytes()
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if expected:
            assert blob == expected, filename
        source_index[filename] = {"url": PREFIX + relative, "git_blob": blob,
                                  "sha256": hashlib.sha256(data).hexdigest()}
    namespace = {"np": np, "Path": PixelPath}
    load_functions(src / "relationship_utils.py", ["get_min_max_visible_depth_for_box", "calculate_occupied_pixels"], namespace)
    load_functions(src / "configuration_utils.py", ["get_object_metrics"], namespace)
    load_functions(src / "configuration.py", ["check_spatial_configuration_relationships"], namespace)
    scene = json.loads((src / "example_input.json").read_text())
    intrinsic = np.array(scene["camera_annotations"]["intrinsic"])
    original_extrinsic = np.array(scene["camera_annotations"]["extrinsic"])
    conditions = {"native": [0,0,0], "joint_x_plus_1m": [1,0,0], "joint_z_plus_1m": [0,0,1]}
    pairs = [(0,1,"potato_relative_to_banana"), (4,0,"clock_relative_to_potato")]
    config = {"scope": "official configuration functions with NumPy OBB adapter; not full pipeline or VLM",
              "source_commit": COMMIT, "scene": "example_dataset/example_scene/example_image.jpg",
              "source_index": source_index, "conditions": conditions, "pair_ids": pairs,
              "strictness": ["strict", "lenient"], "model_calls": 0,
              "python": platform.python_version(), "architecture": platform.machine(),
              "versions": {p: importlib.metadata.version(p) for p in ["numpy","scipy","matplotlib"]},
              "reference": "raw box Z interval/centroid comparisons; a geometry diagnostic, not independent human labels",
              "registered_before_first_execution": True}
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    original_pixels = None
    with (out / "results.jsonl").open("w") as file:
        for condition, shift in conditions.items():
            shift = np.array(shift, dtype=float)
            objects = [{"name": item["Name"], "obb": NumpyOBB(item["bbox_3d"][0], shift)} for item in scene["objects"]]
            extrinsic = original_extrinsic.copy()
            extrinsic[:3,3] += shift
            pixels = [projected_points(o["obb"],extrinsic,intrinsic) for o in objects]
            if original_pixels is None:
                original_pixels = pixels
            projection_delta = max(float(np.abs(a-b).max()) for a,b in zip(pixels,original_pixels))
            _, maps = namespace["calculate_occupied_pixels"](objects, extrinsic, intrinsic, scene["image_size"])
            for strictness in ["strict", "lenient"]:
                for a,b,pair_name in pairs:
                    started = time.perf_counter()
                    relation = namespace["check_spatial_configuration_relationships"](objects[a], objects[b], extrinsic, intrinsic, scene["image_size"], maps, strictness)
                    ma = namespace["get_object_metrics"](objects[a],extrinsic,intrinsic,scene["image_size"],maps)
                    mb = namespace["get_object_metrics"](objects[b],extrinsic,intrinsic,scene["image_size"],maps)
                    raw_above = ma["world_z_min"] > mb["world_z_max"] + 1e-6
                    if strictness == "lenient" and not raw_above:
                        raw_above = ma["world_z_avg"] > mb["world_z_max"] + 1e-6
                    record = {"condition": condition, "strictness": strictness, "pair": pair_name,
                              "target_id": a, "anchor_id": b, "max_projected_corner_delta_px": projection_delta,
                              "target_visible": bool(ma["is_visible"]), "anchor_visible": bool(mb["is_visible"]),
                              "raw_z_target": [float(ma[k]) for k in ["world_z_min","world_z_avg","world_z_max"]],
                              "raw_z_anchor": [float(mb[k]) for k in ["world_z_min","world_z_avg","world_z_max"]],
                              "raw_geometry_above_reference": bool(raw_above),
                              "output": relation, "seconds": time.perf_counter()-started}
                    line = json.dumps(record, default=lambda value: value.item())
                    file.write(line + "\n")
                    print(line, flush=True)
    print("Completed original, X-translation control, and Z-origin intervention; no model used.")


if __name__ == "__main__":
    main()
