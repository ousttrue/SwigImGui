/* vim: set ft=c */

%module swig_imgui
%include "typemaps.i"
%include "std_vector.i"

%begin %{
#ifdef _MSC_VER
#define SWIG_PYTHON_INTERPRETER_NO_DEBUG
#endif
%}

%{
/* Includes the header in the wrapper code */
#include "imgui/imgui.h"
#include <vector>

/* This function matches the prototype of the normal C callback
   function for our widget. However, we use the clientdata pointer
   for holding a reference to a Python callable object. */

static void PythonRenderDrawListsFn(ImDrawData* data)
{
    auto func=(PyObject*)ImGui::GetIO().UserData; // Get Python function
    auto obj = SWIG_NewPointerObj(SWIG_as_voidptr(data)
    , SWIGTYPE_p_ImDrawData, 0 |  0 );
    auto arglist = Py_BuildValue("(O)",obj); // Build argument list
    PyEval_CallObject(func, arglist); // Call Python
    Py_DECREF(arglist); // Trash arglist
    Py_DECREF(obj);
}
%}

%ignore ImGui::TreePush();

//IMGUI_API void GetTexDataAsRGBA32(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 4 bytes-per-pixel
%apply int *OUTPUT { int *out_width, int *out_height };

/* Parse the header file to generate wrappers */
%include "imgui/imgui.h"

%template(UCharVector) std::vector<unsigned char>;
%inline %{

unsigned long long GetTexDataAsRGBA32(int* out_width, int* out_height) 
{ 
    auto &io=ImGui::GetIO();

    unsigned char *p;
    io.Fonts->GetTexDataAsRGBA32(&p, out_width, out_height);
    auto size=(*out_width) * (*out_height);
    //std::vector<unsigned char> data(p, p+size);
    //ImGui::MemFree(p);
    //return data;
    return (unsigned long long)p;
}

%}

// Attach a new method to our plot widget for adding Python functions
%extend ImGuiIO {
    // Set a Python function object as a callback function
    // Note : PyObject *pyfunc is remapped with a typempap
    void SetRenderDrawListsFn(PyObject *pyfunc) {
        ImGui::GetIO().UserData=pyfunc;
        self->RenderDrawListsFn=PythonRenderDrawListsFn;
        Py_INCREF(pyfunc);
    }

    void SetTexID(int id)
    {
        ImGui::GetIO().Fonts->TexID=(void*)id;
    }
}

