#!/usr/bin/env python3
import argparse, sys, os
import configlib
import generallib
import filelib
import matplotlib
import numpy
import sourcelib
import astroalign


if __name__ == "__main__":
	plotWidth, plotHeight = 6, 6
	parser = argparse.ArgumentParser(description='Takes a single frame (in FITS format), creates a catalogue and asks Astrometry .net to solve it.')
	parser.add_argument('image', type=str, help='FITs image of the file to be solved.')
	parser.add_argument('-c', '--config', default = "ucam.cfg", type=str, help='Config file.')
	parser.add_argument('-p', '--plot', action='store_true', help="Plot previews while working.")
	arg = parser.parse_args()

	config = configlib.configClass(debug=False)
	config.load(arg.config)
	
	if workingDir = config.getProperty():
		print("Working directory is:", workingDir)
	filename = os.path.join(rawDirectory, arg.rawfile)
	print("Opening the file: %s"%filename)

	
	sys.exit()


