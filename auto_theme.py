
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

    dark = ''
    light = ''
    mode = ''
    list = []

    def __init__(self):
        plugin.MenuItem.__init__(self)
        self.__class__.load_config()
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
        # theme = '_light2' if isdark else '_light_day'
        theme = AutoTheme.dark if isdark else AutoTheme.light

        print('--change_theme:', isdark, theme)
        # print('---terminals:', len(ts), ts)
        for term in terminator.terminals:
            # print('term:', term)
            term.set_profile(term.get_vte(), theme)
  

    @classmethod
    def save_config(cls, light_sel, dark_sel, mode_sel):
        cfg = {}
        cfg['light'] = light_sel
        cfg['dark'] = dark_sel
        cfg['mode'] = mode_sel

        cls.light = light_sel
        cls.dark  = dark_sel
        cls.mode  = mode_sel

        config = Config()
        config.plugin_set_config(cls.__name__, cfg)
        config.save()

    @classmethod
    def load_config(cls):
        config = Config()                                           
        cfg = config.plugin_get_config(cls.__name__)
        print('--- config:', cfg)

        if cfg:
            light_sel = cfg.get('light', '')
            dark_sel  = cfg.get('dark', '')
            model_sel = cfg.get('mode', 'Auto')
            print('==cur sel:', light_sel, dark_sel, model_sel)

            cls.dark  = dark_sel
            cls.light = light_sel
            cls.mode  = model_sel

    @classmethod
    def do_menu_toggle(cls, _widget, terminal):
        terminator = plugin.Terminator()
        profiles = terminator.config.list_profiles()
        cls.list = profiles
        print('profiles:', profiles)
        cls.load_config()

        dialog = MySettingDialog(None)
        dialog.set_list(profiles)

        # dialog.set_list_sel(1,2)
        # dialog.set_list_sel(0,1)
        dialog.set_list_sel(cls.light, cls.dark)
        dialog.set_mode_sel(cls.mode)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print('Light sel:', dialog.light_sel)
            print('Dark  sel:', dialog.dark_sel)
            print('Mode  sel:', dialog.mode_sel)
            cls.save_config(dialog.light_sel, dialog.dark_sel, dialog.mode_sel)

        dialog.destroy()


class MySettingDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Auto Theme Setting", parent=parent, flags=0)

        self.light_sel = ''
        self.dark_sel = ''
        self.mode_sel = ''
        self.list = []

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
        dark_label = Gtk.Label(label="Dark")
        grid.attach(dark_label,  0, 1, 1, 1)
        grid.attach(light_label, 0, 0, 1, 1)

        light_label.set_name('light_label')
        dark_label.set_name('dark_label')
        self.light_label = light_label
        self.dark_label  = dark_label

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

        ### --------- radio onchange
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
        if val1 == 'Auto':
            self.radio_auto.set_active(True)
        elif val1 == 'Light':
            self.radio_light.set_active(True)
        else:
            self.radio_dark.set_active(True)

    def add_css(self):
        css = b"""
        #dark_label, #light_label {
            padding: 0px 15px;
        }
        #Dark  #dark_label,
        #Light #light_label {
            background-color: green;
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

    def on_radio_button_toggled(self, widget):
        if widget.get_active():
            self.mode_sel = widget.get_label()
            print(f"- radio selected: {widget.get_label()}")
            unsel = 'Light' if self.mode_sel=='Dark' else 'Dark'
            self.box.set_name(self.mode_sel)


    def on_dialog_response(self, dialog, response_id):
        print('== on response:', response_id)
        self.light_sel = self.light_combo.get_active_text()
        self.dark_sel = self.dark_combo.get_active_text()
        if response_id == Gtk.ResponseType.OK:
            pass
        # elif response_id == Gtk.ResponseType.CANCEL:
        else:
            print("-- Cancel/close clicked.")

