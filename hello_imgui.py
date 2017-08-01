# coding: utf-8
'''
Win32APIでOpenGLホストするサンプル
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
    [CLASSES] Controllerクラスは、glglueの規約に沿って以下のコールバックを実装する
    """
    def __init__(self):
        self.width=0
        self.height=0

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
        #logger.debug('onUpdate: delta %d ms', d)
        pass

    def draw(self):
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
    def __init__(self, hwnd, controller):
        self.hwnd=hwnd
        self.controller=controller
        self.time=0
        self.font_texture=None
        io=imgui.GetIO()
        io.SetRenderDrawListsFn(self.render_draw_lists)

    def render_draw_lists(self, draw_data):
        try:
            # Avoid rendering when minimized, scale coordinates for retina displays (screen coordinates != framebuffer coordinates)
            io = imgui.GetIO()
            fb_width = io.DisplaySize.x * io.DisplayFramebufferScale.x
            fb_height = io.DisplaySize.y * io.DisplayFramebufferScale.y
            if fb_width == 0 or fb_height == 0:
                return
            draw_data.ScaleClipRects(io.DisplayFramebufferScale)

            # We are using the OpenGL fixed pipeline to make the example code simpler to read!
            # Setup render state: alpha-blending enabled, no face culling, no depth testing, scissor enabled, vertex/texcoord/color pointers.
            last_texture=glGetIntegerv(GL_TEXTURE_BINDING_2D)
            last_viewport=glGetIntegerv(GL_VIEWPORT)
            last_scissor_box=glGetIntegerv(GL_SCISSOR_BOX)
            glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_TRANSFORM_BIT)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_CULL_FACE)
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_SCISSOR_TEST)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
            glEnable(GL_TEXTURE_2D)
            #glUseProgram(0); // You may want this if using this code in an OpenGL 3+ context where shaders may be bound

            # Setup viewport, orthographic projection matrix
            glViewport(0, 0, int(fb_width), int(fb_height));
            glMatrixMode(GL_PROJECTION);
            glPushMatrix();
            glLoadIdentity();
            glOrtho(0.0, io.DisplaySize.x, io.DisplaySize.y, 0.0, -1.0, 1.0);
            glMatrixMode(GL_MODELVIEW);
            glPushMatrix();
            glLoadIdentity();

            # Render command lists
            #define OFFSETOF(TYPE, ELEMENT) ((size_t)&(((TYPE *)0)->ELEMENT))
            for n in range(draw_data.CmdListsCount):
                cmd_list = draw_data.GetCmdList(n);
                vtx_buffer = cmd_list.GetVtxBufferData();
                float_array=(ctypes.c_float * cmd_list.VtxBuffer.Size)
                vtx_buffer = float_array.from_buffer(bytearray(vtx_buffer))

                idx_buffer = cmd_list.GetIdxBufferData()
                short_array=(ctypes.c_uint16 * cmd_list.IdxBuffer.Size)
                idx_buffer = short_array.from_buffer(bytearray(idx_buffer))
                #idx_buffer = [idx_buffer[i] for i in range(len(idx_buffer))]

                glVertexPointer(2, GL_FLOAT, 5*4, vtx_buffer);
                #glTexCoordPointer(2, GL_FLOAT, sizeof(ImDrawVert), (const GLvoid*)((const char*)vtx_buffer + OFFSETOF(ImDrawVert, uv)));
                #glColorPointer(4, GL_UNSIGNED_BYTE, sizeof(ImDrawVert), (const GLvoid*)((const char*)vtx_buffer + OFFSETOF(ImDrawVert, col)));

                for cmd_i in range(cmd_list.CmdBuffer.Size):
                    pcmd = cmd_list.GetCmdBuffer(cmd_i);
                    if pcmd.UserCallback:
                        pcmd.UserCallback(cmd_list, pcmd);
                    else:
                        glBindTexture(GL_TEXTURE_2D, pcmd.TextureId);
                        #glScissor(pcmd.ClipRect.x, fb_height - pcmd.ClipRect.w, pcmd.ClipRect.z - pcmd.ClipRect.x, pcmd.ClipRect.w - pcmd.ClipRect.y);
                        #glDrawElements(GL_TRIANGLES, pcmd.ElemCount, sizeof(ImDrawIdx) == 2 ? GL_UNSIGNED_SHORT : GL_UNSIGNED_INT, idx_buffer);
                        #indices=idx_buffer[:pcmd.ElemCount]
                        glDrawElements(GL_TRIANGLES, pcmd.ElemCount, GL_UNSIGNED_SHORT, idx_buffer);
                    idx_buffer = idx_buffer[pcmd.ElemCount:]
            #undef OFFSETOF

            # Restore modified state
            glDisableClientState(GL_COLOR_ARRAY);
            glDisableClientState(GL_TEXTURE_COORD_ARRAY);
            glDisableClientState(GL_VERTEX_ARRAY);
            glBindTexture(GL_TEXTURE_2D, last_texture);
            glMatrixMode(GL_MODELVIEW);
            glPopMatrix();
            glMatrixMode(GL_PROJECTION);
            glPopMatrix();
            glPopAttrib();
            glViewport(last_viewport[0], last_viewport[1], last_viewport[2], last_viewport[3]);
            glScissor(last_scissor_box[0], last_scissor_box[1], last_scissor_box[2], last_scissor_box[3]);
        except:
            import traceback
            traceback.print_exc()

    def create_device_objects(self):
        io=imgui.GetIO()

        pixels, width, height=imgui.GetTexDataAsRGBA32()

        # Upload texture to graphics system
        last_texture=glGetIntegerv(GL_TEXTURE_BINDING_2D)
        self.font_texture=int(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.font_texture);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE
                     , ctypes.cast(pixels, ctypes.c_void_p));

        # Store our identifier
        print(type(self.font_texture))
        io.SetTexID(self.font_texture)

        # Restore state
        glBindTexture(GL_TEXTURE_2D, last_texture);

    def new_frame(self):
        if not self.font_texture:
            self.create_device_objects()

        io=imgui.GetIO()

        size=imgui.ImVec2(
            self.controller.width, self.controller.height)
        #print(size)
        io.DisplaySize=size
        io.DisplayFramebufferScale = imgui.ImVec2(1, 1)
        time=glglue.wgl.timeGetTime()
        delta=0
        if self.time!=0:
            delta=time - self.time
        self.time=time
        io.DeltaTime = delta

        #io.MousePos
        #io.MouseDown
        #io.MouseWheel

        imgui.NewFrame()

        return delta


def loop(window):
    bind=ImGuiBind(window.hwnd, window.controller)

    msg = glglue.wgl.MSG()
    pMsg = ctypes.pointer(msg)
    NULL = ctypes.c_int(win32con.NULL)
    #while windll.user32.GetMessageA( pMsg, NULL, 0, 0) != 0:
    #    windll.user32.TranslateMessage(pMsg)
    #    windll.user32.DispatchMessageA(pMsg)
    while True:
        while ctypes.windll.user32.PeekMessageA(pMsg
                , NULL, 0, 0, win32con.PM_NOREMOVE) != 0:
            if ctypes.windll.user32.GetMessageA(pMsg, NULL, 0, 0)==0:
                return msg.wParam
            ctypes.windll.user32.TranslateMessage(pMsg)
            ctypes.windll.user32.DispatchMessageA(pMsg)

            d=bind.new_frame()

            imgui.Text("Hello, world!");

            if d>0:
                window.controller.onUpdate(d)
                window.Redraw()


if __name__=="__main__":

    import win32con
    import pathlib
    p=str(pathlib.Path(__file__).parent.joinpath('glglue'))
    print(p)
    sys.path.append(p)
    import glglue.wgl
    factory=glglue.wgl.WindowFactory()
    window=factory.create(glglue.wgl.Window)
    window.createGLContext(16)
    window.controller=Controller()
    glglue.wgl.ShowWindow(window.hwnd, win32con.SW_SHOWNORMAL)

    loop(window)

