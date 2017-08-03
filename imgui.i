/* vim: set ft=c */

%module swig_imgui
%include "typemaps.i"
%include "std_vector.i"
%include "cpointer.i"
%pointer_functions(float, floatp);

%begin %{
#ifdef _MSC_VER
#define SWIG_PYTHON_INTERPRETER_NO_DEBUG
#endif
%}

%{
/* Includes the header in the wrapper code */
#include "imgui/imgui.h"
//#include <vector>
#include <algorithm>

struct byterange
{
    const char *begin;
    size_t size;

    byterange()
        : begin(nullptr)
        , size(0)
    {}

    byterange(const char *b, size_t s)
        : begin(b)
        , size(s)
    {}

    template<typename T>
        byterange(const T &range)
        : begin((const char *)range.begin())
        , size(std::distance((const char *)range.begin(), (const char *)range.end()))
    {}

    byterange(const byterange &rhs)
    {
        *this=rhs;
    }

    byterange& operator=(const byterange &rhs)
    {
        begin=rhs.begin;
        size=rhs.size;
        return *this;
    }
};

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

%typemap(out) byterange {
  $result = PyBytes_FromStringAndSize($1.begin, $1.size);
}

%typemap(in) float col[3] (float temp[3]) {
  if (!PySequence_Check($input)) {
    PyErr_SetString(PyExc_ValueError,"Expected a sequence");
    return NULL;
  }
  if (PySequence_Length($input) != $1_dim0) {
    PyErr_SetString(PyExc_ValueError,"Size mismatch. Expected more than $1_dim0 elements");
    return NULL;
  }
  for (int i = 0; i < $1_dim0; i++) {
    PyObject *o = PySequence_GetItem($input,i);
    if (PyNumber_Check(o)) {
      temp[i] = (float) PyFloat_AsDouble(o);
    } else {
      PyErr_SetString(PyExc_ValueError,"Sequence elements must be numbers");      
      return NULL;
    }
  }
  $1 = temp;
}

%typemap(argout) float col[3] {
    for (int i = 0; i < $1_dim0; i++) {
        PyObject *o = PyFloat_FromDouble((double) $1[i]);
        PyList_SetItem($input,i,o);
    }
}

%ignore ImGui::TreePush();

//IMGUI_API void GetTexDataAsRGBA32(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 4 bytes-per-pixel
%apply int *OUTPUT { int *out_width, int *out_height };
//%apply float *INOUT { float *v };

/* Parse the header file to generate wrappers */
%include "imgui/imgui.h"

//%template(UCharVector) std::vector<unsigned char>;
%template(ImVectorDrawVert) ImVector<ImDrawVert>;
%template(ImVectorDrawIdx) ImVector<ImDrawIdx>;
%template(ImVectorDrawCmd) ImVector<ImDrawCmd>;

%inline %{

byterange GetTexDataAsRGBA32(int* out_width, int* out_height) 
{ 
    auto &io=ImGui::GetIO();

    unsigned char *p;
    io.Fonts->GetTexDataAsRGBA32(&p, out_width, out_height);
    auto size=(*out_width) * (*out_height);
    //std::vector<unsigned char> data(p, p+size);
    //ImGui::MemFree(p);
    //return data;
    return byterange((const char *)p, *out_width * *out_height * 4);
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
        ImGui::GetIO().Fonts->TexID=reinterpret_cast<void*>(id);
    }

    void SetKeyMap(int k, int v)
    {
        ImGui::GetIO().KeyMap[k]=v;
    }

    void SetMouseDown(int k, int v)
    {
        ImGui::GetIO().MouseDown[k]=v;
    }

    void SetKeysDown(int k, int v)
    {
        ImGui::GetIO().KeysDown[k]=v;
    }
}

%extend ImDrawData {
    ImDrawList* GetCmdList(int n){
        return self->CmdLists[n];
    }
}

%extend ImDrawList {
    byterange GetVtxBufferData(){
        return byterange(self->VtxBuffer);
    }
    byterange GetIdxBufferData(){
        return byterange(self->IdxBuffer);
    }

    ImDrawCmd* GetCmdBuffer(int n){
        return &self->CmdBuffer[n];
    }
}

