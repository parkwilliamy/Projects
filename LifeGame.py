from fltk import *

class Cell(Fl_Button):
	alive=0
	def __init__(self,x,y,w,h,label=None):
		Fl_Button.__init__(self,x,y,w,h,label)
		
	
class Grid(Fl_Window):
	def butcb(self, wid):
		wid.color(FL_YELLOW)
		
	def startcb(self, wid):
		contact=0
		boo=True
		while boo==True:
			for z in range(len(self.bl)):
				if self.bl[z].color()==95:
					Cell.alive+=1
					for a in self.touch:
						if z+a < 0 or z+a > 6400:
							continue
						if self.bl[z+a].color()==FL_YELLOW:
							contact+=1
							
					if contact < 2:
						self.bl[z].color(FL_BACKGROUND_COLOR)
						self.bl[z].redraw()
						Cell.alive=Cell.alive-1
					elif contact >= 4: 
						self.bl[z].color(FL_BACKGROUND_COLOR)
						self.bl[z].redraw()
						Cell.alive=Cell.alive-1
						
				else:
					for a in self.touch:
						if z+a < 0 or z+a > 6400 or z+a == 6321:
							continue
						if self.bl[z+a].color()==FL_YELLOW:
							contact+=1
							
					if contact >= 3:
						self.bl[z].color(FL_YELLOW)
						self.bl[z].redraw()
						Cell.alive+=1
			
			print(Cell.alive)
			if Cell.alive==0:
				boo=False
			
		
						
					
				
					
					
				
				
		
				
		
				
				
	def __init__(self,x,y,w,h,label=None):
		Fl_Window.__init__(self, x, y, w, h, label)
		self.touch=[-80,80,-1,1,-81,-79,79,81]
		self.width=10
		self.bl=[]
		self.begin()
		
		for y in range(80):
			for x in range(80):
				self.but=Cell(x*self.width, y*self.width, self.width,self.width)
				self.bl.append(self.but)
				self.bl[-1].callback(self.butcb)
				
		self.startbut=Cell(800,0,200,80, 'Start')
		self.startbut.callback(self.startcb)
		
		self.end()
		self.show()
		
		
x=Fl.w()//2-400
y=Fl.h()//2-400	
w=1000
h=800		

	
game=Grid(x,y,w,h)

Fl.run()
#if cell touches less than 2 cells, dies
#if cell touches 2 or 3 cells, lives
#if cell touches 4 or more cells, dies
#if empty space touches 3 or more cells, born
