#!/usr/bin/python3
import sys
import subprocess
import os
import gi
import threading
import tempfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

RSRC="/usr/share/air-installer/rsrc"
CSS_FILE=RSRC + "air-installer.css"

class confirmDialog(Gtk.Window):
	def __init__(self,air_file):
		self._load_gui()

	def _debug(self,msg):
		print("DBG: %s"%msg)

	def _load_gui(self):
		Gtk.Window.__init__(self,title="Confirm action")
		self.set_position(Gtk.WindowPosition.CENTER)
		style_provider=Gtk.CssProvider()
		css=b"""
		#label{
			padding: 6px;
			margin:6px;
			font: Roboto 12ox;
		}
		#frame{
			padding: 6px;
			margin:6px;
			font: Roboto 12ox;
			background:white;
		}
		"""
		style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.box=Gtk.Grid(row_spacing=6,column_spacing=6)
		self.add(self.box)
		self.pb=None
		img_banner=Gtk.Image()
		img_banner.set_from_file(RSRC+"/air-installer.png")
		self.box.attach(img_banner,0,0,1,1)
		self.pulse=Gtk.Spinner()
		self.box.attach(self.pulse,0,1,2,2)
#		frm_info=Gtk.Frame(
#		frm_info.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
#		frm_info.set_name('frame')
		img_info=Gtk.Image()
		img_info.set_from_stock(Gtk.STOCK_SAVE,Gtk.IconSize.DIALOG)
		self.lbl_info=Gtk.Label('')
		self.lbl_info.set_name('label')
		self.lbl_info.set_max_width_chars(20)
		self.lbl_info.set_width_chars(20)
		self.lbl_info.set_line_wrap(True)
		file_name=os.path.basename(air_file)
		lbl_text="Install <b>%s</b>"%file_name

		self.lbl_info.set_markup(lbl_text)
		self.lbl_info.set_margin_bottom(6)
		self.lbl_info.set_margin_left(6)
		self.lbl_info.set_margin_right(6)
		self.lbl_info.set_margin_top(6)

		self.box_info=Gtk.Box()
		self.box_info.add(self.lbl_info)
		self.box_info.add(img_info)
		btn_install=Gtk.Button()
		btn_install.add(self.box_info)
		img_icon=Gtk.Image()
		img_icon.set_from_file(RSRC+"/air-installer_icon.png")
		self.pb=img_icon.get_pixbuf()
		lbl_text="<b>Select icon</b> for %s"%file_name
		lbl_icon=Gtk.Label()
		lbl_icon.set_markup(lbl_text)
		lbl_icon.set_name('label')
		lbl_icon.set_max_width_chars(20)
		lbl_icon.set_width_chars(20)
		lbl_icon.set_line_wrap(True)
		self.box_icon=Gtk.Box(spacing=6)
		self.box_icon.add(lbl_icon)
		self.box_icon.add(img_icon)
		btn_icon=Gtk.Button()
		btn_icon.add(self.box_icon)
#		btn_install=Gtk.Button.new_from_stock(Gtk.STOCK_OK)
		self.box_button=Gtk.HBox(spacing=6)
#		self.box_button.add(btn_install)
		self.box_button.props.halign=Gtk.Align.END
		self.box.set_margin_bottom(6)
		self.box.set_margin_left(6)
		self.box.set_margin_top(6)
		btn_cancel=Gtk.Button.new_from_stock(Gtk.STOCK_CLOSE)
		self.box_button.add(btn_cancel)
		self.box.attach_next_to(btn_icon,img_banner,Gtk.PositionType.BOTTOM,1,1)
		self.box.attach_next_to(btn_install,btn_icon,Gtk.PositionType.BOTTOM,1,1)
		self.box.attach_next_to(self.box_button,btn_install,Gtk.PositionType.BOTTOM,1,1)

		btn_install.connect("clicked",self._begin_install_file,air_file)
		btn_icon.connect("clicked",self._set_app_icon,img_icon)
		btn_cancel.connect("clicked",Gtk.main_quit)
		self.connect("destroy",Gtk.main_quit)
		self.show_all()
		Gtk.main()

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
		img_preview.set_margin_right(6)
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

	def _begin_install_file(self,widget,air_file):
		self.box_button.set_sensitive(False)
		self._debug("Launching install thread ")
		self.pulse.start()
		th=threading.Thread(target=self._install_file,args=[air_file])
		th.start()

	def _install_file(self,air_file):
		err=False
		try:
			self._debug("Installing")
			tmpfile=tempfile.mkstemp()[1]
			self._debug(tmpfile)
			#Copy the icon to temp folder
			self.pb.savev(tmpfile,'png',[""],[""])
			self._debug("Installing")
			ins=subprocess.check_call(['pkexec','/usr/share/air-installer/air-helper-installer.py',air_file,tmpfile])
			self._debug("Installing")
		except:
			err=True
		self.pulse.stop()
		self.pulse.set_visible(False)
		if not err:
			msg="Package <b>%s</b> succesfully installed"%air_file
			self.lbl_info.set_markup(msg)
			self.box_info.set_sensitive(False)
			self.box_icon.hide()
			self.box_button.show()
		self.box_button.set_sensitive(True)
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

