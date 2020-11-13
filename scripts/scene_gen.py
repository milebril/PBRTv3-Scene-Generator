import os
import numpy as np
import random
import argparse
from scene import Camera
import secrets
import geometry
import materials
import matrandomizers
import textures

# Constants
OUTPUT = "/output/scenes"

def mkdir(x):
	if not os.path.exists(x):
		os.mkdir(x)

def sample_camera():
    cam_position = [0, 3, 3]
    cam_target = [0, 0, -2]
    cam_up = [0, 1, 0]
    cam_fov = 60

    cam_params = {
        "position": list(cam_position),
        "target": list(cam_target),
        "up": list(cam_up),
        "fov": cam_fov
    }

    return cam_params

def create_pbrt(args, camera, out, mats, objs, lights):
    cam = camera.pbrt()

    film = 'Film "image" "integer xresolution" [%d]' % args.width
    film += ' "integer yresolution" [%d]' % args.height
    if args.output is not None:
        film += f' "string filename" "{out}' + "/" + f'{args.output}"\n\n'

    sampler = f'Sampler "sobol" "integer pixelsamples" {args.spp} \n'
    integrator = f'Integrator "path" "integer maxdepth" 10 \n\n'

    world = "WorldBegin \n"

    world += 'LightSource "infinite" "rgb L" [.4 .45 .5] \nLightSource "distant"  "point from" [ -30 40  100 ] "blackbody L" [3000 1.5]'

    world += '\n'

    for l in lights:
        world += l.pbrt() + '\n'

    for m in mats:
        world += m.pbrt() + '\n'

    for o in objs:
        world += o.pbrt() + '\n'

    world += "WorldEnd \n"

    return cam + film + sampler + integrator + world

def main(args):
    # mkdir(os.path.abspath(OUTPUT)) # Create output dir
    out_dir = os.getcwd().replace("\\","/") + OUTPUT
    try:
        # LOG.debug("Setting up folder {}".format(dst_dir))
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e: 
        print(e)
    
    # file_name = secrets.token_urlsafe(8)
    file_name = "1kpVZww7_S8"
    if os.path.exists(out_dir + f"/{file_name}.pbrt"):
        os.remove(out_dir + f"/{file_name}.pbrt")

    # Create random scene name
    if args.output is None:
        args.output = file_name
        if (args.topng):
            args.output += ".png"
        else:
            args.output += ".exr"

    #Init random camera
    cam = sample_camera()
    camera = Camera(**cam)

    material_list = []
    geometry_list = []
    light_list = []
    

    # for _ in range(15):
    #     obj = geometry.Sphere(radius=np.random.uniform(0, 0.8))
    #     geometry_list.append(obj)
    #     obj.apply_translation([random.randint(0,4)-2, random.randint(0,4)-2, -random.randint(2, 5)])

    #     mat = matrandomizers.random_material(id=secrets.token_urlsafe(5))
    #     material_list.append(mat)
    
    #     obj.assign_material(mat)

    obj = geometry.Sphere(radius=0.5)
    obj.apply_translation([0, 0, -1])
    mat = materials.UberMaterial(id="diff", diffuse=[0.1, 0.3, 0.9])
    obj.assign_material(mat)
    
    geometry_list.append(obj)
    material_list.append(mat)
        
    obj = geometry.Plane(scale=15)
    obj.apply_translation([0, -1, -2])
    tex = textures.Checkerboard("check", "spectrum", uscale=8, vscale=8, tex1=[0.1]*3, tex2=[0.8]*3)
    mat = materials.MatteMaterial(id="checkers", diffuse_texture=tex)
    obj.assign_material(mat)
    
    geometry_list.append(obj)
    material_list.append(mat)

    pbrt = create_pbrt(args, camera, out_dir, material_list, geometry_list, light_list)

    f = open(out_dir + f"/{file_name}.pbrt", "a")
    f.write(pbrt)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # # External binaries need to render the scene and convert the geometry
    # parser.add_argument("pbrt_exe", help="path to the `pbrt` executable.")
    # parser.add_argument("obj2pbrt_exe", help="path to PBRT's `obj2prt` "
    #                     "executable.")

    # # Data and output folders
    # parser.add_argument('assets', help="path to the assets to use.")
    # parser.add_argument('output')

    # Rendering parameters
    parser.add_argument('--spp', type=int, default=32)
    parser.add_argument('--gt_spp', type=int, default=512)
    parser.add_argument('--width', type=int, default=512)
    parser.add_argument('--height', type=int, default=512)
    parser.add_argument('--path_depth', type=int, default=5)
    parser.add_argument('--tile_size', type=int, default=128)
    parser.add_argument('--output', type=str)

    parser.add_argument('--no-clean', dest="clean", action="store_false",
                        default=True)
    parser.add_argument('--png', dest="topng", action="store_true",
                        default=False)

    main(parser.parse_args())