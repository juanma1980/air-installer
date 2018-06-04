
#!/usr/bin/env python3

#import LliurexGoogleDriveManager
#import lliurex.lliurexgdrive
import air_manager
import InstallBox
import ManageBox



class Core:
	
	singleton=None
	DEBUG=True
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	
	def __init__(self,args=None):
		
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):
		
		self.dprint("Creating InstallBox...")
		self.install_box=InstallBox.InstallBox()
		self.manage_box=ManageBox.ManageBox()
		
		
		# Main window must be the last one
		self.dprint("Creating airInstaller...")
		self.airman=air_manager.AirManagerGui()
		
		self.airman.load_gui()
		self.airman.start_gui()
	#def init
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint
