#For the snake.
from collections import deque
#This is absolutely necessary.
import curses
#For the apple.
from random import randint

#Imports from the local library.
from curse_help import read_file
from curse_help import borderize
from curse_help import centralize
from curse_help import ScreenOptions

#Global constants

#The dimensions of the game window.

#The height.
WIN_HEIGHT=30
#The width.
WIN_WIDTH=100
#The Y coordinate of the top left corner.
WIN_Y=3
#The X coordinate of the top left corner.
WIN_X=10

#The characters to be used while rendering.

#For the walls of the maze.
MAZE_CHAR='#'
#For the apple.
APPLE_CHAR='@'
#For the body of the snake.
SNAKE_BODY='+'
#The heads of the snake pointing in various directions.
SNAKE_LEFT,SNAKE_RIGHT,SNAKE_UP,SNAKE_DOWN='<>^V'

#Defining macros for the color constants which will be set inside the set_environment function.

#For the apple
APPLE_COLOR=None
#For the maze
MAZE_COLOR=None
#For the snake
SNAKE_COLOR=None

#This class initializes and contains all the assets of the game being played.
class Game():

	"""
	To add a new map:

	Let your map be called MAP1.
	Add 'MAP1' to the mazes tuple.
	If your map file is in a file called 'map1.txt' , do:
		Add a file to the file_prefix directory called 'map1.txt'.
		Use spaces to denote blanks.
		Use '#' to show walls.
		Use '.' to specify the initial position of the snake.
	Add 'map1'(filemane without extension) to the maze_files tuple.

	(You will have to adjust the spacing of the text file to fit your terminal dimensions.)

	"""

	#The mazes being offered.
	mazes=('None','Garden','Box','Piano')
	#What they map to.
	maze_files=('none','garden','box','piano')
	#The prefix for the files.
	file_prefix='./assets/maps/'
	#The suffix for the files.
	file_suffix='.txt'

	#The speed levels being offered.
	speed=('Slow','Fast','Normal',)
	#What they map to.
	speeds=(500,100,200)


	#Static method to handle creation of the game object.
	@staticmethod
	def get_game_configuration():
		sco1=ScreenOptions('Mazes',Game.mazes,centralize)
		sco2=ScreenOptions('Speed',Game.speed,centralize)
		x=ScreenOptions.manage_sequence((sco1,sco2))
		return Game(x)

	def __init__(self,args):
		#The file containing the amp of the game.
		self.maze_file=''.join((Game.file_prefix,Game.maze_files[args[0]],Game.file_suffix))
		#The speed of the game(this is essentially the delay to wait for between user input).
		self.speed=Game.speeds[args[1]]
		#The score of the game.
		self.score=0



	#Set the maze and the snake into game variables.
	def set_world_map(self):
		#Read the map of the world.
		world_map=read_file(filename=self.maze_file,max_height=WIN_HEIGHT,max_width=WIN_WIDTH,forbidden=' \n')

		#Parse it.
		#If we do not get a baby snake , then we raise an error.
		try:
			self.baby_snake=world_map['.']
		except KeyError:
			raise RuntimeError('Baby snake is not defined on the map.A sequence of \'.\'s was expected.')
		#If we do not get a maze , then the world is blank.
		try:
			self.maze=world_map['#']
		except KeyError:
			self.maze=()

		del world_map


	#Yield a new apple.
	#The limits for the apple depend on the boundaries set by the border of the screen.
	def new_apple(self,snake):
		while True:
			apple_y,apple_x=randint(1,WIN_HEIGHT-2),randint(1,WIN_WIDTH-2)
			if (apple_y,apple_x) not in self.maze and (apple_y,apple_x) not in snake.body:
				return (apple_y,apple_x)

class Snake():

	#The characters to render the head according to the direction of the snake.
	head_right,head_left,head_up,head_down='><^V'

	#Defining a snake.
	def __init__(self,xmax,ymax,init_pos):
		#The body of the snake is a deque
		self.body=deque(init_pos)

		#The head of the snake is the last set of the coordinates.
		self.head=self.body[-1]
		#The character to render the body with.
		self.body_char='+'
		#Velocity of the snake in the X direction is vx
		#Velocity of the snake in the Y direction is vy
		self.__get_init_direction()

		#The upper limits of the position of the snake.
		#These limits are used to wrap the snake around the screen.
		self.wrapx=xmax-1
		self.wrapy=ymax-1


	#Get the initial direction of the snake.
	def __get_init_direction(self):
		#The coordinates of the head.
		hy,hx=self.head
		#The coordinates of the second segment.
		sy,sx=self.body[-2]

		#Analyze the direction.
		if hx==sx:self.vx=0
		elif hx<sx:self.vx=-1
		else:self.vx=1

		if hy==sy:self.vy=0
		elif hy<sy:self.vy=-1
		else:self.vy=1

		#Set the character for the head.
		if self.vx==0 and self.vy==1:self.head_char=Snake.head_down
		elif self.vx==0 and self.vy==-1:self.head_char=Snake.head_up
		elif self.vx==1 and self.vy==0:self.head_char=Snake.head_right
		else:self.head_char=Snake.head_left


	#Update the head of the snake.
	def update_head(self):
		#The old head.
		head_y,head_x=self.head
		#The new head depending upon the direction.
		head_y+=self.vy
		head_x+=self.vx
		#If we have reached the beginning , goto the end.
		#If we have reached the end , goto the beginning.
		if head_x==0:head_x=self.wrapx-1
		elif head_x==self.wrapx:head_x=1

		if head_y==0:head_y=self.wrapy-1
		elif head_y==self.wrapy:head_y=1

		self.head=tuple((head_y,head_x))
		self.body.append(self.head)

	#Move the snake upwards.
	def move_up(self):
		#Do nothing if the snake is moving down or up.
		if self.vy!=0:return
		self.vx,self.vy=0,-1
		self.head_char=Snake.head_up

	#Move the snake downwards.
	def move_down(self):
		#Do nothing if the snake is moving down or up.
		if self.vy!=0:return
		self.vx,self.vy=0,1
		self.head_char=Snake.head_down

	#Move the snake downwards.
	def move_left(self):
		#Do nothing if the snake is moving left or right.
		if self.vx!=0:return
		self.vx,self.vy=-1,0
		self.head_char=Snake.head_left

	#Move the snake right.
	def move_right(self):
		#Do nothing if the snake is moving left or right.
		if self.vx!=0:return
		self.vx,self.vy=1,0
		self.head_char=Snake.head_right

	#Continue moving the snake in the current direction.
	def move_as_is(self):
		self.update_head()

	#As we want to increase the length of the snake , we need a separate function that will move its tail in the front.
	#If the length of the snake must increase , then this function can be called after a delay.
	#We return the coordinates of the tail of the snake as when the time comes to remove it , we can write a blank to that particular location.
	#There will be no reason to rerender the whole screen.
	def move_tail(self):
		return self.body.popleft()

	#Check if the snake has collided with itself.
	#If the coordinates of the head appear on the body , the collision occurs.
	def self_collision(self):
		return self.body.index(self.head)<len(self.body)-1



