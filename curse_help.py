"""
Library of helper functions required to manage various curses elements.

"""
import curses

#Class representing a sequence of options rendered across a common screen.
class ScreenOptions:

	__slots__=\
	'header',\
	'options',\
	'h_c',\
	'str_c',\
	'__selected',\

	#The instance of the screen which will be shared by all objects of this type.
	screen=None
	PREVIOUS=-1

	#Set the screen which will be shared by all the instances of this class.
	@staticmethod
	def set_screen(screen):
		ScreenOptions.screen=screen

	#Manage the rendering of multiple instances of this class.
	@classmethod
	def manage_sequence(cls,screen_options):
		#The current screen-option being displayed
		current=0
		#The array of states to return for the screen options.
		states=[-1 for sco in screen_options]
		#While we have not set all states , do
		while True:
			#Get the option of the option list being rendered.
			option=screen_options[current].manager_loop(current!=0)
			#If the option was to go back...
			if option==cls.PREVIOUS:
				current-=1
			#Otherwise set the state
			else:
				states[current]=option
				#If the option of the last option list was set , return the state array
				if current==len(screen_options)-1:
					return states
				#Otherwise , goto the next option box
				current+=1

	#The constructor.
	#'header' is the header.
	#'options' is the iterable of options.
	#'coord_calculating_function' is a function which takes 3 parameters:
	#	Parameter1:the screen
	#	Parameter2:the header
	#	Parameter3:the iterable of options
	#The functions calculates the positioning of the elements on the screen.
	def __init__(self,header,options,coord_calculating_function):
		#Type checking.
		if self.__class__.screen is None:
			raise Exception('Common screen object is not set.')
		if not isinstance(options,list) and not isinstance(options,tuple):
			raise TypeError('An iterable of options is required.')

		self.header=header
		self.options=options
		#The id of the currently selectd option(default is option 1)
		self.__selected=0
	

		all_coords=coord_calculating_function(ScreenOptions.screen,header,options)

		self.h_c=all_coords[0]
		all_coords.remove(all_coords[0])
		self.str_c=all_coords



	def display_option(self,option_id):
		y,x=self.str_c[option_id]
		if option_id!=self.__selected:
			self.__class__.screen.addstr(y,x,str(self.options[option_id]))
		else:
			self.__class__.screen.addstr(y,x,str(self.options[option_id]),curses.A_UNDERLINE)

	def display_header(self):
		y,x=self.h_c
		self.__class__.screen.addstr(y,x,self.header,curses.A_UNDERLINE)

	def display_all(self):
		self.__class__.screen.clear()
		self.display_header()
		for opt_id,_ in enumerate(self.options):
			self.display_option(opt_id)
		self.__class__.screen.refresh()

	def select_next(self):
		#Nothing to do if only one option exists.
		if len(self.options)==1:
			return
		temp=self.__selected
		self.__selected+=1
		self.__selected%=len(self.options)
		self.display_option(temp)
		self.display_option(self.__selected)
		self.__class__.screen.refresh()

	def select_previous(self):
		#Nothing to do if only one option exists.
		if len(self.options)==1:
			return
		temp=self.__selected
		self.__selected+=len(self.options)-1
		self.__selected%=len(self.options)
		self.display_option(temp)
		self.display_option(self.__selected)
		self.__class__.screen.refresh()

	#Manage the rendering of an instance of this class.
	def manager_loop(self,backward=False):
		self.display_all()
		while True:
			key=self.__class__.screen.getch()
			if key==curses.KEY_DOWN:
				self.select_next()
			elif key==curses.KEY_UP:
				self.select_previous()
			elif key==curses.KEY_RIGHT:
				return self.__selected
			elif backward and key==curses.KEY_LEFT:
				return self.__class__.PREVIOUS




#This function reads the characters of a file.
#The data stored in the file is returned as a dictionary where the coordinates are the keys and the characters are the values.
#'filename' is the name of the file to be read.
#'screen' is the screen whose dimensions have to be met.
#'forbidden' is he string containing the characters to be ignored.
def curses_read_file_fit_to_screen(filename,screen,forbidden=''):
	y,x=screen.getmaxyx()
	return read_file(filename,y,x,forbidden)




#This function reads the characters of a file.
#The data stored in the file is returned as a dictionary where the coordinates are the keys and the characters are the values.
#'filename' is the name of the file to be read.
#'max_height' is the maximum number of lines to be read.
#'max_width' is the number of characters per line to be read.
#'forbidden' is he string containing the characters to be ignored.
def read_file(filename,max_height,max_width,forbidden=''):
	file=None
	#Blindly try to open the file.Any errors will be thrown to the calling function.
	file=open(filename,'r')
	#The data is stored as a dictionary.
	#Each character is a key and a list of all the coordinates where that character occurs is the value for that key.
	#The Y coordinate to render from os 'y'
	data_dict,y={},0
	for line in file:
		for x_index,char in enumerate(line[:max_width:]):
			if char in forbidden:
				continue
			if char not in data_dict.keys():
				data_dict[char]=[]
			#Ignore all characters at the bottom-right corner.
			if (y,x_index)!=(max_height-1,max_width-1):
				data_dict[char].append((y,x_index))
		y+=1
		if y==max_height-1:
			break
	file.close()
	for char in data_dict.keys():
		data_dict[char]=tuple(data_dict[char])
	return data_dict


#Give the 'screen' a border.
def borderize(screen):
	#The characters to render with.
	corner,v,h=tuple('+|-')
	#The limits for the border.
	ymax,xmax=screen.getmaxyx()
	ymax,xmax=ymax-1,xmax-1
	#Upper left corner
	screen.addstr(0,0,corner)
	#Lower left corner
	screen.addstr(ymax,0,corner)
	#Upper right corner
	screen.addstr(0,xmax,corner)
	#The vertical borders.
	for y in range(1,ymax):
		screen.addstr(y,0,v)
		screen.addstr(y,xmax,v)
	#The horizontal borders.
	limit=xmax-1
	screen.addstr(0,1,h*limit)
	screen.addstr(ymax,1,h*limit)
	#Refresh the screen.
	screen.refresh()



#Retrun a set of coordinates containing the positions to render the options and the header at the center of the screen.
def centralize(screen,header,options):
	offsets=[]
	#The number of divisions to horizontally divide the screen into(includes all options and the header).
	n_divs=len(options)+2
	#Get the boundaries of the screen.
	height,width=screen.getmaxyx()
	#The vertical padding between options.
	vpad=height//n_divs
	#Y and X of the header.
	offsets.append((vpad,(width-len(header))//2))
	#The Y and X of all other options(set from the header).
	for i,string in enumerate(options,start=2):
		offsets.append((vpad*i,(width-len(string))//2))
	del height,width,vpad
	return offsets






'''
References:

(Merging two dictionaries)
https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python

(Dictionary comprehensions)
https://stackoverflow.com/questions/20489609/dictionary-comprehension-in-python-3

'''
