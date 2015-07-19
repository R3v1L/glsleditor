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
# core.py
# Main load module for the application
###############################################################################

###############################################################################
# Datos generales de la aplicación
###############################################################################

metadata={
	'APP_NAME': 'GLSL Shader Editor',
	'APP_CODENAME': 'GLSLEditor',
	'APP_VERSION': '0.1',
	'APP_DESC': 'IDE Para la edición y visualización de Shaders',
	'APP_COPYRIGHT': '(C) 2008 EVO Sistemas Libres S.L.N.E. <central@evosistemas.com>',
	'APP_WEBSITE': 'http://www.evosistemas.com',
}
###############################################################################
# Importación de bibliotecas necesarias para la carga de la aplicación
###############################################################################

# Importación de bibliotecas de Python
import sys,os,shutil

# Importación de PyGTK
try:
	import pygtk,gobject,gtk
	pygtk.require('2.0')
except:
	print 'No se encuentra PyGTK en el sistema. Instale las bibliotecas PyGTK para poder ejecutar esta aplicación'
	sys.exit(1)

# Importación de Glade
try:
	import gtk.glade
except:
	print 'No se encuentra Glade en el sistema. Instale las bibliotecas Glade de python para ejecutar esta aplicación'
	sys.exit(1)
	
# Importación de GTK-Sourceview
try:
	import gtksourceview2 as gtksourceview
except:
	print 'No se encuentra GTKSourceView en el sistema. Instale las bibliotecas de GTKSourceView para ejecutar esta aplicación'
	sys.exit(1)

###############################################################################
# Importación de módulos de la aplicación
###############################################################################

# Importación del módulo de interfaz gráfica de usuario
import gui

###############################################################################
# Definición de clase de configuración
###############################################################################

# Clase de carga de configuración de la aplicación
class Config:
	"""
	Clase de carga de la configuración
	"""
	def __init__(self):
		"""
		Constructor de la clase de configuración
		"""
		# Intentar la carga de configuración desde fichero
		try:
			import settings
			print 'Error al cargar la configuración. Cargando configuración por defecto'
		except:
			self.defaults()
		# Cargar las variables en la configuración
		self.loadconfig()

	# Generar una configuración por defecto
	def defaults(self):
		"""
		Genera un fichero de configuración por defecto
		"""
		pass

	def loadconfig(self):
		"""
		Carga de la configuración
		"""
		# Abrir fichero de configuración
		# Cargar configuración
		# Hacer chequeo de la configuración
		pass

	def saveconfig(self):
		"""
		Guardar configuración
		"""
		# Recopilar datos
		# Abrir fichero para escritura
		# Escribir datos
		# Cerrar fichero

###############################################################################
# Inicialización de la aplicación
###############################################################################

def startup(args):
	"""
	Inicialización de la aplicación
	"""
	# Carga de la configuración de la aplicación
	config=Config()
	# Carga de glade
	gladetree=gtk.glade.XML(metadata['APP_CODENAME'] + '.glade')
	# Clase del GUI
	appgui=gui.GUI(metadata,config,gladetree)
	# Salida de la aplicación
	pass

def showhelp():
	"""
	Mostrar ayuda del programa
	"""
	print '%s v%s\n%s\n\t%s' % (metadata['APP_NAME'],metadata['APP_VERSION'],
		metadata['APP_CREDITS'],metadata['APP_DESC'])
	print 'Ayuda'
	sys.exit(1)

def showversion():
	print '%s v%s\n%s\n\t%s' % (metadata['APP_NAME'],metadata['APP_VERSION'],
		metadata['APP_CREDITS'],metadata['APP_DESC'])
	sys.exit(1)
