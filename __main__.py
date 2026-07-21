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
	"colour":          "colour",
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

import colour
import colored
import colorama

colorama.just_fix_windows_console()

print("Starting cleanup")
print("Do not interrupt")

def section(title: str, hue: int) -> None:
	rgb = [int(v * 255) for v in colour.hsl2rgb((hue / 255, 0.235, 0.666))]

	dark = colored.Style.RESET + colored.fore_rgb(*rgb)
	light = colored.fore_rgb(rgb[0] + 40, *rgb[1:]) + colored.Style.BLINK

	print()
	print(dark +("┌───────" + "%s" + "───────┐") % ("─" * (len(title) + 5)))
	print(dark + "└─────── %s⚙️ %s %s───────┘" % (light, title, dark))
	print()

	print(colored.fore_rgb(rgb[0] - 35, rgb[1] - 35, rgb[2] - 35), end='')

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
		access=winreg.KEY_SET_VALUE
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

################################
### SCRIPT: Identity Removal ###
################################

import winreg
import time

section("Identity Removal", 320)

def GID__RemoveTokens(user: str, value: str) -> None:
	index = 0
	entries = winreg.OpenKeyEx(winreg.HKEY_USERS, "%s\\Software\\Microsoft\\IdentityCRL\\Immersive\\production\\Token" % user, access=winreg.KEY_ENUMERATE_SUB_KEYS)

	try:
		while True:
			try:
				token = winreg.EnumKey(entries, index)
			except OSError:
				break

			key = winreg.OpenKeyEx(
				winreg.HKEY_USERS,
				"%s\\Software\\Microsoft\\IdentityCRL\\Immersive\\production\\Token\\%s" % (user, token),
				access=winreg.KEY_QUERY_VALUE
			)

			try:
				deviceID = winreg.QueryValue(key, "DeviceId")
			except:
				print("  ❓ %s:%s ⁄⁄ token invalid" % (user, token))

				index += 1
				continue
			finally:
				winreg.CloseKey(key)

			if deviceID == value:
				try:
					winreg.DeleteKey(
						winreg.HKEY_USERS,
						"%s\\Software\\Microsoft\\IdentityCRL\\Immersive\\production\\Token\\%s" % (user, token)
					)
				except:
					print("  ⛔ %s:%s ⁄⁄ token removed" % (user, token))
				else:
					print("  🛑 %s:%s ⁄⁄ token failed to remove" % (user, token))

			index += 1
	finally:
		winreg.CloseKey(entries)

def GID__RemoveAll() -> None:
	index = 0

	while True:
		try:
			user = winreg.EnumKey(winreg.HKEY_USERS, index)
		except OSError:
			break

		try:
			ExtendedProperties = \
			winreg.OpenKeyEx(
				winreg.HKEY_USERS,
				"%s\\Software\\Microsoft\\IdentityCRL\\ExtendedProperties" % user,
				access=winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE
			)
		except PermissionError:
			print("  Unaccessible identity for %s" % user)

			index += 1
			continue
		except FileNotFoundError:
			#print("  Missing identity for %s" % user)

			index += 1
			continue

		try:
			try:
				lid = winreg.QueryValueEx(ExtendedProperties, "LID")[0]
			except PermissionError:
				print("  Unaccessible LID for %s" % user)

				index += 1
				continue
			except FileNotFoundError:
				print("  Missing LID for %s" % user)

				index += 1
				continue

			print("  LID fetched for %s [%s]" % (user, lid))
			with open(os.getenv("USERPROFILE") + "/Documents/+ Operator User Log-%d.txt" % index, "a", encoding='utf-8', errors='ignore') as f:
				f.write("--- %s ---" % time.strftime("%Y %B %d / %H:%M:%S", time.localtime()))
				f.write("User: " + user)
				f.write("LID: " + lid)
			print("  LID backed up in user log %d" % index)

			print("  Delete id (y/n)? ", end='', flush=True)

			ch = msvcrt.getwche()

			print("\n")

			if ch == 'y':
				GID__RemoveTokens(user, lid)

				try:
					winreg.DeleteValue(ExtendedProperties, "LID", 0)
				except:
					print("  ❗ LID ⁄⁄ unable to remove")
				else:
					print("  🪪 LID ⁄⁄ removed")
		finally:
			winreg.CloseKey(ExtendedProperties)

		index += 1

GID__RemoveAll()

#############################
### SCRIPT: Identity View ###
#############################

import winreg

section("Identity View", 350)

def IL__InspectAccounts(user: str) -> None:
	try:
		index = 0
		entries = winreg.OpenKeyEx(winreg.HKEY_USERS, "%s\\Software\\Microsoft\\IdentityCRL\\StoredIdentities" % user, access=winreg.KEY_ENUMERATE_SUB_KEYS)
	except FileNotFoundError:
		text = ("  No identities for %s" % user,)
		return 0, text
	except PermissionError:
		text = ("  Unaccessible identities for %s" % user,)
		return 1, text

	text = []

	try:
		while True:
			try:
				email = winreg.EnumKey(entries, index)
			except OSError:
				break

			key = winreg.OpenKeyEx(
				winreg.HKEY_USERS,
				"%s\\Software\\Microsoft\\IdentityCRL\\StoredIdentities\\%s" % (user, email),
				access=winreg.KEY_QUERY_VALUE
			)

			try:
				accountCount    = winreg.QueryValueEx(key, "AccountsCount")[0]
				associatedCount = winreg.QueryValueEx(key, "AssociatedCount")[0]
			except:
				text.append("  ❓ %s:%s ⁄⁄ identity invalid" % (user, email))
			else:
				text.append("  ℹ️ Logging off %s's Microsoft account, %s, is recommended." % (user, email))
				text.append("    (accounts:   %d)" % accountCount)
				text.append("    (associated: %d)" % associatedCount)
			finally:
				winreg.CloseKey(key)

			index += 1
	finally:
		winreg.CloseKey(entries)

	return None, text

def IL__InspectAll() -> None:
	index = 0
	last = -67

	while True:
		try:
			user = winreg.EnumKey(winreg.HKEY_USERS, index)
		except OSError:
			break

		res, text = IL__InspectAccounts(user)

		if index != 0 and (res is None or res != last):
			print()
			last = res

		print("\n".join(text))

		index += 1

IL__InspectAll()

#######################
### SCRIPT - Finish ###
#######################

print(colored.fore_rgb(60, 60, 60))
print("-=-   script finished   -=-")
print("-=- press enter to exit -=-")
input()
