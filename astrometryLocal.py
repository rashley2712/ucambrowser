#!/usr/bin/env python3
import requests
import json, subprocess
import argparse, sys, os
import configlib
import generallib
import filelib
import runlib
import matplotlib.pyplot
import numpy
import sourcelib
import wcslib
from astropy.io import fits

if __name__ == "__main__":
	plotWidth, plotHeight = 6, 6
	parser = argparse.ArgumentParser(description='Takes a single frame (in FITS format), creates a catalogue and asks Astrometry .net to solve it.')
	parser.add_argument('runID', type=str, help='RunID to be solved.')
	parser.add_argument('-c', '--config', default = "ucam.cfg", type=str, help='Config file.')
	parser.add_argument('-p', '--plot', action='store_true', help="Plot previews while working.")
	arg = parser.parse_args()

	config = configlib.configClass(debug=False)
	config.load(arg.config)
	
	runObject = runlib.runClass(arg.runID)
	runObject.load()

	print(runObject)

	workingDir = config.getProperty("workingDirectory")
	if workingDir: print("Working directory is:", workingDir)
	else: workingDir = "."
	filename = os.path.join(workingDir, runObject.getProperty('stackedFITS'))
	print("Opening the file: %s"%filename)

	# Run solve-field (from Astrometry.net) on the stacked image file
	stackedFilename = filename
	wcsCommand = ["solve-field"]
	wcsCommand.append(stackedFilename)
	wcsCommand.append("--overwrite")
	wcsCommand.append("--crpix-x")
	wcsCommand.append("200")
	wcsCommand.append("--crpix-y")
	wcsCommand.append("200")
	wcsCommand.append("-T")
	wcsCommand.append("-v")
	
	subprocess.call(wcsCommand)
	
	wcsFilename = generallib.changeExtension(stackedFilename, "new")
	print("WCS solution is in: ", wcsFilename)

	# Read the WCS solution and add this to the JSON object
	wcsFile = fits.open(wcsFilename)
	header = wcsFile[0].header
	wcs = wcslib.wcsSolution()
			
	equinox = float(header['EQUINOX'])
	referenceCoord = float(header['CRVAL1']), float(header['CRVAL2'])
	referencePixel = float(header['CRPIX1']), float(header['CRPIX2'])
			
	CD_array = [ [header['CD1_1'], header['CD1_2']], [ header['CD2_1'], header['CD2_2'] ] ]

	# Extract the SIP values
	for i in range(3):
		for j in range(3):
			try:
				value = float(header["A_%d_%d"%(i, j)])
			except KeyError:
				value = 0
			#print("A_%d_%d: %.12f"%(i, j, value))
			wcs.setSIPAvalue(i, j, value)
	for i in range(3):
		for j in range(3):
			try:
				value = float(header["B_%d_%d"%(i, j)])
			except KeyError:
				value = 0
			#print("B_%d_%d: %.12f"%(i, j, value))
			wcs.setSIPBvalue(i, j, value)
	for i in range(3):
		for j in range(3):
			try:
				value = float(header["AP_%d_%d"%(i, j)])
			except KeyError:
				value = 0
			#print("AP_%d_%d: %.12f"%(i, j, value))
			wcs.setSIPAPvalue(i, j, value)
			
	for i in range(3):
		for j in range(3):
			try:
				value = float(header["BP_%d_%d"%(i, j)])
			except KeyError:
				value = 0
			#print("BP_%d_%d: %.12f"%(i, j, value))
			wcs.setSIPBPvalue(i, j, value)
			
	wcs.setSolution(equinox, referenceCoord, referencePixel, CD_array)
	
	testPixel = (445, 119)
	test = wcs.getWorldCoord(testPixel)
	testSIP = wcs.getWorldSIP(testPixel)

	print("test {}   maps to {}".format(testPixel, test))
	print("test {}   maps to SIP {}".format(testPixel, testSIP))
	print("test {}   maps to {}".format(testPixel, wcs.degToSex(test)))
	print("test {}   maps to SIP {}".format(testPixel, wcs.degToSex(testSIP)))

	wcs.astropyLoad(header)

	apWorld = wcs.astropyPixToWorld(testPixel)
	apWorld = (apWorld[0][0], apWorld[0][1])
	print("Astropy result: ", apWorld)
	print("Astropy result: ", wcs.degToSex(apWorld))

	testPixel = (156,300)
	test = wcs.getWorldCoord(testPixel)
	testSIP = wcs.getWorldSIP(testPixel)

	print("test {}   maps to {}".format(testPixel, test))
	print("test {}   maps to {}".format(testPixel, wcs.degToSex(test)))
	
	testPixel = (5,430)
	test = wcs.getWorldCoord(testPixel)
	testSIP = wcs.getWorldSIP(testPixel)

	print("test {}   maps to {}".format(testPixel, test))
	print("test {}   maps to {}".format(testPixel, wcs.degToSex(test)))
	print(CD_array)

	runObject.addProperty('wcs', wcs.toJSON())		
	runObject.save()

	
	
	sys.exit()


