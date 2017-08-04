import swig_imgui as imgui
from sdl2 import *
import ctypes
from OpenGL.GL import *


SIZEOF_ImDrawVert=imgui.SIZEOF_ImDrawVert
SIZEOF_ImDrawIdx=imgui.SIZEOF_ImDrawIdx
OFFSETOF_ImDrawVert_pos=imgui.OFFSETOF_ImDrawVert_pos
OFFSETOF_ImDrawVert_uv=imgui.OFFSETOF_ImDrawVert_uv
OFFSETOF_ImDrawVert_col=imgui.OFFSETOF_ImDrawVert_col

def Init(window):
    io = imgui.GetIO();
    #io.SetKeyMap(imgui.ImGuiKey_Tab, SDLK_TAB);
    io.SetKeyMap(imgui.ImGuiKey_LeftArrow, SDL_SCANCODE_LEFT);
    io.SetKeyMap(imgui.ImGuiKey_RightArrow, SDL_SCANCODE_RIGHT);
    io.SetKeyMap(imgui.ImGuiKey_UpArrow, SDL_SCANCODE_UP);
    io.SetKeyMap(imgui.ImGuiKey_DownArrow, SDL_SCANCODE_DOWN);
    io.SetKeyMap(imgui.ImGuiKey_PageUp, SDL_SCANCODE_PAGEUP);
    io.SetKeyMap(imgui.ImGuiKey_PageDown, SDL_SCANCODE_PAGEDOWN);
    io.SetKeyMap(imgui.ImGuiKey_Home, SDL_SCANCODE_HOME);
    io.SetKeyMap(imgui.ImGuiKey_End, SDL_SCANCODE_END);
    io.SetKeyMap(imgui.ImGuiKey_Delete, SDLK_DELETE);
    io.SetKeyMap(imgui.ImGuiKey_Backspace, SDLK_BACKSPACE);
    io.SetKeyMap(imgui.ImGuiKey_Enter, SDLK_RETURN);
    io.SetKeyMap(imgui.ImGuiKey_Escape, SDLK_ESCAPE);
    io.SetKeyMap(imgui.ImGuiKey_A, SDLK_a);
    io.SetKeyMap(imgui.ImGuiKey_C, SDLK_c);
    io.SetKeyMap(imgui.ImGuiKey_V, SDLK_v);
    io.SetKeyMap(imgui.ImGuiKey_X, SDLK_x);
    io.SetKeyMap(imgui.ImGuiKey_Y, SDLK_y);
    io.SetKeyMap(imgui.ImGuiKey_Z, SDLK_z);

    # Alternatively you can set this to NULL and call imgui.GetDrawData() after imgui.Render() to get the same ImDrawData pointer.
    def Render(data):
        try:
            RenderDrawLists(data)
        except:
           import traceback
           traceback.print_exc()
    io.SetRenderDrawListsFn(Render);   
    #io.SetClipboardTextFn = SetClipboardText;
    #io.GetClipboardTextFn = GetClipboardText;
    #io.ClipboardUserData = NULL;

#ifdef _WIN32
    wmInfo=SDL_SysWMinfo();
    SDL_VERSION(wmInfo.version);
    SDL_GetWindowWMInfo(window, wmInfo);
    io.SetImeWindowHandle(wmInfo.info.win.window)
#else
    #(void)window;
#endif

    return True;


