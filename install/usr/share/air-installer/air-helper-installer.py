#!/usr/bin/env python3
import  airinstaller.airinstaller as installer
import sys

print("App: %s"%sys.argv[1])
print("Ico: %s"%sys.argv[2])

installer=installer.AirInstaller()
installer.install(sys.argv[1],sys.argv[2])
