
class Camera():
	"""PBRT camera.

	Args:
	"""
	def __init__(self, **kwargs):
		self.xform = kwargs.get("xform", None)
		self.position = kwargs.get("position", [0, 0, 1])
		self.target = kwargs.get("target", [0, 0, 0])
		self.up = kwargs.get("up", [0, 1, 0])
		self.type = kwargs.get("type", "perspective")
		self.fov = kwargs.get("fov", 35)
		self.shutteropen = kwargs.get("shutteropen", 0.0)
		self.shutterclose = kwargs.get("shutterclose", 0.0)
		self.lensradius = kwargs.get("lensradius", 0.0)
		self.focaldistance = kwargs.get("focaldistance", 0.0)

	def __repr__(self):
		out = "camera\n"
		out += " .fov = {}\n".format(self.fov)
		out += " .at ({:.1f} {:.1f} {:.1f})\n".format(*self.position)
		out += " .looking at ({:.1f} {:.1f} {:.1f})\n".format(*self.target)
		out += " .shutter ({:.1f} {:.1f})\n".format(self.shutteropen,
													self.shutterclose)
		out += " .focus distance {:.1f}\n".format(self.focaldistance)
		out += " .lens radius {:.10f}\n".format(self.lensradius)
		return out

	def pbrt(self):
		"""PBRT string representation.

		Returns:
			s(str): PBRT formated string.
		"""
		s = 'LookAt {} {} {}  {} {} {}  {} {} {}\n'.format(
			*(self.position + self.target + self.up))

		# s += ('Camera "{}" "float fov" [{}]\n').format(self.type, self.fov)

		s += ('Camera "{}" "float fov" [{}] "float shutteropen" [{}] '
				'"float shutterclose" [{}] "float lensradius" [{}]'
				' "float focaldistance" [{}]\n').format(self.type, self.fov,
														self.shutteropen,
														self.shutterclose,
														self.lensradius,
														self.focaldistance)
		return s
