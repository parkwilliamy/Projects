from fltk import *
import random

class MineSweeper(Fl_Window):
	def __init__(self,x,y,w,h,label=None):
		Fl_Window.__init__(self, x, y, w, h, label)
		self.running=True
		self.sec=0 #first number on the clock
		self.tens=0 #second number on the clock
		self.min=0 #third number on the clock
		self.tmin=0 #fourth number on the clock
		self.time=0 #time shown
		self.blank=[] #list of blank squares
		self.on=[] #list of squares shown
		self.marked=[] #list of marked flags
		self.countbuts=[] #list of squares touching at least one mine
		self.mnums=[] #list of labels for each button in countbuts
		self.randnum=-1 #used to randomly place mines
		self.randnum2=-1 #used to randomly place mines
		self.usednums=[] #list of used coords for placing mines
		self.grid=[] #2D list of all the squares
		self.width=50
		self.mines=[]
		self.area=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)] #used to find area around blank squares
		
		self.begin()
		
		self.label('Time: 00:00')
		
		for y in range(10):
			self.yrow=[]
			for x in range(10):
				self.but=Fl_Button(x*self.width, y*self.width, self.width,self.width)
				if y%2==0:
					if x%2==0:
						self.but.color(111,69)
					else:
						self.but.color(110,69)
					
				if y%2==1:	
					if x%2==1:
						self.but.color(111,69)
					else:
						self.but.color(110,69)	
					
				self.yrow.append(self.but) #adds the xth square to the yth row
				self.but.callback(self.butcb)
				
				
			self.grid.append(self.yrow) #adds the xth row to the grid
				
		self.end()
		self.resizable(self)
	
	'''FUNCTION TO FIND INDICES OF ITEMS IN 2D LIST (like using list.index(element), but for 2d lists'''
	def index2d(self, L, v):
		for i, x in enumerate(L):
			if v in x:
				return (i, x.index(v))
	
	
	'''RECURSIVE FUNCTION FOR BLANK SQUARES'''
	def checkarea(self, wid): #checks squares around a blank square, uses flood fill algorithm
		i=self.index2d(self.grid, wid)
		row=i[0]
		column=i[1]
		
		for r,c in self.area:
			contact=False
			
			if row+r < 0 or row+r > 9 or column+c < 0 or column+c > 9: #edge cases
				continue	
				
					
			if self.grid[row+r][column+c] in self.blank and self.grid[row+r][column+c] not in self.on:
				self.grid[row+r][column+c].label('')
				contact=True
			
				
			elif self.grid[row+r][column+c] in self.countbuts and self.grid[row+r][column+c] not in self.on:
				self.grid[row+r][column+c].label(self.mnums[self.countbuts.index(self.grid[row+r][column+c])])
				self.grid[row+r][column+c].labelsize(40)
				self.grid[row+r][column+c].color(174,115)
				self.on.append(self.grid[row+r][column+c])
						
			if contact == False:
				continue
				
			self.on.append(self.grid[row+r][column+c])
			self.grid[row+r][column+c].color(174,115)
			self.checkarea(self.grid[row+r][column+c])
			
		self.redraw()
		
		
	def gameend(self, win):
		if win==True:
			fl_message(f'You won in a time of {self.time}!')
		else:
			fl_message('You lost!')
		
	'''TIMER FUNCTION'''
	def timer(self):
		if self.running==True:
			self.time=(f'{self.tmin}{self.min}:{self.tens}{self.sec}')
			self.label(f'Time: {self.time}')
			
			self.sec=self.sec+1
			
			if self.min==10:
				self.min=0
				self.tens=0
				self.tmin+=1
				
			
			if self.tens==6:
				self.tens=0
				self.sec=0
				self.min+=1
			
			if self.sec%10==0 and self.sec != 0:
				self.tens=self.tens+1
				self.sec=0
			
			
			Fl.add_timeout(1, self.timer)
		

	'''CALLBACK FOR EACH BUTTON (ONLY FOR OFF BUTTONS)'''
	def butcb(self, wid):
		
		if Fl.event_button() == FL_RIGHT_MOUSE:	
			
			
			if wid not in self.on and wid not in self.marked: #if square not revealed already and not marked
			
				
				self.marked.append(wid)
				wid.label('@>')
				wid.labelsize(20)
				wid.labelcolor(FL_RED)
			
			elif wid in self.marked: #if marked already, remove the marker
				wid.label('')
				self.marked.remove(wid)
			
		elif Fl.event_button() == FL_LEFT_MOUSE:
			
			if wid.label() != '@>': #if clicked square is not already revealed
			
				if wid not in self.on and wid not in self.mines: 
					wid.color(174,115)
					wid.redraw()
				
				
				if len(self.on)==0: #for first square clicked, starts the timer
					
					self.timer()
					
					self.on.append(wid)
					
					clickidx=self.index2d(self.grid, wid) #finds X,Y location of the square just clicked
					row2=clickidx[0] #Y location of square clicked
					column2=clickidx[1] #X location of square clicked
					bsquares=[self.grid[row2][column2]] #adds the square to blank squares
					
					for r,c in self.area:
						
						if row2+r < 0 or row2+r > 9 or column2+c < 0 or column2+c > 9: #edge cases for square clicked near borders 
							continue
							
						bsquares.append(self.grid[row2+r][column2+c]) #all squares directly touching the FIRST clicked square are safe
					
					
					for x in range(10):
						while (self.randnum,self.randnum2) in self.usednums or self.grid[self.randnum][self.randnum2] in bsquares:
							self.randnum=random.randrange(10)
							self.randnum2=random.randrange(10)
						
						self.usednums.append((self.randnum,self.randnum2)) #ensures no square is repeated for mine placement
						self.mines.append(self.grid[self.randnum][self.randnum2])
						
					for row in range(len(self.grid)):
						for column in range(len(self.grid)):
							if self.grid[row][column] not in self.mines:
								
								contact=0 #number of mines touching a square
								
								for r,c in self.area: 
									
									if row+r < 0 or row+r > 9 or column+c < 0 or column+c > 9: #edge cases
										continue
										
									if self.grid[row+r][column+c] in self.mines: #if a space is touching a mine
										contact+=1
								
								
								if contact == 0:
									self.blank.append(self.grid[row][column])
									continue
									
									
								self.countbuts.append(self.grid[row][column])			
								#self.grid[row][column].label(str(contact))
								self.mnums.append(str(contact))
								
								if contact == 1:
									self.grid[row][column].labelcolor(FL_RED)
								
								if contact == 2:
									self.grid[row][column].labelcolor(FL_DARK_GREEN)
									
								if contact == 3:
									self.grid[row][column].labelcolor(FL_BLUE)	
								
								if contact == 4:
									self.grid[row][column].labelcolor(FL_YELLOW)	
	
					
				if wid in self.blank: #if clicked square is blank
					if len(self.on) > 1: #if this is NOT the first square clicked
						self.on.append(wid)
						
					self.checkarea(wid)
					wid.when(0)
					
				elif wid in self.countbuts and wid not in self.on: #if clicked square is numsquare
					
					wid.label(self.mnums[self.countbuts.index(wid)])
					wid.labelsize(40)
					self.on.append(wid)				
					wid.when(0)
							
				if len(self.on) == 90: 
						for x in self.mines:
							x.label('@circle')
							x.labelcolor(FL_WHITE)
							x.labelsize(25)
							
						for row in range(len(self.grid)):
							for column in range(len(self.grid)):
								self.grid[row][column].when(0)	
						
						win=True	
						self.running=False
						Fl.add_timeout(1.5, self.gameend, win)	
				
				elif wid in self.mines: #if clicked square is a mine
					for x in self.mines:
						x.label('@circle')
						x.labelcolor(FL_RED)
						x.labelsize(25)
						
					for y in self.marked:
						if y not in self.mines:
							y.label('@undo')
							
					for row in range(len(self.grid)):
						for column in range(len(self.grid)):
							self.grid[row][column].when(0)
								
						
					win=False	
					self.running=False
					Fl.add_timeout(1.5, self.gameend, win)
		
		
			
x=Fl.w()//2-250
y=Fl.h()//2-250
w=500
h=500

game=MineSweeper(x,y,w,h, 'MineSweeper')
game.show()
Fl_scheme('gltk')
Fl.run()
