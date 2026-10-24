"""Post-baseline component diagnostic; no deployable improvement is claimed."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
from matplotlib.path import Path as PixelPath

from reproduce_component import NumpyOBB, load_functions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    src = args.source_dir
    scene = json.loads((src / "example_input.json").read_text())
    variants = {}
    for name in ["official", "diagnostic_without_negative_z_clamp"]:
        ns = {"np": np, "Path": PixelPath}
        load_functions(src/"relationship_utils.py", ["get_min_max_visible_depth_for_box", "calculate_occupied_pixels"], ns)
        load_functions(src/"configuration_utils.py", ["get_object_metrics"], ns)
        source = ast.parse((src/"configuration.py").read_text())
        function = next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=="check_spatial_configuration_relationships")
        if name != "official":
            loops = [n for n in function.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=="metrics"]
            assert len(loops)==1 and len(loops[0].body)==3, "Unexpected upstream clamp; abort instead of changing another block"
            function.body.remove(loops[0])
        exec(compile(ast.Module(body=[function],type_ignores=[]),str(src/"configuration.py"),"exec"),ns)
        variants[name]=ns
    results=[]
    for condition, shift in [("native",[0,0,0]),("joint_x_plus_1m",[1,0,0]),("joint_z_plus_1m",[0,0,1])]:
        shift=np.array(shift,dtype=float)
        objects=[{"name":v["Name"],"obb":NumpyOBB(v["bbox_3d"][0],shift)} for v in scene["objects"]]
        extrinsic=np.array(scene["camera_annotations"]["extrinsic"]);extrinsic[:3,3]+=shift
        intrinsic=np.array(scene["camera_annotations"]["intrinsic"])
        _,maps=variants["official"]["calculate_occupied_pixels"](objects,extrinsic,intrinsic,scene["image_size"])
        for name,ns in variants.items():
            output=ns["check_spatial_configuration_relationships"](objects[4],objects[0],extrinsic,intrinsic,scene["image_size"],maps,"lenient")
            results.append({"condition":condition,"variant":name,"target_id":4,"anchor_id":0,"strictness":"lenient","output":output})
    text="".join(json.dumps(v,default=lambda x:x.item())+"\n" for v in results)
    args.output.write_text(text)
    print(text,end="")
    print("Only the top-level negative-Z clamp loop was removed in memory; original source files were not modified.")


if __name__=="__main__":
    main()
