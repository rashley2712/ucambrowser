

def extractSources(data):
	""" Extracts sources from a raw data array
	"""
	from astropy.stats import sigma_clipped_stats	
	from photutils import datasets
	mean, median, std = sigma_clipped_stats(data, sigma=3.0)  
	print("Mean {}, median {}, std {}".format(mean, median, std))
	from photutils import DAOStarFinder
	daofind = DAOStarFinder(fwhm=3.0, threshold=4.*std)  
	sources = daofind(data - median)  
	for col in sources.colnames:
		sources[col].info.format = '%.8g'  # for consistent table output
	return sources   


class sourceClass():
	def __init__(self, debug = False):
		self.debug = debug
		
