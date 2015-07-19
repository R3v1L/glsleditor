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
# glwidget.py
# OpenGL Widget
###############################################################################

# OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# GTK imports
import gtk
from gtk import gtkgl

# Application imports
import glslview

# Default shader
DEFAULT_VERTEX="""
varying vec3 vN;
varying vec3 v;

void main(void)
{

   v = vec3(gl_ModelViewMatrix * gl_Vertex);       
   vN = normalize(gl_NormalMatrix * gl_Normal);

   gl_Position = (gl_ModelViewProjectionMatrix * gl_Vertex);

}
"""

DEFAULT_FRAGMENT="""
varying vec3 vN;
varying vec3 v; 

#define MAX_LIGHTS 8

void main (void) 
{ 
   vec3 N = normalize(vN);
   vec4 finalColor = vec4(0.0, 0.0, 0.0, 0.0);
   
   for (int i=0;i<MAX_LIGHTS;i++)
   {
      vec3 L = normalize(gl_LightSource[i].position.xyz - v); 
      vec3 E = normalize(-v); // we are in Eye Coordinates, so EyePos is (0,0,0) 
      vec3 R = normalize(-reflect(L,N)); 
   
      //calculate Ambient Term: 
      vec4 Iamb = gl_FrontLightProduct[i].ambient; 

      //calculate Diffuse Term: 
      vec4 Idiff = gl_FrontLightProduct[i].diffuse * max(dot(N,L), 0.0);
      Idiff = clamp(Idiff, 0.0, 1.0); 
   
      // calculate Specular Term:
      vec4 Ispec = gl_FrontLightProduct[i].specular 
             * pow(max(dot(R,E),0.0),0.3*gl_FrontMaterial.shininess);
      Ispec = clamp(Ispec, 0.0, 1.0); 
   
      finalColor += Iamb + Idiff + Ispec;
   }
   
   // write Total Color: 
   gl_FragColor = (gl_FrontLightModelProduct.sceneColor + finalColor); 
}
"""

class GLDrawingArea(gtk.DrawingArea, gtk.gtkgl.Widget):
    
    def __init__(self, display_mode):
        """
        Class initialization
        """
        
        # Initialize parent class
        gtk.DrawingArea.__init__(self)
        
        # Manageable events
        self.set_events(gtk.gdk.BUTTON_MOTION_MASK | gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK|
            gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_RELEASE_MASK|
            gtk.gdk.BUTTON_PRESS_MASK |  gtk.gdk.SCROLL_MASK)    

        # OpenGL config
        try:                              
            glconfig = gtk.gdkgl.Config(mode = display_mode)
        except gtk.gdkgl.NoMatches:
            display_mode &= ~gtk.gdkgl.MODE_SINGLE
            glconfig = gtk.gdkgl.Config(mode = display_mode)
        self.set_gl_capability(glconfig)

        self.angle=0
        self.primitive='Plano'
        self.redraw=False
        
        # Signal connections
        self.connect( "expose_event", self.__gldrwexpose)
        self.connect( "realize", self.__gldrwrealize)
        self.connect( "configure_event", self.__gldrwconfigure)        

    def __gldrwconfigure(self, *args):
        """
        GLDrawingArea display configuration
        """
        # Get GL drawable and context
        self.gldrawable = self.get_gl_drawable()
        self.glcontext = self.get_gl_context()
        allocation=self.get_allocation()
        self.gldrawable.gl_begin(self.glcontext)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90.0, allocation.width/float(allocation.height), 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glViewport(0, 0, allocation.width, allocation.height)
        gluLookAt(0.0,0.0,0.5, 0.0,0.0,0.0, 0.0, 1.0, 0.0)
        self.gldrawable.gl_end()
                
    def __gldrwrealize(self, *args):
        """
        GLDrawingArea view setting callback
        """
        # OpenGL state initialization
        self.gldrawable.gl_begin(self.glcontext)
        glutInit()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,GL_TRUE)
        glEnable(GL_COLOR_MATERIAL)
        self.gldrawable.gl_end()
        # Compile default shader
        self.compileshader()
      
    def __gldrwexpose(self, *args):
        """
        GLDrawingArea drawing callback
        """
        self.gldrawable.gl_begin(self.glcontext)
        self.__preview()
        self.gldrawable.swap_buffers()
        self.gldrawable.gl_end()
        if self.redraw:
            self.angle += 0.2
            self.queue_draw()

    def __preview(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.setlights()
        glTranslate(0.0, 0.0, -3.0)
        glRotate(self.angle, 1.0, 1.0, 1.0)
        # Select shader
        glUseProgram(self.program)
        # Draw current primitive
        self.drawprimitive()
        # Deselect shader
        glUseProgram(0)

    def __countfps(self):
        """
        Counts FPS and refresh fps counter
        """
        pass

    def compileshader(self,vertexdata=DEFAULT_VERTEX,fragmentdata=DEFAULT_FRAGMENT):
        """
        Compiles shader data
        """
        self.gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()
        self.gldrawable.gl_begin(self.glcontext)     
        self.program = glslview.compile_program(vertexdata,fragmentdata)
        self.gldrawable.gl_end()

    def setlights(self):
        """
        Set lighting parameters
        """
        ambient = [0, 0, 0, 1]
        diffuse = [0.5, 0.5, 0.5, 0]
        specular = [1, 1, 1, 1]
        specular1 = [1, 0, 0, 1]
        specular2 = [0, 1, 0, 1]
        specular3 = [0, 0, 1, 1]
        position1=[2, 1, 0, 1]
        position2=[-2, 1, 0, 1]
        position3 = [0, 1, 1, 1]
    
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular1)
        glLightfv(GL_LIGHT0, GL_POSITION, position1)
    
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, ambient)
        glLightfv(GL_LIGHT1, GL_SPECULAR, specular2)
        glLightfv(GL_LIGHT1, GL_POSITION, position2)
    
        glLightfv(GL_LIGHT2, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT2, GL_DIFFUSE, ambient)
        glLightfv(GL_LIGHT2, GL_SPECULAR, specular3)
        glLightfv(GL_LIGHT2, GL_POSITION, position3)
    
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 20)
    
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_LIGHTING)

    def setbackground(self,r,g,b,a,image=None):
        """
        Sets background
        """
        self.gldrawable.gl_begin(self.glcontext)
        glClearColor(r,g,b,a)
        print "Cambiado el color"
        self.gldrawable.gl_end()

    def setprimitive(self,id):
        """
        Sets current primitive to be drawn
        """
        self.primitive=id
        self.__gldrwexpose()

    def drawprimitive(self):
        # TODO: Texture Mapping coord for cube,sphere,torus
        if self.primitive=='Plano':
            glBegin(GL_QUADS)
            glVertex3f(-1.5,-1.5,0)
            glTexCoord2d(0,0)
            glNormal3f(0,0,1)
            glVertex3f(-1.5,1.5,0)
            glTexCoord2d(0,1)
            glNormal3f(0,0,1)
            glVertex3f(1.5,1.5,0)
            glTexCoord2d(1,1)
            glNormal3f(0,0,1)
            glVertex3f(1.5,-1.5,0)
            glTexCoord2d(1,0)
            glNormal3f(0,0,1)
            glEnd()
        elif self.primitive=='Cubo':
            glutSolidCube(2)
        elif self.primitive=='Esfera':
            glutSolidSphere(2,32,32)
        elif self.primitive=='Toroide':
            glutSolidTorus(0.35,1.0,32,32)
        elif self.primitive=='Tetera':
            glutSolidTeapot(1.0)
