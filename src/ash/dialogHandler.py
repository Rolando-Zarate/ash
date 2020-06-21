# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is a helper module to assist with various dialogs

from ash import *

class DialogHandler:
	def __init__(self, app):
		self.app = app

	# <----------------------------------- Switch Layout --------------------------------->

	def invoke_switch_layout(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 8, 40)
		self.app.dlgSwitchLayout = ModalDialog(self.app.stdscr, y, x, 8, 40, "SWITCH LAYOUT", self.switch_layout_key_handler)
		
		lstLayouts = ListBox(self.app.dlgSwitchLayout, 2, 2, 36, 5)
		layouts = 	[ 
					"Single", "Horizontal-2", "Horizontal-3", "Horizontal-4",
					"Vertical-2", "2x2", "2x3", "1-Left, 2-Right", "2-Left, 1-Right",
					"1-Top, 2-Bottom", "2-Top, 1-Bottom"
					]

		for i in range(len(layouts)):
			if(self.app.main_window.layout_type == i):
				lstLayouts.add_item("\u2713 " + layouts[i])
			else:
				lstLayouts.add_item(layouts[i])

		self.app.dlgSwitchLayout.add_widget("lstLayouts", lstLayouts)
		self.app.dlgSwitchLayout.show()

	def switch_layout_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.dlgSwitchLayout.hide()
		elif(is_newline(ch)):
			new_layout = self.app.dlgSwitchLayout.get_widget("lstLayouts").get_sel_index()
			self.app.dlgSwitchLayout.hide()

			if(new_layout == self.app.main_window.layout_type):
				return -1
			elif(self.app.main_window.layout_manager.can_change_layout(new_layout)):
				self.app.main_window.layout_manager.set_layout(new_layout)
				return -1
			else:
				return self.app.show_error("One or more files need to be saved first")				
		return ch

	# -------------------------------------------------------------------------------------


	# <----------------------------------- File Save As ---------------------------------->

	def invoke_file_save_as(self, filename=None):
		self.app.readjust()
		y, x = get_center_coords(self.app, 4, 40)
		self.app.dlgSaveAs = ModalDialog(self.app.stdscr, y, x, 4, 40, "SAVE AS", self.file_save_as_key_handler)
		if(filename == None): filename = str(os.getcwd()) + "/untitled.txt"
		txtFileName = TextField(self.app.dlgSaveAs, 2, 2, 36, filename)
		self.app.dlgSaveAs.add_widget("txtFileName", txtFileName)
		self.app.dlgSaveAs.show()

	def file_save_as_key_handler(self, ch):
		if(is_ctrl(ch, "Q")): 
			self.app.dlgSaveAs.hide()
		elif(is_newline(ch)):
			txtFileName = self.app.dlgSaveAs.get_widget("txtFileName")
			if(not os.path.isfile(str(txtFileName))):
				self.save_or_overwrite(str(txtFileName))
				return ch
			else:
				y, x = get_center_coords(self.app, 5, 40)
				self.app.msgBox = MessageBox(self.app.stdscr, y, x, 5, 40, "Replace File", "File already exists, replace?\n(Y)es / (N)o")
				while(True):
					response = self.app.msgBox.show()
					if(response == MSGBOX_YES):	
						self.save_or_overwrite(str(txtFileName))
						return ch
					elif(response == MSGBOX_NO):
						self.app.dlgSaveAs.hide()
						return ch
					else:
						beep()

		return ch

	def save_or_overwrite(self, filename):
		self.app.dlgSaveAs.hide()
		try:
			self.app.main_window.do_save_as(filename)
		except Exception as e:
			y, x = get_center_coords(self.app, 5, 40)
			self.app.msgBox = MessageBox(self.app.stdscr, y, x, 5, 40, "ERROR", "An error occurred while saving file\n(O)K")
			while(True):
				response = self.app.msgBox.show()
				if(response == MSGBOX_OK): return
				beep()

	# --------------------------------------------------------------------------------------