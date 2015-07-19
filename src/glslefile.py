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
# glsledfile.py
# GLSL Editor File Format
###############################################################################

# Python imports
# import base64
import xml.dom.minidom
from xml.sax import saxutils

# Format version
GLSLE_VERSION=0.1

# Format template
GLSLE_TEMPLATE="""<?xml version="1.0" encoding="UTF-8" ?>
<glsleproject name="%s" version="%s">
<!-- Project comments and information -->
<comments>%s</comments>

<!-- Project environment -->
<environment>%s</environment>

<!-- Vertex data section -->
<vertexdata>%s</vertexdata>

<!-- Fragment data section -->
<fragmentdata>%s</fragmentdata>

<!-- Textures section -->
<textures>%s</textures>
</glsleproject>"""

GLSLE_TEXTURE='<texture id="%s" filename="%s" />\n'

GLSLE_TEXTUREDATA="""
<texture id="%s" filename="%s" >
    %s
</texture>
"""

class GLSLEFile:
    """
    GLSLEdFile format class
    """
        
    def __init__(self,filename=None):
        """
        Class constructor
        """
        if filename:
            self.load(filename)
    
    def load(self, filename):
        """
        Loads filename and stores read data
        """
        # Open file and read data
        dom=xml.dom.minidom.parse(filename)
        # Parse read data
        self.__parsedata(dom)

    def save(self,filename,prjinfo, environment, vertexdata, fragmentdata, texturedata):
        """
        Saves data to filename
        """
        # Prepare data
        data=self.__preparedata(prjinfo,environment,vertexdata,fragmentdata,texturedata)
        # Save data to file
        fd=open(filename,'w')
        fd.write(data)
        fd.close()
        
    def __preparedata(self,prjinfo,environment,vertexdata,fragmentdata,texturedata):
        """
        Packing data for writing
        """
        # Generate environment section
        environ=''
        # Generate textures section
        textures=''
        for texture in texturedata:
            textures+=GLSLE_TEXTURE % (texture[0],texture[1])
        return GLSLE_TEMPLATE % (saxutils.escape(prjinfo['name']),GLSLE_VERSION,saxutils.escape(prjinfo['comments']),environ,
            saxutils.escape(vertexdata),saxutils.escape(fragmentdata),textures)
    
    def __parsedata(self,dom):
        """
        Retrieve data from loaded file
        """
        # Load project name
        glsle=dom.documentElement
        self.name=saxutils.unescape(glsle.getAttribute('name'))
        # Load project comments
        # TODO: Check if node has childs before get values
        self.comments=saxutils.unescape(glsle.getElementsByTagName('comments')[0].firstChild.nodeValue)
        # Get vertex data
        self.vertex=saxutils.unescape(dom.getElementsByTagName('vertexdata')[0].firstChild.nodeValue)
        # Get fragment data
        self.fragment=saxutils.unescape(dom.getElementsByTagName('fragmentdata')[0].firstChild.nodeValue)
        # Get textures
        texlist=[]
        textures=glsle.getElementsByTagName('texture')
        for texture in textures:
            # TODO: Save texture data to avoid loading or dependences from external files
            id=texture.getAttribute('id')
            filename=texture.getAttribute('filename')
            texlist.append((id,filename))
        self.textures=texlist
