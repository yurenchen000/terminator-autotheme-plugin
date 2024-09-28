# Terminator AutoTheme Plugin

A Terminator plugin to implement AutoTheme:
  Let profile follow system Dark/Light mode (when system theme change).

https://github.com/gnome-terminator/terminator/issues/775

## Feature
- auto switch profile when system light/dark change
- quick preview different profiles (without tedious clicks)  
 //just mouse-scroll or  keyboard <kbd>↑</kbd>  <kbd>↓</kbd> on the combox

## Requirements

only tested with terminator 2.1.1+, on ubuntu 22 lts

## Install

1. Copy auto_theme.py to ~/.config/terminator/plugins/
2. Terminator Preferences > Plugins: enable `AutoTheme`

## Usage
you need at least 2 terminator profile,  
  one for dark theme  
  one for light theme  

It will auto switch when system dark/light mode swtich.

## Preview

![plugin_preview.png](https://i.imgur.com/q1pUomB.png)
