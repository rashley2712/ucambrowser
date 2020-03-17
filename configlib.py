import inspect, re

def parseValue(value):
	""" Determines if the value is a float, int or a string and returns it.
	"""
	result = None
	if '.' in value:     # If the value contains a '.' treat it as a float
		try:
			result = float(value)
			return result
		except ValueError:
			result = str(value)
			return result
	else:  # Otherwise, try to parse it as an integer
		try:
			result = int(value)
			return result
		except ValueError:
			result = str(value)
			return result
	
	return result


class configClass():
	def __init__(self, debug = False):
		self.debug = debug
		self.comments = ""
		self.settings = []
		self._loaded = False
		
	def show(self):
		for s in self.settings:
			print(s)
		
	def addSetting(self, name, type):
		self.settings[name] = "test"

	def setProperty(self, name, value):
		setattr(self, name, value)

	def setProperties(self, properties):
		for key in properties.keys():
			setattr(self, key, properties[key])
			if self.debug: print("Setting:", key, properties[key])


	def listProperties(self):
		properties = self.__dict__.keys()
		usableProperties = []
		for p in properties:
			if p[0] == '_': continue
			usableProperties.append(p)
		return usableProperties

	def showProperties(self):
		properties = self.__dict__.keys()
		usableProperties = []
		for p in properties:
			if p[0] == '_': continue
			usableProperties.append(p)
		
		retString = ""
		for p in usableProperties:
			retString+= p + " " + str(getattr(self, p)) + "\n"
		
		return retString

	def loadSetting(self, setting, original):
		fields = original.split()
		if self.debug: print("loading setting: ", setting['name'])
		try:
			if setting['type'] == "string":
				setattr(self, setting['name'], original[len(setting['name'])+1:])
			if setting['type'] == "tuple":
				setattr(self, setting['name'], (float(fields[1]), float(fields[2])))
			if setting['type'] == "integer":
				setattr(self, setting['name'], int(fields[1]))
			if setting['type'] == "float":
				setattr(self, setting['name'], float(fields[1]))
			if setting['type'] == 'boolean':
				if fields[1].upper() == "TRUE":
					setattr(self, setting['name'], True)
				else:
					setattr(self, setting['name'], False)
			if setting['type'] == "label":
				if hasattr(self, 'label'):
					print("label already exists!")
					if not hasattr(self, 'labels'): self.labels = []
					self.labels.append(self.label)
					print("Current label", self.label)
					multipleLabels = True
				else:
					multipleLabels = False
				labelObject = {}
				labelObject['x'] = float(fields[1])
				labelObject['y'] = float(fields[2])
				text = ""
				for piece in fields[3:]:
					text+=piece + " "
				labelObject['text'] = text
				print(labelObject)
				setattr(self, setting['name'], labelObject)
				if multipleLabels:
					print("Adding to ", self.labels)
					self.labels.append(labelObject)
					 
		except ValueError:
			print("Warning: Could not read the setting for: %s"%(setting['name']))

		return setting

	def read(self, name):
		for s in self.settings:
			if s['name'] == name: return s

	def load(self, filename):
		try:
			fileHandle = open(filename, 'rt')
		except FileNotFoundError:
			print("Could not open config file %s"%filename)
			return

		allComments = ""
		for lineNumber, line in enumerate(fileHandle):
			line = line.strip()
			if len(line) == 0: continue
			if line[0] == '#':
				comments = line.split('#')[1]
				allComments+= "%d: %s\n"%(lineNumber, comments.strip())
				continue
			commentSplit = line.split('#')
			if len(line.split('#'))>1: 
				comments = commentSplit[1]
				allComments+= "%d: %s\n"%(lineNumber, comments.strip())
			parameter = commentSplit[0].split()[0]
			values = commentSplit[0][len(parameter):]
			if self.debug:
				print("Parameter:", parameter)
				print("Values:", values)
			# Get anything in quotes
			quotedStuff = re.findall('"([^"]*)"', values)
			if len(quotedStuff)>0: 
				value = quotedStuff[0]
				setattr(self, parameter, value)
				continue
			values = values.strip()
			countValues = len(values.split())
			if countValues>1:
				valuesArray = []
				values = values.split()
				for v in values:
					valuesArray.append(parseValue(v))
				if self.debug: print("setting {} to {}".format(parameter, valuesArray))
				setattr(self, parameter, valuesArray)
				continue
			
			setattr(self, parameter, parseValue(values))
			
		fileHandle.close()

		self.comments = allComments
		if self.debug: print("Comments:\n" + str(self.comments))
		self._loaded = True
