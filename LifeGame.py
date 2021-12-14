from fltk import *
import random

#MUST BE RESIZABLE
class MineSweeper(Fl_Window):
	def __init__(self,x,y,w,h,label=None):
		Fl_Window.__init__(self, x, y, w, h, label)
		self.blank=[] #list of blank squares
		self.on=[] #list of squares shown
		self.marked=[] #list of marked flags
		self.countbuts=[] #list of squares touching at least one mine
		self.usednums=[] #list of numbers already
		self.randnum=-1
		self.randnum2=-1
		self.bl=[]
		self.width=50
		self.mines=[]
		self.area=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
		
		self.begin()
		
		for y in range(10):
			self.xcord=[]
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
					
				self.xcord.append(self.but)
				self.but.callback(self.butcb)
				
				
			self.bl.append(self.xcord)
				
		self.end()
	
	
	
	def index2d(self, L, v):
		for i, x in enumerate(L):
			if v in x:
				return (i, x.index(v))
	
	
	
	def checkarea(self, wid): #checks squares around a blank square
		i=self.index2d(self.bl, wid)
		row=i[0]
		column=i[1]
		
		for r,c in self.area:
			contact=False
			
			if row+r < 0 or row+r > 9 or column+c < 0 or column+c > 9: #edge cases
				continue	
				
					
			if self.bl[row+r][column+c] in self.blank and self.bl[row+r][column+c] not in self.on:
				contact=True
			
				
			elif self.bl[row+r][column+c] in self.countbuts and self.bl[row+r][column+c] not in self.on:
				self.bl[row+r][column+c].labelsize(40)
				self.bl[row+r][column+c].color(174,115)
				self.on.append(self.bl[row+r][column+c])
				
			if contact == False:
				continue
				
			self.on.append(self.bl[row+r][column+c])
			self.bl[row+r][column+c].color(174,115)
			self.checkarea(self.bl[row+r][column+c])
			
		self.redraw()

	
	def butcb(self, wid):
		
		if Fl.event_button() == FL_RIGHT_MOUSE:	
			
			
			if wid not in self.on and wid not in self.marked:	
			
				
				self.marked.append(wid)
				wid.label('@>')
				wid.labelsize(20)
				wid.labelcolor(FL_RED)
			
			elif wid in self.marked:
				wid.label('')
				self.marked.remove(wid)
			
		else:
			
			if wid.label() != '@>':
			
				if wid not in self.on and wid not in self.mines:
					wid.color(174,115)
					wid.redraw()
				
				
				if len(self.on)==0:
					
					self.on.append(wid)
					
					clickidx=self.index2d(self.bl, wid)
					row2=clickidx[0]
					column2=clickidx[1]
					bsquares=[self.bl[row2][column2]]
					
					for r,c in self.area:
						
						if row2+r < 0 or row2+r > 9 or column2+c < 0 or column2+c > 9: #edge cases
							continue
							
						bsquares.append(self.bl[row2+r][column2+c])
					
					
					for x in range(10):
						while (self.randnum,self.randnum2) in self.usednums or self.bl[self.randnum][self.randnum2] in bsquares:
							self.randnum=random.randrange(10)
							self.randnum2=random.randrange(10)
						
						self.usednums.append((self.randnum,self.randnum2))
						self.mines.append(self.bl[self.randnum][self.randnum2])
						
					for row in range(len(self.bl)):
						for column in range(len(self.bl)):
							if self.bl[row][column] not in self.mines:
								
								contact=0
								
								for r,c in self.area: 
									
									if row+r < 0 or row+r > 9 or column+c < 0 or column+c > 9: #edge cases
										continue
										
									if self.bl[row+r][column+c] in self.mines: #if a space is touching a mine
										contact+=1
								
								
								if contact == 0:
									self.blank.append(self.bl[row][column])
									continue
									
									
								self.countbuts.append(self.bl[row][column])			
								self.bl[row][column].label(str(contact))
								
								if contact == 1:
									self.bl[row][column].labelcolor(FL_RED)
								
								if contact == 2:
									self.bl[row][column].labelcolor(FL_DARK_GREEN)
									
								if contact == 3:
									self.bl[row][column].labelcolor(FL_BLUE)	
								
								if contact == 4:
									self.bl[row][column].labelcolor(FL_YELLOW)	
								
								self.bl[row][column].labelsize(1)
	
					
				if wid in self.blank: #if clicked square is blank
					self.checkarea(wid)
					wid.when(0)
					self.on.append(wid)
					print(len(self.on))
					
				elif wid in self.countbuts and wid not in self.on: #if clicked square is numsquare
					wid.labelsize(40)
					self.on.append(wid)				
					
					wid.when(0)
					print(len(self.on))
							
				if len(self.on) == 90:
						for x in self.mines:
							x.label('')
							x.labelcolor(FL_BLACK)
							x.labelsize(25)
				
						fl_message('You win!')	
				
				elif wid in self.mines: #if clicked square is a mine
					for x in self.mines:
						x.label('@circle')
						x.labelcolor(FL_BLACK)
						x.labelsize(25)
						
					fl_message('You lose!')
		
			
x=Fl.w()//2-250
y=Fl.h()//2-250
w=500
h=500

game=MineSweeper(x,y,w,h, 'MineSweeper')
game.show()
Fl_scheme('gltk')
Fl.run()

