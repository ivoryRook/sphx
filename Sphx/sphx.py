# python 2 ubuntu 16.04 virtualbox 

from sphx_tools import XdoPy,GuiPiece
from sphx_data import SphxData
from Tkinter import *
import tkFileDialog
from ScrolledText import *
from PIL import Image, ImageTk
import time
import os,sys
import functools
import json


# to use run only in selenium script or other python script:
# from sphx import SphxRun
#
#
# if want to take screenshot within active window geometry only (save time)
# if active_window_bbox:
# x,y,w,h = self.xdopy.get_window_geometry(   )
# self.gooey.gui_bbox = [x,y,x+w,y+h]
# THRESHOLD IS MORE SENSITIVE -- MIGHT NEED TO INCREASE FOR SMALLER OBJECTS
# AND DECREASE FOR MORE OBLONG OBJECTS OR LARGER AND MORE DISTINCTIVE
# TRY TO AVOID OBLONG IMAGES, LONG OR TALL....
# IF REALLY NEEDED, LOWER THRESHOLD, BUT REMEMBER TO INCREASE AGAIN
# ALSO SUGGEST TO USER TO ZOOM IN ON WINDOW WITH SEND_KEYS
# consider adding a 'while_wait_do' to end of script line with wait
# for trial and error ... if clicking doesnt return something, try clicking every second
# until something returns

# CONSIDER CREATING AN OPTION TO CHAIN SCRIPTS TOGETHER
# DUE TO ONLY 50 GUI PIECE LIMIT

