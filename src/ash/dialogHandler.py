# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is a helper module to assist with various dialogs

from ash import *

UNSAVED_BULLET		= "\u2022"
TICK_MARK			= "\u2713"

SUPPORTED_ENCODINGS = [ "utf-8", "ascii", "utf-7", "utf-16", "utf-32", "latin-1" ]

class DialogHandler:
	def __init__(self, app):
		self.app = app

	# <----------------------------------- Find and Replace --------------------------------->

	def invoke_find(self):
		mw = self.app.main_window
		ed = mw.get_active_editor()
		self.app.readjust()
		y, x = get_center_coords(self.app, 5, 30)
		self.app.dlgFind = FindReplaceDialog(mw, y, x, ed)
		self.app.dlgFind.show()
		mw.repaint()

	def invoke_find_and_replace(self):
		mw = self.app.main_window
		ed = mw.get_active_editor()
		self.app.readjust()
		y, x = get_center_coords(self.app, 7, 30)
		self.app.dlgReplace = FindReplaceDialog(mw, y, x, ed, True)
		self.app.dlgReplace.show()
		mw.repaint()

	# <----------------------------------- Go to Line --------------------------------->

	def invoke_go_to_line(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 5, 14)
		self.app.dlgGoTo = ModalDialog(self.app.main_window, y, x, 5, 14, "GO TO LINE", self.go_to_key_handler)
		currentLine = str(self.app.main_window.get_active_editor().curpos.y + 1)
		txtLineNumber = TextField(self.app.dlgGoTo, 3, 2, 10, currentLine, True)
		self.app.dlgGoTo.add_widget("txtLineNumber", txtLineNumber)
		self.app.dlgGoTo.show()

	def go_to_key_handler(self, ch):
		if(is_ctrl(ch, "Q")): 
			self.app.dlgGoTo.hide()
		elif(is_newline(ch)):
			line = str(self.app.dlgGoTo.get_widget("txtLineNumber"))
			if(len(line) == 0):
				beep()
				return -1

			pos = line.find(".")
			try:
				if(pos > -1):
					row = int(line[0:pos]) - 1
					col = int(line[pos+1:]) - 1
				else:
					row = int(line) - 1
					col = 0
			except:
				self.app.show_error("Invalid line number specified")
				return -1
			
			aed = self.app.main_window.get_active_editor()
			if(row < 0 or row >= len(aed.lines)):
				beep()
			elif(col < 0 or col > len(aed.lines[row])):
				beep()
			else:
				self.app.dlgGoTo.hide()
				aed.curpos.y = row
				aed.curpos.x = col
				aed.repaint()
		
		return ch

	# <----------------------------------- Close Editor/App --------------------------------->

	def invoke_forced_quit(self):
		self.app.main_window.hide()

	def invoke_quit(self):
		mw = self.app.main_window
		aed = mw.get_active_editor()

		# Scenarios:
		# 1. Active editor is saved: close editor (maintain buffer)
		# 2. Active editor is unsaved: check if file-allotted or not
		#		(a) if no file allotted: ask to be saved first, before closing
		#		(b)	if file allotted: close editor (maintain buffer)
		# 3. No active editor: check if other editors exist:
		# 		(a) No other editors exist: check if unsaved files exist
		# 			(i) no unsaved files exist: quit application
		#			(ii) unsaved files exist: ask user (Yes: save-all, No: discard-all, Cancel: dont-quit)
		# 		(b) Other editors exist: inform user that other editors exist

		if(aed == None):
			# case 3: no active editor exists
			n = len(mw.editors)
			other_editors_exist = False
			for i in range(n):
				if(mw.editors[i] != None):
					other_editors_exist = True
					break
			
			if(other_editors_exist):
				# case 3(b): other editors exist
				self.app.show_error("Close all windows to quit application or use Ctrl+@ to force-quit")
			else:
				# case 3(a): no other editors exist
				all_saved = True
				for f in self.app.files:
					if(not f.save_status):
						all_saved = False
						break

				if(all_saved):
					# case 3(a)[i]: all buffers saved: quit app
					mw.hide()
				else:
					# case 3(a)[ii]: some buffers are unsaved: confirm with user
					response = self.app.ask_question("SAVE/DISCARD ALL", "One or more unsaved files exist, choose yes(save-all) / no(discard-all) / cancel(dont-quit)", True)
					if(response == None):
						return
					elif(response):
						write_all_buffers_to_disk(self.app.files)
						mw.hide()
						return
					elif(not response):
						mw.hide()
						return
		else:
			if(aed.save_status):
				# case 1: active editor is saved
				save_to_buffer(self.app.files, aed)
				mw.close_active_editor()
			else:
				# case 2: active editor has unsaved changes
				if(not aed.has_been_allotted_file):
					# active editor does not have any allotted file
					if(aed.can_quit()):
						# still if can close (i.e. editor is blank: no data), then close editor
						mw.close_active_editor()
					else:
						# case 2(a): has unsaved changes: confirm with user
						response = self.app.ask_question("DISCARD CHANGES", "Do you want to save this file (Yes) or discard changes (No)?", True)
						if(response == None): return
						if(response):
							# user wants to save before closing: so show file-save-as dialogbox
							self.invoke_file_save_as()
							if(aed.save_status): 
								# no need to add this filedata to list of active files as
								# invoke_file_save_as() already does it
								mw.close_active_editor()
						else:
							# user wants to discard changes
							mw.close_active_editor()
				else:
					# case 2(b) [same as case 1]: active editor has been allotted file
					# so: save the contents into mapped buffer and close editor
					filename = aed.filename
					buffer_index = get_file_buffer_index(self.app.files, filename)
					filedata = aed.get_data()
					self.app.files[buffer_index] = filedata
					mw.close_active_editor()

	# <--------------------------- Set Preferences ------------------------------>

	def invoke_set_preferences(self):
		aed = self.app.main_window.get_active_editor()
		if(aed == None): return

		self.app.readjust()
		y, x = get_center_coords(self.app, 16, 30)
		self.app.dlgPreferences = ModalDialog(self.app.main_window, y, x, 16, 30, "PREFERENCES", self.preferences_key_handler)
		current_tab_size = str(aed.tab_size)
		txtTabSize = TextField(self.app.dlgPreferences, 3, 2, 26, current_tab_size, True)
		lstEncodings = ListBox(self.app.dlgPreferences, 5, 2, 26, 6)
		chkShowLineNumbers = CheckBox(self.app.dlgPreferences, 12, 2, "Show line numbers")
		chkWordWrap = CheckBox(self.app.dlgPreferences, 13, 2, "Word Wrap")
		chkHardWrap = CheckBox(self.app.dlgPreferences, 14, 2, "Hard Wrap")
		
		for enc in SUPPORTED_ENCODINGS:
			lstEncodings.add_item(("  " if aed.encoding != enc else TICK_MARK + " ") +  enc)
		
		chkShowLineNumbers.set_value(aed.show_line_numbers)
		chkWordWrap.set_value(aed.word_wrap)
		chkHardWrap.set_value(aed.hard_wrap)
		lstEncodings.sel_index = SUPPORTED_ENCODINGS.index(aed.encoding)
		
		self.app.dlgPreferences.add_widget("txtTabSize", txtTabSize)
		self.app.dlgPreferences.add_widget("lstEncodings", lstEncodings)
		self.app.dlgPreferences.add_widget("chkShowLineNumbers", chkShowLineNumbers)
		self.app.dlgPreferences.add_widget("chkWordWrap", chkWordWrap)
		self.app.dlgPreferences.add_widget("chkHardWrap", chkHardWrap)
		
		self.app.dlgPreferences.show()

	def preferences_key_handler(self, ch):
		aed = self.app.main_window.get_active_editor()

		if(is_ctrl(ch, "Q")): 
			self.app.dlgPreferences.hide()
		elif(is_newline(ch)):
			try:
				tab_size = int(str(self.app.dlgPreferences.get_widget("txtTabSize")))
			except:
				self.app.show_error("TAB SIZE", "Incorrect tab size: should be in [1,9]")
				return -1

			encoding_index = self.app.dlgPreferences.get_widget("lstEncodings").sel_index
			show_line_numbers = self.app.dlgPreferences.get_widget("chkShowLineNumbers").isChecked()
			word_wrap = self.app.dlgPreferences.get_widget("chkWordWrap").isChecked()
			hard_wrap = self.app.dlgPreferences.get_widget("chkHardWrap").isChecked()

			self.app.dlgPreferences.hide()

			if(tab_size < 1 or tab_size > 9):
				self.app.show_error("TAB SIZE", "Incorrect tab size: should be in [1,9]")
				return -1

			aed.tab_size = tab_size
			aed.encoding = SUPPORTED_ENCODINGS[encoding_index]
			aed.toggle_line_numbers(show_line_numbers)
			aed.set_wrap(word_wrap, hard_wrap)

			self.app.main_window.repaint()
			aed.repaint()
			return -1
		
		return ch

	# <----------------------------------- File New --------------------------------->

	def invoke_file_new(self):
		mw = self.app.main_window
		aed = mw.get_active_editor()
		aedi = mw.active_editor_index

		if(aed == None or (not aed.can_quit() and not aed.has_been_allotted_file)):
			# no active-editor exists OR it is an unsaved buffer
			# so: look for a different editor to place the new file
			ffedi = get_first_free_editor_index(mw)
			if(ffedi == -1):
				# no other editor also exists
				self.app.show_error("No free editors available: switch layout or close an editor")
				return -1

			# different editor found, make it the active editor
			mw.layout_manager.invoke_activate_editor(ffedi)
			aed = mw.get_active_editor()
		else:
			# active editor has allotted-file and can be quit
			
			# so: save recent changes to buffer
			save_to_buffer(self.app.files, aed)

			# close and reopen
			mw.editors[aedi] = None
			mw.layout_manager.invoke_activate_editor(aedi)

		mw.repaint()
		
	# <----------------------------------- File Open --------------------------------->

	def invoke_project_file_open(self):
		pass

	def invoke_file_open(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 14, 60)
		self.app.dlgFileOpen = ModalDialog(self.app.main_window, y, x, 14, 60, "OPEN FILE", self.file_open_key_handler)
		txtFileName = TextField(self.app.dlgFileOpen, 3, 2, 56, str(os.getcwd()) + "/")
		lstActiveFiles = ListBox(self.app.dlgFileOpen, 5, 2, 56, 6, "(No active files)")
		lstEncodings = ListBox(self.app.dlgFileOpen, 12, 2, 56, 1)

		# add the list of active files
		for f in self.app.files:
			lstActiveFiles.add_item(("  " if f.save_status else UNSAVED_BULLET) +  get_file_title(f.filename))
		
		# add the encodings
		for enc in SUPPORTED_ENCODINGS:
			lstEncodings.add_item(enc)
		
		# set default encoding to UTF-8
		lstEncodings.sel_index = SUPPORTED_ENCODINGS.index("utf-8")

		self.app.dlgFileOpen.add_widget("txtFileName", txtFileName)
		self.app.dlgFileOpen.add_widget("lstActiveFiles", lstActiveFiles)
		self.app.dlgFileOpen.add_widget("lstEncodings", lstEncodings)
		
		self.app.dlgFileOpen.show()

	def file_open_key_handler(self, ch):
		txtFileName = self.app.dlgFileOpen.get_widget("txtFileName")
		lstActiveFiles = self.app.dlgFileOpen.get_widget("lstActiveFiles")
		lstEncodings = self.app.dlgFileOpen.get_widget("lstEncodings")
		sel_index = lstActiveFiles.get_sel_index()
		mw = self.app.main_window
		aed = mw.get_active_editor()
		aedi = mw.active_editor_index

		if(is_ctrl(ch, "Q")):
			self.app.dlgFileOpen.hide()
			return -1
		elif(is_newline(ch)):
			if(lstActiveFiles.is_in_focus and sel_index > -1): txtFileName.set_text(self.app.files[sel_index].filename)
			filename = str(txtFileName)
			sel_encoding = str(lstEncodings)
			self.app.dlgFileOpen.hide()
			
			if(not file_exists_in_buffer(self.app.files, filename)):
				# new file is being opened
				if(os.path.isfile(filename)):
					# file exists on disk, so add it to buffer
					try:
						file_data = FileData(filename, encoding = sel_encoding)
						self.app.files.append(file_data)
					except:
						self.app.show_error("The selected encoding does not match file encoding")
						return -1
				else:
					# file does not exist: show error
					self.app.show_error("The selected file does not exist")
					return -1

			new_editor = False
			if(aed == None or (not aed.can_quit() and not aed.has_been_allotted_file)):
				# no active-editor OR it is an unsaved-buffer
				# so: look for a different editor to place the new file
				ffedi = get_first_free_editor_index(mw)
				if(ffedi == -1):
					# no other editor also exists
					self.app.show_error("No free editors available: switch layout or close an editor")
					return -1

				# different editor found, make it the active editor
				mw.layout_manager.invoke_activate_editor(ffedi)
				aed = mw.get_active_editor()
				aedi = ffedi
				new_editor = True
			
			if(not new_editor and aed.has_been_allotted_file):
				# if active editor has a file: find a new editor
				ffedi = get_first_free_editor_index(mw, aedi)

				if(ffedi == -1):
					# no other editor also exists
					if(self.app.ask_question("REPLACE ACTIVE EDITOR", "No free editors available: replace active editor?")):
						# yes: replace the active-editor, save any changes
						save_to_buffer(self.app.files, aed)
					else:
						# cancel open operation
						return -1
				else:
					mw.layout_manager.invoke_activate_editor(ffedi)
					aed = mw.get_active_editor()
					aedi = ffedi
					new_editor = True

			bi = get_file_buffer_index(self.app.files, filename)
			aed.set_data(self.app.files[bi])
			mw.repaint()
			
			return -1
		elif(is_tab(ch) or ch == curses.KEY_BTAB):
			if(sel_index > -1): txtFileName.set_text(self.app.files[sel_index].filename)			
		
		return ch

	# <----------------------------------------------------------------------------------->

	# <----------------------------------- Switch Layout --------------------------------->

	def invoke_switch_layout(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 9, 40)
		self.app.dlgSwitchLayout = ModalDialog(self.app.main_window, y, x, 9, 40, "SWITCH LAYOUT", self.switch_layout_key_handler)
		
		lstLayouts = ListBox(self.app.dlgSwitchLayout, 3, 2, 36, 5)
		layouts = 	[ 
					"Single", "Horizontal-2", "Horizontal-3", "Horizontal-4",
					"Vertical-2", "2x2", "2x3", "1-Left, 2-Right", "2-Left, 1-Right",
					"1-Top, 2-Bottom", "2-Top, 1-Bottom"
					]

		for i in range(len(layouts)):
			if(self.app.main_window.layout_type == i):
				lstLayouts.add_item(TICK_MARK + " " + layouts[i])
				lstLayouts.sel_index = i
			else:
				lstLayouts.add_item("  " + layouts[i])

		self.app.dlgSwitchLayout.add_widget("lstLayouts", lstLayouts)
		self.app.dlgSwitchLayout.show()

	def switch_layout_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.dlgSwitchLayout.hide()
			self.app.main_window.repaint()
			return -1
		elif(is_newline(ch)):
			new_layout = self.app.dlgSwitchLayout.get_widget("lstLayouts").get_sel_index()
			self.app.dlgSwitchLayout.hide()
			self.app.main_window.repaint()

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
		y, x = get_center_coords(self.app, 5, 60)
		self.app.dlgSaveAs = ModalDialog(self.app.main_window, y, x, 5, 60, "SAVE AS", self.file_save_as_key_handler)
		if(filename == None): filename = str(os.getcwd()) + "/untitled.txt"
		txtFileName = TextField(self.app.dlgSaveAs, 3, 2, 56, filename)
		self.app.dlgSaveAs.add_widget("txtFileName", txtFileName)
		self.app.dlgSaveAs.show()

	def file_save_as_key_handler(self, ch):
		if(is_ctrl(ch, "Q")): 
			self.app.dlgSaveAs.hide()
		elif(is_newline(ch)):
			self.app.dlgSaveAs.hide()
			txtFileName = self.app.dlgSaveAs.get_widget("txtFileName")
			if(not os.path.isfile(str(txtFileName))):
				self.save_or_overwrite(str(txtFileName))
			else:				
				if(self.app.ask_question("REPLACE FILE", "File already exists, replace?")):
					self.save_or_overwrite(str(txtFileName))
					
		return ch

	def save_or_overwrite(self, filename):
		self.app.dlgSaveAs.hide()
		try:
			self.app.main_window.do_save_as(filename)
		except Exception as e:
			self.app.show_error("An error occurred while saving file")			

	# --------------------------------------------------------------------------------------