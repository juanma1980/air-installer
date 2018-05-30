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
import subprocess
import tempfile

import gettext
gettext.textdomain('air-installer')
_ = gettext.gettext



RSRC="/usr/share/air-installer/"

CSS_FILE=RSRC + "air-installer.css"
DROP_FILE=RSRC+"rsrc/drop_file.png"
DROP_CORRECT=RSRC+"rsrc/drop_file_correct.png"
DROP_INCORRECT=RSRC+"rsrc/drop_file_incorrect.png"
OUTPUT_FILE="_pmb.sql"
DRAG_ACTION = Gdk.DragAction.COPY
GTK_SPACING=6

class InstallBox(Gtk.VBox):
	
	def __init__(self):
		Gtk.VBox.__init__(self)
		self.DROP_CORRECT=RSRC+"rsrc/drop_file_correct.png"
		self.pb=GdkPixbuf.Pixbuf()
		self.air_file=''
		
		self.core=Core.Core.get_core()
		self.commonFunc=CommonFunc()
		
		builder=Gtk.Builder()
		builder.set_translation_domain('air-installer')
		ui_path=RSRC + "rsrc/air-installer.ui"
		builder.add_from_file(ui_path)

		self.lbl_air=builder.get_object("install_label")
		self.lbl_air.props.halign=Gtk.Align.START

		self.main_box=builder.get_object("install_data_box")
		self.drop=builder.get_object("btn_drop")
		self.drop.set_name("BTN_MENU")
		self.drop.connect('clicked',self._filechooser)
		self.drop_label=builder.get_object("drop_label")
		
		self.install_button=builder.get_object("install_button")
		self.install_label=builder.get_object("install_label")
		
		self.check_window=builder.get_object("check_window")
		self.check_label=builder.get_object("check_label")
		self.check_pbar=builder.get_object("check_pbar")

		drop_param=[self.install_label,self.install_button]
		self.drop_area=DropArea(drop_param)
		self.drop_area.set_info_label(self.lbl_air)
		drop_box=Gtk.Box(spacing=12)
		msg="<b>Drag</b> an air file\nor <b>click</b> to choose"
		lbl_drop=Gtk.Label()
		lbl_drop.set_markup(msg)
		drop_box.add(lbl_drop)
		drop_box.add(self.drop_area)
		drop_box.props.halign=Gtk.Align.CENTER
		self.drop.add(drop_box)	
		self.drop.set_margin_top(12)
				
		img_icon=Gtk.Image()
		img_icon.set_from_file(RSRC+"rsrc/air-installer_icon.png")
		self.pb=img_icon.get_pixbuf()

		lbl_text="Click to <b>select an icon</b> for the app or use the app's default icon"
		lbl_icon=Gtk.Label()
		lbl_icon.props.halign=Gtk.Align.END
		lbl_icon.props.hexpand=False
		lbl_icon.set_markup(lbl_text)
		lbl_icon.set_name('label')
		lbl_icon.set_max_width_chars(20)
		lbl_icon.set_width_chars(20)
		lbl_icon.set_line_wrap(True)

		self.box_icon=Gtk.Box(spacing=6)
		self.box_icon.add(lbl_icon)
		self.box_icon.add(img_icon)

		self.btn_icon=builder.get_object('btn_icon')
		self.btn_icon.set_name("BTN_MENU")
		self.box_icon.props.halign=Gtk.Align.CENTER
		self.btn_icon.add(self.box_icon)
		self.btn_icon.set_margin_top(12)


		self.pack_start(self.main_box,True,True,0)
	
		self.add_text_targets()
		self.connect_signals()
		self.set_css_info()
		self.install_button.set_sensitive(False)
		self.btn_icon.connect("clicked",self._set_app_icon,img_icon)
		self.lbl_air.connect("event",self._debug,"prueba")
		GObject.threads_init()
	#def __init__

	def _debug(self,msg):
		print("InstallBox: %s"%msg)
	#def _debug

	def _filechooser(self,*args):
		dw=Gtk.FileChooserDialog("Select air package",None,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		dw.set_action(Gtk.FileChooserAction.OPEN)
		file_filter=Gtk.FileFilter()
		file_filter.add_pattern('*.air')
		file_filter.set_name("Air files")
		dw.add_filter(file_filter)
		air_chooser=dw.run()
		if air_chooser==Gtk.ResponseType.OK:
			self.drop_area.air_file=dw.get_filename()
			self.drop_area.set_from_file(DROP_CORRECT)
			self.install_button.set_sensitive(True)
			self.lbl_air.set_markup("<b>Install:</b> %s"%os.path.basename(self.drop_area.air_file))
		dw.destroy()
	#def _filechooser

	def add_text_targets(self):
		self.drop_area.drag_dest_set_target_list(None)
		self.drop_area.drag_dest_add_text_targets()
	#def add_text_targets
	
	def _set_app_icon(self,widget,img_icon):
		
		def _update_preview(*arg):
			if dw.get_preview_filename():
				if os.path.isfile(dw.get_preview_filename()):
					pb=GdkPixbuf.Pixbuf.new_from_file_at_scale(dw.get_preview_filename(),64,-1,True)
					img_preview.set_from_pixbuf(pb)
					img_preview.show()
			else:
				img_preview.hide()

		dw=Gtk.FileChooserDialog("Select icon",None,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		dw.set_action(Gtk.FileChooserAction.OPEN)
		img_preview=Gtk.Image()
		img_preview.set_margin_right(GTK_SPACING)
		file_filter=Gtk.FileFilter()
		file_filter.add_pixbuf_formats()
		file_filter.set_name("images")
		dw.add_filter(file_filter)
		dw.set_preview_widget(img_preview)
		img_preview.show()
		dw.set_use_preview_label(False)
		dw.set_preview_widget_active(True)
		dw.connect("update-preview",_update_preview)
		new_icon=dw.run()
		if new_icon==Gtk.ResponseType.OK:
			pb=GdkPixbuf.Pixbuf.new_from_file_at_scale(dw.get_filename(),64,-1,True)
			img_icon.set_from_pixbuf(pb)
			self.pb=pb
		dw.destroy()
	#def _set_app_icon
 
	def connect_signals(self):
		self.install_button.connect("clicked",self.accept_install_clicked)
	#def connect_signals	

	def set_css_info(self):
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(CSS_FILE)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.check_label.set_name("MSG_LABEL")
	#def set_css_info	

	def accept_install_clicked(self,widget):
		self.install_label.set_text("")
		tmp_icon=tempfile.mkstemp()[1]
		self._debug(tmp_icon)
		#Copy the icon to temp folder
		self.pb.savev(tmp_icon,'png',[""],[""])
		air_file=self.drop_area.air_file
		self.install_t=threading.Thread(target=self.install,args=[air_file,tmp_icon])
		self.install_t.daemon=True
		self.install_t.start()
		self.check_window.show_all()
		GLib.timeout_add(100,self.pulsate_install)
	#def accept_install_clicked	

	def pulsate_install(self):
		if self.install_t.is_alive():
			self.check_pbar.pulse()
			return True

		else:
			self.check_window.hide()
			if self.install_err:
				self.install_label.set_name("MSG_LABEL")
				msg=self.commonFunc.get_msg(self.install_err)
			else:
				self.install_label.set_name("MSG_ERROR_LABEL")
				msg=self.commonFunc.get_msg(0)
				
			self.install_label.set_text(msg)
			
			return False
	#def pulsate_install		

	def install(self,air_file,icon):
		self.install_err=True
		subprocess.check_call(['/usr/bin/xhost','+'])
		try:
			ins=subprocess.check_call(['pkexec','/usr/share/air-installer/air-helper-installer.py','install',air_file,icon])
			self.install_err=False
		except Exception as e:
			self._debug(e)
		subprocess.check_call(['/usr/bin/xhost','-'])
	#def install
	
 #class InstallBox	

		
class DropArea(Gtk.Image):

	def __init__(self,drop_param):
		self.dbg=True
		self.drop=False
		self.commonFunc=CommonFunc()
		self.install_label=drop_param[0]
		self.install_button=drop_param[1]
		Gtk.Image.__init__(self)
		Gtk.Image.set_from_file(self,DROP_FILE)
		self.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
		self.air_file=''
		self.info_label=''
		
		self.connect("drag-data-received", self.on_drag_data_received)

		self.text=""
    #def __init__		
	
	def _debug(self,msg):
		if self.dbg:
			print("DropArea: %s"%msg)
	#def _debug

	def set_info_label(self,gtkLabel):
		self._debug("Label: %s"%gtkLabel)
		self.info_label=gtkLabel

	def on_drag_data_received(self, widget, drag_context, x,y, data,info, time):
		self.drop=True
		text = data.get_text()
		text=text.strip().split("//")
		
		text[1]=text[1].replace('%20',' ')
		self._debug("Checking %s"%text[1])
		check=self.commonFunc.check_extension(text[1])

		if check["status"]:
			Gtk.Image.set_from_file(self,DROP_CORRECT)
			self.install_button.set_sensitive(True)
			self.air_file=text[1]
			if self.info_label:
				self.info_label.set_markup("<b>Install:</b> %s"%os.path.basename(self.air_file))
			self._debug("File %s"%self.air_file)
		else:
			Gtk.Image.set_from_file(self,DROP_INCORRECT)
			self.install_button.set_sensitive(False)
			self.air_file=''
			
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

	def manage_outputinfo(self,**kwargs):
		if kwargs:
			path=os.path.dirname(kwargs['file_name'])
	#def manage_ouputinfo	

	def get_msg(self,code):
		msg_text=''	
		if code==0:
			msg_text=_("Installation successful")	
				
		elif code==1:
			msg_text=_("Error: File with incorret extension .air is required")

		elif code==2:
			msg_text=_("Error: Unable to detect file extension")

		elif code==3:
			msg_text=_("Error: Output path is not owned by user")	

		elif code==4:
			msg_text=_("Error: No file upload to install")
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
	#def get_msg	
