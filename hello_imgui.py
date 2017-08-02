# coding: utf-8
'''
swig_imgui on pysdl2
'''
import sys
sys.path.append('.')
import os
python_dir=os.path.dirname(sys.executable)
os.environ['PATH']+=(';'+python_dir)
import ctypes

from OpenGL.GL import *

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
        format='%(levelname)s:%(name)s:%(message)s'
        , level=logging.DEBUG
        )


class Controller:
    """
    OpenGL
    """
    def __init__(self):
        self.width=0
        self.height=0
        self.is_initialized=False
        self.bind=ImGuiBind()

    def onResize(self, w, h):
        logger.debug('onResize: %d, %d', w, h)
        self.width=w
        self.height=h
        glViewport(0, 0, w, h)

    def onLeftDown(self, x, y):
        logger.debug('onLeftDown: %d, %d', x, y)

    def onLeftUp(self, x, y):
        logger.debug('onLeftUp: %d, %d', x, y)

    def onMiddleDown(self, x, y):
        logger.debug('onMiddleDown: %d, %d', x, y)

    def onMiddleUp(self, x, y):
        logger.debug('onMiddleUp: %d, %d', x, y)

    def onRightDown(self, x, y):
        logger.debug('onRightDown: %d, %d', x, y)

    def onRightUp(self, x, y):
        logger.debug('onRightUp: %d, %d', x, y)

    def onMotion(self, x, y):
        logger.debug('onMotion: %d, %d', x, y)

    def onWheel(self, d):
        logger.debug('onWheel: %d', d)

    def onKeyDown(self, keycode):
        logger.debug('onKeyDown: %d', keycode)

    def onUpdate(self, d):
        if not self.is_initialized:
            print(glGetString(GL_VERSION))
            self.is_initialized=True

        #logger.debug('onUpdate: delta %d ms', d)
        self.bind.new_frame(d, self.width, self.height)
        imgui.Text("Hello, world!");

    def draw(self):
        if not self.is_initialized:
            print(glGetString(GL_VERSION))
            self.is_initialized=True

        glClearColor(0.0, 0.0, 1.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBegin(GL_TRIANGLES)
        glVertex(-1.0,-1.0)
        glVertex( 1.0,-1.0)
        glVertex( 0.0, 1.0)
        glEnd()

        imgui.Render()

        glFlush()

import swig_imgui as imgui
class ImGuiBind:
    def __init__(self):
        self.font_texture=None
        self.shader_handle=None
        self.vs_handle=None
        self.fs_handle=None
        self.vbo_handle=None
        self.elements_handle=None
        self.vao_handle=None
        io=imgui.GetIO()
        io.SetRenderDrawListsFn(self.render_draw_lists)

    def new_frame(self, delta, w, h):
        if not self.font_texture:
            try:
                self.create_device_objects()
            except:
                import traceback
                traceback.print_exc()

        io=imgui.GetIO()

        size=imgui.ImVec2(w, h)
        #print(size)
        io.DisplaySize=size
        io.DisplayFramebufferScale = imgui.ImVec2(1, 1)
        io.DeltaTime = delta

        #io.MousePos
        #io.MouseDown
        #io.MouseWheel

        imgui.NewFrame()

        return delta

    def create_device_objects(self):
        io=imgui.GetIO()

        last_texture=glGetIntegerv(GL_TEXTURE_BINDING_2D);
        last_array_buffer=glGetIntegerv(GL_ARRAY_BUFFER_BINDING);
        last_vertex_array=glGetIntegerv(GL_VERTEX_ARRAY_BINDING);

        vertex_shader =b'''#version 330
uniform mat4 ProjMtx;
in vec2 Position;
in vec2 UV;
in vec4 Color;
out vec2 Frag_UV;
out vec4 Frag_Color;
void main()
{
	Frag_UV = UV;
	Frag_Color = Color;
	gl_Position = ProjMtx * vec4(Position.xy,0,1);
};
'''

        fragment_shader =b'''#version 330
uniform sampler2D Texture;
in vec2 Frag_UV;
in vec4 Frag_Color;
out vec4 Out_Color;
void main()
{
	Out_Color = Frag_Color * texture( Texture, Frag_UV.st);
};
'''

        self.shader_handle = glCreateProgram();
        self.vs_handle = glCreateShader(GL_VERTEX_SHADER);
        self.fs_handle = glCreateShader(GL_FRAGMENT_SHADER);
        glShaderSource(self.vs_handle, [vertex_shader]);
        glShaderSource(self.fs_handle, [fragment_shader]);
        glCompileShader(self.vs_handle);
        glCompileShader(self.fs_handle);
        glAttachShader(self.shader_handle, self.vs_handle);
        glAttachShader(self.shader_handle, self.fs_handle);
        glLinkProgram(self.shader_handle);

        self.g_AttribLocationTex = glGetUniformLocation(self.shader_handle, "Texture");
        self.g_AttribLocationProjMtx = glGetUniformLocation(self.shader_handle, "ProjMtx");
        self.g_AttribLocationPosition = glGetAttribLocation(self.shader_handle, "Position");
        self.g_AttribLocationUV = glGetAttribLocation(self.shader_handle, "UV");
        self.g_AttribLocationColor = glGetAttribLocation(self.shader_handle, "Color");

        self.vbo_handle=glGenBuffers(1);
        self.elements_handle=glGenBuffers(1);

        self.vao_handle=glGenVertexArrays(1);
        glBindVertexArray(self.vao_handle);
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_handle);
        glEnableVertexAttribArray(self.g_AttribLocationPosition);
        glEnableVertexAttribArray(self.g_AttribLocationUV);
        glEnableVertexAttribArray(self.g_AttribLocationColor);

        SIZE_OF_ImDrawVert=20
        glVertexAttribPointer(self.g_AttribLocationPosition, 2, GL_FLOAT, GL_FALSE, SIZE_OF_ImDrawVert, ctypes.c_void_p(0));
        glVertexAttribPointer(self.g_AttribLocationUV, 2, GL_FLOAT, GL_FALSE, SIZE_OF_ImDrawVert,  ctypes.c_void_p(8));
        glVertexAttribPointer(self.g_AttribLocationColor, 4, GL_UNSIGNED_BYTE, GL_TRUE, SIZE_OF_ImDrawVert,  ctypes.c_void_p(16));

        self.create_fonts_texture()

        # Restore modified GL state
        glBindTexture(GL_TEXTURE_2D, last_texture);
        glBindBuffer(GL_ARRAY_BUFFER, last_array_buffer);
        glBindVertexArray(last_vertex_array);

    def create_fonts_texture(self):
        # Build texture atlas
        io = imgui.GetIO();

        # Load as RGBA 32-bits (75% of the memory is wasted, but default font is so small) because it is more likely to be compatible with user's existing shaders. If your ImTextureId represent a higher-level concept than just a GL texture id, consider calling GetTexDataAsAlpha8() instead to save on GPU memory.
        pixels, width, height=imgui.GetTexDataAsRGBA32(); 

        # Upload texture to graphics system
        last_texture=glGetIntegerv(GL_TEXTURE_BINDING_2D);
        self.font_texture=glGenTextures(1);
        glBindTexture(GL_TEXTURE_2D, self.font_texture);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);

        # Store our identifier
        io.SetTexID(self.font_texture)

        # Restore state
        glBindTexture(GL_TEXTURE_2D, last_texture);

    def render_draw_lists(self, draw_data):
        # Avoid rendering when minimized, scale coordinates for retina displays (screen coordinates != framebuffer coordinates)
        io = imgui.GetIO();
        fb_width = int(io.DisplaySize.x * io.DisplayFramebufferScale.x);
        fb_height = int(io.DisplaySize.y * io.DisplayFramebufferScale.y);
        if (fb_width == 0 or fb_height == 0):
            return;
        draw_data.ScaleClipRects(io.DisplayFramebufferScale);

        # Backup GL state
        last_active_texture=glGetIntegerv(GL_ACTIVE_TEXTURE);
        glActiveTexture(GL_TEXTURE0);
        last_program=glGetIntegerv(GL_CURRENT_PROGRAM);
        last_texture=glGetIntegerv(GL_TEXTURE_BINDING_2D);
        last_array_buffer=glGetIntegerv(GL_ARRAY_BUFFER_BINDING);
        last_element_array_buffer=glGetIntegerv(GL_ELEMENT_ARRAY_BUFFER_BINDING);
        last_vertex_array=glGetIntegerv(GL_VERTEX_ARRAY_BINDING);
        last_blend_src_rgb=glGetIntegerv(GL_BLEND_SRC_RGB);
        last_blend_dst_rgb=glGetIntegerv(GL_BLEND_DST_RGB);
        last_blend_src_alpha=glGetIntegerv(GL_BLEND_SRC_ALPHA);
        last_blend_dst_alpha=glGetIntegerv(GL_BLEND_DST_ALPHA);
        last_blend_equation_rgb=glGetIntegerv(GL_BLEND_EQUATION_RGB);
        last_blend_equation_alpha=glGetIntegerv(GL_BLEND_EQUATION_ALPHA);
        last_viewport=glGetIntegerv(GL_VIEWPORT);
        last_scissor_box=glGetIntegerv(GL_SCISSOR_BOX);
        last_enable_blend = glIsEnabled(GL_BLEND);
        last_enable_cull_face = glIsEnabled(GL_CULL_FACE);
        last_enable_depth_test = glIsEnabled(GL_DEPTH_TEST);
        last_enable_scissor_test = glIsEnabled(GL_SCISSOR_TEST);

        # Setup render state: alpha-blending enabled, no face culling, no depth testing, scissor enabled
        glEnable(GL_BLEND);
        glBlendEquation(GL_FUNC_ADD);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glDisable(GL_CULL_FACE);
        glDisable(GL_DEPTH_TEST);
        glEnable(GL_SCISSOR_TEST);

        # Setup viewport, orthographic projection matrix
        glViewport(0, 0, fb_width, fb_height);
        ortho_projection = (ctypes.c_float * 16)(
             2.0/io.DisplaySize.x, 0.0,                   0.0, 0.0 ,
             0.0,                  2.0/-io.DisplaySize.y, 0.0, 0.0 ,
             0.0,                  0.0,                  -1.0, 0.0 ,
            -1.0,                  1.0,                   0.0, 1.0 ,
        );
        glUseProgram(self.shader_handle);
        glUniform1i(self.g_AttribLocationTex, 0);
        glUniformMatrix4fv(self.g_AttribLocationProjMtx, 1, GL_FALSE, ortho_projection);
        glBindVertexArray(self.vao_handle);

        for n in range(draw_data.CmdListsCount):
            cmd_list = draw_data.GetCmdList(n);
            idx_buffer_offset = 0;

            glBindBuffer(GL_ARRAY_BUFFER, self.vbo_handle);
            glBufferData(GL_ARRAY_BUFFER, cmd_list.VtxBuffer.Size * 20, cmd_list.GetVtxBufferData(), GL_STREAM_DRAW);

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.elements_handle);
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, cmd_list.IdxBuffer.Size * 2, cmd_list.GetIdxBufferData(), GL_STREAM_DRAW);

            for cmd_i in range(cmd_list.CmdBuffer.Size):
                pcmd = cmd_list.GetCmdBuffer(cmd_i);
                if pcmd.UserCallback:
                    pcmd.UserCallback(cmd_list, pcmd);
                else:
                    glBindTexture(GL_TEXTURE_2D, pcmd.TextureId);
                    #glScissor((int)pcmd->ClipRect.x, (int)(fb_height - pcmd->ClipRect.w), (int)(pcmd->ClipRect.z - pcmd->ClipRect.x), (int)(pcmd->ClipRect.w - pcmd->ClipRect.y));
                    glDrawElements(GL_TRIANGLES, pcmd.ElemCount, GL_UNSIGNED_SHORT, ctypes.c_void_p(idx_buffer_offset));

                idx_buffer_offset += pcmd.ElemCount;

        # Restore modified GL state
        glUseProgram(last_program);
        glBindTexture(GL_TEXTURE_2D, last_texture);
        glActiveTexture(last_active_texture);
        glBindVertexArray(last_vertex_array);
        glBindBuffer(GL_ARRAY_BUFFER, last_array_buffer);
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, last_element_array_buffer);
        glBlendEquationSeparate(last_blend_equation_rgb, last_blend_equation_alpha);
        glBlendFuncSeparate(last_blend_src_rgb, last_blend_dst_rgb, last_blend_src_alpha, last_blend_dst_alpha);
        if (last_enable_blend): 
            glEnable(GL_BLEND); 
        else: 
            glDisable(GL_BLEND);
        if (last_enable_cull_face): 
            glEnable(GL_CULL_FACE); 
        else: 
            glDisable(GL_CULL_FACE);
        if (last_enable_depth_test): 
            glEnable(GL_DEPTH_TEST); 
        else: 
            glDisable(GL_DEPTH_TEST);
        if (last_enable_scissor_test): 
            glEnable(GL_SCISSOR_TEST); 
        else: 
            glDisable(GL_SCISSOR_TEST);
        glViewport(last_viewport[0], last_viewport[1], last_viewport[2], last_viewport[3]);
        glScissor(last_scissor_box[0], last_scissor_box[1], last_scissor_box[2], last_scissor_box[3]);


