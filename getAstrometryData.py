#!/usr/bin/env python3
import argparse, sys, os, subprocess

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Downloads data to the Astrometry.net data directory')
	arg = parser.parse_args()

	rootURL = "http://data.astrometry.net/4200/"
	dataPath = "/home/rashley/astrometry/data"

	# Get the 42xx files
	for i in range(8, 19):
		filename = "index-42%02d.fits"%i
		print(filename)

		# Use wget to grab the file
		saveFilename = os.path.join(dataPath, filename)
		getURL = rootURL + filename
		wcsCommand = ["wget"]
		wcsCommand.append("-c")
		wcsCommand.append("-O")
		wcsCommand.append(saveFilename)
		wcsCommand.append(getURL)
		
		subprocess.call(wcsCommand)


	sys.exit()
	
	# Get the 4205-xx files
	for i in range(11):
		filename = "index-4205-%02d.fits"%i
		print(filename)

		# Use wget to grab the file
		saveFilename = os.path.join(dataPath, filename)
		getURL = rootURL + filename
		wcsCommand = ["wget"]
		wcsCommand.append("-c")
		wcsCommand.append("-O")
		wcsCommand.append(saveFilename)
		wcsCommand.append(getURL)
		
		subprocess.call(wcsCommand)

	# Get the 4206-xx files
	for i in range(11):
		filename = "index-4206-%02d.fits"%i
		print(filename)

		# Use wget to grab the file
		saveFilename = os.path.join(dataPath, filename)
		getURL = rootURL + filename
		wcsCommand = ["wget"]
		wcsCommand.append("-c")
		wcsCommand.append("-O")
		wcsCommand.append(saveFilename)
		wcsCommand.append(getURL)
		
		subprocess.call(wcsCommand)


	# Get the 4207-xx files
	for i in range(11):
		filename = "index-4207-%02d.fits"%i
		print(filename)

		# Use wget to grab the file
		saveFilename = os.path.join(dataPath, filename)
		getURL = rootURL + filename
		wcsCommand = ["wget"]
		wcsCommand.append("-c")
		wcsCommand.append("-O")
		wcsCommand.append(saveFilename)
		wcsCommand.append(getURL)
		
		subprocess.call(wcsCommand)


	sys.exit()

	# Get the 4202-xx files
	for i in range(47):
		filename = "index-4202-%02d.fits"%i
		print(filename)

		# Use wget to grab the file
		saveFilename = os.path.join(dataPath, filename)
		getURL = rootURL + filename
		wcsCommand = ["wget"]
		wcsCommand.append("-c")
		wcsCommand.append("-O")
		wcsCommand.append(saveFilename)
		wcsCommand.append(getURL)
		
		subprocess.call(wcsCommand)



	# Get the 4203-xx files
	for i in range(47):
		filename = "index-4203-%02d.fits"%i
		print(filename)

		# Use wget to grab the file
		saveFilename = os.path.join(dataPath, filename)
		getURL = rootURL + filename
		wcsCommand = ["wget"]
		wcsCommand.append("-c")
		wcsCommand.append("-O")
		wcsCommand.append(saveFilename)
		wcsCommand.append(getURL)
		
		subprocess.call(wcsCommand)


	# Get the 4204-xx files
	for i in range(47):
		filename = "index-4204-%02d.fits"%i
		print(filename)

		# Use wget to grab the file
		saveFilename = os.path.join(dataPath, filename)
		getURL = rootURL + filename
		wcsCommand = ["wget"]
		wcsCommand.append("-c")
		wcsCommand.append("-O")
		wcsCommand.append(saveFilename)
		wcsCommand.append(getURL)
		
		subprocess.call(wcsCommand)

	sys.exit()


