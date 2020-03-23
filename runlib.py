import json


class runClass():
	def __init__(self, runID, debug = False):
		self.debug = debug
		self.runID = runID
		self.runInfo = {'runID': runID }
		self.filename = None

	def load(self):
		### Try to load myself from a JSON file
		if self.filename is None:
			self.filename = self.runID + ".json"
		print("Loading.... %s from %s"%(self.runID, self.filename))
		try:
			fileHandle = open(self.filename, 'rt')
			self.runInfo = json.load(fileHandle)
			fileHandle.close()
		except Exception as e:
			print(e)
		
	def getProperty(self, name):
		return self.runInfo[name]
		
	def save(self):
		fileHandle = open(self.filename, 'wt')
		json.dump(self.runInfo, fileHandle, indent=4)
		fileHandle.close()

		

	def addProperty(self, name, value):
		self.runInfo[name] = value
		self.__setattr__(name, value)

	def __str__(self):
		return "Run object: %s"%(self.runID)