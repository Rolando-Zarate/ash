# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag, and Susmita Guha. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module is a helper class for TopLevelWindow

from ash.widgets import *
from ash.widgets.utils.formatting import *
from ash.widgets.utils.utils import *
from ash.widgets.editor import *

# <------------------- constants -------------------->
BORDER_HORIZONTAL		= "\u2500"		# _
BORDER_VERTICAL			= "\u2502"		# |
BORDER_CROSSROADS		= "\u253C"		# +
BORDER_SPLIT_RIGHT		= "\u251C"		# |-
BORDER_SPLIT_LEFT		= "\u2524"		# -|
BORDER_SPLIT_TOP		= "\u2534"		# _|_
BORDER_SPLIT_BOTTOM		= "\u252C"		# T

# note: layout values must begin at 0
LAYOUT_SINGLE 			= 0
LAYOUT_HORIZONTAL_2		= 1
LAYOUT_HORIZONTAL_3		= 2
LAYOUT_HORIZONTAL_4		= 3
LAYOUT_VERTICAL_2		= 4
LAYOUT_2X2				= 5
LAYOUT_2X3				= 6
LAYOUT_1L_2VR			= 7
LAYOUT_2VL_1R			= 8
LAYOUT_1T_2HB			= 9
LAYOUT_2HT_1B			= 10

# note: editor_count order must match the order of the layout values
EDITOR_COUNTS = [ 1, 2, 3, 4, 2, 4, 6, 3, 3, 3, 3 ]

