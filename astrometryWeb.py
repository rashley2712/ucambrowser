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

	
	plotWidth, plotHeight = (6, 6)
	workingDir = config.getProperty("workingDirectory")
	if workingDir: print("Working directory is:", workingDir)
	else: workingDir = "."
	filename = os.path.join(workingDir, runObject.getProperty('stackedFITS'))
	print("Opening the file: %s"%filename)
	hdu = fits.open(filename)
	print(hdu.info())

	imageData = hdu[0].data
	imageWidth, imageHeight = numpy.shape(hdu[0].data)
	if arg.plot:
		imagePlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
		matplotlib.pyplot.imshow(generallib.percentiles(imageData, 5, 99.9), cmap='Greys', origin='lower')
		matplotlib.pyplot.draw()
		

	sources = sourcelib.extractSources(imageData)
	print(sources)

	# Write the sources to a simple text file
	sourceList = []

	for s in sources:
		source = { 'x' : float(s['xcentroid']), 'y': float(s['ycentroid']), 'flux' : float(s['flux'])}
		sourceList.append(source)

	sourceList = sorted(sourceList, key=lambda object: object['flux'], reverse = True)

	catalogString = ""
	for s in sourceList:
		print("{:.2f} {:.2f} ({:.2f})".format(s['x'], s['y'], s['flux']))
		catalogString+= "{:.2f} {:.2f}\n".format(s['x'], s['y'])

	runObject.addProperty("masterCatalog",sourceList)
	runObject.save()
	if arg.plot:
		from photutils import CircularAperture
		positions = numpy.transpose((sources['xcentroid'], sources['ycentroid']))
		apertures = CircularAperture(positions, r=4.)
		apertures.plot(color='blue', lw=1.5, alpha=0.5)
		matplotlib.pyplot.draw()
		matplotlib.pyplot.show(block=False)
		matplotlib.pyplot.pause(0.1)
    
	
	
	APIkey = config.getProperty('APIkey')
	if APIkey: print("Astrometry.net API:", APIkey)
	else: 
		print("Please specify an Astrometry.net APIkey in the config file.")
		sys.exit()
	response = requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": APIkey})})
	responseJSON = json.loads(response.text)
	print(responseJSON)
	if responseJSON['status'] == "success":
		print("Session %s started"%responseJSON['session'])

	
	imageURL = "http://www.rashley.co.uk/run018_stacked.txt"
	astrometryRequest = { "session": responseJSON['session'], "url" : imageURL}
	astrometryRequest = { "session": responseJSON['session'], 'image_width' : imageWidth, 'image_height': imageHeight}
	astrometryRequestStr = json.dumps(astrometryRequest)
	print("main request:", astrometryRequestStr)
	
	import random
	boundary_key = ''.join([random.choice('0123456789') for i in range(19)])
	boundary = '===============%s==' % boundary_key
	headers = {'Content-Type': 'multipart/form-data; boundary="%s"' % boundary}
	data_pre = (
		'--' + boundary + '\n' +
		'Content-Type: text/plain\r\n' +
		'MIME-Version: 1.0\r\n' +
		'Content-disposition: form-data; name="request-json"\r\n' +
		'\r\n' +
		astrometryRequestStr + '\n' +
		'--' + boundary + '\n' +
                'Content-Type: application/octet-stream\r\n' +
                'MIME-Version: 1.0\r\n' +
                'Content-disposition: form-data; name="file"; filename="catalog.txt"' +
                '\r\n' + '\r\n')
	data_post = (
                '\n' + '--' + boundary + '--\n')
	data = data_pre + catalogString + data_post
	
	print(data)

	import time
	time.sleep(1)
	
	response = requests.post('http://nova.astrometry.net/api/upload', headers=headers, data=data)
	responseJSON = json.loads(response.text)
	print(response.text)
	responseJSON = json.loads(response.text)
	subID = responseJSON['subid']

	jobSuccess = False
	while not jobSuccess:
		time.sleep(8)
		response = requests.post("http://nova.astrometry.net/api/submissions/%s"%(subID))
		print(response.text)
		responseJSON = json.loads(response.text)
		jobCalibrations = responseJSON['job_calibrations']
		jobs = responseJSON['jobs']
		if len(jobCalibrations) > 0: jobSuccess = True

	job = jobs[0]
	time.sleep(4)
	resultsURL = "http://nova.astrometry.net/api/jobs/%s/calibration"%(job)
	print("Requesting results from ", resultsURL)
	response = requests.post(resultsURL)
	print(response.text)
	
	wcsURL = "http://nova.astrometry.net/wcs_file/4014529"
	print("Requesting results from ", wcsURL)
	response = requests.post(wcsURL)
	print(response.text)
	
	# Use wget to grab the WCS file
	wcsFilename = generallib.addSuffixToFilename(runObject.runID, "wcs")
	wcsURL = "http://nova.astrometry.net/wcs_file/%s"%job
	wcsCommand = ["wget"]
	wcsCommand.append("-O")
	wcsCommand.append(wcsFilename)
	wcsCommand.append(wcsURL)
	
	subprocess.call(wcsCommand)
	runObject.addProperty("wcsFITS", wcsFilename)
	runObject.save()
	
	# Read the WCS solution and add this to the JSON object
	wcsFile = fits.open(runObject.getProperty("wcsFITS"))
	header = wcsFile[0].header
	wcs = wcslib.wcsSolution()
			
	equinox = float(header['EQUINOX'])
	referenceCoord = float(header['CRVAL1']), float(header['CRVAL2'])
	referencePixel = float(header['CRPIX1']), float(header['CRPIX2'])
			
	CD_array = [ [header['CD1_1'], header['CD1_2']], [ header['CD2_1'], header['CD2_2'] ] ]

	# Extract the SIP values
	for i in range(3):
		print("A_%d"%i)
			
	wcs.setSolution(equinox, referenceCoord, referencePixel, CD_array)
	
	testPixel = (200, 100)
	test = wcs.getWorldCoord(testPixel)

	print("test {}   maps to {}".format(testPixel, test))
	runObject.addProperty('wcs', wcs.toJSON())		
	runObject.save()
	

	if arg.plot:
		matplotlib.pyplot.show(block=True)

	
	sys.exit()


