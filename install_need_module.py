
import subprocess
import sys

needs = ["plyer" , "kivy" , "android"]

def install_package(packages : list) :
	subprocess.check_call([sys.executable , "-m" , "pip" , "install" , "--upgrade", "pip"])
	for package in packages :
		subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package(needs)