class SphxUI():

	def __init__(self,root):

		self.data = SphxData()
		self.xdopy = XdoPy()
		self.gooey = GuiPiece(self.data.MAIN_PATH,self.data.GUI_PIECE_DIR)
		self.script_dir = self.data.SCRIPT_DIR
		self.txt_dir = self.data.TXT_FILE_DIR
	
		# sphx data to reset upon new or fill upon load
		self.script_lines = []
		self.gui_pieces = []
		self.window_names = []
		self.passed_script_data = None
		self.text_file_pass = None
		self.return_data = None
		self.gui_piece_list_active = False
		self.script_fn = None
		
		# generate UI
		self.root = root
		self.master = Frame(self.root)
		self.master.grid()
		self.add_file_menu()
		self.create_script_pad()
		self.create_action_buttons()
		self.create_gui_pieces_list()	
		return

	def start(self):
		self.root.mainloop()
		return

	def _dummy(self):
		pass

	def _dummy_event(self,event,arg=None):
		pass

	# TOP MENU
	#
	#
	def add_file_menu(self):
		self.menubar = Menu(self.root)
		self.filemenu = Menu(self.menubar,tearoff=0)
		self.filemenu.add_command(label="New", command=self._new)
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Open...", command=self._open)
		self.filemenu.add_command(label="Save", command=lambda: self._save(saveas=False))
		self.filemenu.add_command(label="Save As...", command=lambda: self._save(saveas=True))
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Exit", command=self._regular_exit)
		self.menubar.add_cascade(label="File", menu=self.filemenu)
		self.helpmenu = Menu(self.menubar, tearoff=0)
		self.helpmenu.add_command(label="About", command=self._dummy)
		self.menubar.add_cascade(label="Help", menu=self.helpmenu)
		self.root.config(menu=self.menubar)
	def _clear_everything(self):
		self.script_pad.delete('1.0',END)
		for button in self.gui_piece_buttons:
			button.config(text='')
		for line in self.script_lines:
			if line[2]:
				self.script_pad.tag_delete(line[2]) 
		self.script_lines = []
		self.gui_pieces = []
		self.window_names = []
		self.passed_script_data = None
		self.return_data = None
		self.gui_piece_list_active = False	
	def _new(self):
		self.new_save = Toplevel()
		self.new_save.title('Save Script?')
		new_frame1 = Frame(self.new_save)
		new_frame1.grid(row=0,column=0)
		label = Label(new_frame1,text='Do you want to save your script before starting over?')
		label.grid()
		new_frame2 = Frame(self.new_save)
		new_frame2.grid(row=1,column=0)
		button = Button(new_frame2,text='Yes',
			command=lambda: self._new_save(0))
		button.grid(row=0,column=0)
		button = Button(new_frame2,text='No',
			command=lambda: self._new_save(1))
		button.grid(row=0,column=1)		
		button = Button(new_frame2,text='Cancel',
			command=lambda: self._new_save(2))	
		button.grid(row=0,column=2)
	def _new_save(self,answer):
		if answer==0:
			if self.script_fn:
				self._save()
			else:
				self._save(False)
			self._clear_everything()
			self.new_save.destroy()
		if answer==1:
			self._clear_everything()
			self.new_save.destroy()
		if answer==2:
			self.new_save.destroy()
	def _open(self):
		if self.script_lines == [] and self.gui_pieces == []:
			self._load_everything()
			return
		self.open_save = Toplevel()
		self.open_save.title('Save Script?')
		new_frame1 = Frame(self.open_save)
		new_frame1.grid(row=0,column=0)
		label = Label(new_frame1,text='Do you want to save your script before opening a saved one?')
		label.grid()
		new_frame2 = Frame(self.open_save)
		new_frame2.grid(row=1,column=0)
		button = Button(new_frame2,text='Yes',
			command=lambda: self._open_save(0))
		button.grid(row=0,column=0)
		button = Button(new_frame2,text='No',
			command=lambda: self._open_save(1))
		button.grid(row=0,column=1)		
		button = Button(new_frame2,text='Cancel',
			command=lambda: self._open_save(2))	
		button.grid(row=0,column=2)
	def _open_save(self,answer):
		if answer==0:
			if self.script_fn:
				self._save()
			else:
				self._save(False)
			self.open_save.destroy()
			self._load_everything()
		if answer==1:
			self.open_save.destroy()
			self._load_everything()
		if answer==2:
			self.open_save.destroy()
	def _load_everything(self):
		f = tkFileDialog.askopenfilename(initialdir=self.data.SCRIPT_DIR,title="Open Script",
			filetypes=(("sphx files","*.sphx"),("all files","*.*")))
		with open(f,'r') as openfile:
			sphx_dict = json.load(openfile)
		self.script_fn = f.rpartition('/')[2]
		openfile.close()
		self._clear_everything()
		self.script_lines = sphx_dict['script_lines']
		self.gui_pieces = sphx_dict['gui_pieces']
		button_index = 0
		for gui_piece in self.gui_pieces:
			gui_piece_text = '{0}. {1}'.format(button_index+1,gui_piece)
			self.gui_piece_buttons[button_index].config(text=gui_piece_text)
			button_index += 1
		for line in self.script_lines:
			line_number,script_text,tagname,tag_start,tag_end,script_data = line
			self.script_pad.insert(END,script_text+'\n')
			self._scanfix_script_lines(None)
	def _save(self,saveas=False):
		self._scanfix_script_lines(None)
		script_dict = {'script_lines' : self.script_lines,'gui_pieces' : self.gui_pieces}
		if not saveas and self.script_fn:
			with open(os.path.join(self.data.SCRIPT_DIR,self.script_fn),'w') as outfile:
				json.dump(script_dict, outfile)
				self.script_fn = outfile.name.rpartition('/')[2]
		if (saveas or not self.script_fn) or (saveas and not self.script_fn):
			outfile = tkFileDialog.asksaveasfile(mode='w', defaultextension='.sphx',
				initialdir = self.data.SCRIPT_DIR)
			if outfile is None:
				return
			json.dump(script_dict,outfile)
			outfile.close()
			self.script_fn = outfile.name.rpartition('/')[2]
	def _regular_exit(self):
		self.exit_save = Toplevel()
		self.exit_save.title('Save Script')
		exit_frame1 = Frame(self.exit_save)
		exit_frame1.grid(row=0,column=0)
		label = Label(exit_frame1,text='Do you want to save your script before exiting?')
		label.grid()
		exit_frame2 = Frame(self.exit_save)
		exit_frame2.grid(row=1,column=0)
		button = Button(exit_frame2,text='Yes',
			command=lambda: self._exit_save(0))
		button.grid(row=0,column=0)
		button = Button(exit_frame2,text='No',
			command=lambda: self._exit_save(1))
		button.grid(row=0,column=1)		
		button = Button(exit_frame2,text='Cancel',
			command=lambda: self._exit_save(2))	
		button.grid(row=0,column=2)
	def _exit_save(self,answer):
		if answer==0:
			if self.script_fn:
				self._save()
			else:
				self._save(False)
			self.root.quit()
		if answer==1:
			self.root.quit()
		if answer==2:
			self.exit_save.destroy()
	
	# SCRIPT PAD COLUMN
	#
	#
	def create_script_pad(self):
		script_pad_label = Label(self.master,text='SCRIPT BUILD (right-click for options)')
		script_pad_label.grid(row=0,column=1)
		self.script_pad = ScrolledText(self.master,width=75,height=32)
		self.script_pad.grid(row=1,column=1,sticky='nw')
		self.script_pad.bind('<KeyRelease>',self._scanfix_script_lines)
		self.print_button = Button(self.master,text='Print Script Line Data To Terminal',
			command=self._print_script_line_data)
		self.print_button.grid(row=2,column=1,sticky='nwes')
		return
	def _print_script_line_data(self):
		for line in self.script_lines:
			print(line[1])
	def _get_tag_data(self,line_count,line_text,script_data):
		tag_start = '{0}.{1}'.format(line_count,line_text.index(script_data))
		tag_end = '{0}.{1}'.format(line_count,line_text.index(script_data)+len(script_data))
		return tag_start,tag_end
	def _scanfix_script_lines(self,event):
		new_script_lines = []
		new_text = self.script_pad.get('1.0',END)
		new_text_lines = new_text.split('\n')
		line_count = 0
		gui_tags = []
		win_tags = []
		key_tags = []
		self.script_lines = []
		new_window_names = []
		for line in new_text_lines:
			line_count += 1
			if ';' and ' ' in line:
				line_text = line.rpartition(';')[0]
				line_pieces = line_text.split(' ')
				action = line_pieces[0]
				script_line_data = []
				if action in [a[0] for a in self.data.GUI_ACTIONS]:
					script_data = line_pieces[1]
					tag_index = len(gui_tags)
					tag_name = 'gui{0}'.format(tag_index)
					self.script_pad.tag_delete(tag_name)
					gui_tags.append(tag_name)
					tag_start,tag_end = self._get_tag_data(line_count,line_text,script_data)
					script_line_data = [line_count,line,tag_name,tag_start,tag_end,script_data]
					self.script_pad.tag_add(tag_name,tag_start,tag_end)
					self.script_pad.tag_config(tag_name, background='blue',foreground='white')
					self.script_pad.tag_bind(tag_name, '<Button-3>', 
						lambda event, arg=script_line_data:
							self._gui_piece_menu_popup(event,arg))
				if action in [a[0] for a in self.data.WINDOW_ACTIONS]:
					script_data = line_pieces[1]
					tag_index = len(win_tags)
					tag_name = 'win{0}'.format(tag_index)	
					self.script_pad.tag_delete(tag_name)
					win_tags.append(tag_name)
					tag_start,tag_end = self._get_tag_data(line_count,line_text,script_data)
					script_line_data = [line_count,line,tag_name,tag_start,tag_end,script_data]
					if action == 'name_active_window':
						new_window_names.append(script_data)
						self.script_pad.tag_add(tag_name,tag_start,tag_end)
						self.script_pad.tag_config(tag_name, background='gray',foreground='white')
					else:
						self.script_pad.tag_add(tag_name,tag_start,tag_end)
						self.script_pad.tag_config(tag_name, background='pink',foreground='white')
						self.script_pad.tag_bind(tag_name, '<Button-3>', 
							lambda event, arg=script_line_data:
								self._window_menu_popup(event,arg))
				if action in [a[0] for a in self.data.KEYBOARD_ACTIONS]:
					script_data = line_text.partition(' ')[2]
					tag_index = len(key_tags)
					tag_name = 'key{0}'.format(tag_index)	
					key_tags.append(tag_name)
					tag_start,tag_end = self._get_tag_data(line_count,line_text,script_data)
					script_line_data = [line_count,line,tag_name,tag_start,tag_end,script_data]
					self.script_pad.tag_add(tag_name,tag_start,tag_end)
					if 'type' in action:
						tag_bg,tag_fg ='green','white'
					else:
						tag_bg,tag_fg ='green','yellow'
					self.script_pad.tag_config(tag_name,background=tag_bg,foreground=tag_fg)
					self.script_pad.tag_bind(tag_name, '<Button-3>', 
						lambda event, arg=script_line_data:
							self._text_piece_popup(event,arg))	
				if action in [a[0] for a in self.data.OTHER_ACTIONS]:
					script_data = None
					tag_name = None
					tag_start,tag_end = None,None
					script_line_data = [line_count,line,tag_name,tag_start,tag_end,script_data]
				if len(script_line_data) > 0:
					self.script_lines.append(script_line_data)
		self.window_names = sorted(new_window_names)
		if len(self.window_names) == 0:
			self.action_buttons_list[15].config(state=DISABLED)
			self.action_buttons_list[16].config(state=DISABLED)
		else:
			if not self.gui_piece_list_active:
				self.action_buttons_list[15].config(state='normal')
				self.action_buttons_list[16].config(state='normal')
		return

	# ACTION BUTTONS COLUMN
	#
	#
	def create_action_buttons(self):
		action_buttons_label = Label(self.master,text='SCRIPT ACTIONS')
		action_buttons_label.grid(row=0,column=2)		
		self.action_buttons = Frame(self.master)
		self.action_buttons.grid(row=1,column=2,sticky='nw')
		self.auto_snap = IntVar()
		self.auto_snap.set(1)
		self.auto_snap_check = Checkbutton(self.action_buttons,text='Auto-snap',variable=self.auto_snap)
		self.auto_snap_check.grid(row=0,column=2)
		self.action_buttons_list = []
		action_index = 0
		for i in range(3):
			for j in range(3):
				button = Button(self.action_buttons,text=self.data.GUI_ACTIONS[action_index][0],pady=5,
					command=functools.partial(self._append_gui_piece_action,self.data.GUI_ACTIONS[action_index][1]))
				button.grid(row=i+1,column=j,sticky='nwes')
				action_index += 1
				self.action_buttons_list.append(button)
		action_index = 0
		for i in range(2):
			for j in range(3):
				if i==0 and j==0:
					continue
				button = Button(self.action_buttons,text=self.data.KEYBOARD_ACTIONS[action_index][0],pady=5,
					command=functools.partial(self._append_text_piece_action,self.data.KEYBOARD_ACTIONS[action_index][1]))
				button.grid(row=i+4,column=j,sticky='nwes')
				self.action_buttons_list.append(button)
				action_index += 1
		action_index = 0
		for j in range(3):		
			button = Button(self.action_buttons,text=self.data.WINDOW_ACTIONS[action_index][0],pady=5,
				command=functools.partial(self._append_window_action,self.data.WINDOW_ACTIONS[action_index][1]))
			button.grid(row=6,column=j,sticky='nwes')
			if j > 0:
				button.config(state=DISABLED)
			self.action_buttons_list.append(button)
			action_index += 1
		action_index = 0
		for j in range(2):		
			button = Button(self.action_buttons,text=self.data.OTHER_ACTIONS[action_index][0],pady=5,
				command=functools.partial(self._append_other_action,self.data.OTHER_ACTIONS[action_index][1]))
			button.grid(row=7,column=j+1,sticky='nwes')
			self.action_buttons_list.append(button)
			action_index += 1
		# insert another layer for hover-over data about script action

		return

	# GUI PIECES COLUMN
	#
	#
	def create_gui_pieces_list(self):
		gui_pieces_label = Label(self.master,text='GUI PIECES (click to view)')
		gui_pieces_label.grid(row=0,column=0)
		self.gui_piece_buttons = []
		self.gui_pieces_pad = Frame(self.master)
		self.gui_pieces_pad.grid(row=1,column=0,sticky='nw')
		button_index = 0
		for j in range(2):
			for i in range(25):
				new_button = Button(self.gui_pieces_pad,text='',bg='blue',fg='white',borderwidth=0,width=15,padx=0,pady=0,
					command=functools.partial(self._gui_piece_button_click,button_index))
				button_index += 1
				new_button.grid(row=i,column=j,sticky='w')
				self.gui_piece_buttons.append(new_button)
		self.gui_piece_extras = Frame(self.master)
		self.gui_piece_extras.grid(row=2,column=0,sticky='nwes')
		self.take_new_gui_piece_button = Button(self.gui_piece_extras,text='Take New',
			command=self._get_gui_piece)
		self.take_new_gui_piece_button.grid(row=0,column=0,sticky='nwes')
		# TO FINISH -- LOAD BUTTON
		self.load_png_gui_piece_button = Button(self.gui_piece_extras,text='Load Png',
			command=self._dummy)
		self.load_png_gui_piece_button.config(state=DISABLED)
		self.load_png_gui_piece_button.grid(row=0,column=1,sticky='nwes')		
		# TO FINISH -- REMOVE BUTTON
		self.remove_gui_piece_button = Button(self.gui_piece_extras,text='Remove',
			command=lambda: self._activate_gui_pieces_list(None))
		self.remove_gui_piece_button.grid(row=0,column=2,sticky='nwes')	
		return	
	def _append_gui_pieces_list(self,gui_piece):
		gui_piece_text = '{0}. {1}'.format(len(self.gui_pieces)+1,gui_piece)
		self.gui_piece_buttons[len(self.gui_pieces)].config(text=gui_piece_text)
		self.gui_pieces.append(gui_piece)
		return
	def _remove_gui_piece(self,button_index):
		removed_gui_piece = self.gui_pieces.pop(button_index)
		if button_index < len(self.gui_pieces):
			for replace_index in range(button_index,len(self.gui_pieces)):
				self.gui_piece_buttons[replace_index].config(text='{0}. {1}'.format(replace_index+1,self.gui_pieces[replace_index]))
		self.gui_piece_buttons[len(self.gui_pieces)].config(text='')
		for index in range(len(self.script_lines)):
			line_data = self.script_lines[index][-1]
			if line_data == removed_gui_piece:
				data = '<right-click>',self.script_lines[index]
				self._replace_gui_piece(data)
		return
	def _activate_gui_pieces_list(self,script_line_data):
		if len(self.gui_pieces):
			for button in self.gui_piece_buttons:
				button.config(fg='white',bg='red')
			self.script_pad.config(state=DISABLED)
			self.print_button.config(state=DISABLED)
			for button in self.action_buttons_list:
				button.config(state=DISABLED)
			self.take_new_gui_piece_button.config(state=DISABLED)
			# self.load_png_gui_piece_button.config(state=DISABLED)
			self.remove_gui_piece_button.config(state=DISABLED)
			self.gui_piece_list_active = True
			self.passed_script_data = script_line_data
	def _gui_piece_button_click(self,button_index):
		if button_index < len(self.gui_pieces):
			gui_piece = self.gui_pieces[button_index]
			if not self.gui_piece_list_active:
				self._display_gui_piece(gui_piece)
			else:
				if self.passed_script_data:
					script_line_data = self.passed_script_data
					data = gui_piece,script_line_data
					self._replace_gui_piece(data)
				else:
					self._remove_gui_piece(button_index)
				for button in self.gui_piece_buttons:
					button.config(bg='blue',fg='white')
				self.print_button.config(state='normal')
				for button in self.action_buttons_list:
					button.config(state='normal')
				if len(self.window_names) == 0:
					self.action_buttons_list[15].config(state=DISABLED)
					self.action_buttons_list[16].config(state=DISABLED)
				self.take_new_gui_piece_button.config(state='normal')
				# self.load_png_gui_piece_button.config(state='normal')
				self.remove_gui_piece_button.config(state='normal')
				self.gui_piece_list_active = False

	#     -- gui piece action functions --
	#
	#
	def _append_gui_piece_action(self,script_text):
		if self.auto_snap.get():
			gui_piece = self._get_gui_piece()
		else:
			gui_piece = '<right-click>'
		script_line = script_text.format(gui_piece)
		self.script_pad.insert(END,script_line)
		self._scanfix_script_lines(None)
	def _gui_piece_menu_popup(self,event,script_line_data):
	 	self.popup_menu1 = Menu(self.root,tearoff=0)
	 	self.popup_menu1.add_command(label='View',
			command=functools.partial(self._display_gui_piece,script_line_data[-1]))
		self.popup_menu1.add_command(label='Take New',
			command=functools.partial(self._sub_new_gui_piece,script_line_data))
	 	self.popup_menu1.add_command(label='Choose From Others',
			command=functools.partial(self._activate_gui_pieces_list,script_line_data))
	 	self.popup_menu1.post(event.x_root,event.y_root)
	 	self.master.bind('<Button-1>',self._destroy_gui_piece_menu)
	 	self.master.bind('<Button-3>',self._destroy_gui_piece_menu)
	 	self.script_pad.bind('<Enter>',self._destroy_gui_piece_menu)
	def _get_gui_piece(self):
		self.root.iconify()
		self.gooey.take_new_gui_piece()
		self.root.deiconify()
		gui_piece = self.gooey.gui_piece_filename
		self._append_gui_pieces_list(gui_piece)
		return gui_piece
	def _display_gui_piece(self,gui_piece):
		if gui_piece != '<right-click>':
			self.img_viewer = Toplevel()
			self.img_viewer.title(gui_piece)
			img_open = Image.open(os.path.join(self.data.GUI_PIECE_DIR,gui_piece))
			img = ImageTk.PhotoImage(img_open)
			img_label = Label(self.img_viewer,image=img)
			img_label.image = img
			img_label.grid(row=0,column=0,padx=20,pady=20)
	def _replace_gui_piece(self,data):
		new_gui_piece,script_line_data = data
		line_number,script_text,gui_tagname,gui_tag_start,gui_tag_end,gui_piece = script_line_data
		self.script_pad.config(state='normal')
		self.script_pad.delete(gui_tag_start,gui_tag_end)
		self.script_pad.insert(gui_tag_start,new_gui_piece)
		self._scanfix_script_lines(None)
	def _sub_new_gui_piece(self,gui_tag_data):
		data = self._get_gui_piece(),gui_tag_data
		self._replace_gui_piece(data)
	def _destroy_gui_piece_menu(self,event):
	 	self.popup_menu1.destroy()

	#     -- window action functions --
	#				
	#
	def _append_window_action(self,script_text):
		if script_text.split(' ')[0] == 'name_active_window':	
			if len(self.window_names) == 0:
				self.action_buttons_list[13].config(state='normal')
				self.action_buttons_list[14].config(state='normal')
			window_name = 'window{0}'.format(str(len(self.window_names)).zfill(2))
			self.window_names.append(window_name)
		else:
			window_name = self.window_names[-1]
		script_line = script_text.format(window_name)
		self.script_pad.insert(END,script_line)
		self._scanfix_script_lines(None)
	def _window_menu_popup(self,event,script_line_data):
	 	self.popup_menu2 = Menu(self.root,tearoff=0)
	 	for other_window_name in self.window_names:
	 		data = other_window_name,script_line_data
	 		self.popup_menu2.add_command(label=other_window_name,
				command=functools.partial(self._replace_window_name,data))
	 	self.popup_menu2.post(event.x_root,event.y_root)
	 	self.master.bind('<Button-1>',self._destroy_window_name_menu)
	 	self.master.bind('<Button-3>',self._destroy_window_name_menu)
	 	self.script_pad.bind('<Enter>',self._destroy_window_name_menu)	
	def _replace_window_name(self,data):
		self.popup_menu2.destroy()
		new_window_name,script_line_data = data
		line_number,script_text,win_tagname,win_tag_start,win_tag_end,window_name = script_line_data
		self.script_pad.delete(win_tag_start,win_tag_end)
		self.script_pad.insert(win_tag_start,new_window_name)
		self._scanfix_script_lines(None)
	def _destroy_window_name_menu(self,event):
	 	self.popup_menu2.destroy()

	#     -- type_text action functions --
	#				 
	#
	def _append_text_piece_action(self,script_text):
		text_piece = '<right-click>'
		script_line = script_text.format(text_piece)
		self.script_pad.insert(END,script_line)
		self._scanfix_script_lines(None)	
					
	def _text_piece_popup(self,event,data):
		open_text_file = False
		text_piece = data[-1]
		if text_piece == '<right-click>':
			text_piece = ''
		
		if 'type' in data[1]:
			if 'type_text_file' in data[1]:
				open_text_file = True
			else:
				text_type_title = 'Text to Type:'
		else:
			text_type_title = 'Key(s) to Press:'
		if not open_text_file:
			self.get_text = Toplevel()
			self.get_text.title(text_type_title)
			self.text_entry = Entry(self.get_text,text=text_piece,width=75,font=("Helvetica",12))
			self.text_entry.grid()
			self.text_entry.bind('<Return>',
				lambda event, arg=data: self._replace_text_piece(event,arg))
		else:
			self._open_text_file(data)

	def _open_text_file(self,script_line_data):
		f = tkFileDialog.askopenfilename(initialdir=self.data.TXT_FILE_DIR,title="Open Text File",
			filetypes=(("txt files","*.txt"),("all files","*.*")))
		if f is None:
			return
		with open(f,'r') as openfile:
			text_from_file = openfile.read()
		self.text_file_pass = f.rpartition('/')[2]
		self._replace_text_piece(None,script_line_data)
		return
	
	def _replace_text_piece(self,event,data):
		line_number,script_text,text_tagname,text_tag_start,text_tag_end,text_piece = data
		if 'type_text_file' in script_text:
			new_text_piece = self.text_file_pass
		else:
			new_text_piece = self.text_entry.get()
			self.get_text.destroy()
		self.script_pad.config(state='normal')
		self.script_pad.delete(text_tag_start,text_tag_end)
		self.script_pad.insert(text_tag_start,new_text_piece)
		self._scanfix_script_lines(None)		


	#     -- sleep & other action functions --
	#				
	#
	def _append_other_action(self,script_text):
		script_line = script_text
		self.script_pad.insert(END,script_line)
		self._scanfix_script_lines(None)



