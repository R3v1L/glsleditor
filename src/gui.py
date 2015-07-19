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
# gui.py
# GUI management module
###############################################################################

# Python imports
import os

# Glade and GTK imports
import gobject,gtk,gtk.glade,pango

# GTK Sourceview
import gtksourceview2 as gtksourceview

# Application imports
from srceditor import SRCEditor
from glslefile import GLSLEFile
import glwidget

class GUI:
	"""
	Clase principal del GUI de la aplicación
	"""

	def __init__(self,metadata,config,gladetree):
		"""
		Constructor de la clase de control del GUI
		"""
		# Almacenar metadatos de la aplicación
		self.metadata=metadata
		# Almacenar configuración
		self.config=config
		# Almacenar objeto de Glade para definiciones del GUI
		self.gladetree=gladetree
		# Contenedor para los widgets utilizados
		self.widgets={}
		# Inicialización de la aplicación
		self.apprun()
		
	def getwindows(self):
		"""
		Carga de las ventanas de la aplicación
		"""
		self.winMain=self.gladetree.get_widget('winMain')
		self.winAbout=self.gladetree.get_widget('winAbout')
		self.winFileChooser=self.gladetree.get_widget('winFileChooser')
		self.winGoTo=self.gladetree.get_widget('winGoTo')
		self.winTextureInfo=self.gladetree.get_widget('winTextureInfo')
		self.winPreferences=self.gladetree.get_widget('winPreferences')
		self.winProjectInfo=self.gladetree.get_widget('winProjectInfo')
		self.winFindReplace=self.gladetree.get_widget('winFindReplace')		

	def getwidgets(self):
		"""
		Cargar widgets necesarios para el control de la aplicación
		"""
		# Lista de widgets a cargar
		widgetlist=[
			# Menu items
			'mnuFileClose',	'mnuViewLineNums',
			# Toolbar buttons
			'tlbtClose',
			# Status bars
			'stbMain', 'sbtEditor',
			# Editor widgets
			'ntbEditor','lblEditorStatus',
			# Go to entry
			'entGoTo',
			# Texture sizes combo box
			'cmbTextureSizes',
			# Texture icon view
			'icvTextures',
			# Project info
			'entProjectInfoName', 'txtProjectInfoComments',
			# Texture info dialog widgets
			'lblTextureInfoID', 'lblTextureInfoFile', 'lblTextureInfoSize', 'imgTextureInfo', 'imgTextureInfoOrig',
			'scrTextureInfo',
			# OpenGL Shader preview widgets
			'vbxPreviewBox','cmbPreviewPrimitive',
		]
		for widgetname in widgetlist:
			self.widgets[widgetname]=self.gladetree.get_widget(widgetname)

	def connectsignals(self):
		"""
		Conectar señales del GUI
		"""
		# Conectar las señales
		signals = {
			# Main signals
			'quitApplication': self.quitApplication, # Application quit
			'showAbout': self.showAbout, # Show about dialog
			# File operation signals
			'fileNew': self.fileNew,
			'fileOpen': self.fileOpen,
			'fileClose': self.fileClose,
			'fileSave': self.fileSave,
			# TODO: SaveAs Functionality
			#'fileSaveAs': self.fileSaveAs,
			# Edition signals
			'editUndo': self.editUndo,
			'editRedo': self.editRedo,
			'editCopy': self.editCopy,
			'editCut': self.editCut,
			'editPaste': self.editPaste,
			'editDelete': self.editDelete,
			'editSelectAll': self.editSelectAll,
			'editSelectNone': self.editSelectNone,
			'editGoTo': self.editGoTo,
			'editPreferences': self.editPreferences,
			# Viewing signals
			'viewLineNums': self.viewLineNums,
			# Formatting signals
			'formatUnindent': self.formatUnindent,
			'formatIndent': self.formatIndent,			
			'formatToLower': self.formatToLower,
			'formatToUpper': self.formatToUpper,
			# Texture signals
			'toolsProjectProperties': self.toolsProjectProperties,
			'toolsAddTexture': self.toolsAddTexture,
			'toolsDelTexture': self.toolsDelTexture,
			'toolsRefreshTextures': self.toolsRefreshTextures,
			'toolsTextureInfo': self.toolsTextureInfo,
			'toolsReloadShader': self.toolsReloadShader,
			'toolsAnimatePreview': self.toolsAnimatePreview,
			'toolsStopAnimatePreview': self.toolsStopAnimatePreview,
			'toolsSetPrimitive': self.toolsSetPrimitive,
			# Texture info dialog signals
			'textureZoomIn': self.textureZoomIn,
			'textureZoomOut': self.textureZoomOut,
			'textureZoomOrig': self.textureZoomOrig,
			'textureZoomAdjust': self.textureZoomAdjust,
			'textureZoomWheel': self.textureZoomWheel,
			# Background parameters signals
			'changeBGColor': self.changeBGColor,
		}
		self.gladetree.signal_autoconnect(signals)

	def loadmetadata(self):
		"""
		Metadata loading method
		"""
		# Load main window metadata
		self.winMain.set_title(self.metadata['APP_CODENAME'] + ' ' + self.metadata['APP_VERSION'])
		# Load about dialog metadata
		self.winAbout.set_name(self.metadata['APP_CODENAME'])
		self.winAbout.set_version(self.metadata['APP_VERSION'])
		self.winAbout.set_copyright(self.metadata['APP_COPYRIGHT'])
		self.winAbout.set_website(self.metadata['APP_WEBSITE'])
		self.winAbout.set_comments(self.metadata['APP_DESC'])
		self.winAbout.set_logo(gtk.gdk.pixbuf_new_from_file('pixmaps/' + self.metadata['APP_CODENAME'] + '.png'))

	def loadconfig(self):
		"""
		Configuration loading method
		"""
		# Disable close file actions
		self.widgets['tlbtClose'].set_sensitive(False)
		self.widgets['mnuFileClose'].set_sensitive(False)
		# Set default texture size
		self.widgets['cmbTextureSizes'].set_active(0)
		# Set default primitive for preview
		self.widgets['cmbPreviewPrimitive'].set_active(0)
		# Project file selection filter
		self.ffglsle=gtk.FileFilter()
		self.ffglsle.set_name('Proyecto de GLSL Editor (*.glsle)')
		self.ffglsle.add_pattern('*.glsle')
		# File chooser window parameters
		self.winFileChooser.set_select_multiple(False)
		# Image file selection filter
		self.ffimage = gtk.FileFilter()
		self.ffimage.set_name('Archivos de imagen soportados (*.jpg, *.jpeg, *.png, *.bmp)')
		self.ffimage.add_pattern('*.jpg')
		self.ffimage.add_pattern('*.jpeg')
		self.ffimage.add_pattern('*.png')
		self.ffimage.add_pattern('*.bmp')

	def initializeapp(self):
		"""
		Widget initialization for application
		"""
		# Editor objects initialization
		self.feditor=SRCEditor(self.widgets['ntbEditor'],'Fragment',self.widgets['lblEditorStatus'],lang='text/x-csrc')
		self.veditor=SRCEditor(self.widgets['ntbEditor'],'Vertex',self.widgets['lblEditorStatus'],lang='text/x-csrc')
		# Project info dictionary
		self.prjinfo={'name':'','comments':'',}
		# Texture list objects initialization
		self.texturelist = gtk.ListStore(str, gtk.gdk.Pixbuf, str)
		self.widgets['icvTextures'].set_model(self.texturelist)
		self.widgets['icvTextures'].set_text_column(0)
		self.widgets['icvTextures'].set_pixbuf_column(1)
		self.widgets['icvTextures'].set_text_column(2)
		# OpenGL Preview widget initialization
		display_mode = (gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE)
		self.glarea = glwidget.GLDrawingArea(display_mode)
		self.widgets['vbxPreviewBox'].add(self.glarea)
		self.glarea.show()

	def apprun(self):
		"""
		GUI initialization and main event loop
		"""
		# Window and dialog widgets loading
		self.getwindows()
		# Widget loading
		self.getwidgets()
		# Signal connection
		self.connectsignals()
		# Load metadata
		self.loadmetadata()
		# Initialize required objects
		self.initializeapp()
		# Load config
		self.loadconfig()
		# Enter main event loop
		gtk.main()

	def cleanup(self):
		"""
		Program cleanup
		"""
		gtk.main_quit()

	########################################################################
	# Auxiliar methods
	########################################################################

	def getCurrentEditor(self):
		"""
		Gets the editor object associated to the current page
		"""
		curpage=self.widgets['ntbEditor'].get_current_page()
		child=self.widgets['ntbEditor'].get_nth_page(curpage)
		if child==self.veditor.scroll:
			return self.veditor
		elif child==self.feditor.scroll:
			return self.feditor
		return None

	def setFileChooserFilters(self,filters):
		"""
		Clear current filechooser filters and add the specified ones
		"""
		for filter in self.winFileChooser.list_filters():
			self.winFileChooser.remove_filter(filter)		
		for filter in filters:
			self.winFileChooser.add_filter(filter)
			
	def getTextureSize(self):
		"""
		Returns the current width,height texture size parameters
		"""
		w,h=self.widgets['cmbTextureSizes'].get_active_text().split('x')
		return(int(w),int(h))

	def packTextureData(self):
		"""
		Packs texture data for saving
		"""
		texlist=[]
		iter=self.texturelist.get_iter_first()
		if iter:
			while iter:
				file=self.texturelist.get_value(iter,0)
				id=self.texturelist.get_value(iter, 2)
				iter=self.texturelist.iter_next(iter)
				texlist.append((id,file))
		return texlist

	def getProjectInfo(self):
		"""
		Saves project info to project info dictionary
		"""
		self.prjinfo['name']=self.widgets['entProjectInfoName'].get_text()
		buffer=self.widgets['txtProjectInfoComments'].get_buffer()
		startiter,enditer=buffer.get_bounds()
		self.prjinfo['comments']=startiter.get_text(enditer)

	def clearProject(self):
		"""
		Clears project data
		"""
		if self.confirmNotSaving():
			if not self.msgDialog('question','Aún no ha grabado los cambios en el proyecto. ¿Confirma que desea cerrar el proyecto actual?'):
				return False
		self.widgets['entProjectInfoName'].set_text('')
		self.widgets['txtProjectInfoComments'].get_buffer().set_text('')
		self.veditor.clear()
		self.feditor.clear()
		self.texturelist.clear()
		return True

	def loadProject(self,data):
		"""
		Loads project data
		"""
		self.widgets['entProjectInfoName'].set_text(data.name)
		self.widgets['txtProjectInfoComments'].get_buffer().set_text(data.comments)
		self.veditor.set_text(data.vertex)
		self.feditor.set_text(data.fragment)
		self.loadTextures(data.textures)

	def loadTextures(self,texturedata):
		"""
		Loads texture list
		"""
		self.texturelist.clear()
		for texture in texturedata:
			self.texturelist.append([texture[1], None,texture[0]])
		self.toolsRefreshTextures()

	def confirmNotSaving(self):
		"""
		Confirms not to save the current project
		"""
		return self.veditor.ismodified() or self.feditor.ismodified()

	########################################################################
	# Signal callbacks
	########################################################################

	def fileNew(self,widget):
		"""
		Creates a new project
		"""
		self.clearProject()
		
	def fileOpen(self,widget):
		"""
		Open an existing project
		"""
		# Check if it's an already loaded project or modified files
		self.clearProject()
		# Set dialog to open mode
		self.winFileChooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
		# Select filter and open dialog
		self.setFileChooserFilters([self.ffglsle,])
		resp=self.openDialog(self.winFileChooser,close=True)
		file=self.winFileChooser.get_filename()
		if file and resp==gtk.RESPONSE_OK:
			# Convert filename to UTF8
			file=unicode(file,'utf-8')
			# Load file data
			#try:
			data=GLSLEFile(file)
			self.loadProject(data)
			#except:
			#self.msgDialog('error','No se ha podido cargar el archivo %s' % file)
			return
		else:
			# No file selected
			return

	def fileClose(self,widget):
		"""
		Closing current loaded project
		"""
		# Comprobar si hay un fichero cargado
		if True:
			# Confirmar cierre
			if self.msgDialog('question','¿Confirma que desea cerrar el proyecto actual?'):
				# Limpieza de variables
				self.clearProject()
				# Deshabilitar opciones de cierre de archivo
				self.widgets['tlbtClose'].set_sensitive(False)
				self.widgets['mnuFileClose'].set_sensitive(False)
				return True
			else:
				return False
	
	def fileSave(self,widget):
		"""
		Save an existing project
		"""
		# Check if project has information set
		if self.prjinfo['name']=='':
			self.toolsProjectProperties()
		# Set dialog to save mode
		self.winFileChooser.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
		# Select filter and open dialog
		self.setFileChooserFilters([self.ffglsle,])
		resp=self.openDialog(self.winFileChooser,close=True)
		file=self.winFileChooser.get_filename()
		if file and resp==gtk.RESPONSE_OK:
			# Convert filename to UTF8
			file=unicode(file,'utf-8')
			# Save data to file
			data=GLSLEFile()
			vertexdata=self.veditor.get_text()
			fragmentdata=self.feditor.get_text()
			#try:
			data.save(file,self.prjinfo,'',vertexdata,fragmentdata,self.packTextureData())
			#except:
			#	self.msgDialog('error','No se ha podido grabar el archivo %s' % file)
			# Change editors state
			self.veditor.unmodifiedbuffer()
			self.feditor.unmodifiedbuffer()
		else:
			# No file selected
			return

	def editUndo(self,widget):
		"""
		Undo last action
		"""
		editor=self.getCurrentEditor()
		if editor:
			if not editor.undo():
				self.msgDialog('warning','No hay acciones que puedan deshacerse')

	def editRedo(self,widget):
		"""
		Redo last undo
		"""
		editor=self.getCurrentEditor()
		if editor:
			if not editor.redo():
				self.msgDialog('warning','No hay acciones que puedan rehacerse')
			
	def editCopy(self,widget):
		"""
		Cut text to clipboard
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.copy()
			
	def editCut(self,widget):
		"""
		Cut text to clipboard
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.cut()

	def editPaste(self,widget):
		"""
		Paste text from clipboard
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.paste()

	def editDelete(self,widget):
		"""
		Delete selected text
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.delete()

	def editSelectAll(self,widget):
		"""
		Select all text in current editor
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.selectall()

	def editSelectNone(self,widget):
		"""
		Clear selection in current editor
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.selectnone()

	def editGoTo(self,widget):
   	    """
   	    Place cursor at selected line
   	    """
   	    editor=self.getCurrentEditor()
   	    if editor:
   	        self.widgets['entGoTo'].set_text('')
   	        resp=self.openDialog(self.winGoTo)
   	        if resp==gtk.RESPONSE_OK:
   	        	line=int(self.widgets['entGoTo'].get_text().strip())
   	        	editor.goto(line)
   	        self.closeDialog(self.winGoTo)
   	    else:
   	    	self.msgDialog('error','No hay ningún editor de código en uso')

	def editPreferences(self,widget):
   	    """
   	    Shows preferences dialog
   	    """
   	    resp=self.openDialog(self.winPreferences)
   	    if resp==gtk.RESPONSE_OK:
   	    	# Save and apply new preferences
   	    	print "Grabar preferencias"
   	    else:
   	    	# Reload actual preferences
   	    	print "Recargar preferencias"	
   	    self.closeDialog(self.winPreferences)


   	def viewLineNums(self,widget=None):
		"""
		Show line numbers
		"""
   		if widget:
   			status=widget.get_active()
   		else:
   			status=self.widgets['mnuViewLineNums'].get_active()
   		self.veditor.linenums(status)
   		self.feditor.linenums(status)
   		self.widgets['mnuViewLineNums'].set_active(status)

	def formatIndent(self,widget):
		"""
		Indents current selection or line
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.indent()

	def formatUnindent(self,widget):
		"""
		Unindents current selection or line
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.unindent()

	def formatToUpper(self,widget):
		"""
		Converts current selection to upper case
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.toupper()

	def formatToLower(self,widget):
		"""
		Converts current selection to upper case
		"""
		editor=self.getCurrentEditor()
		if editor:
			editor.tolower()

	def toolsProjectProperties(self,widget=None):
		"""
		Shows project properties dialog
		"""
		while True:
			resp=self.openDialog(self.winProjectInfo,close=True)
			if self.widgets['entProjectInfoName'].get_text()=='':
				self.msgDialog('error','El proyecto debe tener un nombre')
			else:
				break
			# Get project properties and save to project dictionary
		self.getProjectInfo()

	def toolsAddTexture(self,widget):
		"""
		Adds a new texture to list
		"""
		# Open texture file selection dialog 
		self.winFileChooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
		self.winFileChooser.set_select_multiple(False)
		# Clear filters
		self.setFileChooserFilters([self.ffimage,])
		resp=self.openDialog(self.winFileChooser,close=True)
		file=self.winFileChooser.get_filename()
		if file and resp==gtk.RESPONSE_OK:
			# Convert filename to UTF8
			file=unicode(file,'utf-8')
			self.texturelist.append([file, None,''])
			self.toolsRefreshTextures(msg='Añadida nueva textura desde fichero %s' % file)
		else:
			return

	def toolsDelTexture(self,widget):
		"""
		Deletes currently selected texture
		"""
		paths=self.widgets['icvTextures'].get_selected_items()
		for path in paths:
			iter=self.texturelist.get_iter(path)
			textureid=self.texturelist.get_value(iter,2)
			if self.msgDialog('question','¿Confirma eliminar la textura %s?' % textureid):
				self.texturelist.remove(iter)
				self.toolsRefreshTextures(reload=False,msg='Eliminada textura. Lista de texturas actualizada')
		
	def toolsRefreshTextures(self,widget=None,reload=True,msg='Lista de texturas actualizada'):
		"""
		Refresh texture list
		"""
		# TODO: Problem with iconview refreshing
		self.glarea.redraw=False
		iter=self.texturelist.get_iter_first()
		id=0
		w,h=self.getTextureSize()
		if iter:
			while iter:
				id+=1
				file=self.texturelist.get_value(iter,0)
				if reload:
					self.statusMessage('info','Cargando fichero de textura %s' % file)
					icon = gtk.gdk.pixbuf_new_from_file(file)
					# Resize pixbuf to preferred size
					icon=icon.scale_simple(w,h,gtk.gdk.INTERP_BILINEAR)
					self.texturelist.set_value(iter, 1, icon)
				self.texturelist.set_value(iter, 2, 'Texture' + str(id))
				iter=self.texturelist.iter_next(iter)
			self.statusMessage('info',msg)
			if widget==self.widgets['cmbTextureSizes']:
				self.widgets['icvTextures'].set_item_width(w)
		else:
			self.statusMessage('info','')
		self.glarea.redraw=True
	
	def toolsTextureInfo(self,widget,event=None):
		"""
		Shows texture info dialog
		"""
		paths=self.widgets['icvTextures'].get_selected_items()
		for path in paths:
			# Retrieve texture info
			iter=self.texturelist.get_iter(path)
			file=self.texturelist.get_value(iter,0)
			id=self.texturelist.get_value(iter,2)
			img = gtk.gdk.pixbuf_new_from_file(file)
			size=str(img.get_width()) + 'x' + str(img.get_height())
			# Show info in texture info dialog
			self.widgets['lblTextureInfoID'].set_text(id)
			self.widgets['lblTextureInfoFile'].set_text(file)
			self.widgets['lblTextureInfoSize'].set_text(size)
			self.widgets['imgTextureInfoOrig'].set_from_pixbuf(img)
			self.widgets['imgTextureInfo'].set_from_pixbuf(img)
			resp=self.openDialog(self.winTextureInfo,close=True)

	def toolsReloadShader(self,widget):
		"""
		Recompile shader to be shown in preview window
		"""
		self.glarea.compileshader(self.veditor.get_text(),self.feditor.get_text())
		self.glarea.queue_draw()

	def toolsAnimatePreview(self,widget):
		"""
		Start shader preview animation
		"""
		self.glarea.redraw=True
		self.glarea.queue_draw()

	def toolsStopAnimatePreview(self,widget):
		"""
		Stop shader preview animation
		"""
		self.glarea.redraw=False

	def toolsSetPrimitive(self,widget):
		"""
		Set the currently selected primitive to be rendered
		"""
		self.glarea.setprimitive(self.widgets['cmbPreviewPrimitive'].get_active_text())

	def changeBGColor(self,widget):
		"""
		Set the currently selected color to background clearing color
		"""
		color=widget.get_color()
		r=color.red/65535.0
		g=color.green/65535.0
		b=color.blue/65535.0
		a=widget.get_alpha()/65535.0
		print (r,g,b,a)
		self.glarea.setbackground(r,g,b,a)

	########################################################################
	# Texture info dialog signals
	########################################################################

	def textureZoomIn(self,widget=None):
		"""
		Zoom in texture
		"""
		orig=self.widgets['imgTextureInfoOrig'].get_pixbuf()
		img=self.widgets['imgTextureInfo'].get_pixbuf()
		w=int(img.get_width()*1.5)
		h=int(img.get_height()*1.5)
		if w>1500: w=1500
		if h>1500: h=1500
		# Disable zoom in
		img=orig.scale_simple(w+1,h+1,gtk.gdk.INTERP_BILINEAR)
		self.widgets['imgTextureInfo'].set_from_pixbuf(img)

	def textureZoomOut(self,widget=None):
		"""
		Zoom out texture
		"""
		orig=self.widgets['imgTextureInfoOrig'].get_pixbuf()
		img=self.widgets['imgTextureInfo'].get_pixbuf()
		w=int(img.get_width()*0.5)
		h=int(img.get_height()*0.5)
		if w<5: w=5
		if h<5: h=5
		# Disable zoom out
		img=orig.scale_simple(w,h,gtk.gdk.INTERP_BILINEAR)
		self.widgets['imgTextureInfo'].set_from_pixbuf(img)

	def textureZoomOrig(self,widget):
		"""
		Set original texture size
		"""
		self.widgets['imgTextureInfo'].set_from_pixbuf(self.widgets['imgTextureInfoOrig'].get_pixbuf())

	def textureZoomAdjust(self,widget):
		"""
		Adjust texture size to image widget size
		TODO: Width and height of viewing area has to be got
		"""
		orig=self.widgets['imgTextureInfoOrig'].get_pixbuf()
		img=self.widgets['imgTextureInfo'].get_pixbuf()
		x,y=self.widgets['scrTextureInfo'].get_child_requisition()
		img=orig.scale_simple(x,y,gtk.gdk.INTERP_BILINEAR)
		self.widgets['imgTextureInfo'].set_from_pixbuf(img)

	def textureZoomWheel(self,widget,event):
		"""
		Texture mouse-wheel zooming callback
		"""
		if event.direction == gtk.gdk.SCROLL_UP and event.state & gtk.gdk.CONTROL_MASK==gtk.gdk.CONTROL_MASK:
			self.textureZoomIn()
		if event.direction == gtk.gdk.SCROLL_DOWN and event.state & gtk.gdk.CONTROL_MASK==gtk.gdk.CONTROL_MASK:
			self.textureZoomOut()
		# Event propagation
		return False
	
	########################################################################
	# About dialog signals
	########################################################################

	def showAbout(self,widget):
		"""
		Mostrar diálogo Acerca de...
		"""
		self.openDialog(self.winAbout,close=True)

	########################################################################
	# Other tool methods
	########################################################################

	def msgDialog(self,mode,msg,desc=None,parent=None,cancel=False):
		"""
		Shows a message dialog
		"""
		dialogmodes={
			'info': (gtk.MESSAGE_INFO,gtk.BUTTONS_OK),
			'warning': (gtk.MESSAGE_WARNING,gtk.BUTTONS_CLOSE),
			'question': (gtk.MESSAGE_WARNING,gtk.BUTTONS_YES_NO),
			'error': (gtk.MESSAGE_ERROR,gtk.BUTTONS_CLOSE),
		}
		# Comprobamos si el modo de diálogo es correcto
		if dialogmodes.has_key(mode):
			mode=dialogmodes[mode]
			if not parent:
				parent=self.winMain
		else:
			parent=self.winMain
			mode=dialogmodes['error']
			msg='Error interno'
			desc='Se ha producido un error al definir un diálogo de mensaje'
		# Creación del diálogo
		dialog=gtk.MessageDialog(parent,gtk.DIALOG_MODAL and gtk.DIALOG_DESTROY_WITH_PARENT,mode[0],mode[1])
		if cancel:
			dialog.add_button('Cancelar', 1)
		# Añadir el mensaje del diálogo
		dialog.set_markup('<b>' + msg + '</b>')
		# Añadir mensaje secundario si se ha especificado
		if desc:
			dialog.format_secondary_markup(desc)
		# Mostrar diálogo y recoger respuesta
		resp=dialog.run()
		# Interpretación de la respuesta
		if cancel:
			if resp==1:
				resp='cancel'
			else:
				resp=resp==gtk.RESPONSE_YES
		else:
			resp=resp==gtk.RESPONSE_YES
		# Cierre del diálogo
		dialog.destroy()
		return resp

	def statusMessage(self,context,message,desc=None,showdialog=False):
		"""
		Shows a message in main status bar
		"""
		contextid=self.widgets['stbMain'].get_context_id(context)
		self.widgets['stbMain'].pop(contextid)
		self.widgets['stbMain'].push(contextid,message)
		if desc or showdialog:
			self.msgDialog(context,message)

	def preOpenDialog(self):
		"""
		Executes dialog pre-opening operations
		"""
		self.animstatus=self.glarea.redraw
		self.glarea.redraw=False
		
	def postOpenDialog(self):
		"""
		Executes dialog post-opening operations
		"""
		self.glarea.redraw=self.animstatus
		
	def openDialog(self,dialog,delete=False,close=False):
		"""
		Open a dialog
		"""
		self.preOpenDialog()
		resp=dialog.run()
		if (not delete and resp==gtk.RESPONSE_DELETE_EVENT) or close:
			self.closeDialog(dialog)
		self.postOpenDialog()
		return resp

	def closeDialog(self,dialog):
		"""
		Close a dialog
		"""
		dialog.hide()
		return True

	def quitApplication(self,widget,event=None):
		"""
		Salida del programa
		"""
		if self.msgDialog('question','¿Realmente desea salir de %s?' % self.metadata['APP_NAME']):
			self.cleanup()
		return True

	def htmlColor(self,color):
		"""
		Convertir una instancia de gtk.gdk.Color() en color HTML
		"""
		r=hex(color.red/256)[2:].upper()
		g=hex(color.green/256)[2:].upper()
		b=hex(color.blue/256)[2:].upper()
		if len(r)<2: r='0'+r
		if len(g)<2: g='0'+g
		if len(b)<2: b='0'+b
		return '#%s%s%s' % (r,g,b)
