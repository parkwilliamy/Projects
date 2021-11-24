from fltk import *

class Cell(Fl_Button):
	alive=False
	def __init__(self,x,y,w,h,label=None):
		Fl_Button.__init__(self,x,y,w,h,label)
		
	
class Grid(Fl_Double_Window):
	
	running=False
	
	
	'''Creates the cells'''
	def butcb(self, wid):
		wid.color(FL_BLUE)
		Cell.alive=True
		self.startbut.activate()
		if Grid.running==False:
			self.lexbut.deactivate()
	
	'''Start button'''	
	def startcb(self, wid):
		wid.label('Pause')
		Grid.running=Cell.alive
		self.clicks+=1
		if self.clicks % 2 == 0:
			self.pausecb()
			Grid.running=False
		contact=0
		born=[]
		kill=[]
		livecells=[]
		
		while Cell.alive == True:
			born=[]
			kill=[]
			livecells=[]
			for row in range(len(self.bl)):
				for column in range(len(self.bl)):
					
					if self.bl[row][column].color()==216:
						
						contact=0
						livecells.append(self.bl[row][column])
						
						
						for r,c in self.area:
							
							if row+r < 0 or row+r > 79 or column+c < 0 or column+c > 79:
								continue
								
							if self.bl[row+r][column+c].color()==216:
								contact+=1
									
										
										
						if contact < 2 or contact >= 4:
							kill.append(self.bl[row][column]) #adds the cell to be killed
							
						
					else:
						contact=0
						
						
						
						for r,c in self.area:
							
							if row+r < 0 or row+r > 79 or column+c < 0 or column+c > 79:
								continue
								
							if self.bl[row+r][column+c].color()==FL_BLUE:
								contact+=1	
									
						if contact == 3:
							born.append(self.bl[row][column])
									
						
			for cell in born:
				cell.color(FL_BLUE)
				
			self.redraw()
			
			
			for cell in kill:
				cell.color(FL_BACKGROUND_COLOR)
				livecells.remove(cell)
			
			self.redraw()
				
			if len(livecells) == 0:
				Cell.alive = False
				self.lexbut.activate()
				self.startbut.deactivate()
				self.pausecb()
				self.clicks=0
						
			Fl.check()	
			
	'''Pause button'''		
	def pausecb(self):
		self.startbut.label('Start')
		self.startbut.value(0)
		
	'''Clear button'''
	def clearcb(self, wid):
		Cell.alive=False
		self.clicks=0
		self.pausecb()
		self.lexbut.activate()
		self.startbut.deactivate()
		for row in range(len(self.bl)):
				for column in range(len(self.bl)):
					self.bl[row][column].color(FL_BACKGROUND_COLOR)
					
		self.redraw()
		
	'''Creates glider in middle of grid'''	
	def lexcb(self, wid):
		
		self.clearcb(wid)
		for r,c in self.lexcords:
			self.bl[r][c].color(FL_BLUE)
			
		self.redraw()
		self.startbut.activate()
		Cell.alive=True
		
	def __init__(self,x,y,w,h,label=None):
		Fl_Double_Window.__init__(self, x, y, w, h, label)
		self.area=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
		self.lexcords=[(38,40),(39,41),(40,39),(40,40),(40,41)]
		self.width=10
		self.clicks=0
		self.bl=[]
		self.begin()
		
		for y in range(80):
			self.xcord=[]
			for x in range(80):
				self.but=Cell(x*self.width, y*self.width, self.width,self.width)
				self.but.box(FL_FLAT_BOX)
				self.xcord.append(self.but)
				self.xcord[-1].callback(self.butcb)
				
			self.bl.append(self.xcord)
				
				
		self.startbut=Fl_Light_Button(800,0,200,80, 'Start')
		self.startbut.callback(self.startcb)
		self.clearbut=Fl_Button(800,100,200,80, 'Clear')
		self.clearbut.callback(self.clearcb)
		self.lexbut=Fl_Button(800,200,200,80, 'Glider')
		self.lexbut.callback(self.lexcb)
		self.startbut.deactivate()
		
		
		self.end()
		self.show()
		
		
x=Fl.w()//2-400
y=Fl.h()//2-400	
w=1000
h=800		

game=Grid(x,y,w,h)

Fl_scheme('gtk+')

Fl.run()


