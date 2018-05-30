#!/usr/bin/env python3
import os
import stat
import datetime
import subprocess
import sys
import shutil
import tempfile
import zipfile
import urllib.request as url

LOG='/tmp/air_installer.log'

class AirInstaller():
	def __init__(self):
		self.dbg=True
		self.default_icon="/usr/share/air-installer/rsrc/air-installer_icon.png"
		self.adobeair_folder="/opt/AdobeAirApp/"
		self.adobeair_pkgname="adobeair"
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("airinstaller: %s"%msg)
			self._log(msg)
	#def _debug

	def _log(self,msg):
		f=open(LOG,'a')
		f.write("%s"%msg)
		f.close()
	#def _log

	def install(self,air_file,icon=None):
		sw_err=0
		sw_install_adobe=False
		sw_install_sdk=False
		sw_download=False
		try:
			res=subprocess.check_output(["dpkg-query","-W","-f='${Status}'",self.adobeair_pkgname])
			if "not" in str(res):
				self._debug("adobeair not installed")
				sw_install_adobe=True
		except Exception as e:
			self._debug("dpkg-query failed: %s"%e)
			sw_install_adobe=True
		finally:
			if sw_install_adobe:
				sw_download=self._install_adobeair()

		if sw_download==False:
			self._debug("Adobeair failed to install")
				
		if not os.path.isdir(self.adobeair_folder):
			os.makedirs(self.adobeair_folder)
		if not icon:
			icon=self.default_icon
		self._debug("Procced with file: %s"%air_file)
		file_name=os.path.basename(air_file)
		if self._check_file_is_air(air_file):
			basedir_name=file_name.replace(".air","")
			self._debug("Installing %s"%air_file)
			#Non SDK 
#			os.system("DISPLAY=:0 /usr/bin/Adobe\ AIR\ Application\ Installer -silent -eulaAccepted -location /opt/AdobeAirApp "+air_file)
			sw_err=self._install_air_package(air_file)
			if sw_err:
				self._debug("Trying rebuild...")
				modified_air_file=self._recompile_for_certificate_issue(air_file)
				self._debug("Installing %s"%modified_air_file)
				sw_err=self._install_air_package(modified_air_file)
			if sw_err:
				self._debug("Failed to install code: %s"%sw_err)
				self._debug("Going with sdk installation")
				sw_err=self._install_air_package_sdk(air_file,icon)
				sw_install_sdk=True

			if not sw_err and sw_install_sdk:
				#Copy icon to hicolor
				sw_installed=self._generate_desktop(file_name)
				if sw_installed:
					hicolor_icon='/usr/share/icons/hicolor/48x48/apps/%s.png'%basedir_name
					shutil.copyfile (icon,hicolor_icon)
					self._debug("Installed in %s"%(basedir_name))
				else:
					self._debug("%s Not Installed!!!"%(basedir_name))
	#def install

	def _install_air_package(self,air_file):
		sw_err=1
		my_env=os.environ.copy()
		my_env["DISPLAY"]=":0"
		try:
			subprocess.check_output(["/usr/bin/Adobe AIR Application Installer","-silent","-eulaAccepted","-location","/opt/AdobeAirApp",air_file],env=my_env)
			sw_err=0
		except Exception as e:
			self._debug("Install Error: %s"%e)
		return sw_err
	#def _install_air_package

	def _install_air_package_sdk(self,air_file,icon=None):
		sw_err=0
		if not icon:
			icon=self.default_icon
		file_name=os.path.basename(air_file)
		basedir_name=file_name.replace('.air','')
		wrkdir=self.adobeair_folder+basedir_name
		if os.path.isdir(wrkdir):
			try:
				shutil.rmtree(wrkdir)
			except Exception as e:
				sw_err=3
				self._debug(e)
		try:
			os.makedirs(wrkdir)
		except Exception as e:
			sw_err=4
			self._debug(e)
		if sw_err==0:
			try:
				shutil.copyfile (air_file,wrkdir+"/"+file_name)
			except:
				sw_err=1
		#Copy icon to hicolor
		if sw_err==0:
			hicolor_icon='/usr/share/icons/hicolor/48x48/apps/%s.png'%basedir_name
			try:
				shutil.copyfile (icon,hicolor_icon)
			except:
				sw_err=2

		self._generate_desktop_sdk(file_name)
		self._debug("Installed in %s/%s"%(wrkdir,air_file))
		return sw_err
	#def _install_air_package_sdk

	def _generate_desktop(self,file_name):
		basedir_name=file_name.replace('.air','')
		desktop="/usr/share/applications/%s.desktop"%basedir_name
		exec_file=self._get_air_bin_file(basedir_name)
		self._debug("Exec: %s"%exec_file)
		if exec_file:
			f=open(desktop,'w')
			f.write("[Desktop Entry]\n\
Encoding=UTF-8\n\
Version=1.0\n\
Type=Application\n\
Exec=\""+exec_file+"\"\n\
Icon="+basedir_name+".png\n\
Terminal=false\n\
Name="+basedir_name+"\n\
Comment=Application from AdobeAir "+basedir_name+"\n\
MimeType=application/x-scratch-project\n\
Categories=Application;Education;Development;ComputerScience;\n\
")
			f.close()
			return True
		else:
			return False
