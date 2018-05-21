#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import copy
import gettext
import Core

#import Dialog
import dialog
import time
import threading
import os
from os.path import splitext


import gettext
gettext.textdomain('air-installer')
_ = gettext.gettext



RSRC="/usr/share/lliurex-abies2pmb/"
RSRC="/home/lliurex/trabajo/air-installer/src/"

CSS_FILE=RSRC + "air-installer.css"
DROP_FILE=RSRC+"rsrc/drop_file.png"
DROP_CORRECT=RSRC+"rsrc/drop_file_correct.png"
DROP_INCORRECT=RSRC+"rsrc/drop_file_incorrect.png"
OUTPUT_FILE="_pmb.sql"
DRAG_ACTION = Gdk.DragAction.COPY


class ConvertBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		self.commonFunc=CommonFunc()
		
		builder=Gtk.Builder()
		builder.set_translation_domain('air-installer')
		ui_path=RSRC + "rsrc/air-installer.ui"
		builder.add_from_file(ui_path)

		self.main_box=builder.get_object("install_data_box")
		self.drop=builder.get_object("drop_area_box")
		self.drop_label=builder.get_object("drop_label")
		self.inputfile_label=builder.get_object("inputfile_label")
		self.inputfile_entry=builder.get_object("filechooser_input")
#		self.outputpath_label=builder.get_object("outputpath_label")
#		self.outputpath_entry=builder.get_object("filechooser_output")
#		self.outputfile_label=builder.get_object("outputfile_label")
#		self.outputfile_label.set_width_chars(24)
#		self.outputfile_label.set_max_width_chars(24)
#		self.outputfile_label.set_xalign(-1)
#		self.outputfile_label.set_ellipsize(Pango.EllipsizeMode.START)
		
		self.install_button=builder.get_object("install_button")
		self.install_label=builder.get_object("install_label")
		
		self.check_window=builder.get_object("check_window")
		self.check_label=builder.get_object("check_label")
		self.check_pbar=builder.get_object("check_pbar")

#		drop_param=[self.inputfile_entry,self.outputpath_entry,self.outputfile_label,self.install_label,self.install_button]
		drop_param=[self.inputfile_entry,self.install_label,self.install_button]
		self.drop_area= DropArea(drop_param)
		self.drop.pack_start(self.drop_area, True,True,0)	
				
		self.pack_start(self.main_box,True,True,0)
	
		self.add_text_targets()
		self.connect_signals()
		self.set_css_info()
		self.install_button.set_sensitive(False)
#		self.outputpath_entry.set_sensitive(False)
		GObject.threads_init()

					
	#def __init__

	def _debug(self,msg):
		print("DBG: %s"%msg)

	def add_text_targets(self):

		self.drop_area.drag_dest_set_target_list(None)
		self.drop_area.drag_dest_add_text_targets()

    #def add_text_targets    
 
	def connect_signals(self):

		self.inputfile_entry.connect("file-set",self.input_file_changed)
#		self.outputpath_entry.connect("file-set",self.output_file_changed)
		self.install_button.connect("clicked",self.accept_convert_clicked)

	#def connect_signals	

	def set_css_info(self):

		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(CSS_FILE)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.drop_label.set_name("OPTION_LABEL")
		self.inputfile_label.set_name("OPTION_LABEL")
#		self.outputpath_label.set_name("OPTION_LABEL")
#		self.outputfile_label.set_name("OUTPUT_LABEL")
		self.check_label.set_name("MSG_LABEL")

	#def set_css_info	

	def input_file_changed(self,widget):

		entry=self.inputfile_entry.get_filename()
		check_extension=self.commonFunc.check_extension(entry)
#		param=[check_extension['status'],check_extension['code'],entry,self.outputpath_entry,self.outputfile_label,self.install_label,self.install_button]
		param=[check_extension['status'],check_extension['code'],self.install_label,self.install_button]

		self.commonFunc.manage_outputinfo(param)

	#def input_file_changed	
	
		
	def output_file_changed(self,widget):

		name=os.path.basename(self.inputfile_entry.get_filename()).strip(".mdb")+OUTPUT_FILE
		self.outputfile_label.set_text(name)	

	#def output_file_changed	

	def accept_convert_clicked(self,widget):
	
			#		check_outputpath=self.check_outputpath()

#		if check_outputpath["status"]:
		self.install_label.set_text("")
		self.install_t=threading.Thread(target=self.install)
		self.install_t.daemon=True
		self.install_t.start()
		self.check_window.show_all()
		GLib.timeout_add(100,self.pulsate_install)
#		else:
#			msg=self.commonFunc.get_msg(check_outputpath["code"])
#			self.install_label.set_text(msg)
#			self.install_label.set_name("MSG_ERROR_LABEL")

	#def accept_convert_clicked	

	def check_outputpath(self):
	
