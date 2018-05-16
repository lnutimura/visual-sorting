class Sorter ():
	# Receives the reference to the variable 'app'
	# from main.py;
	def __init__ (self, app, plotWidget):
		self.app = app
		self.plotWidget = plotWidget

		# Control variable.
		# Every sorting algorithm checks this var's value because the
		# user can stop the processing at any time by clicking the "Stop" button;
		self.isRunning = False

	# Control method used to set the variable isRunning;
	def startAlgorithm (self): 
		self.isRunning = True

	# Control method used to reset the variable isRunning;
	def stopAlgorithm (self): 
		self.isRunning = False

	# Updates the graph using the 'app' and 'plotWidget';
	def updateGraph (self, data):
		self.plotWidget.plot(data, pen=None, symbolBrush=(255,0,0), clear=True)
		self.app.processEvents()

	# unflagged Bubble Sort;
	def unflaggedBubbleSort (self, arr):
		for i in range (len(arr) - 1):
			for j in range (len(arr) - 1 - i):
				if self.isRunning == False:
					return

				if arr[j] > arr[j + 1]:
					arr[j], arr[j + 1] = arr[j + 1], arr[j]
					self.updateGraph(arr)

	# flagged Bubble Sort (Optimized version of the Unflagged Bubble Sort);
	def flaggedBubbleSort (self, arr):
		swapped = True
		for i in range(len(arr) - 1):
			if swapped:
				swapped = False
				for j in range(len(arr) - 1 - i):
					if self.isRunning == False:
						return

					if arr[j] > arr[j + 1]:
						swapped = True
						arr[j], arr[j + 1] = arr[j + 1], arr[j]
						self.updateGraph(arr)