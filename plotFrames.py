#!/usr/bin/env python3
import argparse, sys, os
import configlib
import generallib
import hipercam as hcam
import matplotlib
import numpy
import sourcelib
import astroalign

if __name__ == "__main__":
	plotWidth, plotHeight = 6, 6
	parser = argparse.ArgumentParser(description='Plots the frames in a UCAM file.')
	parser.add_argument('rawfile', type=str, help='Raw file containing UCAM data.')
	parser.add_argument('-c', '--config', default = "ucam.cfg", type=str, help='Config file.')
	parser.add_argument('-s', '--stop', default=1E8, type=int, help="Stop after processing 's' frames.")
	arg = parser.parse_args()

	config = configlib.configClass(debug=False)
	config.load(arg.config)

	if hasattr(config, 'percentiles'):
		percentiles = True
		plo = config.percentiles[0]
		phi = config.percentiles[1]
	else: percentiles = False
	print("HiPERCAM pipeline version:", hcam.version())

	rawDirectory = config.rawDirectory
	
	print("Using the raw file path %s"%rawDirectory)

	if config.flat is not None:
		print("Using flat %s"%config.flat)
		flat = hcam.MCCD.read(config.flat)
		print(flat)
		from astropy.visualization import SqrtStretch
		from astropy.visualization.mpl_normalize import ImageNormalize
				
		for ccd in flat.values():
			for window in ccd.values():
				flatPlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
				flatData = window.data
				norm = ImageNormalize(flatData, stretch=SqrtStretch())
				matplotlib.pyplot.imshow(generallib.percentiles(flatData, 5, 95), cmap='Greys', origin='lower')
				flatBinning = (window.xbin, window.ybin)
				flatWindow = (window.llx, window.lly, window.nx, window.ny)
				print("Flat binning:", flatBinning)
				matplotlib.pyplot.draw()
				matplotlib.pyplot.show(block=False)
			
	
	filename = os.path.join(rawDirectory, arg.rawfile)
	print("Opening the file: %s"%filename)

	from hipercam.ucam import Rdata
	ucamData = Rdata(filename)
	print("Number of frames: %d"%(ucamData.ntotal()))
	framePlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
	
	sampledFlat = None
	stop=arg.stop
	if hasattr(config, 'skipstart'): ucamData(config.skipstart)
	firstFrame = None
	stackedImage = None
	for n, mccd in enumerate(ucamData):
		# subtract median from each window of each CCD
		print(n)
		for ccd in mccd.values():
			for wind in ccd.values():
				frameBinning = (wind.xbin, wind.ybin)
				frameWindow = (wind.llx, wind.lly, wind.nx, wind.ny)
				
				if sampledFlat is None: 
					print("Frame binning:",frameBinning)
					print("Flat window: {}".format(flatWindow))
					print("Frame window: {}".format(frameWindow))
					frameShape = numpy.shape(wind.data)
					from skimage.transform import downscale_local_mean
					sampledFlat = downscale_local_mean(flatData, (2, 2))
					sampleFlatPlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
					matplotlib.pyplot.imshow(generallib.percentiles(sampledFlat, 35, 99), cmap='Greys', origin='lower')
					matplotlib.pyplot.draw()
					matplotlib.pyplot.show(block=False)
					matplotlib.pyplot.pause(0.01)
					matplotlib.pyplot.figure(framePlot.number)
					print(numpy.shape(sampledFlat))
				if config.trim is not None:
					trim = config.trim
					left = wind.llx+config.trim[0]
					right = wind.nx - wind.llx - trim[1]
					bottom = wind.lly + trim[2]
					top = wind.ny - wind.lly - trim[3]
					print(left, right)
					wind.data = wind.data[bottom: top, left: right]
					windowedFlat = sampledFlat[bottom : top, left:right]
				thisFrame = numpy.divide(wind.data, windowedFlat)
				thisFrame -= numpy.median(thisFrame)
				#thisFrame = numpy.divide(thisFrame, windowedFlat)
				
				#sources = sourcelib.extractSources(wind.data)
				if firstFrame is None:
					firstFrame = thisFrame
					stackedImage = numpy.zeros(numpy.shape(thisFrame))
				else:
					# registered_image, footprint = astroalign.register(wind.data, firstFrame)
					transf, (source_list, target_list) = astroalign.find_transform(thisFrame, firstFrame)
					print("Translation", transf.translation)
					print("Rotation", transf.rotation)
					print("Scale", transf.scale)
					transformedData, footprint = astroalign.apply_transform(transf, thisFrame, firstFrame)
					stackedImage+= transformedData
				matplotlib.pyplot.imshow(generallib.percentiles(thisFrame, 5, 95), origin='lower')
				# Plot the sources
				"""from astropy.visualization import SqrtStretch
				from astropy.visualization.mpl_normalize import ImageNormalize
				from photutils import CircularAperture
				positions = numpy.transpose((sources['xcentroid'], sources['ycentroid']))
				apertures = CircularAperture(positions, r=7.)
				apertures.plot(color='red', lw=1.5, alpha=0.5)"""
				matplotlib.pyplot.draw()
				matplotlib.pyplot.show(block=False)
				matplotlib.pyplot.pause(0.002)
				matplotlib.pyplot.clf()
		if n>stop: break

	print(windowedFlat)
	stackedImage /= n
	stackedPlot = matplotlib.pyplot.figure(figsize=(plotWidth, plotHeight))
	if percentiles: matplotlib.pyplot.imshow(generallib.percentiles(stackedImage, plo, phi), origin='lower')
	else: matplotlib.pyplot.imshow(stackedImage , origin='lower')
	matplotlib.pyplot.draw()
	matplotlib.pyplot.show(block=True)

	# Write the stackedFrame to a FITS file
	from astropy.io import fits
	import numpy as np
	hdu = fits.PrimaryHDU(stackedImage)
	hdul = fits.HDUList([hdu])
	hdul.writeto('new1.fits', overwrite=True)
	
	sys.exit()