#		outputpath=self.outputpath_entry.get_filename()
		result={}
		result["status"]=""
		result["code"]=""
		return result	
		
		if os.access(outputpath,os.W_OK):	
			result["status"]=True
			
		else:
			result["status"]=False
			result["code"]=3

		return result	
	
	#def check_outputpath
 
	def pulsate_install(self):
	
		if self.install_t.is_alive():
			self.check_pbar.pulse()
			return True

		else:
			self.check_window.hide()
			if self.result_install["status"]:
				self.install_label.set_name("MSG_LABEL")
				msg=self.commonFunc.get_msg(4)
			else:
				self.install_label.set_name("MSG_ERROR_LABEL")
				msg=self.commonFunc.get_msg(self.result_install["code"])

				
			self.install_label.set_text(msg)
			
			return False

	#def pulsate_install		

	def install(self):
		inputfile=self.inputfile_entry.get_filename()
		print("INSTALL %s"%inputfile)
		self.result_install=self.core.airinstaller.install(inputfile)

	def convert(self):
		
		inputfile=self.inputfile_entry.get_filename()
		output_file=os.path.basename(inputfile).strip(".mdb").replace(' ' ,'_')+OUTPUT_FILE
		output_path=os.path.join(self.outputpath_entry.get_filename(),output_file)
		self.result_convert=self.core.abies2pmb.beginMigration(inputfile,output_path)
		
	#def convert
	
 #class ConvertBox	

		
class DropArea(Gtk.Image):

	def __init__(self,drop_param):
	
		self.drop=False
		self.commonFunc=CommonFunc()
		self.inputpath=drop_param[0]
		#self.origpathlabel=origpathlabel
#		self.destpath=drop_param[1]
#		self.outputfile_label=drop_param[2]
		self.install_label=drop_param[1]
		self.install_button=drop_param[2]
		Gtk.Image.__init__(self)
		Gtk.Image.set_from_file(self,DROP_FILE)
		self.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
		
		self.connect("drag-data-received", self.on_drag_data_received)
		self.text=""

    #def __init__		
	
	def _debug(self,msg):
		print("DropArea: %s"%msg)

	def on_drag_data_received(self, widget, drag_context, x,y, data,info, time):
		
		self.drop=True
		text = data.get_text()
		text=text.strip().split("//")
		
		text[1]=text[1].replace('%20',' ')
		self._debug("Checking %s"%text[1])
		check=self.commonFunc.check_extension(text[1])
		self.inputpath.set_filename(text[1])
		self.inputpath.set_sensitive(False)

		if check["status"]:
			Gtk.Image.set_from_file(self,DROP_CORRECT)
			
		else:

			Gtk.Image.set_from_file(self,DROP_INCORRECT)
			
#		param=[check['status'],check['code'],text[1],self.destpath,self.install_label,self.install_button]
#		param=[check['status'],check['code'],text[1],self.install_label,self.install_button]
		param={'status':check['status'],'code':check['code'],'file_name':text[1],'install_label':self.install_label,'install_button':self.install_button}
		self.commonFunc.manage_outputinfo(**param)	

	#def on_drag_data_received
	
#class DropArea		


class CommonFunc():

	def _debug(self,msg):
		print("%s"%msg)

	def check_extension(self,file_name):

		result={}
		result["status"]=""
		result["code"]=""
#		file_name=self.inputfile_entry.get_filename()
		
		if file_name ==None:
			result["status"]=False
			result["code"]=0
			
		else:
			
			try:	
				if file_name.endswith('.air'):
					result["status"]=True
				else:
					result["status"]=False
					result["code"]=1
				
			except:
				result["status"]=False
				result["code"]=2
				print ("Unable to detect extension"	)
	
		self._debug(result)
		return result	

	#def check_extension	

#	def manage_outputinfo(self,param):
	def manage_outputinfo(self,**kwargs):
		if kwargs:
			path=os.path.dirname(kwargs['file_name'])
			kwargs['install_button'].set_sensitive(True)
#			param[3].set_sensitive(True)
#			param[3].set_filename(path)
#			name=os.path.basename(param[2]).strip(".mdb").replace(' ','_')+OUTPUT_FILE
#			param[4].set_text(name)
#			param[5].set_text("")
#			param[6].set_sensitive(True)
#		if param[0]:
#			path=os.path.dirname(param[2])
#			param[3].set_sensitive(True)
#			param[3].set_filename(path)
#			name=os.path.basename(param[2]).strip(".mdb").replace(' ','_')+OUTPUT_FILE
#			param[4].set_text(name)
#			param[5].set_text("")
#			param[6].set_sensitive(True)
			
#		else:
#			msg=self.get_msg(param[1])
#			param[3].set_sensitive(False)
#			param[4].set_text("")
#			param[5].set_name("MSG_ERROR_LABEL")
#			param[5].set_text(msg)
#			param[6].set_sensitive(False)
			
	#def manage_ouputinfo	

	def get_msg(self,code):

		msg_text=''	
		if	code==0:
			msg_text=_("Error: No file upload to convert")
		
		elif code==1:
			msg_text=_("Error: File with incorret extension .mdb is required")

		elif code==2:
			msg_text=_("Error: Unable to detect file extension")

		elif code==3:
			msg_text=_("Error: Output path is not owned by user")	

		elif code==4:
			msg_text=_("Conversion successful")	

		elif code==10:
			msg_text=_("Error: Table not found in input file")

		elif code==11:
			msg_text=_("Error: Problem ocurred while importing input file")

		elif code==12:
			msg_text=_("Error: Problem exporting input file to csv")

		elif code==13:
			msg_text=_("Error: Problem generating intermediate sql file")

		elif code==14:
			msg_text=_("Error: Problem generating output file")
	
		elif code==15:
			msg_text=_("Error: No table in input file to virtual table")

		elif code==16:
			msg_text=_("Error: Couldn't fetch data from table")
	
		
		return msg_text		

	#deg get_msg	
