#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib
import dialog


import signal
import os
import sys
import Core


signal.signal(signal.SIGINT, signal.SIG_DFL)


RSRC="/usr/share/air-installer/"
CSS_FILE=RSRC + "air-installer.css"


class AirInstaller:
	
	def __init__(self):

		self.core=Core.Core.get_core()
		

	#def init

	def load_gui(self):
		
		builder=Gtk.Builder()
		ui_path=RSRC + "rsrc/air-installer.ui"
		builder.add_from_file(ui_path)
		
		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("Air Installer")
		self.main_box=builder.get_object("main_box")
		self.exit_button=builder.get_object("exit_button")
		
		self.install_box=self.core.install_box
		ev_box=Gtk.EventBox()
#		ev_box.add(self.install_box.drop)
		stack=Gtk.Stack()
		stack.set_transition_duration(1000)
		stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		stack.add_titled(self.install_box,"installbox","Install")
#		stack.add_titled(ev_box,"installbox","Install")
		stack_switcher=Gtk.StackSwitcher()
		stack_switcher.set_stack(stack)
		stack_switcher.props.halign=Gtk.Align.CENTER
		stack_switcher.set_margin_top(12)
		
		# Add components
		listbox=self.core.manage_box
		stack.add_titled(listbox,"pkglist","Manage")
		stack_switcher.connect('button-release-event',self._load_air_list,stack,listbox)
			
		self.set_css_info()
		self.connect_signals()
		stack.set_visible_child_name("installbox")
		self.main_box.add(stack_switcher)
		self.main_box.add(Gtk.Separator())
		self.main_box.add(stack)
		self.main_window.show_all()
	#def load_gui

	def _load_air_list(self,*args):
		stack=args[-2]
		listbox=args[-1]
		if stack.get_visible_child_name()=='pkglist':
			listbox._load_installed_apps()
			listbox.show_all()


	def set_css_info(self):
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(CSS_FILE)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")
						
	#def set_css_info					
			
	def connect_signals(self):
		self.main_window.connect("destroy",self.quit)
#		self.exit_button.connect("clicked",self.quit)
	#def connect_signals

	def quit(self,widget):
		Gtk.main_quit()	
	#def quit

	def start_gui(self):
		GObject.threads_init()
		Gtk.main()
	#def start_gui


	
#class LliurexAbiesToPmb


if __name__=="__main__":
	
	airman=AirInstaller()
	airman.start_gui()
	