from sdl2 import *
def loop(width, height, title=b'title'):

    SDL_Init(SDL_INIT_VIDEO)
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
    window = SDL_CreateWindow(title
            , SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED
            , width, height
            , SDL_WINDOW_OPENGL)
    SDL_GL_CreateContext(window)
    controller=Controller()
    controller.onResize(width, height)

    lastTime=SDL_GetTicks()
    event = SDL_Event()
    while True:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                return
            elif event.type == SDL_KEYDOWN:
                controller.onKeyDown(event.key.keysym.sym)
            elif event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.button==SDL_BUTTON_LEFT:
                    controller.onLeftDown(event.button.x, event.button.y)
                elif event.button.button==SDL_BUTTON_MIDDLE:
                    controller.onMiddleDown(event.button.x, event.button.y)
                elif event.button.button==SDL_BUTTON_RIGHT:
                    controller.onRightDown(event.button.x, event.button.y)
            elif event.type == SDL_MOUSEBUTTONUP:
                if event.button.button==SDL_BUTTON_LEFT:
                    controller.onLeftUp(event.button.x, event.button.y)
                elif event.button.button==SDL_BUTTON_MIDDLE:
                    controller.onMiddleUp(event.button.x, event.button.y)
                elif event.button.button==SDL_BUTTON_RIGHT:
                    controller.onRightUp(event.button.x, event.button.y)
            elif event.type == SDL_MOUSEMOTION:
                controller.onMotion(event.motion.x, event.motion.y)
            elif event.type == SDL_MOUSEWHEEL:
                controller.onWheel(-event.wheel.y)

        time=SDL_GetTicks()
        d=time-lastTime
        lastTime=time
        if d>0:
            controller.onUpdate(d)
            controller.draw()
            SDL_GL_SwapWindow(window)

if __name__=="__main__":

    loop(640, 480)
