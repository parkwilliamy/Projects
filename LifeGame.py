from fltk import *

class Cell(Fl_Button):
	alive=0
	def __init__(self,x,y,w,h,label=None):
		Fl_Button.__init__(self,x,y,w,h,label)
		
	
class Grid(Fl_Double_Window):
	def butcb(self, wid):
		wid.color(FL_YELLOW)
		
	def startcb(self, wid):
		Fl.add_timeout(0.05, self.timeout)
		
	def timeout(self):
		contact=0
		born=[]
		kill=[]
		Cell.alive=0
		
		
		for row in range(len(self.bl)):
			for column in range(len(self.bl)):
				if self.bl[row][column].color()==95:
					contact=0
					Cell.alive+=1
					
					try:
						for r,c in self.area:
							
							if self.bl[row+r][column+c].color()==FL_YELLOW:
									contact+=1
									
					except:
						continue
						
					
								
					if contact < 2 or contact >= 4:
						kill.append(self.bl[row+r][column+c]) #adds the cell to be killed
					
				
				
				else:
					contact=0
					
					try:
						for r,c in self.area:
							
							if self.bl[row+r][column+c].color()==FL_YELLOW:
								contact+=1
								
					except:
						continue
						
					if contact == 3:
						born.append(self.bl[row+r][column+c])
					
				
			for cell in born:
					cell.color(FL_YELLOW)
					cell.redraw()
							
			
				
			for cell in kill:
				cell.color(FL_BACKGROUND_COLOR)
				cell.redraw()
				
				
			if Cell.alive > 0:
				Fl.repeat_timeout(0.05, self.timeout)
			
		
		
	def __init__(self,x,y,w,h,label=None):
		Fl_Double_Window.__init__(self, x, y, w, h, label)
		self.area=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
		self.width=10
		self.bl=[]
		self.begin()
		
		for y in range(80):
			self.xcord=[]
			for x in range(80):
				self.but=Cell(x*self.width, y*self.width, self.width,self.width)
				self.xcord.append(self.but)
				self.xcord[-1].callback(self.butcb)
				
				
			
			self.bl.append(self.xcord)
				
				
		self.startbut=Cell(800,0,200,80, 'Start')
		self.startbut.callback(self.startcb)
		
		self.end()
		self.show()
		
		
x=Fl.w()//2-400
y=Fl.h()//2-400	
w=1000
h=800		

	
game=Grid(x,y,w,h)

Fl_scheme('gltk+')

Fl.run()
#if cell touches less than 2 cells, dies
#if cell touches 2 or 3 cells, lives
#if cell touches 4 or more cells, dies
#if empty space touches 3 or more cells, born
