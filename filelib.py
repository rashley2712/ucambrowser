class loggerClass():
	def __init__(self, filename="log.dat"):
		self.filename = filename

	def open(self):
		self.filehandle = open(self.filename, 'wt')

	def close(self):
		self.filehandle.close()

	def write(self, line):
		self.filehandle.write(line)