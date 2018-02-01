#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-
#    Yum Exteder (yumex) - A GUI for yum
#    Copyright (C) 2013 Tim Lauridsen < timlau<AT>fedoraproject<DOT>org >
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to
#    the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
    This module serves to detect themes and auto-adjust custom colors to have
    enough, but not too much, contrast.
"""


from gi.repository import Gtk

import logging
import os

logger = logging.getLogger('yumex.misc')


class ThemeDetector:
    """
        This class is used to detect themes.
    """
    theme_dark = False

    def __init__(self):
        self.theme_dark = ThemeDetector._detect_theme()

    def _detect_from_env():
        """
            Environment variables have priority over GtkSettings, see
            https://developer.gnome.org/gtk3/stable/gtk-running.html .
            Since Gtk+ devs don't want this to be implemented in Gtk+, we have
            to do this dirty workaround.
            See https://bugzilla.gnome.org/show_bug.cgi?id=748985
        """
        env = os.environ
        if env.get('GTK_THEME') is not None:
            env_gtk_theme = env['GTK_THEME']
            if env_gtk_theme.endswith(':dark'):
                logger.debug('Detected dark theme variant from environment.')
                return True
            elif env_gtk_theme.endswith(':light'):
                logger.debug('Detected light theme variant from environment.')
                return False
        return None

    def _calculate_contrast(foreground, background):
        """
            Calculate contrast of colors.
            Returns a positive number if font is dark on light background.
            abs(contrast) indicates the contrast intensity. Should be > 1 for
            readability.
        """
        contrast = background.red - foreground.red \
            + background.green - foreground.green \
            + background.blue - foreground.blue
        return contrast

    def _detect_from_widget():
        """
            Create a GtkWidget and from it detect whether a light (False) or
            dark (True) theme is used. This is a guessing game.
            Gtk+ might be using a theme that is dark but doesn't specify this in
            its variant or doesn't have a variant.
        """
        window = Gtk.Window()
        stc = window.get_style_context()
        foreground = stc.get_color(Gtk.StateFlags.NORMAL)
        background = stc.get_background_color(Gtk.StateFlags.NORMAL)
        contrast = ThemeDetector._calculate_contrast(foreground, background)
        if contrast > 1:
            logger.debug('Guessed light theme from widget.')
            return False
        elif contrast < -1:
            logger.debug('Guessed dark theme from widget.')
            return True
        else:
            logger.debug('Unable to guess theme brightness from widget.')
            return None

    def _detect_theme():
        """
            Tries to detect or guess whether the theme is dark (True) or light
            (False).
        """
        theme_dark = ThemeDetector._detect_from_env()
        if theme_dark is not None:
            return theme_dark

        gtk_settings = Gtk.Settings.get_default()
        if gtk_settings is not None:
            if gtk_settings.get_property('gtk-theme-name') == 'Adwaita':
                logger.debug('Detected theme Adwaita from GtkSettings.')
                return gtk_settings.get_property('gtk-application-prefer-dark-theme')

        theme_dark = ThemeDetector._detect_from_widget()
        if theme_dark is not None:
            return theme_dark

        # Rely on GtkSettings anyway and hope they are right
        if gtk_settings is not None:
            logger.debug('Detected theme from GtkSettings.')
            return gtk_settings.get_property('gtk-application-prefer-dark-theme')

        # Default to light theme, we don't know any better.
        return False


def __test():
    "For testing purposes, not for public use."

    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gdk

    os.environ.pop('GTK_THEME')
    assert ThemeDetector._detect_from_env() is None

    os.environ['GTK_THEME'] = 'Adwaita:dark'
    assert ThemeDetector._detect_from_env()

    os.environ['GTK_THEME'] = 'Adwaita:light'
    assert not ThemeDetector._detect_from_env()

    os.environ['GTK_THEME'] = 'Adwaita:foo'
    assert ThemeDetector._detect_from_env() is None

    os.environ['GTK_THEME'] = 'Foobar'
    assert ThemeDetector._detect_from_env() is None

    #assert ThemeDetector._detect_from_widget() == True
    # note: one can only test _detect_from_widget once per process.
    #assert ThemeDetector._detect_from_widget() == False

    os.environ.pop('GTK_THEME')
    assert ThemeDetector._detect_from_env() is None
    assert ThemeDetector._detect_from_widget() is True

    foreground = Gdk.RGBA()
    Gdk.RGBA.parse(foreground, "rgb(148,151,150)")
    background = Gdk.RGBA()
    Gdk.RGBA.parse(background, "rgb(57,63,63)")
    assert ThemeDetector._calculate_contrast(foreground, background) < -1
    assert ThemeDetector._calculate_contrast(foreground, foreground) == 0


__test()
