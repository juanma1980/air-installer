#!/usr/bin/env python3
import os
import datetime
import subprocess
import sys
import shutil
import tempfile

class AirInstaller():
	def __init__(self):
		self.dbg=True
		self.default_icon="/usr/share/mate/applications/edu.media.mit.scratch2editor.desktop"
		self.adobeair_folder="/opt/adobe-air-sdk/"

	def _debug(self,msg):
		if self.dbg:
			logf=open('/tmp/log','a')
			print("DBG: %s"%msg)
			logf.write("%s\n"%msg)
			logf.close()

	def _log(self,msg):
		f=open('a',logfile)
		f.write("%s"%msg)
		f.close()

	def install(self,air_file,icon=None):
		if not os.path.isdir(self.adobeair_folder):
			self._install_adobeair()
		if not icon:
			icon=self.default_icon
		self._debug("Procced with file: %s"%air_file)
		file_name=os.path.basename(air_file)
		if self._check_file_is_air(air_file):
			basedir_name=file_name.replace(".air","")
			self._debug("Installing %s"%air_file)
			wrkdir=self.adobeair_folder+basedir_name
			if os.path.isdir(wrkdir):
				try:
					shutil.rmtree(wrkdir)
				except Exception as e:
					self._debug(e)

			try:
				os.makedirs(wrkdir)
			except Exception as e:
				self._debug(e)
			shutil.copyfile (air_file,wrkdir+"/"+file_name)
			#Copy icon to hicolor
			hicolor_icon='/usr/share/icons/hicolor/48x48/apps/%s.png'%basedir_name
			shutil.copyfile (icon,hicolor_icon)

			self._generate_desktop(file_name)
			self._debug("Installed in %s/%s"%(wrkdir,air_file))
			#select_icon

	def _install_adobeair(self):
		self._debug("Removing old versions...")
		subprocess.call(["apt-get","-y","--purge","remove","adobeair"])
		if os.uname().machine=='x86_64':
			self._debug("Installing i386 libs")
			subprocess.call(["apt-get","-q","update"])
			subprocess.call(["apt-get","-q","-y","install","libgtk2.0-0:i386 libstdc++6:i386 libxml2:i386 libxslt1.1:i386 libcanberra-gtk-module:i386 gtk2-engines-murrine:i386 libqt4-qt3support:i386 libgnome-keyring0:i386 libnss-mdns:i386 libnss3:i386"])
		self._debug("Linking libs")
		try:
			os.symlink("/usr/lib/i386-linux-gnu/libgnome-keyring.so.0","/usr/lib/libgnome-keyring.so.0")
			os.symlink("/usr/lib/i386-linux-gnu/libgnome-keyring.so.0.2.0","/usr/lib/libgnome-keyring.so.0.2.0")
		except:
			pass

		self._debug("Installing Adobe Air SDK")
		subprocess.call(["zero-lliurex-wget","http://lliurex.net/recursos-edu/misc/AdobeAIRSDK.tbz2","/tmp"])
		os.makedirs ("/opt/adobe-air-sdk")
		subprocess.call(["tar","jxf","/tmp/AdobeAIRSDK.tbz2","-C","/opt/adobe-air-sdk"])

		self._debug("Downloading Air Runtime SDK from Archlinux")
		subprocess.call(["zero-lliurex-wget","http://lliurex.net/recursos-edu/misc/adobe-air.tar.gz","/tmp"])
		subprocess.call(["tar","xvf","/tmp/adobe-air.tar.gz","-C","/opt/adobe-air-sdk"])
		subprocess.call(["chmod","+x","/opt/adobe-air-sdk/adobe-air/adobe-air"])

	def _generate_desktop(self,file_name,):
		basedir_name=file_name.replace('.air','')
		desktop="/usr/share/applications/%s.desktop"%basedir_name
		f=open(desktop,'w')
		f.write("[Desktop Entry]\n\
Encoding=UTF-8\n\
Version=1.0\n\
Type=Application\n\
Exec=/opt/adobe-air-sdk/adobe-air/adobe-air /opt/adobe-air-sdk/"+basedir_name+"/"+file_name+"\n\
Icon="+basedir_name+".png\n\
Terminal=false\n\
Name="+basedir_name+"\n\
Comment=Application from AdobeAir "+basedir_name+"\n\
MimeType=application/x-scratch-project\n\
Categories=Application;Education;Development;ComputerScience;\n\
")
		f.close()
#chmod +x $NEW_ICON_FILE

	def _check_file_is_air(self,air_file):
		retval=False
		if air_file.endswith(".air"):
			retval=True
		return retval
		
