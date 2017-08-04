# ImGui - standalone example application for SDL2 + OpenGL
# If you are new to ImGui, see examples/README.txt and documentation at the top of imgui.cpp.
import os
import sys

if not 'PYSDL2_DLL_PATH' in os.environ:
    os.environ['PYSDL2_DLL_PATH']=os.environ['VCPKG_DIR'] + '/installed/x64-windows/bin'
from sdl2 import *

python_dir=os.path.dirname(sys.executable)
os.environ['PATH']+=(';'+python_dir)
import swig_imgui as imgui

import ImplSdlGL3
from OpenGL.GL import *


def main():

    # Setup SDL
    if (SDL_Init(SDL_INIT_VIDEO|SDL_INIT_TIMER) != 0):
        print("Error: %s\n", SDL_GetError());
        return -1;

    # Setup window
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24);
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 2);
    current=SDL_DisplayMode();
    SDL_GetCurrentDisplayMode(0, current);
    window = SDL_CreateWindow(b"ImGui SDL2+OpenGL3 example", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 1280, 720, SDL_WINDOW_OPENGL|SDL_WINDOW_RESIZABLE);
    glcontext = SDL_GL_CreateContext(window);
    #gl3wInit();

    # Setup ImGui binding
    ImplSdlGL3.Init(window);

    # Load Fonts
    # (there is a default font, this is only if you want to change it. see extra_fonts/README.txt for more details)
    #ImGuiIO& io = imgui.GetIO();
    #io.Fonts->AddFontDefault();
    #io.Fonts->AddFontFromFileTTF("../../extra_fonts/Cousine-Regular.ttf", 15.0f);
    #io.Fonts->AddFontFromFileTTF("../../extra_fonts/DroidSans.ttf", 16.0f);
    #io.Fonts->AddFontFromFileTTF("../../extra_fonts/ProggyClean.ttf", 13.0f);
    #io.Fonts->AddFontFromFileTTF("../../extra_fonts/ProggyTiny.ttf", 10.0f);
    #io.Fonts->AddFontFromFileTTF("c:\\Windows\\Fonts\\ArialUni.ttf", 18.0f, NULL, io.Fonts->GetGlyphRangesJapanese());

    show_test_window = imgui.new_boolp();
    imgui.boolp_assign(show_test_window, True)
    show_another_window = imgui.new_boolp();
    imgui.boolp_assign(show_another_window, False)
    clear_color = [114/255.0, 144/255.0, 154/255.0, 0];

    # Main loop
    done = False;
    while not done:

        event=SDL_Event();
        while SDL_PollEvent(event)!=0:

            ImplSdlGL3.ProcessEvent(event);
            if event.type == SDL_QUIT:
                done = True;

        ImplSdlGL3.NewFrame(window);

        # 1. Show a simple window
        # Tip: if we don't call imgui.Begin()/imgui.End() the widgets appears in a window automatically called "Debug"

        f=imgui.new_floatp()
        imgui.floatp_assign(f, 0.0)
        imgui.Text("Hello, world!");
        imgui.SliderFloat("float", f, 0.0, 1.0);
        imgui.ColorEdit3("clear color", clear_color);
        if imgui.Button("Test Window"): imgui.boolp_assign(show_test_window, not imgui.boolp_value(show_test_window))
        if imgui.Button("Another Window"): imgui.boolp_assign(show_another_window, not imgui.boolp_value(show_another_window));
        imgui.Text("Application average %.3f ms/frame (%.1f FPS)", 1000.0 / imgui.GetIO().Framerate, imgui.GetIO().Framerate);

        # 2. Show another simple window, this time using an explicit Begin/End pair
        if imgui.boolp_value(show_another_window):
            imgui.SetNextWindowSize(imgui.ImVec2(200,100), imgui.ImGuiSetCond_FirstUseEver);
            imgui.Begin("Another Window", show_another_window);
            imgui.Text("Hello");
            imgui.End();

        # 3. Show the ImGui test window. Most of the sample code is in imgui.ShowTestWindow()
        if imgui.boolp_value(show_test_window):
            imgui.SetNextWindowPos(imgui.ImVec2(650, 20), imgui.ImGuiSetCond_FirstUseEver);
            imgui.ShowTestWindow(show_test_window);

        # Rendering
        glViewport(0, 0, int(imgui.GetIO().DisplaySize.x), int(imgui.GetIO().DisplaySize.y));
        glClearColor(*clear_color);
        glClear(GL_COLOR_BUFFER_BIT);
        imgui.Render();
        SDL_GL_SwapWindow(window);

    # Cleanup
    ImplSdlGL3.Shutdown();
    SDL_GL_DeleteContext(glcontext);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;

if __name__=='__main__':
    main()
