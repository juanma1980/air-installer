import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib
import Core
import os
import subprocess
import airmanager.airmanager as installer
import threading

RSRC="/usr/share/air-manager/rsrc/"

CSS_FILE=RSRC + "air-manager.css"

class ManageBox(Gtk.ScrolledWindow):
	def __init__(self):
		self.dbg=True
		Gtk.ScrolledWindow.__init__(self)
#		self.override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(255,255,255,1))
		self.grid=Gtk.Grid()
		self.set_css_info()
		self.core=Core.Core.get_core()
		self.airinstaller=installer.AirManager()	
		self.listbox=Gtk.ListBox()
		self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
		layout=Gtk.Layout()
		vadjustment=layout.get_vadjustment()
		vscrollbar=Gtk.Scrollbar(orientation=Gtk.Orientation.VERTICAL,adjustment=vadjustment)
#		self.grid.attach(vscrollbar,1,0,1,1)
		self.grid.attach(self.listbox,0,1,1,1)
		self._load_installed_apps()

		self.check_window=Gtk.Window()
		self.check_window.set_position(Gtk.WindowPosition.CENTER)
		self.check_window.set_decorated(False)
		self.check_window.set_modal(True)
		self.check_window.set_keep_above(True)
		check_box=Gtk.VBox()
		check_label=Gtk.Label("Removing file...")
		check_label.set_margin_top(5)
		check_label.set_margin_bottom(10)
		check_label.set_margin_right(30)
		check_label.set_margin_left(30)
		self.check_pbar=Gtk.ProgressBar()
		self.check_pbar.set_margin_top(5)
		self.check_pbar.set_margin_bottom(10)
		self.check_pbar.set_margin_right(30)
		self.check_pbar.set_margin_left(30)
		check_box.add(check_label)
		check_box.add(self.check_pbar)
		check_label.set_name("MSG_LABEL")
		self.check_window.add(check_box)
		self.add(self.grid)
		GObject.threads_init()

	def _debug(self,msg):
		if self.dbg:
			print("UninstallBox: %s"%msg)

	def set_css_info(self):
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(CSS_FILE)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
	#def set_css_info	

	def _load_installed_apps(self):
		img_remove=RSRC+'trash.svg'
		img_run=RSRC+'run.svg'
		spacing=6
		total_apps=len(self.airinstaller.get_installed_apps())
		count=0
		for child in self.listbox.get_children():
			if type(child)==type(Gtk.ListBoxRow()):
				for row_child in child.get_children():
					child.remove(row_child)
				self.listbox.remove(child)
		for app,data in self.airinstaller.get_installed_apps().items():
			count+=1
#			listrow=Gtk.Box(spacing=12,hexpand=True)
			listrow=Gtk.Grid(row_spacing=6,hexpand=True,column_spacing=12)
			listrow.set_margin_left(12)
			listrow.set_margin_right(12)
			listrow.set_margin_top(6)
			listrow.set_margin_bottom(6)
			img_icon=Gtk.Image.new_from_file(self._get_desktop_icon(data["desktop"]))
			label=Gtk.Label(app)
			label.set_name("LIST_LABEL")
			label.set_margin_bottom(spacing)
			img_trash=Gtk.Image.new_from_file(img_remove)
			btn_remove=Gtk.Button()
			btn_remove.add(img_trash)
			btn_remove.props.expand=False
			btn_remove.props.halign=Gtk.Align.END
			btn_remove.set_name("BTN_REMOVE")
			btn_remove.connect('clicked',self._remove_air,data)
			img_exe=Gtk.Image.new_from_file(img_run)
			btn_run=Gtk.Button()
			btn_run.add(img_exe)
			btn_run.props.expand=True
			btn_run.props.halign=Gtk.Align.END
			btn_run.set_name("BTN_RUN")
			btn_run.connect('clicked',self._run_air,data)
			info_box=Gtk.Box(spacing=12,hexpand=True)
			info_box.add(label)
			info_box.add(btn_run)
			info_box.add(btn_remove)
			listrow.attach(img_icon,1,1,1,1)
			listrow.attach(info_box,2,1,1,1)
			listrow.set_name("LIST_ROW")
			self.listbox.insert(listrow,-1)
			if count<total_apps:
				separator=Gtk.Separator()
				separator.set_name("LIST_SEPARATOR")
#				listrow.attach(separator,2,2,1,1)
				separator.set_margin_left(66)
				separator.set_margin_top(0)
				separator.set_margin_bottom(0)
				self.listbox.insert(separator,-1)

	def _get_desktop_icon(self,desktop):
		icon=''
		if os.path.isfile(desktop):
			f=open(desktop,'r')
			flines=f.readlines()
			for fline in flines:
				fline=fline.strip()
				if fline.startswith("Icon"):
					icon=fline
					icon=icon.replace('Icon=','')
					break
			if not os.path.isfile(icon):
				icon='/usr/share/icons/hicolor/48x48/apps/'+icon
				if not icon.endswith('.png'):
					icon=icon+'.png'
		if not os.path.isfile(icon):
			icon='/usr/share/icons/hicolor/48x48/apps/air.png'

		return icon

	def _run_air(self,*args):
		air_data=args[-1]
		app_name=os.path.basename(air_data['desktop'])
		try:
			self._debug("Launching %s (%s)"%(app_name,air_data['desktop']))
			sw_run_err=subprocess.check_call(['gtk-launch',app_name])
		except Exception as e:
			self._debug(e)

	def _remove_air(self,*args):
		self.listbox.set_sensitive(False)
		self.remove_t=threading.Thread(target=self._remove_air_th,args=[*args])
		self.remove_t.start()
		self.check_window.show_all()
		GLib.timeout_add(100,self.pulsate_install)

	def _remove_air_th(self,*args):
		self.check_pbar.pulse()
		air_data=args[-1]
		sw_remove_err=1
#		sw_remove=self.airinstaller.remove_air_app(air_data)
		try:
			sw_remove_err=subprocess.check_call(['pkexec','/usr/bin/air-helper-installer.py','remove',air_data['air_id'],air_data['desktop']])
		except Exception as e:
			self._debug(e)
		if sw_remove_err:
			self._debug("Removed KO")
		else:
			self._debug("Removed OK")

	def pulsate_install(self):
		if self.remove_t.is_alive():
			self.check_pbar.pulse()
			return True

		else:
			self._load_installed_apps()
			self.show_all()
			self.listbox.set_sensitive(True)
			self.check_window.hide()
			return False
	#def pulsate_install		
