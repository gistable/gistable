# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2012 Owais Lone <hello@owaislone.org>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import os
import urllib
import urlparse
import logging
import locale
from locale import gettext as _
locale.textdomain('fogger')

from gi.repository import Gdk, GObject, GLib, Gtk, WebKit, Soup # pylint: disable=E0611

op = os.path
logger = logging.getLogger('fogger')

from fogger_lib import AppWindow, DesktopBridge, ConfirmDialog, DownloadManager
from fogger_lib.helpers import get_media_file, get_or_create_directory
from fogger_lib.BackgroundLoader import get_chameleonic_pixbuf_from_svg

from fogger.AboutFoggerDialog import AboutFoggerDialog
from fogger.PreferencesFoggerDialog import PreferencesFoggerDialog

MAXIMIZED = Gdk.WindowState.MAXIMIZED
FULLSCREEN = Gdk.WindowState.FULLSCREEN


# TODO: Move WebView and DownloadManager to their own classes and tidy up
# FoggerAppWindow class

class FoggerAppWindow(AppWindow):
    __gtype_name__ = "FoggerAppWindow"

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(FoggerAppWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutFoggerDialog
        self.PreferencesDialog = PreferencesFoggerDialog

        self.ui_loading = self.builder.get_object('ui_loading')
        self.webcontainer = self.builder.get_object('webview_container')
        self.appname = self.builder.get_object('appname')
        self.menubar = self.builder.get_object('menubar')
        self.statusbar = self.builder.get_object('statusbar')
        self.status_text = self.builder.get_object('status_text')
        self.progressbar = self.builder.get_object('progressbar')
        self.menu_app = self.builder.get_object('mnu_app')

        self.background_image = self.builder.get_object('bgimage')
        self.background_image.set_from_pixbuf(get_chameleonic_pixbuf_from_svg(
                                                       'background-app.svg'))
        self.extra_windows = []

    def setup_webview(self):
        self.webview = getattr(self, 'webview', None) or WebKit.WebView()
        self.setup_websettings()
        self.setup_webkit_session()
        self.webview_inspector = self.webview.get_inspector()
        self.webview_inspector.connect('inspect-web-view', self.inspect_webview)
        self.inspector_window = Gtk.Window()
        if self.root:
            self.downloads = self.root.downloads
        else:
            self.downloads = DownloadManager(self)
        self.webview.connect('notify::progress', self.on_load_progress)
        self.webview.connect('notify::title', self.on_title_changed)
        self.webview.connect('download-requested', self.downloads.requested)
        self.webview.connect('resource-request-starting', self.on_resource_request_starting)
        self.webview.connect('geolocation-policy-decision-requested', self.on_request_geo_permission)
        self.webview.connect('create-web-view', self.on_create_webview)
        self.webview.connect('database-quota-exceeded', self.on_database_quota_exceeded)
        frame = self.webview.get_main_frame()
        frame.connect('notify::load-status', self.on_frame_load_status)

        self.webcontainer.add(self.webview)
        self.webview.show()

        try:
            self.js_lib = open(get_media_file('js/fogger.js', '')).read()
        except:
            logger.error('Error reading fogger.js')
            self.js_lib = ""

    def inject_scripts(self):
        userscripts = self.app.scripts
        self.webview.execute_script(self.js_lib)
        for script in userscripts:
            self.webview.execute_script(script)

    def inject_styles(self):
        style_string = '\n'.join([S for S in self.app.styles if S and S != '\n'])

        doc = self.webview.get_dom_document()
        style = doc.create_element('style')
        style.set_attribute('rel', 'stylesheet')
        style.set_attribute('type', 'text/css')
        style.set_inner_html(style_string)

        def wait_and_inject(style):
            #head ou= doc.get_head()
            doc_element = doc.get_document_element()
            if doc_element:
                doc_element.append_child(style)
                return False
            return True
        GObject.timeout_add(50, wait_and_inject, style)

    def setup_webkit_session(self):
        session = WebKit.get_default_session()
        cache = get_or_create_directory(op.join(
            GLib.get_user_cache_dir(), 'fogger', self.app.uuid))
        cookie_jar = Soup.CookieJarText.new(op.join(cache, 'WebkitSession'), False)
        session.add_feature(cookie_jar)
        session.props.max_conns_per_host = 8

    def setup_websettings(self):
        self.webview.props.full_content_zoom = True
        self.websettings = WebKit.WebSettings()
        self.websettings.props.html5_local_storage_database_path = \
                                    get_or_create_directory(op.join(
                                            GLib.get_user_cache_dir(),
                                            'fogger/%s/db' % self.app.uuid))
        self.websettings.props.enable_accelerated_compositing = True
        self.websettings.props.enable_dns_prefetching = True
        self.websettings.props.enable_fullscreen = True
        self.websettings.props.enable_offline_web_application_cache = True
        self.websettings.props.javascript_can_open_windows_automatically = True
        self.websettings.props.enable_html5_database = True
        self.websettings.props.enable_html5_local_storage = True
        self.websettings.props.enable_hyperlink_auditing = False
        self.websettings.props.enable_file_access_from_file_uris = True
        self.websettings.props.enable_universal_access_from_file_uris = True
        self.websettings.props.enable_site_specific_quirks = True
        self.websettings.props.enable_spell_checking = True
        self.websettings.props.enable_webaudio = True
        self.websettings.props.enable_webgl = True
        self.websettings.props.enable_page_cache = True
        self.websettings.props.enable_plugins = True
        if logger.level == logging.DEBUG:
            self.websettings.props.enable_developer_extras = True

        # Change user-agent if USERAGENT environment variable is present.
        # e.g. add to launcher :
        # Exec=/usr/bin/env USERAGENT="iPad" /opt/extras.ubuntu.com/fogger/bin/fogger uuid
        useragent = os.getenv('USERAGENT')
        if useragent:
            self.websettings.set_property('user-agent', useragent)

        self.webview.set_settings(self.websettings)

    def inspect_webview(self, inspector, widget, data=None):
        inspector_view = WebKit.WebView()
        self.inspector_window.add(inspector_view)
        self.inspector_window.resize(800, 400)
        self.inspector_window.show_all()
        self.inspector_window.present()
        return inspector_view

    def open_downloads_folder(self, *args, **kwargs):
        self.downloads.open_folder(*args, **kwargs)

    def on_title_changed(self, webview, title, data=None):
        self.set_title(webview.props.title or self.app.name)

    def on_download_clicked(self, *args, **kwargs):
        return self.downloads.on_download_clicked(*args, **kwargs)

    def show_download_window(self, widget, data=None):
        self.downloads.show()

    def is_maximized(self):
        if self.props.window:
            return self.props.window.get_state() & MAXIMIZED == MAXIMIZED
        else:
            return False

    def is_fullscreen(self):
        if self.props.window:
            return self.props.window.get_state() & FULLSCREEN == FULLSCREEN
        else:
            return False

    def do_window_state_event(self, widget, data=None):
        if self.app and not self.is_popup:
            self.app.maximized = self.is_maximized()
            self.app.save()

    def on_size_allocate(self, widget, data=None):
        if not self.is_popup and not self.is_maximized():
            self.app.window_size = self.get_size()
            self.app.save()

    def on_load_progress(self, widget, propname):
        self.progressbar.set_fraction(self.webview.props.progress)

    def on_load_status_changed(self, widget, propname):
        if self.webview.props.load_status in \
                (WebKit.LoadStatus.FINISHED, WebKit.LoadStatus.FAILED):
            self.statusbar.hide()
        else:
            self.statusbar.show()

    def on_database_quota_exceeded(self, webview, frame, database, data=None):
        so = database.get_security_origin()
        quota = so.get_web_database_quota()
        so.set_web_database_quota(quota + 5242880) # Increase by 5mb

    def on_frame_load_status(self, frame, value):
        status = frame.props.load_status
        if status == WebKit.LoadStatus.COMMITTED:
            self.inject_scripts()
            self.inject_styles()
        #elif status == WebKit.LoadStatus.FINISHED:
            #self.inject_styles()
        elif status in (WebKit.LoadStatus.FIRST_VISUALLY_NON_EMPTY_LAYOUT,
                        WebKit.LoadStatus.FAILED):
            if self.ui_loading:
                self.ui_loading.destroy()
                self.ui_loading = None
                self.webview.connect('notify::load-status', self.on_load_status_changed)
                self.webcontainer.show()

    def on_web_view_ready(self, webview, data=None):
        window = self.__class__()
        # FIXME: Fix this hack and create proper support for popups
        app = type('FogApp', tuple(),
            {'icon': self.app.icon,
             'name': self.app.name,
             'url': webview.get_uri(),
             'uuid': self.app.uuid,
             'window_size': self.app.window_size,
             'maximized': False,
             'scripts': self.app.scripts,
             'styles': self.app.styles})
        window.webview = webview
        if self.is_popup:
            self.root.popups.append(window)
        else:
            self.popups.append(window)
        window.run_app(app, self.root or self)

    def on_resource_request_starting(self, widget, frame, resource, request, response, data=None):
        uri = urllib.unquote(request.props.uri)
        if uri.startswith('http://fogger.local/'):
            request.props.uri = 'about:blank'
            query = urlparse.parse_qs(urlparse.urlparse(uri).query)
            method = query.get('action', None)
            if method:
                method = method[0]
                getattr(self.bridge, method)(self, query)
            return True

    def on_request_geo_permission(self, view, frame, decision, data=None):
        d = ConfirmDialog(self.app.name, _('Geolocation permission requested'),
            _('%s wants to know your current location. Do you want to share?'\
            % (frame.get_uri() or self.app.name)), None, self,
            _('Share'))
        response = d.run()
        d.destroy()

        if response == Gtk.ResponseType.YES:
            WebKit.geolocation_policy_allow(decision)
        else:
            WebKit.geolocation_policy_deny(decision)
        return True

    def on_create_webview(self, widget, frame, data=None):
        webview = WebKit.WebView()
        webview.set_settings(self.webview.get_settings())
        webview.connect('web-view-ready', self.on_web_view_ready)
        return webview

    def on_zoom_in(self, widget, data=None):
        self.webview.zoom_in()

    def on_zoom_out(self, widget, data=None):
        self.webview.zoom_out()

    def on_zoom_reset(self, widget, data=None):
        self.webview.props.zoom_level = 1.0

    def on_reload(self, widget, data=None):
        self.webview.reload()
    on_retry = on_reload

    def on_go_home(self, widget, data=None):
        l = self.webview.get_back_forward_list()
        steps = l.get_back_length()
        if self.is_popup:
            self.parent.webview.go_back_or_forward(steps * -1)
            self.parent.preset()
        else:
            self.webview.go_back_or_forward(steps * -1)

    def on_go_fullscreen(self, widget, data=None):
        if self.is_fullscreen():
            self.unfullscreen()
        else:
            self.fullscreen()

    def on_go_back(self, widget, data=None):
        self.webview.go_back()

    def on_go_forward(self, widget, data=None):
        self.webview.go_forward()

    def on_fogger_app_remove(self, widget, data=None):
        self.app.remove()
        self.destroy()

    def on_fogger_app_reset(self, widget, data=None):
        self.app.reset()
        self.webview.reload()

    def on_fogger_autostart_changed(self, widget, autostart):
        self.app.autostart = autostart

    def resize_window(self, MW, MH, W, H):
        H = H if H <= MH else MH
        W = W if W <= MW else MW
        self.resize(W, H)

    def run_app(self, app, root=None):
        self.app = app
        self.root = root
        self.menu_app.set_label('_%s' % self.app.name)
        self.setup_webview()
        if op.isfile(self.app.icon):
            self.set_icon_from_file(self.app.icon)
        else:
            self.set_icon_name(self.app.icon)
        self.set_title(app.name or app.url or 'FogApp')
        self.set_role('fogger-%s' % app.uuid)
        wm_class = 'fogapp-%s' % app.uuid
        self.set_wmclass('fogapp', wm_class)
        screen = Gdk.Screen.get_default()
        max_h = screen.get_height()
        max_w = screen.get_width()
        if not root:
            self.bridge = DesktopBridge(self, self.app.desktop_file_name, self.app.icon)
            self.appname.set_text(app.name)
            self.webview.load_uri(self.app.url)
            self.resize_window(max_w, max_h, *self.app.window_size)
            if self.app.maximized:
                self.maximize()
        else:
            self.bridge = self.root.bridge
            self.downloads = self.root.downloads
            self.appname.set_text('Loading...')
            wf = root.webview.props.window_features
            if wf.props.width > 0 and wf.props.height > 0:
                self.resize_window(max_w, max_h, wf.props.width, wf.props.height)
            else:
                self.resize(800, 600)
            if wf.props.fullscreen:
                self.fullscreen()
        self.show()
