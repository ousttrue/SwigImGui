%module swig_imgui
%{
/* Includes the header in the wrapper code */
#include "imgui/imgui.h"
%}

%ignore ImGui::TreePush();

/* Parse the header file to generate wrappers */
%include "imgui/imgui.h"

