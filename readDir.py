#!/usr/bin/env python3
import argparse, sys, os
import configlib

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Reads a directory containing UCAM files and produces some metadata.')
	parser.add_argument('-d', '--directory', type=str, help='Path of the directory.')
	parser.add_argument('-c', '--config', default = "ucam.cfg", type=str, help='Config file.')
	arg = parser.parse_args()

	config = configlib.configClass(debug=False)
	config.load(arg.config)
	
	if arg.directory is None:
		rawDirectory = config.rawDirectory
	else:
		rawDirectory = arg.directory

	print("Looking for files in %s"%rawDirectory)
	filenames = os.listdir(rawDirectory)
	for f in filenames:
		print(f)
	
	sys.exit()


