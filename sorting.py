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

	# quick Sort
	# partitionMethod == 0: Leftmost Elem. as Pivot;
	# partitionMethod == 1: Middle Elem. as Pivot;
	def quickSort (self, arr, left, right, partitionMethod):
		if partitionMethod == 0:
			pivot = arr[left]
		else:
			pivot = arr[(left + right) // 2]

		d = left
		u = right

		while d <= u and self.isRunning:
			while arr[d] < pivot: d += 1
			while arr[u] > pivot: u -= 1

			if d <= u:
				arr[d], arr[u] = arr[u], arr[d]
				self.updateGraph(arr)

				d += 1
				u -= 1

		if left < u:
			self.quickSort (arr, left, u, partitionMethod)
		if d < right:
			self.quickSort (arr, d, right, partitionMethod)

	# insertion Sort;
	def insertionSort (self, arr):
		for i in range (1, len(arr)):
			pivot = arr[i]
			j = i - 1

			while j >= 0 and arr[j] > pivot and self.isRunning:
				arr[j + 1] = arr[j]
				j -= 1

				self.updateGraph(arr)

			arr[j + 1] = pivot
			self.updateGraph(arr)

	# shell Sort (Papernov/Stasevic's approach);
	def shellSort (self, arr):
		cols = [63, 31, 15, 7, 3, 1]

		for k in range (len(cols)):
			h = cols[k]
			for i in range (h, len(arr)):
				pivot = arr[i]
				j = i

				while j >= h and arr[j - h] > pivot and self.isRunning:
					arr[j] = arr[j - h]
					j -= h

					self.updateGraph(arr)

				arr[j] = pivot
				self.updateGraph(arr)

	# selection Sort;
	def selectionSort (self, arr):
		for i in range (len(arr) - 1):
			min_Index = i
			for j in range (i + 1, len(arr)):
				if arr[j] < arr[min_Index]:
					min_Index = j

			if self.isRunning == False:
				return

			arr[i], arr[min_Index] = arr[min_Index], arr[i]
			self.updateGraph(arr)

	# Core method of heap Sort;
	def maxHeapify (self, arr, heapSize, i):
		newRoot = i
		leftChild = (2 * i) + 1
		rightChild = (2 * i) + 2

		if leftChild < heapSize and arr[leftChild] > arr[newRoot]:
			newRoot = leftChild

		if rightChild < heapSize and arr[rightChild] > arr[newRoot]:
			newRoot = rightChild

		if newRoot != i:
			arr[i], arr[newRoot] = arr[newRoot], arr[i]
			self.updateGraph(arr)
			self.maxHeapify(arr, heapSize, newRoot)

	# Auxiliary method to create a max Heap;
	def buildMaxHeap (self, arr):
		for i in range ((len(arr) // 2) - 1, -1, -1):
			self.maxHeapify(arr, len(arr), i)

	# heap Sort;
	def heapSort (self, arr):
		self.buildMaxHeap (arr)

		for i in range (len(arr) - 1, -1, -1):
			if self.isRunning == False:
				return

			arr[0], arr[i] = arr[i], arr[0]
			self.updateGraph(arr)
			self.maxHeapify(arr, i, 0)

	# Core method of merge Sort;
	def merge (self, arr, leftIndex, middleIndex, rightIndex):
		leftListSize = middleIndex - leftIndex + 1
		rightListSize = rightIndex - middleIndex

		leftList = []
		rightList = []

		for i in range (leftListSize):
			leftList.append(arr[leftIndex + i])

		for j in range (rightListSize):
			rightList.append(arr[middleIndex + 1 + j])

		v1_Index = v2_Index = 0
		m_Index = leftIndex

		while v1_Index < leftListSize and v2_Index < rightListSize and self.isRunning:
			if leftList[v1_Index] <= rightList[v2_Index]:
				arr[m_Index] = leftList[v1_Index]
				v1_Index += 1
				self.updateGraph(arr)
			else:
				arr[m_Index] = rightList[v2_Index]
				v2_Index += 1
				self.updateGraph(arr)
			m_Index += 1

		while v1_Index < leftListSize and self.isRunning:
			arr[m_Index] = leftList[v1_Index]
			v1_Index += 1
			m_Index += 1
			self.updateGraph(arr)

		while v2_Index < rightListSize and self.isRunning:
			arr[m_Index] = rightList[v2_Index]
			v2_Index += 1
			m_Index += 1
			self.updateGraph(arr)

	# merge Sort;
	def mergeSort (self, arr, leftIndex, rightIndex):
		if leftIndex < rightIndex:
			middleIndex = (leftIndex + rightIndex) // 2
			self.mergeSort(arr, leftIndex, middleIndex)
			self.mergeSort(arr, middleIndex + 1, rightIndex)
			self.merge(arr, leftIndex, middleIndex, rightIndex)