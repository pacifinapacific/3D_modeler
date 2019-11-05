import sys
 
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox,QSlider, QWidget, QPushButton,QGridLayout,QLineEdit
from PyQt5.QtGui import QIcon
 
 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QCursor
import numpy as np
import math
 
from visualize import read_obj
from smpl_controller import Make_SMPL



class MyWindow(QMainWindow):

	def __init__(self):

		super(MyWindow, self).__init__()
		self.title="visualize_smpl"
		self.top=0
		self.left=0
		self.width=1500
		self.height=1000
		self.slider_value=np.ones((24,3))*50
		print(np.shape(self.slider_value))
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update)
		self.timer.start(100)

 
		self.m = PlotCanvas(self, width=5, height=4)
		self.m.move(0,0)

		#self.m.mpl_connect('button_press_event', self.mousePressEvent)
		#self.m.mpl_connect('button_release_event', self.mouseReleaseEvent)

		self.startCursorPos = QPoint(0, 0)
		self.isDragging = False
		self.elev = 0
		self.azim =0

		self.pose_slider_widgets = [ [None for j in range(3)] for i in range(24) ]
		for j in range(24):
			for i in range(3):
				self.pose_slider_widgets[j][i]=QSlider(Qt.Horizontal,self)
				#print((j//8))
				self.pose_slider_widgets[j][i].setGeometry(100+(j//8)*450+i*110,400+(45)*(j%8),100,100)
				self.pose_slider_widgets[j][i].setValue(50)

		#grid=QGridLayout()
		#self.setLayout(grid)
		#grid.addWidget(QSlider(Qt.Horizontal),10,10)

		#self.slider=QSlider(Qt.Horizontal,self)
		#self.slider.setGeometry(500,100,100,100)
		#self.slider.valueChanged.connect(self.changeValue)
		#self.grid.move(600,500)
		self.label_widgets=[ [None for j in range(3)] for i in range(3) ]
		for j in range(3):
			for i in range(3):
				self.label_widgets[j][i]=QLineEdit(self)
				if i%3==0:
					self.label_widgets[j][i].setText("X_Rotate")
					self.label_widgets[j][i].setGeometry(100+450*(j%3),400,80,30)
				elif i%3==1:
					self.label_widgets[j][i].setText("Y_Rotate")
					self.label_widgets[j][i].setGeometry(100+450*(j%3)+120,400,80,30)
				else:
					self.label_widgets[j][i].setText("Z_Rotate")
					self.label_widgets[j][i].setGeometry(100+450*(j%3)+220,400,80,30)


		for j in range(24):
			for i in range(3):
				#self.pose_slider_widgets[j][i].valueChanged.connect(self.changeValue)#(lambda:self.changeValue(self.pose_slider_widgets[j][i].value(),j,i))
				self.pose_slider_widgets[j][i].valueChanged.connect(lambda value,segment=(j,i):self.changeValue(value,segment))

		#self.label_widget.setText("0")
		#self.label = QLineEdit(self)
		#self.label.setText("0")
		#self.label.setGeometry(600,100,30,30)

		#self.move(500,200) 
		self.fresh_button = QPushButton('Refresh SMPL', self)
		self.fresh_button.clicked.connect(lambda:self.m.refresh(self.slider_value))
		self.fresh_button.setToolTip('This s an example button')
		self.fresh_button.setGeometry(500,0,140,100)


		#self.change_button = QPushButton('Chabge Slider', self)
		#self.change_button.clicked.connect(self.change_slider)
		#self.fresh_button.clicked.connect(lambda:self.m.refresh(self.slider_value))
		#self.change_button.setToolTip('This s an example button')
		#self.change_button.setGeometry(500,200,140,100)
		#button.resize(140,100)
 
		self.show()

	def paintEvent(self, event):
		if self.isDragging:
			diff = QCursor.pos() - self.startCursorPos
			self.m.ax.view_init(self.elev + diff.y(), self.azim - diff.x())
			self.m.draw()


	def mousePressEvent(self, event):
		if event.button == Qt.LeftButton:
			self.startCursorPos = QCursor.pos()
			self.isDragging = True

	def mouseReleaseEvent(self, event):
		if event.button == Qt.LeftButton:
			diff = QCursor.pos() - self.startCursorPos
			self.elev += diff.y()
			self.azim -= diff.x()
			self.update()
			self.isDragging = False
	def changeValue(self,value,segment):
		#print(self.sender().value())
		#print(j)
		#print(i)
		#self.label.setText(str(value)
		#print(segment[0],segment[1],value)
		self.slider_value[segment[0]][segment[1]]=value
		#print(self.slider_value)
		#print(self.slider_value[j][i])


class PlotCanvas(FigureCanvas):
 
	def __init__(self, parent=None, width=4, height=3, dpi=100):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.ax = Axes3D(fig)
		#self.ax = plt.axes(projection='3d')
		self.smpl_model=Make_SMPL("model.pkl")
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
		smpl_pose_shape=[24,3]
		smpl_beta_shape=[10]
		smpl_trans_shape=[3]
		#self.pose = (np.random.rand(*smpl_pose_shape) - 0.5) * 0.4
		#self.beta = (np.random.rand(*smpl_beta_shape) - 0.5) * 0.06
		self.pose=np.zeros((24,3))
		self.beta=np.zeros((10))
		self.trans = np.zeros(smpl_trans_shape)
		self.num=0
 
		FigureCanvas.setSizePolicy(self,
				QSizePolicy.Expanding,
				QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.plot()
 

 
	def plot(self):
		vertices,triangles=read_obj("smpl_np.obj")
		x = vertices[:,0]
		y = vertices[:,1]
		z = vertices[:,2]


		self.ax.set_xlim([-1, 1])
		self.ax.set_ylim([-1, 1])
		self.ax.set_zlim([-1, 1])
		self.ax.set_xlabel('$X$', fontsize=10)
		self.ax.set_ylabel('$Y$')
		self.ax.set_zlabel('$Z$', fontsize=10)
		self.ax.plot_trisurf(x, z, triangles, y, shade=True, color='white')
		self.ax.set_title('PyQt Matplotlib Example')
		#plt.show()
		self.draw()

	def refresh(self,value):
		self.ax.cla()
		#print(value)
		value_norm=(value/50)-1 #-1~1
		self.num+=1
		#value_norm=100
		#print(value_norm)
		rotation=math.pi*value_norm/2
		#print(rotation)
		self.pose=rotation
		self.smpl_model.create_smpl(self.beta,self.pose,self.trans,self.num)
		vertices,triangles=read_obj("smpl_np{}.obj".format(self.num))


		self.ax.set_xlim([-1, 1])
		self.ax.set_ylim([-1, 1])
		self.ax.set_zlim([-1, 1])

		self.ax.set_xlabel('$X$', fontsize=10)
		self.ax.set_ylabel('$Y$')
		self.ax.set_zlabel('$Z$', fontsize=10)
		x = vertices[:,0]
		y = vertices[:,1]
		z = vertices[:,2]
		self.ax.plot_trisurf(x, z, triangles, y, shade=True, color='white')
		self.draw()







if __name__ == '__main__':

	app = QApplication(sys.argv)
	w = MyWindow()
	app.exec_()