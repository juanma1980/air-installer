#!/usr/bin/env python3
import  airmanager.airmanager as installer
import sys
import subprocess

installer=installer.AirManager()
err=0
dbg=False

def _debug(msg):
	if dbg:
		print("Helper: %s"%msg)
#def _debug

if sys.argv[1]=='install':
	_debug("Installing %s %s"%(sys.argv[2],sys.argv[3]))
	err=installer.install(sys.argv[2],sys.argv[3])
	try:
		subprocess.check_call(['gtk-update-icon-cache','/usr/share/icons/hicolor/'])
	except:
		err=1
elif sys.argv[1]=='remove':
	_debug("Removing %s %s"%(sys.argv[2],sys.argv[3]))
	air_pkg={'desktop':sys.argv[3],'air_id':sys.argv[2]}
	err=installer.remove_air_app(air_pkg)
	try:
		subprocess.check_call(['gtk-update-icon-cache','/usr/share/icons/hicolor/'])
	except:
		err=1

exit (err)