class LayoutManager:
	def __init__(self, win):
		self.win = win

	# draw the line divisions between editors
	def draw_layout_borders(self):
		if(self.win.layout_type == LAYOUT_SINGLE): 
			return		
		elif(self.win.layout_type == LAYOUT_VERTICAL_2):
			self.win.addstr(self.win.height//2, 0, BORDER_HORIZONTAL * self.win.width, gc(COLOR_DIVISION))
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_2):
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width//2, BORDER_VERTICAL, gc(COLOR_DIVISION))
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_3):
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width//3, BORDER_VERTICAL, gc(COLOR_DIVISION))
				self.win.addstr(row, (self.win.width*2)//3, BORDER_VERTICAL, gc(COLOR_DIVISION))
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_4):
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width//4, BORDER_VERTICAL, gc(COLOR_DIVISION))
				self.win.addstr(row, self.win.width//2, BORDER_VERTICAL, gc(COLOR_DIVISION))
				self.win.addstr(row, (self.win.width*3)//4, BORDER_VERTICAL, gc(COLOR_DIVISION))
		elif(self.win.layout_type == LAYOUT_2X2):
			for row in range(1, self.win.height//2):
				self.win.addstr(row, self.win.width//2, BORDER_VERTICAL, gc(COLOR_DIVISION))
			self.win.addstr(self.win.height//2, 0, BORDER_HORIZONTAL * self.win.width, gc(COLOR_DIVISION))
			self.win.addstr(self.win.height//2, self.win.width//2, BORDER_CROSSROADS, gc(COLOR_DIVISION))
			for row in range(self.win.height//2 + 1, self.win.height-1):
				self.win.addstr(row, self.win.width//2, BORDER_VERTICAL, gc(COLOR_DIVISION))
		elif(self.win.layout_type == LAYOUT_2X3):
			pass
		elif(self.win.layout_type == LAYOUT_1L_2VR):
			pass
		elif(self.win.layout_type == LAYOUT_2VL_1R):
			pass
		elif(self.win.layout_type == LAYOUT_1T_2HB):
			pass
		elif(self.win.layout_type == LAYOUT_2HT_1B):
			pass
	

	# check if terminal window has been resized, if so, readjust
	def readjust(self, forced=False):
		h, w = self.win.app.readjust()
		if(not forced and h == self.win.height and w == self.win.width): return
		
		self.win.height, self.win.width = h, w

		ec = EDITOR_COUNTS[self.win.layout_type]
		dim = self.get_dimensions(self.win.layout_type)
		for i in range(ec):
			if(self.editor_exists(i)):
				y = dim[i].get("y")
				x = dim[i].get("x")
				h = dim[i].get("height")
				w = dim[i].get("width")
				self.win.editors[i].resize(y, x, h, w, True)
	
	# repaint editor if available or appropriate text
	def repaint_editors(self):
		ec = EDITOR_COUNTS[self.win.layout_type]
		dim = self.get_dimensions(self.win.layout_type)
		aed = self.win.get_active_editor()

		# Note: editor repaint must be done after self.__addstr() to correctly
		# reposition cursor inside the editor
		for i in range(ec):
			if(not self.editor_exists(i)):
				y, x, w = self.get_center_of_area(dim[i])
				self.__addstr(y, x, w)

		for i in range(ec):
			if(self.editor_exists(i) and i != self.win.active_editor_index): 
				self.win.editors[i].repaint()
				
		if(aed != None): aed.repaint()
		
	# checks if given editor exists
	def editor_exists(self, index):
		if(index >= len(self.win.editors)): return False
		return (False if self.win.editors[index] == None else True)

	# returns the appropriate position of text to be placed in center-vertical position in the area
	def get_center_of_area(self, area):
		# Example:
		# y=1,h=8 = y-->(y+h-1) = 1-->8, center = 4.5 (4)
		# y=1,h=9 = y-->(y+h-1) = 1-->9, center = 5
		start_y = area.get("y")
		end_y = (area.get("y") + area.get("height") - 1)
		y = (start_y + end_y) // 2
		x = area.get("x")
		w = area.get("width")-1
		return (y, x, w)
		
	def __addstr(self, y, x, w):
		self.win.win.addstr(y, x, pad_center_str("No files selected", w), gc(COLOR_LIGHTGRAY_ON_DARKGRAY))

	def get_dimensions(self, layout_type):
		if(self.win.layout_type == LAYOUT_SINGLE): 
			return([{
				"y": 1,
				"x": 0,
				"height": (self.win.height-2),
				"width": self.win.width
			}])
		elif(self.win.layout_type == LAYOUT_VERTICAL_2):
			# H=10[1-8]: 1-->4, b=5, 6-->8 ; 11[1-9] 1-->4, b=5, 6-->9
			return([{
				"y": 1,
				"x": 0,
				"height": (self.win.height-2) // 2,
				"width": self.win.width
			}, {
				"y": ((self.win.height-2) // 2) + 2,
				"x": 0,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": self.win.width
			}])
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_2):
			# W=10[0-9]: 0-->4, b=5, 6-->9 ; 11[0-10] 0-->4, b=5, 6-->10
			return([{
				"y": 1,
				"x": 0,
				"height": self.win.height-2,
				"width": (self.win.width // 2)
			}, {
				"y": 1,
				"x": (self.win.width // 2) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}])
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_3):
			# W=100[0-99]: 0-->32, b1=33, 34-->65, b2=66, 67-->99 ; 
			# W=101[0-100] 0-->32, b1=33, 34-->66, b2=67, 68-->100 ;
			return([{
				"y": 1,
				"x": 0,
				"height": self.win.height-2,
				"width": (self.win.width // 3)
			}, {
				"y": 1,
				"x": (self.win.width // 3) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 3) - (1 - (self.win.width % 2))
			}, {
				"y": 1,
				"x": ((self.win.width * 2) // 3) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 3)
			}])
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_4):
			pass
		elif(self.win.layout_type == LAYOUT_2X2):
			pass
		elif(self.win.layout_type == LAYOUT_2X3):
			pass
		elif(self.win.layout_type == LAYOUT_1L_2VR):
			pass
		elif(self.win.layout_type == LAYOUT_2VL_1R):
			pass
		elif(self.win.layout_type == LAYOUT_1T_2HB):
			pass
		elif(self.win.layout_type == LAYOUT_2HT_1B):
			pass

	# checks if layout can be changed
	def can_change_layout(self, layout_type):
		old_ec = EDITOR_COUNTS[self.win.layout_type]
		new_ec = EDITOR_COUNTS[layout_type]

		if(new_ec >= old_ec):
			return True
		else:
			for i in range(new_ec, old_ec):
				if(self.editor_exists(i) and not self.win.editors[i].save_status): 
					# if blank buffer then okay, otherwise cannot switch layout without saving
					if(not self.win.editors[i].has_been_allotted_file and len(str(self.win.editors[i]))==0): continue
					return False
			return True

	# changes the current layout
	def set_layout(self, layout_type):
		if(not self.can_change_layout(layout_type)): return

		old_ec = EDITOR_COUNTS[self.win.layout_type]
		new_ec = EDITOR_COUNTS[layout_type]

		if(new_ec >= old_ec):
			self.win.layout_type = layout_type
			while(len(self.win.editors) > old_ec):
				self.win.editors.pop(old_ec)
			for i in range(old_ec, new_ec):
				self.win.editors.append(None)
		else:
			for i in range(new_ec, old_ec):
				if(self.editor_exists(new_ec)):
					self.win.remove_editor(new_ec)

		self.readjust(True)
		self.win.repaint()

	# called from app_main() in response to Function key press
	def invoke_activate_editor(self, index):
		ec = EDITOR_COUNTS[self.win.layout_type]
		aei = self.win.active_editor_index
		
		# layout does not support that editor
		if(index >= ec):
			self.win.app.show_error("Selected editor does not exist")
			return
		
		# if already active, return
		if(aei == ec): return

		if(self.win.editors[index] == None):
			self.win.editors[index] = Editor(self.win)
		
		self.win.active_editor_index = index
		self.readjust(True)
		self.win.repaint()
		
		if(aei >= 0): 
			# before switching, save recent changes to buffer
			save_to_buffer(self.win.app.files, self.win.editors[aei])
			
			# remove focus
			self.win.editors[aei].blur()

		# load most recent changes from buffer
		load_from_buffer(self.win.app.files, self.win.editors[index])
		
		# put focus
		self.win.editors[index].focus()