#!/usr/bin/env python3
import os
import stat
import datetime
import subprocess
import sys
import shutil
import tempfile
import urllib.request as url

class AirInstaller():
	def __init__(self):
		self.dbg=True
		self.default_icon="/usr/share/mate/applications/edu.media.mit.scratch2editor.desktop"
		self.adobeair_folder="/opt/AdobeAirApp/"
		self.adobeair_pkgname="adobeair"
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			logf=open('/tmp/log','a')
			print("DBG: %s"%msg)
			logf.write("%s\n"%msg)
			logf.close()
	#def _debug

	def _log(self,msg):
		f=open('a',logfile)
		f.write("%s"%msg)
		f.close()
	#def _log

	def install(self,air_file,icon=None):
		sw_install=False
		try:
			res=subprocess.check_output(["dpkg-query","-W","-f='${Status}'",self.adobeair_pkgname])
			if "not" in res:
				sw_install=True
		except:
			sw_install=True
		finally:
			if sw_install:
				self._install_adobeair()
#				self._install_adobeair_sdk()

		if not os.path.isdir(self.adobeair_folder):
			os.makedirs(self.adobeair_folder)
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
			#Non SDK 
			os.system("DISPLAY=:0 /usr/bin/Adobe\ AIR\ Application\ Installer -silent -eulaAccepted -location /opt/AdobeAirApp "+air_file)
			#subprocess.call(["/usr/bin/Adobe AIR Application Installer","-silent","-eulaAccepted","-location","/opt/AdobeAirApp",air_file])
			#Adobeair SDK (deprecated)
#			shutil.copyfile (air_file,wrkdir+"/"+file_name)
			#Copy icon to hicolor
			hicolor_icon='/usr/share/icons/hicolor/48x48/apps/%s.png'%basedir_name
			shutil.copyfile (icon,hicolor_icon)

			self._generate_desktop(file_name)
			self._debug("Installed in %s/%s"%(wrkdir,air_file))
			#select_icon
	#def install

	def _generate_desktop(self,file_name,):
		basedir_name=file_name.replace('.air','')
		desktop="/usr/share/applications/%s.desktop"%basedir_name
		f=open(desktop,'w')
		f.write("[Desktop Entry]\n\
Encoding=UTF-8\n\
Version=1.0\n\
Type=Application\n\
Exec=/opt/adobe-air-sdk/"+basedir_name+"/"+file_name+"\n\
Icon="+basedir_name+".png\n\
Terminal=false\n\
Name="+basedir_name+"\n\
Comment=Application from AdobeAir "+basedir_name+"\n\
MimeType=application/x-scratch-project\n\
Categories=Application;Education;Development;ComputerScience;\n\
")
		f.close()
#chmod +x $NEW_ICON_FILE
	#def _generate_desktop

	#Deprecated as we no longer work with adobeair-sdk
	def _install_adobeair_sdk(self):
		self._install_adobeair_depends()
		self._debug("Installing Adobe Air SDK")
		subprocess.call(["zero-lliurex-wget","http://lliurex.net/recursos-edu/misc/AdobeAIRSDK.tbz2","/tmp"])
		os.makedirs ("/opt/adobe-air-sdk")
		subprocess.call(["tar","jxf","/tmp/AdobeAIRSDK.tbz2","-C","/opt/adobe-air-sdk"])

		self._debug("Downloading Air Runtime SDK from Archlinux")
		subprocess.call(["zero-lliurex-wget","http://lliurex.net/recursos-edu/misc/adobe-air.tar.gz","/tmp"])
		subprocess.call(["tar","xvf","/tmp/adobe-air.tar.gz","-C","/opt/adobe-air-sdk"])
		subprocess.call(["chmod","+x","/opt/adobe-air-sdk/adobe-air/adobe-air"])
	#def _install_adobeair_sdk

	def _install_adobeair(self):
			self._install_adobeair_depends()
			self._debug("Installing Adobe Air")
			adobeair_url="http://airdownload.adobe.com/air/lin/download/2.6/AdobeAIRInstaller.bin"
			adobeair_file=url.urlopen(adobeair_url)
			(tmpfile,tmpfile_name)=tempfile.mkstemp()
			os.close(tmpfile)
			with open(tmpfile_name,'wb') as output:
				output.write(adobeair_file.read())
			st=os.stat(tmpfile_name)
			os.chmod(tmpfile_name,st.st_mode | 0o111)
#			subprocess.call([tmpfile_name,"-silent","-eulaAccepted","-pingbackAllowed"])
			os.system("DISPLAY=:0 " + tmpfile_name + " -silent -eulaAccepted -pingbackAllowed")
			os.remove(tmpfile_name)
			os.remove("/usr/lib/libgnome-keyring.so.0")
			os.remove("/usr/lib/libgnome-keyring.so.0.2.0")
	#def _install_adobeair

	def _install_adobeair_depends(self):
		self._debug("Removing old versions...")
		subprocess.call(["apt-get","-y","--purge","remove","adobeair"])
		subprocess.call(["apt-get","-q","update"])
		if os.uname().machine=='x86_64':
			self._debug("Installing i386 libs")
			subprocess.call(["apt-get","-q","-y","install","libgtk2.0-0:i386","libstdc++6:i386","libxml2:i386","libxslt1.1:i386","libcanberra-gtk-module:i386","gtk2-engines-murrine:i386","libqt4-qt3support:i386","libgnome-keyring0:i386","libnss-mdns:i386","libnss3:i386","libatk-adaptor:i386","libgail-common:i386"])
		else:
			subprocess.call(["apt-get","-q","-y","install","libgtk2.0-0","libxslt1.1","libxml2","libnss3","libxaw7","libgnome-keyring0","libatk-adaptor","libgail-common"])
		self._debug("Linking libs")
		try:
			os.symlink("/usr/lib/i386-linux-gnu/libgnome-keyring.so.0","/usr/lib/libgnome-keyring.so.0")
			os.symlink("/usr/lib/i386-linux-gnu/libgnome-keyring.so.0.2.0","/usr/lib/libgnome-keyring.so.0.2.0")
		except:
			pass
	#def _install_adobeair_depends

	def _check_file_is_air(self,air_file):
		retval=False
		if air_file.endswith(".air"):
			retval=True
		return retval
	#def _check_file_is_air
		
