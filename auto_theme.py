
'''
Terminator plugin to implement AutoTheme:
  Let profile follow system Dark/Light mode (when system theme change).

 Author: yurenchen@yeah.net
License: GPLv2
   Site: https://github.com/yurenchen000/terminator-autotheme-plugin
'''

# import os
from gi.repository import Gtk
from gi.repository import Gdk
import terminatorlib.plugin as plugin
from terminatorlib.config import Config
from terminatorlib.translation import _

from terminatorlib.util import dbg
from terminatorlib.terminal import Terminal
from terminatorlib.terminator import Terminator

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['AutoTheme']

## disable log
# print = lambda *a:None

"""Terminator Plugin AutoTheme"""
class AutoTheme(plugin.MenuItem):
    """Add custom commands to the terminal menu"""
    capabilities = ['terminal_menu']

    light = ''
    dark = ''
    mode = ''
    list = []
    change_cb = None

    def __init__(self):
        plugin.MenuItem.__init__(self)
        self.__class__.load_config()
        self.setup_theme_monitor()

    ## on menu_show
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
            print('== on_theme_name change:', theme_name, theme_variant)
            is_dark = 'dark' in theme_name
            AutoTheme.change_theme(is_dark)
            if callable(AutoTheme.change_cb):
                AutoTheme.change_cb(is_dark)

        Gtk.Settings.get_default().connect("notify::gtk-theme-name", _on_theme_name_changed)


    @staticmethod
    def is_dark_theme():
        settings = Gtk.Settings.get_default()
        theme_name = settings.get_property('gtk-theme-name')
        theme_variant = settings.get_property('gtk-application-prefer-dark-theme')
        print('--theme_name:', theme_name, theme_variant)
        is_dark = 'dark' in theme_name
        return is_dark

    @staticmethod
    def apply_theme(name):
        terminator = plugin.Terminator()
        # print('---terminals:', len(ts), ts)
        for term in terminator.terminals:
            # print('term:', term)
            term.set_profile(term.get_vte(), name)

    @staticmethod
    def change_theme(isdark):
        # theme = '_light2' if isdark else '_light_day'
        theme = AutoTheme.dark if isdark else AutoTheme.light
        print('--change_theme:', isdark, theme)
        AutoTheme.apply_theme(theme)

    @classmethod
    def save_config(cls, light, dark, mode):
        print('=== save_config:', light, dark, mode)
        cls.light = light
        cls.dark  = dark
        cls.mode  = mode

        cfg = {'light': light, 'dark': dark, 'mode': mode}
        config = Config()
        config.plugin_set_config(cls.__name__, cfg)
        config.save()

    @classmethod
    def load_config(cls):
        cur_profile = plugin.Terminator().terminals[0].get_profile()
        cfg = Config().plugin_get_config(cls.__name__) or {}
        print('--- load_config:', cfg)
        cls.light = cfg.get('light', cur_profile)
        cls.dark  = cfg.get('dark',  cur_profile)
        cls.mode  = cfg.get('mode', 'Auto')
        print('=== load_config:', cls.light, cls.dark, cls.mode)

    @classmethod
    def do_menu_toggle(cls, _widget, terminal):
        terminator = plugin.Terminator()
        cls.list = terminator.config.list_profiles()
        print('profiles:', cls.list)
        cls.load_config()

        dialog = MySettingDialog(None, cls)
        # dialog.set_list(cls.list)
        # dialog.set_list_sel(cls.light, cls.dark)
        # dialog.set_mode_sel(cls.mode)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            cls.save_config(dialog.light_sel, dialog.dark_sel, dialog.mode_sel)

        dialog.destroy()