def ProcessEvent(event):
    global g_MouseWheel
    global g_MousePressed

    io = imgui.GetIO();
    if event.type==SDL_MOUSEWHEEL:
        if (event.wheel.y > 0):
            g_MouseWheel = 1;
        if (event.wheel.y < 0):
            g_MouseWheel = -1;
        return True;
    elif event.type==SDL_MOUSEBUTTONDOWN:
        if (event.button.button == SDL_BUTTON_LEFT): g_MousePressed[0] = True;
        if (event.button.button == SDL_BUTTON_RIGHT): g_MousePressed[1] = True;
        if (event.button.button == SDL_BUTTON_MIDDLE): g_MousePressed[2] = True;
        return True;
    elif event.type==SDL_TEXTINPUT:
        io.AddInputCharactersUTF8(event.text.text);
        return True;
    elif event.type==SDL_KEYDOWN or event.type==SDL_KEYUP:
        key = event.key.keysym.sym & ~SDLK_SCANCODE_MASK;
        io.SetKeysDown(key, event.type == SDL_KEYDOWN);
        io.KeyShift = ((SDL_GetModState() & KMOD_SHIFT) != 0);
        io.KeyCtrl = ((SDL_GetModState() & KMOD_CTRL) != 0);
        io.KeyAlt = ((SDL_GetModState() & KMOD_ALT) != 0);
        io.KeySuper = ((SDL_GetModState() & KMOD_GUI) != 0);
        return True;

    return False;


g_FontTexture=None
g_ShaderHandle=None
g_VertHandle=None
g_FragHandle=None
g_AttribLocationTex=None
g_AttribLocationProjMtx=None;
g_AttribLocationPosition=None;
g_AttribLocationUV=None;
g_AttribLocationColor=None;
g_VboHandle=None;
g_ElementsHandle=None;
g_VaoHandle=None;

def CreateFontsTexture():
    # Build texture atlas
    io = imgui.GetIO();
    # Load as RGBA 32-bits for OpenGL3 demo because it is more likely to be compatible with user's existing shader.
    pixels, width, height=io.Fonts.GetTexDataAsRGBA32();

    # Upload texture to graphics system
    last_texture=glGetIntegerv(GL_TEXTURE_BINDING_2D);
    g_FontTexture=glGenTextures(1);
    glBindTexture(GL_TEXTURE_2D, g_FontTexture);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glPixelStorei(GL_UNPACK_ROW_LENGTH, 0);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);

    # Store our identifier
    io.Fonts.SetTexID(g_FontTexture);

    # Restore state
    glBindTexture(GL_TEXTURE_2D, last_texture);

def CreateDeviceObjects():

    global g_ShaderHandle
    global g_VertHandle
    global g_FragHandle
    global g_AttribLocationTex
    global g_AttribLocationProjMtx;
    global g_AttribLocationPosition;
    global g_AttribLocationUV;
    global g_AttribLocationColor;
    global g_VboHandle;
    global g_ElementsHandle;
    global g_VaoHandle;

    # Backup GL state
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

    g_ShaderHandle = glCreateProgram();
    g_VertHandle = glCreateShader(GL_VERTEX_SHADER);
    g_FragHandle = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(g_VertHandle, vertex_shader);
    glShaderSource(g_FragHandle, fragment_shader);
    glCompileShader(g_VertHandle);
    glCompileShader(g_FragHandle);
    glAttachShader(g_ShaderHandle, g_VertHandle);
    glAttachShader(g_ShaderHandle, g_FragHandle);
    glLinkProgram(g_ShaderHandle);

    g_AttribLocationTex = glGetUniformLocation(g_ShaderHandle, "Texture");
    g_AttribLocationProjMtx = glGetUniformLocation(g_ShaderHandle, "ProjMtx");
    g_AttribLocationPosition = glGetAttribLocation(g_ShaderHandle, "Position");
    g_AttribLocationUV = glGetAttribLocation(g_ShaderHandle, "UV");
    g_AttribLocationColor = glGetAttribLocation(g_ShaderHandle, "Color");

    g_VboHandle=glGenBuffers(1);
    g_ElementsHandle=glGenBuffers(1);

    g_VaoHandle=glGenVertexArrays(1);
    glBindVertexArray(g_VaoHandle);
    glBindBuffer(GL_ARRAY_BUFFER, g_VboHandle);
    glEnableVertexAttribArray(g_AttribLocationPosition);
    glEnableVertexAttribArray(g_AttribLocationUV);
    glEnableVertexAttribArray(g_AttribLocationColor);

