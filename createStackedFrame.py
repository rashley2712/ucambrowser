#!/usr/bin/env python3
import argparse, sys, os
import configlib
import generallib
import filelib, runlib
import hipercam as hcam
import matplotlib
import numpy
import sourcelib
import astroalign
from PIL import Image


if __name__ == "__main__":
	plotWidth, plotHeight = 6, 6
	parser = argparse.ArgumentParser(description='Takes a run(.dat, .xml) and produces a stacked frame useful for previews and generating catalogue for WCS solution.')
	parser.add_argument('run', type=str, help='Raw file containing UCAM data (don''t include the .dat, .xml extension).')
	parser.add_argument('-c', '--config', default = "ucam.cfg", type=str, help='Config file.')
	parser.add_argument('-p', '--plot', action='store_true', help="Plot previews while working.")
	parser.add_argument('-s', '--save', action='store_true', help="Save the image to a png file.")
	
	arg = parser.parse_args()
	
	runID = arg.run

	config = configlib.configClass(debug=False)
	config.load(arg.config)

	if hasattr(config, 'percentiles'):
		percentiles = True
		plo = config.percentiles[0]
		phi = config.percentiles[1]
	else: percentiles = False
	print("HiPERCAM pipeline version:", hcam.version())

	rawDirectory = config.rawDirectory
	
	runObject = runlib.runClass(runID)
	if not runObject.load():
		runObject.save()
	print("Using the raw file path %s"%rawDirectory)

	if hasattr(config, 'flat') is not None:
		print("Using flat %s"%config.flat)
		flat = hcam.MCCD.read(config.flat)
				
		for ccd in flat.values():
			for window in ccd.values():
				flatData = window.data
				
				flatBinning = (window.xbin, window.ybin)
				flatWindow = (window.llx, window.lly, window.nx, window.ny)
				
				if arg.plot:
					flatPlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
					matplotlib.pyplot.imshow(generallib.percentiles(flatData, 5, 95), cmap='Greys', origin='lower')
					matplotlib.pyplot.draw()
					matplotlib.pyplot.show(block=False)
			
	
	filename = os.path.join(rawDirectory, runID)
	print("Opening the file: %s"%filename)

	from hipercam.ucam import Rdata
	ucamData = Rdata(filename)
	print("Number of frames: %d"%(ucamData.ntotal()))
	if arg.plot: framePlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
	
	sampledFlat = None
	if hasattr(config, 'stopframe'): stop=config.stopframe
	else: stop=1E8
	print(stop)
	if hasattr(config, 'skipstart'): ucamData(config.skipstart)
	firstFrame = None
	stackedImage = None
	for n, mccd in enumerate(ucamData):
		statusLine = str(n) + " : " 
		# subtract median from each window of each CCD
		for ccd in mccd.values():
			for wind in ccd.values():
				frameBinning = (wind.xbin, wind.ybin)
				frameWindow = (wind.llx, wind.lly, wind.nx, wind.ny)
				
				if sampledFlat is None: 
					print("Frame binning:",frameBinning)
					print("Flat window: {}".format(flatWindow))
					print("Frame window: {}".format(frameWindow))
					frameShape = numpy.shape(wind.data)
					flatShape = numpy.shape(flatData)
					if flatShape == frameShape:
						print("Flat and frame have the same dimensions")
						sampledFlat = flatData
					else: 
						from skimage.transform import downscale_local_mean
						sampledFlat = downscale_local_mean(flatData, (2, 2))
					if arg.plot: 
						sampleFlatPlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
						matplotlib.pyplot.imshow(generallib.percentiles(sampledFlat, 5, 95), cmap='Greys', origin='lower')
						matplotlib.pyplot.draw()
						matplotlib.pyplot.show(block=False)
						matplotlib.pyplot.pause(0.01)
						matplotlib.pyplot.figure(framePlot.number)
				if config.trim is not None:
					trim = config.trim
					left = wind.llx+config.trim[0]
					right = wind.nx - wind.llx - trim[1]
					bottom = wind.lly + trim[2]
					top = wind.ny - wind.lly - trim[3]
					wind.data = wind.data[bottom: top, left: right]
					windowedFlat = sampledFlat[bottom : top, left:right]
				thisFrame = numpy.divide(wind.data, windowedFlat)
				#thisFrame -= numpy.median(thisFrame)
			
				if firstFrame is None:
					firstFrame = thisFrame
					stackedImage = numpy.zeros(numpy.shape(thisFrame))
				else:
					transf, (source_list, target_list) = astroalign.find_transform(thisFrame, firstFrame)
					statusLine += "t_l ({:.3f}, {:.3f}) t_r ({:.3f}) t_s ({:.3f})".format(transf.translation[0], transf.translation[1], transf.rotation, transf.scale)
					transformedData, footprint = astroalign.apply_transform(transf, thisFrame, firstFrame)
					stackedImage+= transformedData
				if arg.plot: 
					matplotlib.pyplot.imshow(generallib.percentiles(thisFrame, 5, 95), origin='lower')
					matplotlib.pyplot.draw()
					matplotlib.pyplot.show(block=False)
					matplotlib.pyplot.pause(0.002)
					matplotlib.pyplot.clf()
		sys.stdout.write("\r" + statusLine + "               ")
		sys.stdout.flush()
		if n>=stop: break

	sys.stdout.write("\n")
	sys.stdout.flush()
		

	stackedImage /= n
	if arg.plot:
		stackedPlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
		if percentiles: matplotlib.pyplot.imshow(generallib.percentiles(stackedImage, plo, phi), origin='lower')
		else: matplotlib.pyplot.imshow(stackedImage , origin='lower')
		matplotlib.pyplot.draw()
		matplotlib.pyplot.show(block=True)
	if arg.save:
		pngImage = stackedImage
		savename = runID + ".png"
		imgData = pngImage
		imgData = numpy.rot90(imgData)
		imgData = numpy.rot90(imgData)
		imgData = numpy.rot90(imgData)
		imgSize = numpy.shape(imgData)
		print("imgSize", imgSize)
		imgLength = imgSize[0] * imgSize[1]
		testData = numpy.reshape(generallib.percentiles(imgData, 5, 99.5), imgLength, order="F")
		img = Image.new("L", imgSize)
		
		palette = []
		for i in range(256):
			palette.extend((255-i, 255-i, 255-i)) # inverse grey scale
		img.putpalette(palette)
		
		img.putdata(testData)
		#img = img.rotate(90)
		img.show()
		print("Writing PNG file: " + savename) 
		img.save(savename, "PNG", clobber=True)
		
	
		runObject.addProperty('runImage', savename)
		runObject.save()
		

	# Write the stackedFrame to a FITS file
	from astropy.io import fits
	hdu = fits.PrimaryHDU(stackedImage)
	hdul = fits.HDUList([hdu])
	FITSfilename = "{:s}_{:s}".format(runID, "stacked.fits")
	outputFilename = os.path.join(config.workingDirectory, FITSfilename)
	hdul.writeto(outputFilename, overwrite=True)

	runObject.addProperty("stackedFITS", FITSfilename)
	runObject.save()
	sys.exit()


