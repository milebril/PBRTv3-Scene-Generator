import os
import numpy as np
import random
import argparse
from scene import Camera
import secrets
import geometry
import materials
import matrandomizers
import textures as texture
import xforms

# Helpfull commands
# find . -name "*.tga" > textures.txt

# Constants
OUTPUT = "/output/scenes"
ASSETS = "/assets"

def mkdir(x):
	if not os.path.exists(x):
		os.mkdir(x)

def random_aperture(min_=0.001, max_=0.05):
	"""Sample a camera aperture value, uniformly in log domain).
	Args:
		min_(float): smallest aperture.
		max_(float): largest aperture.
	"""
	log_aperture = np.random.uniform(np.log(min_), np.log(max_))
	aperture = np.exp(log_aperture)
	return aperture


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

	# do_dof = np.random.choice([True, False])
	# do_mblur = np.random.choice([True, False])
	do_dof = False
	do_mblur = True

	if do_mblur:
		cam_params["shutterclose"] = 1.0

	if do_dof:
		aperture = random_aperture()
	else:
		aperture = 0.0
	
	cam_params["focaldistance"] = 2
	cam_params["lensradius"] = aperture

	return cam_params

def create_pbrt(args, camera, out, mats, objs, lights):
	cam = camera.pbrt()

	film = 'Film "image" "integer xresolution" [%d]' % args.width
	film += ' "integer yresolution" [%d]' % args.height
	if args.output is not None:
		film += f' "string filename" "{out}' + "/" + f'{args.output}"\n\n'

	sampler = f'Sampler "random" "integer pixelsamples" {args.spp} \n'
	integrator = f'Integrator "path" "integer maxdepth" 5 \n\n'

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

def load_from_filelist(listpath):
	data = []

	if not os.path.exists(listpath):
		return data

	root = os.path.dirname(listpath)
	with open(listpath) as fid:
		for l in fid.readlines():
			path = os.path.join(root, l.strip())
			path = path.replace("./", "")  # removes relative path if any
			if os.path.exists(path):
				data.append(path)
	return data

def main(args):
	# mkdir(os.path.abspath(OUTPUT)) # Create output dir
	out_dir = os.getcwd().replace("\\","/") + OUTPUT
	try:
		# LOG.debug("Setting up folder {}".format(dst_dir))
		os.makedirs(out_dir, exist_ok=True)
	except Exception as e: 
		print(e)
	
	# Assets
	assets = os.getcwd().replace("\\","/") + ASSETS
	if not os.path.exists(assets):
		print("No valid assets folder provided.")
	
	# envmaps = os.path.join(assets, "envmaps.txt")
	textures = os.path.join(assets, "textures.txt")
	# models = os.path.join(assets, "models.txt")

	# envmaps = load_from_filelist(envmaps)
	textures = load_from_filelist(textures)
	# models = load_from_filelist(models)

	print("Assets in:" + ASSETS)
	# LOG.debug("  - %d envmaps" % len(self.envmaps))
	print("  - %d textures" % len(textures))
	# LOG.debug("  - %d models" % len(self.models))


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
	dist = np.linalg.norm(
	np.array(cam["position"])-np.array([0, 0, -1]))
	cam["focaldistance"] = dist

	camera = Camera(**cam)

	material_list = []
	geometry_list = []
	light_list = []

	obj = geometry.Sphere(radius=0.5)
	xforms.translate(obj, [0, 0, -1])
	mat = materials.UberMaterial(id="diff", diffuse=[0.1, 0.3, 0.9])
	# mat = materials.MirrorMaterial(id="Mirror")
	obj.assign_material(mat)

	#Motion blur on sphere
	radius = 1
	mvec_r = np.random.uniform(0.00, 2)*radius
	mvec_dir = np.random.uniform(size=(3,))
	mvec_dir /= np.linalg.norm(mvec_dir)
	mvec = mvec_dir*mvec_r

	xforms.translate(obj, mvec, target="end")
	
	geometry_list.append(obj)
	material_list.append(mat)
		
	obj = geometry.Plane(scale=15)
	xforms.translate(obj, [0, -1, -2])
	# tex = texture.Checkerboard("check", "spectrum", uscale=8, vscale=8, tex1=[0.1]*3, tex2=[0.8]*3)
	tex = matrandomizers.random_texture(textures)
	mat = materials.MatteMaterial(id="checkers", diffuse_texture=tex)
	obj.assign_material(mat)

	geometry_list.append(obj)
	material_list.append(mat)

	obj = geometry.Plane(scale=4)
	xforms.rotate(obj, [1, 0, 0], 90)
	xforms.translate(obj, [0, 0, -5])
	# tex = texture.Checkerboard("check", "spectrum", uscale=8, vscale=8, tex1=[0.1]*3, tex2=[0.8]*3)
	mat = mat = materials.MirrorMaterial(id="Mirror")
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