#chmod +x $NEW_ICON_FILE
	#def _generate_desktop

	def _get_air_bin_file(self,basedir_name):
		target_bin=''
		for folder in os.listdir(self.adobeair_folder):
			target_folder=''
			if basedir_name.lower() in folder.lower() or basedir_name.lower==folder.lower():
				target_folder=os.listdir(self.adobeair_folder+folder)
			else:
				split_name=''
				if '-' in basedir_name.lower():
					split_name=basedir_name.lower().split('-')[0]
				elif ' ' in basedir_name.lower():
					split_name=basedir_name.lower().split(' ')[0]
				elif '.' in basedir_name.lower():
					split_name=basedir_name.lower().split('.')[0]
				if split_name!='' and split_name in folder.lower():
					target_folder=os.listdir(self.adobeair_folder+folder)
			if target_folder:
				if 'bin' in target_folder:
					candidate_list=os.listdir(self.adobeair_folder+folder+'/bin')
					for candidate_file in candidate_list:
						test_file=self.adobeair_folder+folder+'/bin/'+candidate_file
						self._debug("Testing %s"%test_file)
						if os.access(test_file,os.X_OK):
							target_bin=test_file
							self._debug("Test OK for %s"%target_bin)
							break
		return(target_bin)

	def _generate_desktop_sdk(self,file_name):
		basedir_name=file_name.replace('.air','')
		desktop="/usr/share/applications/%s.desktop"%basedir_name
		f=open(desktop,'w')
		f.write("[Desktop Entry]\n\
Encoding=UTF-8\n\
Version=1.0\n\
Type=Application\n\
Exec=/opt/adobe-air-sdk/adobe-air/adobe-air "+self.adobeair_folder+basedir_name+"/"+file_name+"\n\
Icon="+basedir_name+".png\n\
Terminal=false\n\
Name="+basedir_name+"\n\
Comment=Application from AdobeAir "+basedir_name+"\n\
MimeType=application/x-scratch-project\n\
Categories=Application;Education;Development;ComputerScience;\n\
")
		f.close()
	#def _generate_desktop_sdk

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
			req=url.Request(adobeair_url,headers={'User-Agent':'Mozilla/5.0'})
			try:
				adobeair_file=url.urlopen(req)
			except Exception as e:
				self._debug(e)
				return False
			(tmpfile,tmpfile_name)=tempfile.mkstemp()
			os.close(tmpfile)
			with open(tmpfile_name,'wb') as output:
				output.write(adobeair_file.read())
			st=os.stat(tmpfile_name)
			os.chmod(tmpfile_name,st.st_mode | 0o111)