class MySettingDialog(Gtk.Dialog):
    def __init__(self, parent, mgr):
        super().__init__(title="Auto Theme Setting", parent=parent, flags=0)

        self.light_sel = ''
        self.dark_sel = ''
        self.mode_sel = ''
        self.list = []
        self.mgr = mgr

        box = self.get_content_area()
        self.box = box

        ## --------- Create grid layout
        grid = Gtk.Grid()
        box.add(grid)

        # Set column and row spacing
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)

        # Add padding to the grid
        grid.set_margin_top(20)
        grid.set_margin_bottom(5)
        grid.set_margin_start(20) # left
        grid.set_margin_end(20)   # right

        # Set default dialog size
        self.set_default_size(400, 300)


        ## --------- col0: plain label
        light_label = Gtk.Label(label="Light")
        dark_label  = Gtk.Label(label="Dark")
        grid.attach(dark_label,  0, 1, 1, 1)
        grid.attach(light_label, 0, 0, 1, 1)

        light_label.set_name('light_label')
        dark_label.set_name('dark_label')
        # self.light_label = light_label
        # self.dark_label  = dark_label

        ## --------- col1: profile combo
        # Light combo box
        self.light_combo = Gtk.ComboBoxText()
        self.light_combo.append_text("Option 1")
        self.light_combo.append_text("Option 2")
        self.light_combo.append_text("Option 3")

        # Dark combo box
        self.dark_combo = Gtk.ComboBoxText()
        self.dark_combo.append_text("Option 1")
        self.dark_combo.append_text("Option 2")
        self.dark_combo.append_text("Option 3")

        grid.attach(self.light_combo,  1, 0, 1, 1)
        grid.attach(self.dark_combo,   1, 1, 1, 1)
        grid.get_child_at(1, 0).set_hexpand(True)
        grid.get_child_at(1, 1).set_hexpand(True)
        # print('--grid.get_child:', grid.get_child_at(1, 0) == self.light_combo)

        ### --------- row2: space
        space_label = Gtk.Label(label="")
        grid.attach(space_label, 1, 2, 1, 1)

        ### --------- row3: mode radio
        self.radio_light = Gtk.RadioButton.new_with_label_from_widget(None, "Light")
        self.radio_dark  = Gtk.RadioButton.new_with_label_from_widget(self.radio_light, "Dark")
        self.radio_auto  = Gtk.RadioButton.new_with_label_from_widget(self.radio_light, "Auto")

        self.radio_auto.set_tooltip_text('follow system theme')
        self.radio_light.set_mode(False)
        self.radio_dark.set_mode(False)
        self.radio_auto.set_mode(False)

        # button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        # button_box.set_layout(Gtk.ButtonBoxStyle.START)
        button_box.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        # button_box.set_spacing(5)

        # Pack buttons into the button box
        button_box.pack_start(self.radio_light, True, True, 0)
        button_box.pack_start(self.radio_dark,  True, True, 0)
        button_box.pack_start(self.radio_auto,  True, True, 0)

        # Attach the button box to the grid
        mode_label = Gtk.Label(label="Mode")
        grid.attach(mode_label, 0, 3, 1, 1)
        grid.attach(button_box, 1, 3, 1, 1)

        ### --------- init values
        self.set_list(mgr.list)
        self.set_list_sel(mgr.light, mgr.dark)
        self.set_mode_sel(mgr.mode)

        mgr.change_cb = self.change_cb
        ### --------- radio onchange

        self.light_combo.connect('changed', self.on_light_combo_change)
        self.dark_combo.connect('changed',  self.on_dark_combo_change)

        # In the __init__ method, connect the toggle signal
        self.radio_light.connect("toggled", self.on_radio_button_toggled)
        self.radio_dark.connect("toggled",  self.on_radio_button_toggled)
        self.radio_auto.connect("toggled",  self.on_radio_button_toggled)

        ### --------- footer: action buttons
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        # Connect the response signal
        self.connect("response", self.on_dialog_response)

        # grid.set_row_spacing(15)
        self.add_css()
        self.show_all()

    def set_list(self, list1):
         self.light_combo.remove_all()
         self.dark_combo.remove_all()
         self.list = list1
         for name in list1:
            self.light_combo.append_text(name)
            self.dark_combo.append_text(name)

    def set_list_sel(self, val1, val2):
        if val1 in self.list:
            self.light_combo.set_active(self.list.index(val1))
        if val2 in self.list:
            self.dark_combo.set_active(self.list.index(val2))

    def set_mode_sel(self, val1):
        self.box.set_name(val1) # css active
        if val1 == 'Auto':
            self.radio_auto.set_active(True)
            theme_mode = 'Dark' if self.mgr.is_dark_theme() else 'Light'
            self.box.set_name(theme_mode) # css active
        elif val1 == 'Light':
            self.radio_light.set_active(True)
        else:
            self.radio_dark.set_active(True)
            # self.radio_dark.active = True

    def add_css(self):
        css = b"""
        #dark_label, #light_label {
            padding: 0px 15px;
        }
        #Dark  #dark_label,
        #Light #light_label {
            /* background-color: green; */
            background-color: rgba(0, 255, 0, 0.2);
            /* color: green; */
            border-radius: 8px;
            padding: 0px 15px;
            /* border-bottom: 1px solid green; */
            /* text-decoration: underline; */
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def on_light_combo_change(self, widget):
        theme = widget.get_active_text()
        print('-- light selected:', theme)
        self.mgr.apply_theme(theme)
    def on_dark_combo_change(self, widget):
        theme = widget.get_active_text()
        print('-- dark selected:', theme)
        self.mgr.apply_theme(theme)

    def change_cb(self, is_dark):
        print('-- change_cb:', is_dark)
        theme_mode = 'Dark' if is_dark else 'Light'
        self.box.set_name(theme_mode) # css active

    def on_radio_button_toggled(self, widget):
        if widget.get_active():
            print('-- mode selected:', widget.get_label())
            # unsel = 'Light' if self.mode_sel=='Dark' else 'Dark'
            self.mode_sel = widget.get_label()
            self.box.set_name(self.mode_sel) # css active

            theme_mode = self.mode_sel
            if self.mode_sel == 'Auto':
                theme_mode = 'Dark' if self.mgr.is_dark_theme() else 'Light'
                self.box.set_name(theme_mode) # css active

            theme_name = self.dark_combo.get_active_text() if theme_mode == 'Dark' else self.light_combo.get_active_text()
            self.mgr.apply_theme(theme_name)

    def on_dialog_response(self, dialog, response_id):
        # print('== on response:', response_id)
        self.mgr.change_cb = None
        self.light_sel = self.light_combo.get_active_text()
        self.dark_sel  = self.dark_combo.get_active_text()
        if response_id == Gtk.ResponseType.OK:
            pass
        # elif response_id == Gtk.ResponseType.CANCEL:
        else:
            print("-- Cancel/close clicked.")