class SphxRun():
	
	def __init__(self,threshold=0.9):
		self.data = SphxData()
		self.xdopy = XdoPy()
		self.gooey = GuiPiece(self.data.MAIN_PATH,self.data.GUI_PIECE_DIR)
		self.gooey.threshold = threshold
		self.script_dir = self.data.SCRIPT_DIR		
		self.script_lines = []
		self.gui_pieces = []
		self.cv_gui_pieces_dict = {}
		self.window_name_links = {}
		return
	
	def run_script(self,root=None):
		finished_script = True
		self.line_failed = False
		for line in self.script_lines:
			script_text = line[1]
			line_data = line[-1]
			if ';' in script_text:
				script_text = script_text[:-1]
				action = script_text[:-1].split(' ')[0]
				if action=='exists?':
					self.exists(line_data)
				if action=='wait_to_appear':
					max_wait = int(script_text.rpartition('=')[2])
					self.wait_to_appear(line_data,max_wait)
				if action=='wait_to_disappear':
					max_wait = int(script_text.rpartition('=')[2])
					self.wait_to_disappear(line_data,max_wait)
				if action=='click':
					button = script_text.rpartition('=')[2]
					self.click(line_data,button)				
				if action=='double_click':
					button = script_text.rpartition('=')[2]
					self.double_click(line_data,button)
				if action=='rapid_click':
					button = script_text.partition('=')[2].partition(' clicks')[0]
					clicks = script_text.rpartition('=')[2]
					self.double_click(line_data,button,clicks)				
				if action=='mouse_hold':
					button = script_text.rpartition('=')[2]
					self.mousedown(line_data,button)
				if action=='mouse_release':
					button = script_text.rpartition('=')[2]
					self.mouseup(line_data,button)
				if action=='hover':
					self.hover(line_data)				
				if action=='type_text':
					self.type_text(line_data)			
				if action=='type_text_file':
					self.type_text_file(line_data)
				if action=='send_key':
					self.send_key(line_data)
				if action=='send_keydown':
					self.send_keydown(line_data)
				if action=='send_keyup':
					self.send_keyup(line_data)
				if action=='name_active_window':
					self.name_active_window(line_data)
				if action=='activate_window':
					self.activate_window(line_data)
				if action=='minimize_window':
					self.minimize_window(line_data)
				if action=='set_threshold':
					threshold = float(script_text.rpartition('=')[2])/100.0
					self.gooey.threshold = threshold
				if action=='sleep':
					how_long = int(script_text.rpartition('=')[2])
					time.sleep(how_long)
			if self.line_failed:
				print('action failed, ending script')
				finished_script = False
				break
		return finished_script

	def load_script(self,sphx_file):
		self.sphx_file = sphx_file
		with open(os.path.join(self.script_dir,sphx_file),'r') as openfile:
			sphx_dict = json.load(openfile)
		self.script_lines = sphx_dict['script_lines']
		self.gui_pieces = sphx_dict['gui_pieces']
		self.convert_gui_pieces()
		return

	def convert_gui_pieces(self):
		for gui_piece in self.gui_pieces:
			self.cv_gui_pieces_dict[gui_piece] = self.gooey.convert_png_to_cv(gui_piece)

	def exists(self,gui_piece):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		does_exist = False
		if self.gooey.get_current_locations():
			print('{0} exists!'.format(gui_piece))
			does_exist = True
		else:
			print('{0} does not exist!'.format(gui_piece))
			does_exist = False
			self.line_failed = True
		return does_exist

	def wait_to_appear(self,gui_piece,max_wait):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		print('waiting {0} seconds for {1} to appear'.format(max_wait,gui_piece))
		is_found = self.gooey.wait_for_template(max_wait)
		if is_found:
			print('appeared!')
		else:
			print('not there...')
			self.line_failed = True
		return is_found

	def wait_to_disappear(self,gui_piece,max_wait):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		print('waiting {0} seconds for {1} to disappear'.format(max_wait,gui_piece))		
		has_disappeared = self.gooey.wait_for_template_disappear(max_wait)
		if is_found:
			print('disappeared!')
		else:
			print('still there...')
			self.line_failed = True
		return has_disappeared
	
	def click(self,gui_piece,button):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		centers = self.gooey.get_current_locations()
		if centers:
			click_x,click_y = centers[0]
			self.xdopy.mouse_moveto_click(click_x,click_y,button)
			if len(centers)>1:
				print('multiple nearly identical gui_pieces')
				print centers
			return True
		else:
			print('gui piece not there')
			self.line_failed = True
			return False
	
	def double_click(self,gui_piece,button):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		centers = self.gooey.get_current_locations()
		if centers:
			click_x,click_y = centers[0]
			self.xdopy.mouse_moveto_click(click_x,click_y,button,click_count=2)
			if len(centers)>1:
				print('multiple nearly identical gui_pieces')
			return True
		else:
			print('gui piece not there')
			self.line_failed = True
			return False
	
	def rapid_click(self,gui_piece,button,clicks):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		centers = self.gooey.get_current_locations()
		if centers:
			click_x,click_y = centers[0]
			self.xdopy.mouse_moveto_click(click_x,click_y,button,click_count=int(clicks))
			if len(centers)>1:
				print('multiple nearly identical gui_pieces')
			return True
		else:
			print('gui piece not there')
			self.line_failed = True
			return False		
		pass
	
	def mousedown(self,gui_piece,button):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		centers = self.gooey.get_current_locations()
		if centers:
			click_x,click_y = centers[0]
			self.xdopy.mouse_moveto_down(click_x,click_y,button)
			if len(centers)>1:
				print('multiple nearly identical gui_pieces')
			return True
		else:
			print('gui piece not there')
			self.line_failed = True
			return False

	def mouseup(self,gui_piece,button):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		centers = self.gooey.get_current_locations()
		if centers:
			click_x,click_y = centers[0]
			self.xdopy.mouse_moveto_up(click_x,click_y,button)
			if len(centers)>1:
				print('multiple nearly identical gui_pieces')
			return True
		else:
			print('gui piece not there')
			self.line_failed = True
			return False
	
	def hover(self,gui_piece):
		self.gooey.load_saved_gui_piece_cv(self.cv_gui_pieces_dict[gui_piece])
		centers = self.gooey.get_current_locations()
		if centers:
			moveto_x,moveto_y = centers[0]
			self.xdopy.mouse_moveto(moveto_x,moveto_y)
			if len(centers)>1:
				print('multiple nearly identical gui_pieces')
			return True
		else:
			print('gui piece not there')
			self.line_failed = True
			return False
	
	def type_text(self,type_text):
		print type_text
		self.xdopy.type_to(type_text)
		return True

	def type_text_file(self,type_text_file):
		with open(os.path.join(self.data.TXT_FILE_DIR,type_text_file),'r') as openfile:
			text_from_file = openfile.read()
		self.xdopy.type_to(text_from_file)
		return True

	def send_key(self,key_to_send):
		print key_to_send
		self.xdopy.send_key(key_to_send)
		return True

	def send_keydown(self,key_to_send):
		print key_to_send
		self.xdopy.send_keydown(key_to_send)
		return True	
		
	def send_keyup(self,key_to_send):
		print key_to_send
		self.xdopy.send_keyup(key_to_send)
		return True

	def name_active_window(self,window_name):
		self.xdopy.get_active_window()
		active_window = self.xdopy.active_window_id
		self.window_name_links[window_name] = active_window
		print self.window_name_links[window_name]
		return self.window_name_links[window_name]
	
	def minimize_window(self,window_name):
		self.xdopy.minimize_window(self.window_name_links[window_name])
		return		

	def activate_window(self,window_name):
		self.xdopy.activate_window(self.window_name_links[window_name])
		return  


if __name__ == '__main__':
	root = Tk(className="sphx")
	sphx = SphxUI(root)
	sphx.start()

