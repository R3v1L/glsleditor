# -*- coding: utf-8 -*-
###############################################################################
# Copyright (C) 2008 EVO Sistemas Libres <central@evosistemas.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
###############################################################################
# srceditor.py
# Source editor module
###############################################################################

###############################################################################
# Source editor class
###############################################################################

# GTK imports
import gtk,pango

# GTK Sourceview
import gtksourceview2 as gtksourceview

# Application imports
import keymap

class SRCEditor:
    
    def __init__(self,ntbwidget,labeltext,statuslabel=None,closeable=False,lang=None):
        """
        Editor initialization
        """
        # Widget initialization
        self.ntbwidget=ntbwidget
        self.statuslabel=statuslabel
        self.labeltext=labeltext
        self.lang=lang
        # Create sourceview and related objects
        self.sbuffer = gtksourceview.SourceBuffer()
        self.scroll=gtk.ScrolledWindow()
        self.srcview=gtksourceview.SourceView(self.sbuffer)
        self.srcview.modify_font(pango.FontDescription('monospace 8'))
        self.scroll.add(self.srcview)
        # Editor signal connection
        self.sbuffer.connect('modified-changed', self.modifiedbuffer)
        self.sbuffer.connect('changed', self.updatestatus)
        self.srcview.connect('key_press_event',self.enhanceinput)
        self.srcview.connect('scroll_event',self.zoomeditor)
        self.srcview.connect('event', self.updatestatus)
        # Editor label
        self.label=gtk.Label(labeltext)
        self.label.set_padding(5,0)
        self.label.set_use_markup(True)
        # Set current language
        if self.lang:
            self.setlang(self.lang)
        # Show widgets
        self.scroll.show()
        self.srcview.show()
        self.label.show()
        # Adding widgets to notebook widget
        page=ntbwidget.prepend_page(self.scroll, self.label)
        # self.setPageConfig(page)
        self.ntbwidget.set_current_page(page)
        self.srcview.grab_focus()
        # Setup clipboard
        self.clipboard=gtk.Clipboard()
        # Status variables
        self.status={
            'line': 0,
            'offset': 0,
            'inputmode': 'INS',
        }
        # Update status
        self.updatestatus()
                
    def modifiedbuffer(self,widget):
        """
        Modified callback
        """
        self.label.set_label('<span foreground="#FF0000">' + self.labeltext + '</span>')

    def unmodifiedbuffer(self):
        """
        Modified callback
        """
        self.label.set_label(self.labeltext)
    
    def updatestatus(self,widget=None,event=None):
        """
        Status updating callback
        """
        curpos=self.getcursorpos()
        self.status['line']=curpos.get_line()+1
        self.status['offset']=curpos.get_line_offset()
        if self.srcview.get_overwrite():
            self.status['inputmode']='SOB'
        else:
            self.status['inputmode']='INS'
        if self.statuslabel:
            self.statuslabel.set_markup('%s  Línea: <b>%s</b>  Pos: <b>%s</b>' % (self.status['inputmode'],self.status['line'],self.status['offset']))
        if not self.sbuffer.get_modified():
            self.unmodifiedbuffer()
            
    def ismodified(self):
        """
        Returns if current editor has pending to save changes made
        """
        return self.sbuffer.get_modified()
        
    def enhanceinput(self,widget,event):
        """
        Enhanced input callback
        """
        # Selection tabbing
        if event.keyval==keymap.keycodes['tab']:
            self.indent()
            return True
        if event.keyval==keymap.keycodes['shifttab']:
            self.unindent()
            return True
        # Event propagation
        return False

    def getcursorpos(self):
        """
        Returns current cursor position
        """
        curiter=self.sbuffer.get_iter_at_offset(self.sbuffer.get_property('cursor-position'))
        return curiter


    def undo(self):
        """
        Undo last action
        """
        if self.sbuffer.can_undo():
            self.sbuffer.undo()
            self.srcview.scroll_to_iter(self.getcursorpos(),0.4)
        else:
            return False
        return True

    def redo(self):
        """
        Redo last undo
        """
        if self.sbuffer.can_redo():
            self.sbuffer.redo()
            self.srcview.scroll_to_iter(self.getcursorpos(),0.4)
        else:
            return False
        return True

    def cut(self):
        """
        Cut current selection to clipboard
        """
        if self.sbuffer.get_has_selection():
            self.sbuffer.cut_clipboard(self.clipboard,True)
    
    def copy(self):
        """
        Copy current selection to clipboard
        """
        if self.sbuffer.get_has_selection():
            self.sbuffer.copy_clipboard(self.clipboard)
    
    def paste(self):
        """
        Paste clipboard text into current cursor position
        """
        self.sbuffer.paste_clipboard(self.clipboard, None, True)
    
    def delete(self):
        """
        Delete current selection
        """
        if self.sbuffer.get_has_selection():
            self.sbuffer.delete_selection(False, False)

    def selectall(self):
        """
        Select all content
        """
        start,end=self.sbuffer.get_bounds()
        self.sbuffer.select_range(start,end)

    def selectnone(self):
        """
        Clears current selection
        """
        if self.sbuffer.get_has_selection():
            curpos=self.getcursorpos()
            start,end=self.sbuffer.get_selection_bounds()
            self.sbuffer.place_cursor(start)
            self.sbuffer.place_cursor(end)
            self.sbuffer.place_cursor(curpos)

    def goto(self,line):
        """
        Place cursor at specified line
        """
        lines=self.sbuffer.get_line_count()
        if line>lines:
            line=lines
        cur=self.sbuffer.get_iter_at_line(line-1)
        self.sbuffer.place_cursor(cur)
        self.srcview.scroll_to_iter(cur,0.4)

    def zoomeditor(self,widget=None,event=None):
        """
        Editor content zooming callback
        """
        def zoomIn():
            """
            Increase zooming
            """
            fontsize=self.srcview.get_pango_context().get_font_description().get_size() / 1024
            if fontsize<32:
                fontsize+=1
                self.srcview.modify_font(pango.FontDescription('monospace %s' % fontsize))
            return True

        def zoomOut():
            """
            Decrease zooming
            """
            fontsize=self.srcview.get_pango_context().get_font_description().get_size() / 1024
            if fontsize>6:
                fontsize-=1
                self.srcview.modify_font(pango.FontDescription('monospace %s' % fontsize))
            return True
        
        if widget.get_name()=='mnuViewZoomIn':
            return zoomIn()
        if widget.get_name()=='mnuViewZoomOut':
            return zoomOut()
        if event.direction == gtk.gdk.SCROLL_UP and event.state & gtk.gdk.CONTROL_MASK==gtk.gdk.CONTROL_MASK:
            return zoomIn()
        if event.direction == gtk.gdk.SCROLL_DOWN and event.state & gtk.gdk.CONTROL_MASK==gtk.gdk.CONTROL_MASK:
            return zoomOut()
        # Event propagation
        return False

    def linenums(self,status):
        """
        Shows/Hides line numbers
        """
        self.srcview.set_show_line_numbers(status)

    def indent(self):
        """
        Indents current selection or current line
        """
        tab='\t'
        if self.sbuffer.get_has_selection():
            # Indent complete selection
            selstart,selend=self.sbuffer.get_selection_bounds()
            startline=selstart.get_line()
            endline=selend.get_line()
            for line in range(startline,endline+1):
                self.sbuffer.insert(self.sbuffer.get_iter_at_line_offset(line,0),tab)
        else:
            # Only indent current line
            curiter=self.sbuffer.get_iter_at_offset(self.sbuffer.get_property('cursor-position'))
            self.sbuffer.insert(curiter,tab)

    def unindent(self):
        """
        Deindent current selection or current line
        """
        tab='\t'
        if self.sbuffer.get_has_selection():
            # Deindent complete selection
            selstart,selend=self.sbuffer.get_selection_bounds()
            startline=selstart.get_line()
            endline=selend.get_line()
            for line in range(startline,endline+1):
                # Comprobar si se puede desindentar
                starttab=self.sbuffer.get_iter_at_line_offset(line,0)
                if not starttab.ends_line() and starttab.get_chars_in_line()>len(tab):
                    endtab=self.sbuffer.get_iter_at_line_offset(line,len(tab))
                    if tab==self.sbuffer.get_text(starttab,endtab):
                        self.sbuffer.delete(starttab,endtab)
        else:
            # Only deindent current line
            curiter=self.sbuffer.get_iter_at_offset(self.sbuffer.get_property('cursor-position'))
            line=curiter.get_line()
            starttab=self.sbuffer.get_iter_at_line_offset(line,0)
            if not starttab.ends_line():
                endtab=self.sbuffer.get_iter_at_line_offset(line,len(tab))
                if tab==self.sbuffer.get_text(starttab,endtab):
                    self.sbuffer.delete(starttab,endtab)

    def toupper(self):
        """
        Converts selected text to upper case
        """
        if self.sbuffer.get_has_selection():
            start,end=self.sbuffer.get_selection_bounds()
            text=self.sbuffer.get_text(start,end)
            self.sbuffer.insert(start,text.upper())
            self.sbuffer.delete_selection(False,False)

    def tolower(self):
        """
        Converts selected text to lower case
        """
        if self.sbuffer.get_has_selection():
            start,end=self.sbuffer.get_selection_bounds()
            text=self.sbuffer.get_text(start,end)
            self.sbuffer.insert(start,text.lower())
            self.sbuffer.delete_selection(False,False)

    def get_text(self):
        """
        Returns text in editor
        """
        startiter,enditer=self.sbuffer.get_bounds()
        # Cargar datos del buffer
        return startiter.get_text(enditer)
    
    def clear(self,modified=False):
        """
        Clear editor contents
        """
        self.sbuffer.set_text('')
        if not modified:
            self.unmodifiedbuffer()

    def set_text(self,text,modified=False):
        """
        Replaces contents with especified text
        """
        start=self.sbuffer.set_text(text)
        if not modified:
            self.unmodifiedbuffer()

    def setlang(self,mimetype):
        """
        Set current language syntax hifunctionghlighting
        """
        # TODO: Syntax Highlighting doesn't go
        print "Cambiando lenguage a %s" % mimetype
        slmanager=gtksourceview.SourceLanguagesManager()
        lang=slmanager.get_language_from_mime_type(mimetype)     
        self.sbuffer.set_language(lang)
        self.sbuffer.set_highlight(True)