#			subprocess.call([tmpfile_name,"-silent","-eulaAccepted","-pingbackAllowed"])
			os.system("DISPLAY=:0 " + tmpfile_name + " -silent -eulaAccepted -pingbackAllowed")
			os.remove(tmpfile_name)
			#Remove symlinks
			if os.path.isfile("/usr/lib/libgnome-keyring.so.0"):
				os.remove("/usr/lib/libgnome-keyring.so.0")
			if os.path.isfile("/usr/lib/libgnome-keyring.so.0.2.0"):
				os.remove("/usr/lib/libgnome-keyring.so.0.2.0")
			return True
	#def _install_adobeair

	def _install_adobeair_depends(self):
		self._debug("Removing old versions...")
		subprocess.call(["apt-get","-y","--purge","remove","adobeair"])
		subprocess.call(["apt-get","-q","update"])
		lib_folder='x86_64-linux-gnu'
		if os.uname().machine=='x86_64':
			self._debug("Installing i386 libs")
			subprocess.call(["apt-get","-q","-y","install","libgtk2.0-0:i386","libstdc++6:i386","libxml2:i386","libxslt1.1:i386","libcanberra-gtk-module:i386","gtk2-engines-murrine:i386","libqt4-qt3support:i386","libgnome-keyring0:i386","libnss-mdns:i386","libnss3:i386","libatk-adaptor:i386","libgail-common:i386"])
		else:
			lib_folder='i386-linux-gnu'
			subprocess.call(["apt-get","-q","-y","install","libgtk2.0-0","libxslt1.1","libxml2","libnss3","libxaw7","libgnome-keyring0","libatk-adaptor","libgail-common"])
		self._debug("Linking libs")
		try:
			if os.path.isfile("/usr/lib/libgnome-keyring.so.0"):
				os.remove("/usr/lib/libgnome-keyring.so.0")
			if os.path.isfile("/usr/lib/libgnome-keyring.so.0.2.0"):
				os.remove("/usr/lib/libgnome-keyring.so.0.2.0")
			os.symlink("/usr/lib/"+lib_folder+"/libgnome-keyring.so.0","/usr/lib/libgnome-keyring.so.0")
			os.symlink("/usr/lib/"+lib_folder+"/libgnome-keyring.so.0.2.0","/usr/lib/libgnome-keyring.so.0.2.0")
		except Exception as e:
			self._debug(e)
	#def _install_adobeair_depends

	def _recompile_for_certificate_issue(self,air_file):
		self._debug("Rebuilding package %s"%air_file)
		new_air_file=''
		tmpdir=tempfile.mkdtemp()
		self._debug("Extracting to %s"%tmpdir)
		os.chdir(tmpdir)
		air_pkg=zipfile.ZipFile(air_file,'r')
		for file_to_unzip in air_pkg.infolist():
			try:
				air_pkg.extract(file_to_unzip)
			except:
				pass
		air_pkg.close()
		air_xml=''
		for xml_file in os.listdir("META-INF/AIR"):
			if xml_file.endswith(".xml"):
				air_xml=xml_file
				break
		if air_xml:
			shutil.move("META-INF/AIR/"+air_xml,air_xml)
			shutil.rmtree("META-INF/",ignore_errors=True)
			os.remove("mimetype")
			self._debug("Generating new cert")
			subprocess.call(["/opt/adobe-air-sdk/bin/adt","-certificate","-cn","lliurex","2048-RSA","lliurex.p12","lliurex"])
			new_air_file=os.path.basename(air_file)
			my_env=os.environ.copy()
			my_env["DISPLAY"]=":0"
			try:
				subprocess.check_output(["/opt/adobe-air-sdk/bin/adt","-package","-tsa","none","-storetype","pkcs12","-keystore","lliurex.p12",new_air_file,air_xml,"."],input=b"lliurex",env=my_env)
			except Exception as e:
				self._debug(e)
		return tmpdir+'/'+new_air_file
	#def _recompile_for_certificate_issue

	def get_installed_apps(self):
		installed_apps={}
		for app_dir in os.listdir(self.adobeair_folder):
			self._debug("Testing %s"%app_dir)
			app_desktop=''
			if os.path.isdir(self.adobeair_folder+app_dir+'/bin') or os.path.isfile(self.adobeair_folder+app_dir+'/'+app_dir+'.air'):
				#Search the desktop of the app
				self._debug("Searching desktop %s"%'/usr/share/applications/'+app_dir+'.desktop')
				sw_desktop=False
				if os.path.isdir(self.adobeair_folder+app_dir+'/share/META-INF/AIR'):
					for pkg_file in os.listdir(self.adobeair_folder+app_dir+'/share/META-INF/AIR'):
						if pkg_file.endswith('.desktop'):
							app_desktop='/usr/share/applications/'+pkg_file
							sw_desktop=True
							break
				if sw_desktop==False:
					if os.path.isfile('/usr/share/applications/'+app_dir+'.desktop'):
						app_desktop='/usr/share/applications/'+app_dir+'.desktop'
					elif os.path.isfile('/usr/share/applications/'+app_dir.lower()+'.desktop'):
						app_desktop='/usr/share/applications/'+app_dir.lower()+'.desktop'
				#Get the app_id
				self._debug("Searching id %s"%self.adobeair_folder+app_dir+'/share/application.xml')
				if os.path.isfile(self.adobeair_folder+app_dir+'/share/application.xml'):
					f=open(self.adobeair_folder+app_dir+'/share/application.xml','r')
					flines=f.readlines()
					app_id=''
					for fline in flines:
						fline=fline.strip()
						if fline.startswith('<id>'):
							app_id=fline
							app_id=app_id.replace('<id>','')
							app_id=app_id.replace('</id>','')
							break
					f.close()
				elif os.path.isfile(self.adobeair_folder+app_dir+'/'+app_dir+'.air'):
					app_id=app_dir+'.air'
				installed_apps[app_dir]={'desktop':app_desktop,'air_id':app_id}
		return installed_apps
	#def get_installed_apps

	def remove_air_app(self,*kwarg):
		sw_err=1
		my_env=os.environ.copy()
		my_env["DISPLAY"]=":0"
		air_dict=kwarg[0]
		sw_uninstall_err=False
		if 'air_id' in air_dict.keys():
			self._debug("Removing %s"%air_dict['air_id'])
			if air_dict['air_id'].endswith('.air'):
				air_file=self.adobeair_folder+air_dict['air_id'].replace('.air','')+'/'+air_dict['air_id']
				self._debug("SDK app detected %s"%air_file)
				if os.path.isfile(air_file):
					try:
						shutil.rmtree(os.path.dirname(air_file))
						sw_err=0
					except Exception as e:
						self._debug(e)
			else:
				try:
					#Let's try with supercow's power
					pkgname=subprocess.check_output(["apt-cache","search",air_dict['air_id']],env=my_env,universal_newlines=True)
					pkglist=pkgname.split(' ')
					for pkg in pkglist:
						self._debug("Testing %s"%pkg)
						if air_dict['air_id'].lower() in pkg.lower():
							try:
								self._debug("Uninstalling %s"%pkg)
								sw_uninstall_err=subprocess.check_output(["apt-get","-y","remove",pkg],universal_newlines=True)
								self._debug("Uninstalled OK %s"%pkg)
								sw_err=0
							except Exception as e:
								self._debug(e)
							break
				except Exception as e:
						sw_uninstall_err=True
				
				if sw_err:
					try:
						sw_uninstall_err=subprocess.check_output(["/usr/bin/Adobe AIR Application Installer","-silent","-uninstall","-location","/opt/AdobeAirApp",air_dict['air_id']],env=my_env)
						sw_err=0
					except Exception as e:
						self._debug(e)

		if 'desktop' in air_dict.keys():
			if os.path.isfile(air_dict['desktop']):
				try:
					os.remove(air_dict['desktop'])
				except Exception as e:
					self._debug(e)
		return sw_err

	def _check_file_is_air(self,air_file):
		retval=False
		if air_file.endswith(".air"):
			retval=True
		return retval
	#def _check_file_is_air
		
