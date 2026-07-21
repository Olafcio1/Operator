import os
import sys

if os.name != "nt":
	print("[!] Operator only works on Windows systems.")
	print("[!] Aborting.")

	sys.exit(1)

import msvcrt
import subprocess
import importlib.util

from typing import Never

############
### UTIL ###
############

def require(**options: str) -> int | Never:
	while True:
		ch = msvcrt.getwch()

		if ch == '\x03':
			print("^C\n\nAborting.")
			sys.exit(1)

		for index, key in enumerate(options):
			if ch == key:
				print(key + "\n[>] " + options[key] + ".")

				if index == len(options) - 1:
					sys.exit(1)
				else:
					return index

####################
### DEPENDENCIES ###
####################

required = {
	"pyfiglet":        "pyfiglet",
	"gradient_figlet": "gradient-figlet",
	"colored":         "colored",
	"colorama":        "colorama"
}

missing = set()

for pkg in required:
	if importlib.util.find_spec(pkg) is None:
		missing.add(required[pkg])

if missing:
	print("[!] Dependencies %r are missing." % missing)
	print("[!] Install/exit (y/n): ", end='', flush=True)

	require(
		y="Installing",
		n="Exiting"
	)

	subprocess.run("%s -m pip install --disable-pip-version-check %s" % (sys.executable, " ".join(missing)))

#################
### ELEVATION ###
#################

from ctypes import windll
if not windll.shell32.IsUserAnAdmin():
	print("[!] Elevation required.")

	if importlib.util.find_spec("elevate") is not None:
		print("[!] Would you like to elevate automatically (y/n): ", end='', flush=True)

		require(
			y="Elevating",
			n="Exiting"
		)
	else:
		print("[!] Would you like to install a package to elevate automatically?")
		print("[!] Required packages: 'elevate'")
		print("[!] (y/n): ", end='', flush=True)

		require(
			y="Elevating",
			n="Exiting"
		)

	import elevate

	elevate.elevate()

	sys.exit(0)

##############
### SCRIPT ###
##############

import colored
import colorama

colorama.just_fix_windows_console()

print("Starting cleanup")
print("Do not interrupt")

def section(title: str, hue: int) -> None:
	dark = colored.Style.RESET + colored.fore_rgb(hue, 150, 150)
	light = colored.fore_rgb(hue + 40, 150, 150) + colored.Style.BLINK

	print()
	print(dark +("┌───────" + "%s" + "───────┐") % ("─" * (len(title) + 5)))
	print(dark + "└─────── %s⚙️ %s %s───────┘" % (light, title, dark))
	print()

	print(colored.fore_rgb(hue-35, 115, 115), end='')

############################
### SCRIPT: Service Stop ###
############################

section("Service Stop", 190)

services = [
	"DoSvc",
	"CDPSvc",
	"CDPUserSvc",
	"wlidsvc"
]

maxLength = max([len(raw) for raw in services])

for service in services:
	resp = subprocess.run("net stop %s" % service, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout

	service += " " * (maxLength - len(service))

	if 'service was stopped successfully.' in resp or ' is not started.' in resp:
		print("  ⛔ %s ⁄⁄ stopped" % service)
	else:
		print("  🛑 %s ⁄⁄ running" % service)

################################
### SCRIPT: Service Registry ###
################################

import winreg

section("Service Registry", 30)

services = [
	"DoSvc",
	"CDPSvc",
	"CDPUserSvc",
	"wlidsvc"
]

maxLength = max([len(raw) for raw in services])

for service in services:
	key = winreg.OpenKeyEx(
		winreg.HKEY_LOCAL_MACHINE,
		"System\\CurrentControlSet\\Services\\" + service,
		access=winreg.KEY_WRITE
	)

	service += " " * (maxLength - len(service))

	try:
		winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
	except:
		print("  ❗ %s ⁄⁄ unable to disable" % service)
	else:
		print("  🚧 %s ⁄⁄ disabled" % service)
	finally:
		winreg.CloseKey(key)

	service += " " * (maxLength - len(service))

#######################
### SCRIPT - Finish ###
#######################

print(colored.fore_rgb(60, 60, 60))
print("-=-   script finished   -=-")
print("-=- press enter to exit -=-")
input()
