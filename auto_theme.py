
'''
Terminator plugin to implement AutoTheme:
  Let profile follow system Dark/Light mode (when system theme change).

 Author: yurenchen@yeah.net
License: GPLv2
   Site: https://github.com/yurenchen000/terminator-autotheme-plugin
'''

# import os
from gi.repository import Gtk
import terminatorlib.plugin as plugin
from terminatorlib.translation import _

from terminatorlib.util import dbg
from terminatorlib.terminal import Terminal
from terminatorlib.terminator import Terminator

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['AutoTheme']

## disable log
print = lambda *a:None

"""Terminator Plugin AutoTheme"""
class AutoTheme(plugin.MenuItem):
    """Add custom commands to the terminal menu"""
    capabilities = ['terminal_menu']

    theme_light = 'light'
    theme_dark  = 'dark'
    # theme_light = '_light_day'
    # theme_dark  = '_light2'

    def __init__(self):
        plugin.MenuItem.__init__(self)
        self.setup_theme_monitor()

    ## on menu_show  // it not really need context-menu
    def callback(self, menuitems, menu, terminal):
        item = Gtk.CheckMenuItem(_(' -  AutoTheme'))
        # item.set_active(True)
        item.connect("toggled", self.do_menu_toggle, terminal)
        menuitems.append(item)
        # print('AutoTheme __init__..')

    @staticmethod
    def setup_theme_monitor():
        print('++ setup_theme_monit')
        settings = Gtk.Settings.get_default()
        theme_name = settings.get_property('gtk-theme-name')
        theme_variant = settings.get_property('gtk-application-prefer-dark-theme')
        print('--theme_name:', theme_name, theme_variant)

        def _on_theme_name_changed(settings, gparam):
            theme_name = settings.get_property('gtk-theme-name')
            theme_variant = settings.get_property('gtk-application-prefer-dark-theme')
            print('--on_theme_name change:', theme_name, theme_variant)
            is_dark = 'dark' in theme_name
            AutoTheme.change_theme(is_dark)

        Gtk.Settings.get_default().connect("notify::gtk-theme-name", _on_theme_name_changed)

    @staticmethod
    def change_theme(isdark):
        terminator = plugin.Terminator()
        ts = terminator.terminals
        theme = AutoTheme.theme_dark if isdark else AutoTheme.theme_light
        print('--change_theme:', isdark, theme)
        # print('---terminals:', len(ts), ts)
        for term in terminator.terminals:
            # print('term:', term)
            term.set_profile(term.get_vte(), theme)


    @classmethod
    def do_menu_toggle(cls, _widget, terminal):
        print('-- AutoTheme menu clicked')


