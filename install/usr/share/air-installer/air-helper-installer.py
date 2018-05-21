#!/usr/bin/env python3
import  airinstaller.airinstaller as installer
import sys
import subprocess

installer=installer.AirInstaller()
installer.install(sys.argv[1],sys.argv[2])
subprocess.check_call(['gtkgtk-update-icon-cache','/usr/share/icons/hicolor/')