#Function to render the 'snake' on a curses 'screen'.
#As the screen can have maps , we do not want to clear the entire screen.
def render_snake(screen,snake):
	for y,x in snake.body:
		screen.addstr(y,x,snake.body_char,SNAKE_COLOR)
	screen.addstr(snake.body[-1][0],snake.body[-1][1],snake.head_char,SNAKE_COLOR)
	screen.refresh()

#Overwrite the tail of the snake with a ' ' , removing it from the screen.
def remove_tail(screen,snake):
	tail=snake.move_tail()
	screen.addstr(tail[0],tail[1],' ')
	screen.refresh()

#Check if the 'apple' is eaten by the 'snake'.
def apple_is_eaten(snake,apple):
	return snake.head==apple

#Render the 'apple' onto the 'screen'.
def render_apple(apple,screen):
	screen.addstr(apple[0],apple[1],APPLE_CHAR,APPLE_COLOR)
	screen.refresh()

#Remove the 'apple' from the 'screen'.
def remove_apple(apple,screen):
	screen.addstr(apple[0],apple[1],' ')
	screen.refresh()

#Render the 'maze' on the 'screen'
def render_maze(maze,screen):
	for y,x in maze:
		screen.addstr(y,x,MAZE_CHAR,MAZE_COLOR)
	screen.refresh()


#Wrapper to check all sorts of collisions
def collision_alert(snake,maze):
	if snake.self_collision():return True
	#Check if the head of the snake overlaps with any of the coordinates given in 'maze'.
	if snake.head in maze:return True
	return False


#Prepare the curses environment for the game.
def set_environment(screen):

	#Setup the screen.
	screen.clear()
	screen.refresh()
	curses.curs_set(False)

	#Set all the colors.
	global APPLE_COLOR,SNAKE_COLOR,MAZE_COLOR
	curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
	APPLE_COLOR=curses.color_pair(1)
	curses.init_pair(2,curses.COLOR_RED,curses.COLOR_BLACK)
	MAZE_COLOR=curses.color_pair(2)
	curses.init_pair(3,curses.COLOR_YELLOW,curses.COLOR_BLACK)
	SNAKE_COLOR=curses.color_pair(3)


def snake(screen):

	set_environment(screen)

	ScreenOptions.set_screen(screen)
	game=Game.get_game_configuration()

	screen.timeout(game.speed)

	#The window for the snake-game.
	game_window=curses.newwin(WIN_HEIGHT,WIN_WIDTH,WIN_Y,WIN_X)

	#Generate the map.
	game.set_world_map()

	#Render the game area.
	render_maze(maze=game.maze,screen=game_window)
	borderize(game_window)

	#Get the snake.
	snake=Snake(xmax=WIN_WIDTH,ymax=WIN_HEIGHT,init_pos=game.baby_snake)
	del game.baby_snake

	#Number of iterations to delay removing the tail.
	#This is used to increase the length of the snake.
	drag=0
	#Need a new apple?
	new_apple=True
	#The apple.
	apple=None

	#The game loop.
	while True:
		snake.move_as_is()
		if collision_alert(snake,game.maze):
			break
		render_snake(game_window,snake)
		if new_apple:
			apple=game.new_apple(snake)
			render_apple(apple,game_window)
			new_apple=False
		key=screen.getch()
		if key==curses.KEY_UP:
			snake.move_up()
		elif key==curses.KEY_DOWN:
			snake.move_down()
		elif key==curses.KEY_LEFT:
			snake.move_left()
		elif key==curses.KEY_RIGHT:
			snake.move_right()
		elif key==-1:
			pass
		else:
			continue
		if apple_is_eaten(snake,apple):
			drag,new_apple,game.score=drag+1,True,game.score+1
			remove_apple(apple,game_window)
		if drag>0:
			drag-=1
		elif drag==0:
			remove_tail(game_window,snake)

	screen.clear()
	screen.addstr(15,50,f'Your final score is {game.score}.')
	screen.addstr(16,50,'Thank you for playing.')
	screen.refresh()
	curses.napms(3000)



x=curses.wrapper(snake)
print(x)



"""
References

(Non-blocking getch)
https://docs.python.org/3/library/curses.html#curses.window.timeout

"""
