#!/usr/bin/python3
###

import sys
import subprocess
import os
import gi
import threading
import tempfile
import time
import airmanager.airmanager as installer
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import gettext
gettext.textdomain('air-installer')
_ = gettext.gettext

RSRC="/usr/share/air-installer/rsrc"
CSS_FILE=RSRC + "air-installer.css"
GTK_SPACING=6

class confirmDialog(Gtk.Window):
	def __init__(self,air_file):
		self._load_gui(air_file)
	#def __init__

	def _debug(self,msg):
		print("air_installer: %s"%msg)
	#def _debug

	def _load_gui(self,air_file):
		air_file_path=os.path.abspath(air_file)
		self._debug("Installing %s (%s)"%(air_file,air_file_path))
		file_name=os.path.basename(air_file)
		Gtk.Window.__init__(self,title=_("Install air app"))
		self.set_position(Gtk.WindowPosition.CENTER)
		style_provider=Gtk.CssProvider()
		css=b"""
		#label #label_install{
			padding: 6px;
			margin:6px;
			font: 12px Roboto;
		}
		#label_install:insensitive{
			padding: 6px;
			margin:6px;
			font: 12px Roboto;
			color:white;
			background-image:-gtk-gradient (linear, left top, left bottom, from (#7ea8f2),to (#7ea8f2));
			box-shadow: -0.5px 3px 2px #aaaaaa;
		}
		#frame{
			padding: 6px;
			margin:6px;
			font: 12px Roboto;
			background:white;
		}
		"""
		style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.pb=GdkPixbuf.Pixbuf()
		self.box=Gtk.Grid(row_spacing=6,column_spacing=6)
		self.add(self.box)
		img_banner=Gtk.Image()
		img_banner.set_from_file(RSRC+"/air-installer.png")
		self.box.attach(img_banner,0,0,1,1)
		self.pulse=Gtk.Spinner()
		self.box.attach(self.pulse,0,1,2,2)
		
		img_info=Gtk.Image()
		img_info.set_from_stock(Gtk.STOCK_SAVE,Gtk.IconSize.DIALOG)

		self.lbl_info=Gtk.Label('')
		self.lbl_info.set_name('label_install')
		self.lbl_info.set_max_width_chars(20)
		self.lbl_info.set_width_chars(20)
		self.lbl_info.set_line_wrap(True)
		lbl_text=_("Install <b>%s</b>")%file_name
		self.lbl_info.set_markup(lbl_text)
		self.lbl_info.set_margin_bottom(GTK_SPACING)
		self.lbl_info.set_margin_left(GTK_SPACING)
		self.lbl_info.set_margin_right(GTK_SPACING)
		self.lbl_info.set_margin_top(GTK_SPACING)

		self.box_info=Gtk.Box()
		self.box_info.add(self.lbl_info)
		self.box_info.add(img_info)

		self.btn_install=Gtk.Button()
		self.btn_install.add(self.box_info)

		img_icon=Gtk.Image()
		img_icon.set_from_file(RSRC+"/air-installer_icon.png")
		self.pb=img_icon.get_pixbuf()
		air_info=installer.AirManager().get_air_info(air_file_path)
		if 'pb' in air_info.keys():
			if air_info['pb']:
				img_icon.set_from_pixbuf(air_info['pb'])
				self.pb=air_info['pb']

		lbl_text=_("<b>Select icon</b> for %s")%file_name
		lbl_icon=Gtk.Label()
		lbl_icon.set_markup(lbl_text)
		lbl_icon.set_name('label')
		lbl_icon.set_max_width_chars(20)
		lbl_icon.set_width_chars(20)
		lbl_icon.set_line_wrap(True)

		self.box_icon=Gtk.Box(spacing=6)
		self.box_icon.add(lbl_icon)
		self.box_icon.add(img_icon)

		self.btn_icon=Gtk.Button()
		self.btn_icon.add(self.box_icon)

		self.box_button=Gtk.HBox(spacing=6)
		self.box_button.props.halign=Gtk.Align.END
		self.box.set_margin_bottom(GTK_SPACING)
		self.box.set_margin_left(GTK_SPACING)
		self.box.set_margin_top(GTK_SPACING)

		btn_cancel=Gtk.Button.new_from_stock(Gtk.STOCK_CLOSE)

		self.box_button.add(btn_cancel)
		self.box.attach_next_to(self.btn_icon,img_banner,Gtk.PositionType.BOTTOM,1,1)
		self.box.attach_next_to(self.btn_install,self.btn_icon,Gtk.PositionType.BOTTOM,1,1)
		self.box.attach_next_to(self.box_button,self.btn_install,Gtk.PositionType.BOTTOM,1,1)

		self.btn_install.connect("clicked",self._begin_install_file,air_file_path)
		self.btn_icon.connect("clicked",self._set_app_icon,img_icon)
		btn_cancel.connect("clicked",Gtk.main_quit)
		self.connect("destroy",Gtk.main_quit)
		self.show_all()
		Gtk.main()
	#def _load_gui

	def _set_app_icon(self,widget,img_icon):
		
		def _update_preview(*arg):
			if dw.get_preview_filename():
				if os.path.isfile(dw.get_preview_filename()):
					pb=GdkPixbuf.Pixbuf.new_from_file_at_scale(dw.get_preview_filename(),64,-1,True)
					img_preview.set_from_pixbuf(pb)
					img_preview.show()
			else:
				img_preview.hide()
		dw=Gtk.FileChooserDialog(_("Select icon"),None,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		dw.set_action(Gtk.FileChooserAction.OPEN)
		img_preview=Gtk.Image()
		img_preview.set_margin_right(GTK_SPACING)
		file_filter=Gtk.FileFilter()
		file_filter.add_pixbuf_formats()
		file_filter.set_name(_("images"))
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

	def _begin_install_file(self,widget,air_file):
		self.box_button.set_sensitive(False)
		self.btn_install.set_sensitive(False)
		self.btn_icon.set_sensitive(False)
		self._debug("Launching install thread ")
		self.pulse.start()
		subprocess.check_call(['/usr/bin/xhost','+'])
		th=threading.Thread(target=self._install_file,args=[air_file])
		th.start()
		self.box_button.set_sensitive(True)
	#def _begin_install_file

	def _install_file(self,air_file):
		err=False
		try:
			self._debug("Installing")
			tmp_icon=tempfile.mkstemp()[1]
			self._debug(tmp_icon)
			#Copy the icon to temp folder
			self.pb.savev(tmp_icon,'png',[""],[""])
			try:
				ins=subprocess.check_call(['pkexec','/usr/bin/air-helper-installer.py','install',air_file,tmp_icon])
				os.path.remove(tmp_icon)
			except subprocess.CalledProcessError as e:
				self._debug(e)
				err=True
			except Exception as e:
				self._debug(e)
		except Exception as e:
			self._debug(e)
			err=True
		self.pulse.stop()
		self.pulse.set_visible(False)
		if err:
			self.btn_install.set_sensitive(True)
			self.btn_icon.set_sensitive(True)
		if not err:
			msg=_("Package <b>%s</b> succesfully installed")%air_file
			self.lbl_info.set_markup(msg)
			self.box_button.show()
			self.box_icon.hide()
		subprocess.check_call(['/usr/bin/xhost','-'])
		subprocess.check_output(["xdg-mime","install","/usr/share/mime/packages/x-air-installer.xml"])
		subprocess.check_output(["xdg-mime","default","/usr/share/applications/air-installer.desktop","/usr/share/mime/packages/x-air-installer.xml"],input=b"")
	#def _install_file

#Main
AIR_FOLDER="/opt/adobe-air-sdk/"
air_file=sys.argv[1]

if AIR_FOLDER in os.path.dirname(air_file):
	#Launch the air file
	air_basename=os.path.basename(air_file)
	air_basename=air_basename.replace('.air','')
	subprocess.call(['gtk-launch',air_basename])

else:

	dialog=confirmDialog(air_file)
	#install the air file
#	os.execle("pkexec","/usr/share/air-installer/air-helper-installer.py",air_file)

