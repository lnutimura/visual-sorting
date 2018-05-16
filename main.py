# Personal Project;
# @author: lnutimura;
from pyqtgraph import QtGui, QtCore
from sorting import Sorter

import sys
import numpy as np
import pyqtgraph as pg

class VisualSorting (QtGui.QWidget):
	def __init__ (self):
		self.app = QtGui.QApplication(sys.argv)

		# Initializes the:
		# 	- The data that will be sorted;
		#	- The plot that will display the sorting process;
		#	- The sorter that contains all the sorting algorithms;
		#	Note:
		#	  Because the 'Sorter' class is from another file (sorting.py),
		#	  this instance needs references to both 'app/plotWidget' variables to update
		#	  the graph in real-time (through calls in the middle of the sorting algorithms);

		self.data = []
		self.plotWidget = None
		self.sorter = None

		super(VisualSorting, self).__init__()
		self.initUI()

	def initUI (self):
		horizontalLayout = QtGui.QHBoxLayout()
		verticalLayout = QtGui.QVBoxLayout()

		# Menu ----------------------------------
		# Creates the first groupBox to hold all the radioButtons;
		groupBox1 = QtGui.QGroupBox('Algorithms')
		groupBox1Layout = QtGui.QVBoxLayout()
		groupBox1.setLayout(groupBox1Layout)
		# radioButtons;
		self.bubbleSort_RBtn1 = QtGui.QRadioButton('Unflagged BubbleSort')
		self.bubbleSort_RBtn2 = QtGui.QRadioButton('Flagged BubbleSort')

		# Creates the second groupBox to hold all the pushButtons;
		groupBox2 = QtGui.QGroupBox('Execution')
		groupBox2Layout = QtGui.QVBoxLayout()
		groupBox2.setLayout(groupBox2Layout)
		# pushButtons;
		startBtn = QtGui.QPushButton('Start')
		stopBtn = QtGui.QPushButton('Stop')

		# Plot Area -----------------------------
		# Creates the plotWidget that will display the data being sorted;
		self.initPlot()

		# Adds all the Widgets and Layouts;
		groupBox1Layout.addWidget(self.bubbleSort_RBtn1)
		groupBox1Layout.addWidget(self.bubbleSort_RBtn2)
		groupBox2Layout.addWidget(startBtn)
		groupBox2Layout.addWidget(stopBtn)
		verticalLayout.addWidget(groupBox1)
		verticalLayout.addWidget(groupBox2)
		verticalLayout.addStretch()
		horizontalLayout.addLayout(verticalLayout)
		horizontalLayout.addWidget(self.plotWidget)

		# Adds all the Events;
		startBtn.clicked.connect(self.clickedStart)
		stopBtn.clicked.connect(self.clickedStop)

		# Sets the main window;
		self.setLayout(horizontalLayout)
		self.setGeometry(100, 100, 800, 600)
		self.setWindowTitle('VisualSorting')

		# Checks a default sorting algorithm;
		self.bubbleSort_RBtn1.setChecked(True)

		self.show()
		sys.exit(self.app.exec_())

	# Initializes the data (with random values);
	def initData (self):
		self.data = np.random.randint(100, size=100)

	# Initializes all the plot-related stuff;
	def initPlot (self):
		self.initData()

		# Initializes the plotWidget
		self.plotWidget = pg.PlotWidget()

		# Initializes the instance of Sorter with app/plotWidget;
		self.sorter = Sorter(self.app, self.plotWidget)

	# Resets the graph for a new sorting;
	def resetGraph (self):
		self.initData()
		self.plotWidget.plot(self.data, pen=None, symbolBrush=(255,0,0), clear=True)

	# startBtn's function;
	def clickedStart (self):
		# Prepares the sorting by setting the
		# Sorter's control variable;
		self.sorter.startAlgorithm()

		# Generates new random data and
		# draw the new graph;
		self.resetGraph()

		# Checks the active radioButton and
		# calls the respective method;
		if self.bubbleSort_RBtn1.isChecked() == True: self.sorter.unflaggedBubbleSort(self.data)
		elif self.bubbleSort_RBtn2.isChecked() == True: self.sorter.flaggedBubbleSort(self.data)

	# stopBtn's function;
	def clickedStop (self):
		# Stops the sorting by resetting the
		# Sorter's control variable;
		self.sorter.stopAlgorithm()



if __name__ == '__main__':
	visualSorting = VisualSorting()