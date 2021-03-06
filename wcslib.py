import numpy
import json
from astropy import wcs

class wcsSolution:

	def __init__(self):
		self.equinox = 2000.0
		self.SIPOrder = 3
		self.pixReference = (512.0, 512.0)
		self.ra = 0.0
		self.dec = 0.0 
		self.raDeg = 0.0
		self.SIP_A = numpy.zeros((3, 3))
		self.SIP_B = numpy.zeros((3, 3))
		self.SIP_AP = numpy.zeros((3, 3))
		self.SIP_BP = numpy.zeros((3, 3))
		
		self.linearTransform = [ [0.0, 0.0], [0.0, 0.0] ]
		
	def astropyLoad(self, wcsHeader):
		self.w = wcs.WCS(wcsHeader)
		print(self.w.wcs.name)
		self.w.wcs.print_contents()

	def astropyPixToWorld(self, pixel):
		pixel = [ pixel]
		world = self.w.wcs_pix2world(pixel, 0)
		return world

	def setSolution(self, equinox, refCoord, refPixel, CD):
		self.equinox = equinox
		self.raDeg = refCoord[0]
		self.dec = refCoord[1]
		# self.ra = self.raDeg
		self.ra = self.raDeg / 15.
		self.linearTransform = CD
		self.pixReference = refPixel
		
	def setSIPAvalue(self, i, j, value):
		self.SIP_A[i][j] = value
		
	def setSIPBvalue(self, i, j, value):
		self.SIP_B[i][j] = value
	
	def setSIPAPvalue(self, i, j, value):
		self.SIP_AP[i][j] = value
		
	def setSIPBPvalue(self, i, j, value):
		self.SIP_BP[i][j] = value

	def degToSex(self, world):
		ra = world[0] / 15.
		dec = world[1]
		hours = int(ra)
		minutes = (ra - int(ra)) * 60
		seconds = (minutes - int(minutes)) * 60
		
		decDegrees = int(dec)
		decMinutes = (dec - int(dec)) * 60
		decSeconds = (decMinutes - int(decMinutes)) * 60
		
		outString = "RA: %02d:%02d:%02.1f"%(hours, minutes, seconds)
		outString+= " DEC: %02d:%02d:%02.3f"%(dec, decMinutes, decSeconds)
		return outString
		
	def getSexagesimal(self):
		ra = self.ra
		hours = int(ra)
		minutes = (ra - int(ra)) * 60
		seconds = (minutes - int(minutes)) * 60
		
		dec = self.dec
		decDegrees = int(dec)
		decMinutes = (dec - int(dec)) * 60
		decSeconds = (decMinutes - int(decMinutes)) * 60
		
		outString = "RA: %2d:%2d:%2.1f"%(hours, minutes, seconds)
		outString+= " DEC: %2d:%2d:%2.3f"%(dec, decMinutes, decSeconds)
		return outString
		
	def __str__(self):
		outString = "RA: %.4f DEC: %.4f --- "%(self.ra, self.dec)
		outString+= self.getSexagesimal()
		outString+= "\nRef pixel: " + str(self.pixReference)
		outString+= "\nA" + str(self.SIP_A)
		outString+= "\nB" + str(self.SIP_B)
		outString+= "\nAP" + str(self.SIP_AP)
		outString+= "\nBP" + str(self.SIP_BP)
		return outString
		
	def getWorldSIP(self, position):
		u = position[0] - self.pixReference[0]
		v = position[1] - self.pixReference[1]
		print("u: {} v:{}".format(u, v))
		fuvArray = numpy.zeros((3, 3))
		fuvArray[0][0] = 1
		fuvArray[0][1] = v
		fuvArray[0][2] = v*v
		fuvArray[1][0] = u
		fuvArray[1][1] = u*v
		fuvArray[1][2] = u*v*v
		fuvArray[2][0] = u*u
		fuvArray[2][1] = u*u*v
		fuvArray[2][2] = u*u*v*v
		print(fuvArray)
		print(self.SIP_A)
		uprime = numpy.sum(numpy.diagonal(numpy.dot(self.SIP_A, fuvArray)))
		vprime = numpy.sum(numpy.diagonal(numpy.dot(self.SIP_B, fuvArray)))
		
		print("u': " + str(uprime)) 
		print("v': " + str(vprime)) 
		u = u + uprime
		v = v + vprime
		CD = numpy.array(self.linearTransform)
		print("CD", CD)
		pixel = numpy.array((u,v))
		world = numpy.dot(CD,pixel)
		world = (world[0] + self.raDeg, world[1] + self.dec)
		
		return (world[0], world[1])
		
	def getPixel(self, position):
		pixel = (0,0)
		u = position[0] - self.raDeg
		v = position[1] - self.dec
		#print "Incoming", u, v
		world = numpy.array((u, v))
		CD = numpy.array(self.linearTransform)
		invCD = numpy.linalg.inv(CD)
		pixel = numpy.dot(invCD, world)

		fuvArray = numpy.zeros((4, 4))
		fuvArray[0][0] = 1
		fuvArray[0][1] = v
		fuvArray[0][2] = v*v
		fuvArray[0][3] = v*v*v
		fuvArray[1][0] = u
		fuvArray[1][1] = u*v
		fuvArray[1][2] = u*v*v
		fuvArray[2][0] = u*u
		fuvArray[2][1] = u*u*v
		fuvArray[3][0] = u*u*u

		pixel[0] = pixel[0] + numpy.sum(numpy.diagonal(numpy.dot(self.SIP_AP, fuvArray)))
		pixel[1] = pixel[1] + numpy.sum(numpy.diagonal(numpy.dot(self.SIP_BP, fuvArray)))
		
		#print "Reference", self.pixReference, "offset", pixel
		pixel = pixel + self.pixReference
		return (pixel[0], pixel[1])
		
		
	def getWorldCoord(self, position):
		u = position[0] - self.pixReference[0]
		v = position[1] - self.pixReference[1]
		print("ref pixel", self.pixReference)
		#xi = CD1_1 * (x - CRPIX1) + CD1_2 * (y - CRPIX2)
        #eta = CD2_1 * (x - CRPIX1) + CD2_2 * (y - CRPIX2)
		CD = numpy.array(self.linearTransform)
		print("CD:", CD)
		pixel = numpy.array((u,v))
		print("pixel:", pixel)
		world = numpy.dot(CD,pixel)
		print(world)
		print(self.raDeg, self.dec)
		world = (world[0] + self.raDeg, world[1] + self.dec)
		print(world)
				
		return world
		
	def toJSON(self):
		jsonObject = {}
		jsonObject['equinox'] = self.equinox
		jsonObject['ra'] = self.raDeg
		jsonObject['dec'] = self.dec
		jsonObject['x_ref'] = self.pixReference[0]
		jsonObject['y_ref'] = self.pixReference[1]
		
		jsonObject['CD_1_1'] = self.linearTransform[0][0]
		jsonObject['CD_1_2'] = self.linearTransform[0][1]
		jsonObject['CD_2_1'] = self.linearTransform[1][0]
		jsonObject['CD_2_2'] = self.linearTransform[1][1]
		
		return jsonObject
