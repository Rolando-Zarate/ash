from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

class Password(Widget):
	def __init__(self, parent, y, x, width, theme, focus_theme = None, strict_numeric = False, maxlen = -1):
		super().__init__(WIDGET_TYPE_PASSWORD)
		self.y = y
		self.x = x
		self.width = width
		self.curpos = 0
		self.theme = theme
		self.text = ""
		self.parent = parent
		self.strict_numeric = strict_numeric
		self.maxlen = maxlen
		self.focus_theme = focus_theme
		self.is_in_focus = False

		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? "
		self.numeric_charset = "0123456789"
		self.password_symbol = "\u2022"

		self.focus()
	
	def focus(self):
		self.is_in_focus = True
		self.repaint()

	def blur(self):
		self.is_in_focus = False
		self.repaint()

	def perform_action(self, ch):
		self.focus()

		if(ch == -1):
			self.repaint()
			return None
		
		if(ch == curses.KEY_BACKSPACE):
			if(self.curpos > 0):
				self.text = (self.text[0:self.curpos-1] if self.curpos > 1 else "") + (self.text[self.curpos:] if self.curpos < len(self.text) else "")
				self.curpos -= 1
			else:
				curses.beep()
		elif(ch == curses.KEY_DC):
			if(self.curpos == len(self.text)):
				curses.beep()
			else:
				self.text = (self.text[0:self.curpos] if self.curpos > 0 else "") + (self.text[self.curpos+1:] if self.curpos < len(self.text)-1 else "")
		elif(ch == curses.KEY_END):
			self.curpos = len(self.text)
		elif(ch == curses.KEY_HOME):
			self.curpos = 0
		elif(ch == curses.KEY_LEFT):
			if(self.curpos > 0): 
				self.curpos -= 1
			else:
				curses.beep()
		elif(ch == curses.KEY_RIGHT):
			if(self.curpos < len(self.text)): 
				self.curpos += 1
			else:
				curses.beep()
		else:
			char = str(chr(ch))
			if(self.charset.find(char) != -1):
				if(not self.strict_numeric or self.numeric_charset.find(char) != -1):
					if(self.maxlen < 0 or self.curpos < self.maxlen-1):					
						self.text = (self.text[0:self.curpos] if self.curpos>0 else "") + char + (self.text[self.curpos:] if self.curpos<len(self.text) else "")
						self.curpos += 1
					else:
						curses.beep()
				else:
					curses.beep()
			else:
				curses.beep()
		
		self.repaint()

	def repaint(self):
		if(self.is_in_focus): curses.curs_set(True)
		paint_theme = self.theme
		if(self.is_in_focus and self.focus_theme != None): paint_theme = self.focus_theme
		
		self.parent.addstr(self.y, self.x, " " * self.width, paint_theme)
		
		n = len(self.text)
		if(n <= self.width):
			self.parent.addstr(self.y, self.x, self.password_symbol * len(self.text), paint_theme)
			self.parent.move(self.y, self.x+self.curpos)
		else:
			# width=50, n=51
			# curpos=51, flank=25
			# start=26, end=76 (end>n)
			# delta=76 - 51=25
			# start=1, end=51, vcurpos=51-1=50
			
			flank = self.width // 2
			start = self.curpos - flank
			end = self.curpos + flank

			if(start < 0):
				delta = abs(start)
				start += delta
				end += delta				
			elif(end > n):
				delta = end - n
				start -= delta
				end -= delta
			
			vtext = self.text[start:end]
			vcurpos = self.curpos - start

			self.parent.addstr(self.y, self.x, self.password_symbol * len(vtext), paint_theme)
			self.parent.move(self.y, self.x+vcurpos)
		
	def __str__(self):
		return self.text