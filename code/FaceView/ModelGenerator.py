import subprocess
import os
import shutil

#Gets a list of MakeHuman model features
def getFeatureList():
	f = open(os.devnull, 'w')
	child = subprocess.Popen(["python", "ModelGenerator.py", "-l"], stdin=None, stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'), shell=False, universal_newlines=True)
	l = child.communicate(None)[0]
	child.wait()
	l = l.split("\n")
	l = filter(None, l)
	f.close()
	return l
	
#Generate models from normalized data
def generateModels(dataList):

	if os.path.exists("../models"):
		shutil.rmtree("../models")

	f = open(os.devnull, 'w')
	child = subprocess.Popen(["python", "ModelGenerator.py"], stdin=subprocess.PIPE, stdout=None, stderr=None, shell=False, universal_newlines=True)
	
	message = ""
	for sample in dataList:
		message += ("BEGIN MODEL\n")
		paramList = sample.toParamList()
		message += ("\n".join(paramList) + '\n')
		message += ("END MODEL\n")
	child.communicate(message)
	child.wait()
	f.close()
		
	
#If it's the main module in the program 
if __name__ == '__main__':
	import re

	import time


	import os, sys
	lib_path = os.path.abspath(os.path.join('..', 'makehuman'))
	sys.path.append(lib_path)
	lib_path = os.path.abspath(os.path.join('..', 'makehuman', 'plugins', '9_export_obj'))
	sys.path.append(lib_path)
	lib_path = os.path.abspath(os.path.join('..', 'makehuman', 'plugins'))
	sys.path.append(lib_path)
	lib_path = os.path.abspath(os.path.join('..', 'makehuman', 'shared'))
	sys.path.append(lib_path)
	lib_path = os.path.abspath(os.path.join('..', 'makehuman', 'core'))
	sys.path.append(lib_path)
	lib_path = os.path.abspath(os.path.join('..', 'makehuman', 'lib'))
	sys.path.append(lib_path)

	f = open(os.devnull, 'w')
	stdout = sys.stdout
	sys.stdout = f
	
	import mh2obj

	from makehuman import *
	try:
		set_sys_path()
		make_user_dir()
		get_platform_paths()
		#redirect_standard_streams()
		get_hg_revision()
		os.environ['MH_VERSION'] = getVersionStr()
		os.environ['MH_SHORT_VERSION'] = getShortVersion()
		os.environ['MH_MESH_VERSION'] = getBasemeshVersion()
		argv = sys.argv
		sys.argv = [argv[0]]
		args = parse_arguments()
		init_logging()
	except Exception as e:
		print >> sys.stderr,  "error: " + format(unicode(e))
		import traceback
		bt = traceback.format_exc()
		print >> sys.stderr, bt

	# Pass release info to debug dump using environment variables
	os.environ['MH_FROZEN'] = "Yes" if isBuild() else "No"
	os.environ['MH_RELEASE'] = "Yes" if isRelease() else "No"

	debug_dump()
	from core import G
	G.args = args

	# Set numpy properties
	if not args.get('debugnumpy', False):
		import numpy
		# Suppress runtime errors
		numpy.seterr(all = 'ignore')

	# Here pyQt and PyOpenGL will be imported
	from mhmain import MHApplication
	import human
	import files3d
	import mh
	import skeleton
	import log

	#application.loadPlugin("plugins/9_export_obj")

	#dummy out the functionality from MakeHuman that we don't need
	class logDummy:
		def __init__(self):
			"derp"

	class splashDummy:
		def __init__(self):
			"derp"
		def logMessage(self, mess):
			"noop"
			
	class log_windowDummy:
		def __init__(self):
			"derp"

	log = logDummy()

	class appDummy:
		def __init__(self, human):
			self.selectedHuman = human
			self.splash = splashDummy()
			self.log_window = log_windowDummy()
			self.statusBar = None
			self.progress = None
		def addLogMessage(self, arg1, arg2):
			"Noop"
		


	buddy = human.Human(files3d.loadMesh(mh.getSysDataPath("3dobjs/base.obj"), maxFaces = 5))
	G.app = appDummy(buddy)
	base_skel = skeleton.load(mh.getSysDataPath('rigs/default.mhskel'), buddy.meshData)
	buddy.setBaseSkeleton(base_skel)

	import humanmodifier
	humanmodifier.loadModifiers("data/modifiers/modeling_modifiers.json", buddy)
	mods = []
	cats = []
	acceptableModGroups = [0, 1, 2, 7, 9, 12, 17, 18, 21]
	for i in acceptableModGroups:
		cats.append(buddy.modifierGroups[i])
		mods.append(buddy.getModifiersByGroup(cats[-1]))
	newMods = [item for sublist in mods for item in sublist]
	mods = newMods
	if "-l" in argv:
		# -l for list
		print
		sys.stdout = stdout
		for i in mods:
			print i.name
		sys.stdout = f
	else:		

		samples = []
		#syntax for parameter passing is 
		# <name>:<value between 0 and 1>\n
		
		#TODO in later update: make parsing more robust
		params = {}
		modDict = {}
		
		for line in sys.stdin:
			if line == "BEGIN MODEL\n":
				params = {}
				modDict = {}
				for mod in mods:
					modDict[mod.name] = mod
				continue
			if line == "END MODEL\n":
				samples.append((params, modDict))
				continue
			
			components = line.replace("\n", "").replace("\r", "").split(":")
			if components[0] == 'name':
				params[components[0]] = components[1]
			else:
				params[components[0]] = float(components[1])			
		
		sys.stdout = stdout
		import mh2obj
		ObjConfig = __import__('9_export_obj').ObjConfig
		conf = ObjConfig()
		conf.useNormals = True
		conf.human = buddy
		#for each sample
		for params, modDict in samples:
			#set all the modifiers to their default
			for val in modDict.values():
				val.setValue(val._defaultValue)
			#Set the value of the modifier to the value passed in
			for key, val in params.iteritems():
				if key == 'name':
					continue
				if not modDict.has_key(key):
					raise SyntaxError("There is no modifier: " + key)
				else:
					mod = modDict[key]
					val *= mod.getMax() - mod.getMin()
					val += mod.getMin()
					modDict[key].setValue(val)
			buddy.applyAllTargets()
			name = 'default'
			if params.has_key('name'):
				name = params['name']
			
			if not os.path.exists("../models"):
				os.makedirs("../models")
			sys.stdout = stdout
			mh2obj.exportObj("../models/" + name + ".obj", conf)
			
	#application.run()

	#import cProfile
	#cProfile.run('application.run()')

	close_standard_streams()