#define OFFSETOF(TYPE, ELEMENT) ((size_t)&(((TYPE *)0).ELEMENT))
    glVertexAttribPointer(g_AttribLocationPosition, 2, GL_FLOAT, GL_FALSE, SIZEOF_ImDrawVert, ctypes.c_void_p(OFFSETOF_ImDrawVert_pos));
    glVertexAttribPointer(g_AttribLocationUV, 2, GL_FLOAT, GL_FALSE, SIZEOF_ImDrawVert, ctypes.c_void_p(OFFSETOF_ImDrawVert_uv));
    glVertexAttribPointer(g_AttribLocationColor, 4, GL_UNSIGNED_BYTE, GL_TRUE, SIZEOF_ImDrawVert, ctypes.c_void_p(OFFSETOF_ImDrawVert_col));
#undef OFFSETOF

    CreateFontsTexture();

    # Restore modified GL state
    glBindTexture(GL_TEXTURE_2D, last_texture);
    glBindBuffer(GL_ARRAY_BUFFER, last_array_buffer);
    glBindVertexArray(last_vertex_array);

    return True;

g_MousePressed=[False, False, False]
g_MouseWheel=0
g_Time=0
def NewFrame(window):
    global g_MousePressed, g_MouseWheel, g_Time

    if not g_FontTexture:
        CreateDeviceObjects();

    io = imgui.GetIO();

    # Setup display size (every frame to accommodate for window resizing)
    w=ctypes.c_int()
    h=ctypes.c_int()
    SDL_GetWindowSize(window, w, h);
    display_w=ctypes.c_int()
    display_h=ctypes.c_int()
    SDL_GL_GetDrawableSize(window, display_w, display_h);
    io.DisplaySize = imgui.ImVec2(w.value, h.value);
    io.DisplayFramebufferScale = imgui.ImVec2(
        (display_w.value / float(w.value)) if w.value > 0 else 0, 
        (display_h.value / float(h.value)) if h.value > 0 else 0);

    # Setup time step
    time = SDL_GetTicks();
    current_time = time / 1000.0;
    io.DeltaTime = (current_time - g_Time) if g_Time > 0.0 else (1.0 / 60.0);
    g_Time = current_time;

    # Setup inputs
    # (we already got mouse wheel, keyboard keys & characters from SDL_PollEvent())
    mx=ctypes.c_int()
    my=ctypes.c_int()
    mouseMask = SDL_GetMouseState(mx, my);
    if (SDL_GetWindowFlags(window) & SDL_WINDOW_MOUSE_FOCUS):
        # Mouse position, in pixels (set to -1,-1 if no mouse / on another screen, etc.)
        io.MousePos = imgui.ImVec2(mx.value, my.value);   
    else:
        io.MousePos = imgui.ImVec2(-1, -1);

    # If a mouse press event came, always pass it as "mouse held this frame", so we don't miss click-release events that are shorter than 1 frame.
    io.SetMouseDown(0, g_MousePressed[0] or (mouseMask & SDL_BUTTON(SDL_BUTTON_LEFT)) != 0);		
    io.SetMouseDown(1, g_MousePressed[1] or (mouseMask & SDL_BUTTON(SDL_BUTTON_RIGHT)) != 0);
    io.SetMouseDown(2, g_MousePressed[2] or (mouseMask & SDL_BUTTON(SDL_BUTTON_MIDDLE)) != 0);
    g_MousePressed[0] = g_MousePressed[1] = g_MousePressed[2] = False;

    io.MouseWheel = g_MouseWheel;
    g_MouseWheel = 0.0;

    # Hide OS mouse cursor if ImGui is drawing it
    SDL_ShowCursor(0 if io.MouseDrawCursor else 1);

    # Start the frame
    imgui.NewFrame();


