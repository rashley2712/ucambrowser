#!/usr/bin/env python3
import runlib, configlib
import argparse, os

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Creates a web page for a specific run. Needs a runXXXX.json file.')
	parser.add_argument('run', type=str, help='JSON file containing the run number (no extension).')
	parser.add_argument('-c', '--config', default = "ucam.cfg", type=str, help='Config file.')
	arg = parser.parse_args()

	config = configlib.configClass(debug=False)
	config.load(arg.config)

	workingDirectory = config.getProperty('workingDirectory')
	installDirectory = config.getProperty('installDirectory')
	rawDirectory = config.getProperty('rawDirectory')
	
	runObject = runlib.runClass(arg.run)
	filename = os.path.join(workingDirectory, arg.run + ".json")
	runObject.addProperty('filename', filename)
	runObject.load()
	
	print(runObject)

	runHTMLFile = config.getProperty("runHTMLFile")
	destinationFile = os.path.join(workingDirectory, runObject.runID + ".html")
	print("writing to: ", destinationFile)
	outFile = open(destinationFile, 'wt')
	fileHandle = open(os.path.join(installDirectory, runHTMLFile), 'rt')
	for line in fileHandle:
		line = line.replace("{{ runImage }}", runObject.getProperty('runImage'))
		line = line.replace("{{ runID }}", runObject.runID)
		outFile.write(line)

	outFile.close()
	runObject.save()