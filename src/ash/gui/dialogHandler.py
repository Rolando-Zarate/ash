# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is a helper module to assist with various dialogs

from ash import *
from ash.gui import *

from ash.core.bufferManager import *
from ash.gui.modalDialog import *
from ash.gui.findReplaceDialog import *
from ash.gui.projectFindReplaceDialog import *
from ash.gui.checkbox import *
from ash.gui.listbox import *
from ash.gui.textfield import *
from ash.gui.treeview import TreeView
from ash.gui.label import *

class DialogHandler:
	def __init__(self, app):
		self.app = app

	# <--------------------------- Project-Wide Find and Replace --------------------------------->

	def invoke_project_find(self):
		mw = self.app.main_window
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 20, 70)
		except:
			self.app.warn_insufficient_screen_space()			
			return

		self.app.dlgProjectFind = ProjectFindReplaceDialog(mw, y, x, self.app.buffers)
		self.app.dlgProjectFind.show()
		mw.repaint()

	def invoke_project_find_and_replace(self):
		mw = self.app.main_window
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 20, 70)
		except:
			self.app.warn_insufficient_screen_space()			
			return

		self.app.dlgProjectFindReplace = ProjectFindReplaceDialog(mw, y, x, self.app.buffers, True)
		self.app.dlgProjectFindReplace.show()
		mw.repaint()

	# <----------------------------------- Find and Replace --------------------------------->

	def invoke_find(self):
		mw = self.app.main_window
		ed = mw.get_active_editor()
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 7, 50)
		except:
			self.app.warn_insufficient_screen_space()			
			return

		self.app.dlgFind = FindReplaceDialog(mw, y, x, ed)
		self.app.dlgFind.show()
		mw.repaint()

	def invoke_find_and_replace(self):
		mw = self.app.main_window
		ed = mw.get_active_editor()
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 9, 50)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgReplace = FindReplaceDialog(mw, y, x, ed, True)
		self.app.dlgReplace.show()
		mw.repaint()

	# <----------------------------------- Go to Line --------------------------------->

	def invoke_go_to_line(self):
		self.app.readjust()
		
		try:
			y, x = get_center_coords(self.app, 5, 25)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgGoTo = ModalDialog(self.app.main_window, y, x, 5, 25, "GO TO LINE", self.go_to_key_handler)
		currentLine = str(self.app.main_window.get_active_editor().curpos.y + 1)
		txtLineNumber = TextField(self.app.dlgGoTo, 3, 2, 21, currentLine, True, callback = self.go_to_live_preview_key_handler)
		self.app.dlgGoTo.add_widget("txtLineNumber", txtLineNumber)
		self.app.old_goto_curpos = copy.copy(self.app.main_window.get_active_editor().curpos)
		self.app.dlgGoTo.show()

	def go_to_key_handler(self, ch):
		if(KeyBindings.is_key(ch, "CLOSE_WINDOW")):
			self.app.main_window.get_active_editor().curpos = copy.copy(self.app.old_goto_curpos)
			self.app.dlgGoTo.hide()
			self.app.main_window.repaint()
		return ch

	def go_to_live_preview_key_handler(self, ch):
		if(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "FINALIZE_CHOICE") or str(chr(ch)) in ".0123456789"):
			isn = KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "FINALIZE_CHOICE")
			line = str(self.app.dlgGoTo.get_widget("txtLineNumber"))
			
			if(len(line) == 0):
				if(isn): 
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
				if(isn): 
					self.app.show_error("Invalid line number specified")
					return -1
				else:
					return ch
			
			aed = self.app.main_window.get_active_editor()
			if(row < 0 or row >= len(aed.buffer.lines)):
				beep()
			elif(col < 0 or col > len(aed.buffer.lines[row])):
				beep()
			else:
				if(isn): self.app.dlgGoTo.hide()
				aed.curpos.y = row
				aed.curpos.x = col
				self.app.main_window.repaint()				
		
		return ch

	# <----------------------------------- Close Editor/App --------------------------------->

	def invoke_forced_quit(self):
		self.app.session_storage.destroy()
		self.app.main_window.hide()

	def invoke_quit(self):
		mw = self.app.main_window
		aed = mw.get_active_editor()
		am = self.app.app_mode

		unsaved_count = self.app.buffers.get_true_unsaved_count()
		editor_count = mw.get_editor_count()
		
		if(unsaved_count == 0):
			if(editor_count <= 1 and am == APP_MODE_FILE):
				self.invoke_forced_quit()
			elif(editor_count == 0 and am == APP_MODE_PROJECT):
				self.invoke_forced_quit()
			else:
				mw.close_active_editor()
		else:
			if(aed != None): 
				mw.close_active_editor()
				return
			
			response = self.app.ask_question("SAVE/DISCARD ALL", "One or more unsaved files exist, choose:\nYes: save all filed-changes and quit\nNo: discard all unsaved changes and quit\nCancel: don't quit", True)
			if(response == None): return
			if(response): self.app.buffers.write_all_wherever_possible()
			
			self.invoke_forced_quit()
			
	# <--------------------------- Recent Files List ------------------------------>

	def invoke_recent_files(self):
		self.app.readjust()

		recent_files_list = self.app.session_storage.get_recent_files_list()
		
		if(len(recent_files_list) == 0):
			self.app.show_error("No recent files on record")
			return

		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgRecentFiles = ModalDialog(self.app.main_window, y, x, 20, 80, "RECENT FILES/PROJECTS", self.recent_files_key_handler)
		
		lblSearch = Label(self.app.dlgRecentFiles, 3, 2, "Search:")
		txtSearchFile = TextField(self.app.dlgRecentFiles, 3, 10, 68, callback=self.recent_files_search_text_changed)
		
		lblFiles = Label(self.app.dlgRecentFiles, 5, 2, "Recent Files:", gc("form-label") | curses.A_BOLD)		
		lstRecentFiles = ListBox(self.app.dlgRecentFiles, 6, 2, 38, 13, placeholder_text="(No recent files)")
		lblProjects = Label(self.app.dlgRecentFiles, 5, 41, "Recent Projects:", gc("form-label") | curses.A_BOLD)		
		lstRecentProjects = ListBox(self.app.dlgRecentFiles, 6, 41, 37, 13, placeholder_text="(No recent projects)")
		
		for i in range(len(recent_files_list)-1, -1, -1):
			disp = get_file_title(recent_files_list[i])
			if(os.path.isfile(recent_files_list[i])):
				lstRecentFiles.add_item(disp, tag=recent_files_list[i])
			elif(os.path.isdir(recent_files_list[i])):
				lstRecentProjects.add_item(disp, tag=recent_files_list[i])
			else:
				continue
			

		self.app.dlgRecentFiles.add_widget("lblSearch", lblSearch)
		self.app.dlgRecentFiles.add_widget("txtSearchFile", txtSearchFile)
		self.app.dlgRecentFiles.add_widget("lblFiles", lblFiles)
		self.app.dlgRecentFiles.add_widget("lstRecentFiles", lstRecentFiles)
		self.app.dlgRecentFiles.add_widget("lblProjects", lblProjects)
		self.app.dlgRecentFiles.add_widget("lstRecentProjects", lstRecentProjects)
		self.app.dlgRecentFiles.show()

	def recent_files_search_text_changed(self, ch):
		lstRecentFiles = self.app.dlgRecentFiles.get_widget("lstRecentFiles")
		lstRecentProjects = self.app.dlgRecentFiles.get_widget("lstRecentProjects")
		search_text = str(self.app.dlgRecentFiles.get_widget("txtSearchFile")).lower()
		recent_files_list = self.app.session_storage.get_recent_files_list()
		lstRecentFiles.clear()
		lstRecentProjects.clear()
		for i in range(len(recent_files_list)-1, -1, -1):
			disp = get_file_title(recent_files_list[i])
			if(os.path.isfile(recent_files_list[i])):
				if(len(search_text) == 0 or disp.lower().find(search_text) >= 0): lstRecentFiles.add_item(disp, tag=recent_files_list[i])
			elif(os.path.isdir(recent_files_list[i])):
				if(len(search_text) == 0 or disp.lower().find(search_text) >= 0): lstRecentProjects.add_item(disp, tag=recent_files_list[i])
			else:
				continue

	def recent_files_key_handler(self, ch):
		recent_files_list = self.app.session_storage.get_recent_files_list()

		if(KeyBindings.is_key(ch, "CLOSE_WINDOW") or KeyBindings.is_key(ch, "SHOW_RECENT_FILES")):
			self.app.dlgRecentFiles.hide()
			self.app.main_window.repaint()
			return -1
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "FINALIZE_CHOICE") or KeyBindings.is_key(ch, "LIST_MAKE_SELECTION")):
			mw = self.app.main_window

			filename = self.app.dlgRecentFiles.get_widget("lstRecentFiles").get_sel_tag()
			self.app.dlgRecentFiles.hide()
			mw.repaint()
			
			if(not os.path.isfile(filename)):
				if(os.path.isdir(filename)):
					self.app.dlgRecentFiles.hide()
					self.app.app_mode = APP_MODE_PROJECT
					self.app.project_dir = filename
					self.app.open_project(self.app.progress_handler)
					return -1
				else:
					self.app.show_error("The selected file/directory does not exist")
					mw.repaint()
					self.app.dlgRecentFiles.repaint()
					return -1

			if(BufferManager.is_binary(filename)):
				self.app.show_error("Cannot open binary file!")
				mw.repaint()
				self.app.dlgRecentFiles.repaint()
				return -1

			sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
			if(sel_buffer == None):
				sel_bid, sel_buffer = self.app.buffers.create_new_buffer(filename=filename, has_backup=BufferManager.backup_exists(filename))
				if(sel_bid == None or sel_buffer == None): return -1		# cancelled by user
			
			self.app.dlgRecentFiles.hide()
			mw.invoke_activate_editor(sel_buffer.id, sel_buffer)
			return -1
			
		return ch
	
	# <--------------------------- Set Preferences ------------------------------>

	def invoke_set_preferences(self):
		aed = self.app.main_window.get_active_editor()
		if(aed == None): return

		self.app.readjust()
		
		try:
			y, x = get_center_coords(self.app, 17, 35)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgPreferences = ModalDialog(self.app.main_window, y, x, 17, 35, "PREFERENCES", self.preferences_key_handler)
		current_tab_size = str(aed.tab_size)
		txtTabSize = TextField(self.app.dlgPreferences, 3, 2, 31, current_tab_size, True)
		lstEncodings = ListBox(self.app.dlgPreferences, 5, 2, 31, 5)
		chkShowLineNumbers = CheckBox(self.app.dlgPreferences, 11, 2, "Show line numbers")
		chkWordWrap = CheckBox(self.app.dlgPreferences, 12, 2, "Word wrap")
		chkHardWrap = CheckBox(self.app.dlgPreferences, 12, 18, "Hard wrap")
		chkStylize = CheckBox(self.app.dlgPreferences, 13, 2, "Syntax highlighting")
		chkAutoClose = CheckBox(self.app.dlgPreferences, 14, 2, "Complete matching pairs")
		chkShowScrollbars = CheckBox(self.app.dlgPreferences, 15, 2, "Show scrollbar")
		
		for enc in SUPPORTED_ENCODINGS:
			lstEncodings.add_item(("  " if aed.buffer.encoding != enc else TICK_MARK + " ") +  enc)
		
		chkShowLineNumbers.set_value(aed.show_line_numbers)
		chkWordWrap.set_value(aed.word_wrap)
		chkHardWrap.set_value(aed.hard_wrap)
		chkStylize.set_value(aed.should_stylize)
		chkAutoClose.set_value(aed.auto_close)
		chkShowScrollbars.set_value(aed.show_scrollbars)
		lstEncodings.sel_index = SUPPORTED_ENCODINGS.index(aed.buffer.encoding)
		
		self.app.dlgPreferences.add_widget("txtTabSize", txtTabSize)
		self.app.dlgPreferences.add_widget("lstEncodings", lstEncodings)
		self.app.dlgPreferences.add_widget("chkShowLineNumbers", chkShowLineNumbers)
		self.app.dlgPreferences.add_widget("chkWordWrap", chkWordWrap)
		self.app.dlgPreferences.add_widget("chkHardWrap", chkHardWrap)
		self.app.dlgPreferences.add_widget("chkStylize", chkStylize)
		self.app.dlgPreferences.add_widget("chkAutoClose", chkAutoClose)
		self.app.dlgPreferences.add_widget("chkShowScrollbars", chkShowScrollbars)
		
		self.app.dlgPreferences.show()

	def preferences_key_handler(self, ch):
		aed = self.app.main_window.get_active_editor()

		if(KeyBindings.is_key(ch, "CLOSE_WINDOW")):
			self.app.dlgPreferences.hide()
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "FINALIZE_CHOICE")):
			try:
				tab_size = int(str(self.app.dlgPreferences.get_widget("txtTabSize")))
			except:
				self.app.show_error("TAB SIZE", "Incorrect tab size: should be in [1,9]")
				return -1

			encoding_index = self.app.dlgPreferences.get_widget("lstEncodings").sel_index
			show_line_numbers = self.app.dlgPreferences.get_widget("chkShowLineNumbers").is_checked()
			word_wrap = self.app.dlgPreferences.get_widget("chkWordWrap").is_checked()
			hard_wrap = self.app.dlgPreferences.get_widget("chkHardWrap").is_checked()
			stylize = self.app.dlgPreferences.get_widget("chkStylize").is_checked()
			auto_close = self.app.dlgPreferences.get_widget("chkAutoClose").is_checked()
			show_scrollbars = self.app.dlgPreferences.get_widget("chkShowScrollbars").is_checked()

			self.app.dlgPreferences.hide()

			if(tab_size < 1 or tab_size > 9):
				self.app.show_error("TAB SIZE", "Incorrect tab size: should be in [1,9]")
				return -1

			aed.buffer.set_encoding(SUPPORTED_ENCODINGS[encoding_index])
			aed.set_preferences(tab_size, show_line_numbers, word_wrap, hard_wrap, stylize, auto_close, show_scrollbars)
			self.app.main_window.repaint()
			aed.repaint()
			return -1
		
		return ch

	# <----------------------------------- File New --------------------------------->

	def invoke_file_new(self):
		mw = self.app.main_window
		aed = mw.get_active_editor()

		# create blank buffer
		new_bid, new_buffer = self.app.buffers.create_new_buffer()
		open_in_new_tab = False
		if(aed != None and self.app.ask_question("CREATE IN NEW TAB", "Create buffer in new tab?")):
			open_in_new_tab = True
		mw.invoke_activate_editor(new_bid, new_buffer, open_in_new_tab)

	# <------------------------------------ Help --------------------------------------------->

	def invoke_help_about(self):
		self.app.readjust()
		try:
			y, x = get_center_coords(self.app, 13, 60)
		except:
			self.app.warn_insufficient_screen_space()
			return
		
		self.app.dlgHelp = ModalDialog(self.app.main_window, y, x, 13, 60, "ABOUT", self.help_key_handler)
		self.app.dlgHelp.add_widget("label1", Label(self.app.dlgHelp, 3, 2, "Ash text-editor", gc("form-label") | curses.A_BOLD))
		self.app.dlgHelp.add_widget("label1", Label(self.app.dlgHelp, 4, 2, "Version: " + ash.__version__ + " (Build: 6)", gc("form-label")))
		
		self.app.dlgHelp.add_widget("label2", Label(self.app.dlgHelp, 6, 2, "Copyright 2020, Akash Nag. All rights reserved.", gc("form-label")))
		self.app.dlgHelp.add_widget("label2", Label(self.app.dlgHelp, 7, 2, "Licensed under the MIT License", gc("form-label")))

		self.app.dlgHelp.add_widget("label2", Label(self.app.dlgHelp, 9, 2, "For more information, visit:", gc("form-label")))
		self.app.dlgHelp.add_widget("label2", Label(self.app.dlgHelp, 10, 2, "Website: https://akashnag.github.io", gc("form-label")))
		self.app.dlgHelp.add_widget("label2", Label(self.app.dlgHelp, 11, 2, "GitHub: https://github.com/akashnag/ash", gc("form-label")))
		
		self.app.dlgHelp.show()

	def invoke_help_key_bindings(self):
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgHelp = ModalDialog(self.app.main_window, y, x, 20, 80, "HELP", self.help_key_handler)
		lstKeys = ListBox(self.app.dlgHelp, 3, 2, 76, 16)

		kbs = KeyBindings.get_list_of_bindings()
		coms = self.app.command_interpreter.get_command_list()
		for kb in kbs:
			key = kb[0].ljust(16)
			desc = kb[1]
			lstKeys.add_item(key + desc)
		lstKeys.add_item(" ")
		lstKeys.add_item("Commands to be entered in command-window:", None, True)
		lstKeys.add_item(" ")
		for command, info in coms.items():
			lstKeys.add_item(command, None, True)
			lstKeys.add_item(info[1])
			lstKeys.add_item(" ")
		
		lstKeys.add_item("Custom colors can be set in $HOME/.ash-editor/theme.txt")
		lstKeys.add_item("Custom key mappings can be set in $HOME/.ash-editor/keymappings.txt")
		
		self.app.dlgHelp.add_widget("lstKeys", lstKeys)
		self.app.dlgHelp.show()

	def help_key_handler(self, ch):
		if(KeyBindings.is_key(ch, "CLOSE_WINDOW") or KeyBindings.is_key(ch, "SHOW_HELP")):
			self.app.dlgHelp.hide()
			self.app.main_window.repaint()
			return -1
		return ch

	# <----------------------------------- Project Explorer --------------------------------->

	def invoke_project_explorer(self):
		self.app.readjust()
		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return
		self.app.dlgProjectExplorer = ModalDialog(self.app.main_window, y, x, 20, 80, "PROJECT EXPLORER", self.project_explorer_key_handler)
		
		lblSearch = Label(self.app.dlgProjectExplorer, 3, 2, "Search:")
		txtSearchFile = TextField(self.app.dlgProjectExplorer, 3, 10, 68, callback=self.project_explorer_search_text_changed)
		lstFiles = TreeView(self.app.dlgProjectExplorer, 5, 2, 76, 14, self.app.buffers, self.app.project_dir)
		
		self.app.dlgProjectExplorer.add_widget("lblSearch", lblSearch)
		self.app.dlgProjectExplorer.add_widget("txtSearchFile", txtSearchFile)
		self.app.dlgProjectExplorer.add_widget("lstFiles", lstFiles)		
		self.app.dlgProjectExplorer.show()

	def project_explorer_search_text_changed(self, ch):
		lstFiles = self.app.dlgProjectExplorer.get_widget("lstFiles")
		search_text = str(self.app.dlgProjectExplorer.get_widget("txtSearchFile"))
		lstFiles.search(search_text)

	def project_explorer_key_handler(self, ch):
		lstFiles = self.app.dlgProjectExplorer.get_widget("lstFiles")
		
		mw = self.app.main_window
				
		if(KeyBindings.is_key(ch, "CLOSE_WINDOW") or KeyBindings.is_key(ch, "SHOW_PROJECT_EXPLORER")):
			self.app.dlgProjectExplorer.hide()
			mw.repaint()
			return -1
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "LIST_MAKE_SELECTION") or KeyBindings.is_key(ch, "FINALIZE_CHOICE")):
			tag = lstFiles.get_sel_tag()		# format: {d/f}:path
			if(tag == None): return -1
			file_type = tag[0].lower()
			filename = tag[2:]
			if(file_type == "d"): return -1
			
			if(BufferManager.is_binary(filename)):
				self.app.show_error("Cannot open binary file!")
				mw.repaint()
				self.app.dlgProjectExplorer.repaint()
				return -1

			sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
			if(sel_buffer == None):
				sel_bid, sel_buffer = self.app.buffers.create_new_buffer(filename=filename, has_backup=BufferManager.backup_exists(filename))
				if(sel_bid == None or sel_buffer == None): return -1		# cancelled by user
			
			self.app.dlgProjectExplorer.hide()
			mw.invoke_activate_editor(sel_buffer.id, sel_buffer)
			return -1
		
		return ch


	# <----------------------------------- File Open --------------------------------->

	def invoke_file_open(self, target_ed_index = -1):
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return
		
		self.app.dlgFileOpen = ModalDialog(self.app.main_window, y, x, 20, 80, "OPEN FILE", self.file_open_key_handler)
		
		lblFileName = Label(self.app.dlgFileOpen, 3, 2, "File/Folder:")
		txtFileName = TextField(self.app.dlgFileOpen, 3, 15, 63, str(os.getcwd()) + "/", callback=self.file_open_filename_changed)
		lstFiles = ListBox(self.app.dlgFileOpen, 5, 2, 76, 12, "(Empty directory)")
		lstEncodings = ListBox(self.app.dlgFileOpen, 18, 2, 76, 1)

		# add the encodings
		for enc in SUPPORTED_ENCODINGS:
			lstEncodings.add_item(enc)
		
		# set default encoding to UTF-8
		lstEncodings.sel_index = SUPPORTED_ENCODINGS.index("utf-8")

		self.app.dlgFileOpen.add_widget("lblFileName", lblFileName)
		self.app.dlgFileOpen.add_widget("txtFileName", txtFileName)
		self.app.dlgFileOpen.add_widget("lstFiles", lstFiles)
		self.app.dlgFileOpen.add_widget("lstEncodings", lstEncodings)
		
		self.file_open_filename_changed()

		self.app.target_open_ed_index = target_ed_index
		self.app.dlgFileOpen.show()

	def file_open_filename_changed(self, ch=None):
		filename = str(self.app.dlgFileOpen.get_widget("txtFileName"))
		lstFiles = self.app.dlgFileOpen.get_widget("lstFiles")

		filename = os.path.dirname(filename)
		if(os.path.isdir(filename)):
			lstFiles.clear()
			all_files = sorted(glob.glob(filename + "/*", recursive=False))
			for f in all_files:
				if(os.path.isfile(f)):
					lstFiles.add_item(get_file_title(f), tag=str(f))
				else:
					lstFiles.add_item(f"[{get_file_title(f)}]", tag=str(f), highlight=True)
			lstFiles.repaint()

	def file_open_key_handler(self, ch):
		txtFileName = self.app.dlgFileOpen.get_widget("txtFileName")
		lstFiles = self.app.dlgFileOpen.get_widget("lstFiles")
		lstEncodings = self.app.dlgFileOpen.get_widget("lstEncodings")

		sel_index = lstFiles.get_sel_index()
		sel_tag = lstFiles.get_sel_tag()
		mw = self.app.main_window
		aed = mw.get_active_editor()

		if(KeyBindings.is_key(ch, "CLOSE_WINDOW")):
			self.app.dlgFileOpen.hide()
			mw.repaint()
			return -1
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "LIST_MAKE_SELECTION") or KeyBindings.is_key(ch, "FINALIZE_CHOICE")):
			is_buffer = False
			sel_buffer = None

			if(lstFiles.is_in_focus and sel_index > -1):
				filename = sel_tag
				if(os.path.isfile(filename)):
					sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
					if(sel_buffer != None): is_buffer = True
			else:							
				filename = str(txtFileName)

			if(filename != None):
				if(os.path.isdir(filename)):
					self.app.dlgFileOpen.hide()
					self.app.app_mode = APP_MODE_PROJECT
					self.app.project_dir = filename
					# do not ask to restore session because files may have been modified already (since ash is already running and user may have been working on those files) and restoring edit history may clear that
					self.app.open_project(self.app.progress_handler, False)
					mw.repaint()
					return -1

				if(BufferManager.is_binary(filename)):
					self.app.show_error("Cannot open binary file!")
					mw.repaint()
					self.app.dlgFileOpen.repaint()
					return -1
			
			sel_encoding = str(lstEncodings)
			self.app.dlgFileOpen.hide()
			
			if(not is_buffer):
				# it is a file
				if(not os.path.isfile(filename)):
					# file does not exist on disk
					response = self.app.ask_question("CREATE FILE", "The selected file does not exist, create?")
					if(not response): return -1

				sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
				if(sel_buffer == None):
					# create buffer from file
					backup_status = BufferManager.backup_exists(filename)
					sel_bid, sel_buffer = self.app.buffers.create_new_buffer(filename=filename, encoding=sel_encoding, has_backup=backup_status)
					if(sel_bid == None or sel_buffer == None): return -1		# cancelled by user
				
			# at this point, buffer exists in sel_buffer
			open_in_new_tab = False
			if(aed != None and self.app.ask_question("OPEN IN NEW TAB", "Open file/buffer in new tab?")):
				open_in_new_tab = True
			mw.invoke_activate_editor(sel_buffer.id, sel_buffer, open_in_new_tab)
			return -1
		
		return ch

	# <-------------------------------- List active files ------------------------------->

	def invoke_list_active_files(self):
		self.app.readjust()
		try:
			y, x = get_center_coords(self.app, 14, 60)
		except:
			self.app.warn_insufficient_screen_space()
			return
		self.app.dlgActiveFiles = ModalDialog(self.app.main_window, y, x, 14, 60, "ACTIVE FILES/BUFFERS", self.active_files_key_handler)
		lstActiveFiles = ListBox(self.app.dlgActiveFiles, 3, 2, 56, 10, "(No active files)")
		
		# add the list of active files
		blist = self.app.buffers.get_list()
		for (bid, save_status, bname) in blist:
			lstActiveFiles.add_item((" " if save_status else UNSAVED_BULLET) + " " + get_file_title(bname), tag=bid)
			
		self.app.dlgActiveFiles.add_widget("lstActiveFiles", lstActiveFiles)
		self.app.dlgActiveFiles.show()

	def active_files_key_handler(self, ch):
		lstActiveFiles = self.app.dlgActiveFiles.get_widget("lstActiveFiles")
		
		sel_bid = lstActiveFiles.get_sel_tag()
		mw = self.app.main_window
		aed = mw.get_active_editor()

		if(KeyBindings.is_key(ch, "CLOSE_WINDOW")):
			self.app.dlgActiveFiles.hide()
			mw.repaint()
			return -1
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "LIST_MAKE_SELECTION")):
			sel_buffer = self.app.buffers.get_buffer_by_id(sel_bid)			
			self.app.dlgActiveFiles.hide()
			open_in_new_tab = False
			if(aed != None and self.app.ask_question("OPEN IN NEW TAB", "Open file/buffer in new tab?")):
				open_in_new_tab = True
			mw.invoke_activate_editor(sel_buffer.id, sel_buffer, open_in_new_tab)
			return -1
		
		return ch


	# <----------------------------------------------------------------------------------->

	# <----------------------------------- Show Active Tabs --------------------------------->

	def invoke_show_active_tabs(self):
		self.app.readjust()
		try:
			y, x = get_center_coords(self.app, 9, 40)
		except:
			self.app.warn_insufficient_screen_space()
			return
	
		self.app.dlgActiveTabs = ModalDialog(self.app.main_window, y, x, 9, 40, "ACTIVE TABS", self.show_active_tabs_key_handler)
		lstActiveTabs = ListBox(self.app.dlgActiveTabs, 3, 2, 36, 5, callback = self.active_tab_selection_changed)
		
		tabs_info = self.app.main_window.get_tabs_info()
		active_tab_index = self.app.main_window.get_active_tab_index()

		for i in range(len(tabs_info)):
			tab_name, ed_count = tabs_info[i]
			disp = tab_name + " (" + str(ed_count) + " editors)"
			if(i == active_tab_index):
				lstActiveTabs.add_item(TICK_MARK + " " + disp)
				lstActiveTabs.sel_index = i
			else:
				lstActiveTabs.add_item("  " + disp)
	
		self.app.old_active_tab_index = active_tab_index
		self.app.dlgActiveTabs.add_widget("lstActiveTabs", lstActiveTabs)
		self.app.dlgActiveTabs.show()

	def show_active_tabs_key_handler(self, ch):
		if(KeyBindings.is_key(ch, "CLOSE_WINDOW") or KeyBindings.is_key(ch, "SHOW_ACTIVE_TABS")):
			self.app.dlgActiveTabs.hide()
			self.app.main_window.switch_to_tab(self.app.old_active_tab_index)
			self.app.main_window.repaint()
			return -1
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "LIST_MAKE_SELECTION")):
			new_tab_index = self.app.dlgActiveTabs.get_widget("lstActiveTabs").get_sel_index()
			self.app.dlgActiveTabs.hide()
			self.app.main_window.switch_to_tab(new_tab_index)
			self.app.main_window.repaint()			
			return -1
			
		return ch

	def active_tab_selection_changed(self, new_tab_index):
		self.app.main_window.switch_to_tab(new_tab_index)
		self.app.main_window.repaint()

	# -------------------------------------------------------------------------------------
	
	def handle_save_all(self):
		unsaved_counter = self.app.buffers.write_all_wherever_possible()
		if(unsaved_counter > 0): self.app.show_error(f"{unsaved_counter} buffer(s) were not saved as\nthey have not been allotted files;\nyou must save them individually.", False)

	def handle_exit(self):
		self.app.main_window.close_all_tabs()
		self.invoke_quit()

	# <----------------------------------- File Save As ---------------------------------->

	def invoke_file_save_as(self, buffer):
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return
			
		self.app.dlgSaveAs = ModalDialog(self.app.main_window, y, x, 20, 80, "SAVE AS", self.file_save_as_key_handler)
		if(buffer.filename == None): 
			filename = str( self.app.project_dir if self.app.app_mode == APP_MODE_PROJECT else os.getcwd() ) + "/" + buffer.get_name()
		else:
			filename = get_copy_filename(buffer.filename)
		
		lblFileName = Label(self.app.dlgSaveAs, 3, 2, "Filename:")
		txtFileName = TextField(self.app.dlgSaveAs, 3, 12, 66, filename, callback=self.file_save_as_filename_changed)
		lstFiles = ListBox(self.app.dlgSaveAs, 5, 2, 76, 12, "(Empty directory)")

		self.app.dlgSaveAs_Buffer = buffer
		self.app.dlgSaveAs.add_widget("lblFileName", lblFileName)
		self.app.dlgSaveAs.add_widget("txtFileName", txtFileName)
		self.app.dlgSaveAs.add_widget("lstFiles", lstFiles)
		self.file_save_as_filename_changed()
		self.app.dlgSaveAs.show()

	def file_save_as_filename_changed(self, ch=None):
		filename = str(self.app.dlgSaveAs.get_widget("txtFileName"))
		lstFiles = self.app.dlgSaveAs.get_widget("lstFiles")

		filename = os.path.dirname(filename)
		if(os.path.isdir(filename)):
			lstFiles.clear()
			all_files = sorted(glob.glob(filename + "/*", recursive=False))
			for f in all_files:
				if(os.path.isfile(f)):
					lstFiles.add_item(get_file_title(f), tag=str(f))
				else:
					lstFiles.add_item(f"[{get_file_title(f)}]", tag=str(f), highlight=True)
			lstFiles.repaint()

	def file_save_as_key_handler(self, ch):
		if(KeyBindings.is_key(ch, "CLOSE_WINDOW")):
			self.app.dlgSaveAs.hide()
			return -1
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW") or KeyBindings.is_key(ch, "FINALIZE_CHOICE") or KeyBindings.is_key(ch, "LIST_MAKE_SELECTION")):
			buffer = self.app.dlgSaveAs_Buffer
			self.app.dlgSaveAs.hide()
			
			txtFileName = self.app.dlgSaveAs.get_widget("txtFileName")
			if(txtFileName.is_in_focus):
				filename = str(txtFileName)
			else:
				filename = self.app.dlgSaveAs.get_widget("lstFiles").get_sel_tag()

			if(not os.path.isfile(filename)):
				buffer.write_to_disk(filename)
			elif(not os.path.isdir(filename) and os.path.isfile(filename)):
				if(self.app.ask_question("REPLACE FILE", "File already exists, replace?")):
					buffer.write_to_disk(filename)
			else:
				self.app.show_error("Invalid filename!")
			return -1
					
		return ch

	# <-------------------------------- Command Palette -------------------------->

	def invoke_command_palette(self):
		self.app.command_interpreter.interpret_command(self.app.prompt("COMMAND", "Enter command:", width=50))