def RenderDrawLists(draw_data):
    global g_ShaderHandle

    # Avoid rendering when minimized, scale coordinates for retina displays (screen coordinates != framebuffer coordinates)
    io = imgui.GetIO();
    fb_width = int(io.DisplaySize.x * io.DisplayFramebufferScale.x);
    fb_height = int(io.DisplaySize.y * io.DisplayFramebufferScale.y);
    if fb_width == 0 or fb_height == 0:
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
         2.0/io.DisplaySize.x, 0.0,                   0.0, 0.0,
         0.0,                  2.0/-io.DisplaySize.y, 0.0, 0.0,
         0.0,                  0.0,                  -1.0, 0.0,
        -1.0,                  1.0,                   0.0, 1.0,
    );
    glUseProgram(g_ShaderHandle);
    glUniform1i(g_AttribLocationTex, 0);
    glUniformMatrix4fv(g_AttribLocationProjMtx, 1, GL_FALSE, ortho_projection);
    glBindVertexArray(g_VaoHandle);

    for n in range(draw_data.CmdListsCount):

        cmd_list = draw_data.GetCmdList(n);
        idx_buffer_offset = 0;

        glBindBuffer(GL_ARRAY_BUFFER, g_VboHandle);
        glBufferData(GL_ARRAY_BUFFER, cmd_list.VtxBuffer.Size * SIZEOF_ImDrawVert, cmd_list.GetVtxBufferData(), GL_STREAM_DRAW);

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, g_ElementsHandle);
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, cmd_list.IdxBuffer.Size * SIZEOF_ImDrawIdx, cmd_list.GetIdxBufferData(), GL_STREAM_DRAW);

        for cmd_i in range(cmd_list.CmdBuffer.Size):

            pcmd = cmd_list.GetCmdBuffer(cmd_i);
            if pcmd.UserCallback:
                pcmd.UserCallback(cmd_list, pcmd);
            else:
                glBindTexture(GL_TEXTURE_2D, pcmd.TextureId);
                glScissor(int(pcmd.ClipRect.x), 
                          int(fb_height - pcmd.ClipRect.w), 
                          int(pcmd.ClipRect.z - pcmd.ClipRect.x), 
                          int(pcmd.ClipRect.w - pcmd.ClipRect.y)
                          );
                glDrawElements(GL_TRIANGLES, pcmd.ElemCount, GL_UNSIGNED_SHORT if SIZEOF_ImDrawIdx==2 else GL_UNSIGNED_INT, ctypes.c_void_p(idx_buffer_offset));

            idx_buffer_offset += (pcmd.ElemCount * SIZEOF_ImDrawIdx);

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

def SetClipboardText():
    pass

def GetClipboardText():
    pass

def Shutdown():
    InvalidateDeviceObjects();
    imgui.Shutdown();

def InvalidateDeviceObjects():
    global g_VaoHandle
    global g_VboHandle
    global g_ElementsHandle
    global g_ShaderHandle
    global g_VertHandle
    global g_FragHandle
    global g_FontTexture

    if (g_VaoHandle): glDeleteVertexArrays(1, g_VaoHandle);
    if (g_VboHandle): glDeleteBuffers(1, g_VboHandle);
    if (g_ElementsHandle): glDeleteBuffers(1, g_ElementsHandle);
    g_VaoHandle = g_VboHandle = g_ElementsHandle = 0;

    if (g_ShaderHandle and g_VertHandle): glDetachShader(g_ShaderHandle, g_VertHandle);
    if (g_VertHandle): glDeleteShader(g_VertHandle);
    g_VertHandle = 0;

    if (g_ShaderHandle and g_FragHandle): glDetachShader(g_ShaderHandle, g_FragHandle);
    if (g_FragHandle): glDeleteShader(g_FragHandle);
    g_FragHandle = 0;

    if (g_ShaderHandle): glDeleteProgram(g_ShaderHandle);
    g_ShaderHandle = 0;

    if (g_FontTexture):
        glDeleteTextures(1, g_FontTexture);
        imgui.GetIO().Fonts.SetTexID(0);
        g_FontTexture = 0;
