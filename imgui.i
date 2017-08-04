/* vim: set ft=c */
%module swig_imgui
%begin %{
#ifdef _MSC_VER
#define SWIG_PYTHON_INTERPRETER_NO_DEBUG
#endif
%}

%{
/* Includes the header in the wrapper code */
#include "imgui/imgui.h"
%}

%ignore ImGui::TreePush();

%constant int SIZEOF_ImDrawVert = sizeof(ImDrawVert);
%constant int SIZEOF_ImDrawIdx = sizeof(ImDrawIdx);

%{
#define OFFSETOF(TYPE, ELEMENT) ((size_t)&(((TYPE *)0)->ELEMENT))
const int OFFSETOF_ImDrawVert_pos = OFFSETOF(ImDrawVert, pos);
const int OFFSETOF_ImDrawVert_uv = OFFSETOF(ImDrawVert, uv);
const int OFFSETOF_ImDrawVert_col = OFFSETOF(ImDrawVert, col);
#undef OFFSETOF
%}
const int OFFSETOF_ImDrawVert_pos = OFFSETOF_ImDrawVert_pos;
const int OFFSETOF_ImDrawVert_uv = OFFSETOF_ImDrawVert_uv;
const int OFFSETOF_ImDrawVert_col = OFFSETOF_ImDrawVert_col;

%{
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

//%include "typemaps.i"
%typemap(in, numinputs=0) (unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel) (unsigned char *tempP, int tempW, int tempH, int tempB) {
    $1 = &tempP;
    $2 = &tempW;
    $3 = &tempH;
    $4 = &tempB;
}
%typemap(argout)(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel){
    auto b = PyBytes_FromStringAndSize((const char *)*$1, (*$2) * (*$3) * (*$4));
    auto w = PyLong_FromLong(*$2);
    auto h = PyLong_FromLong(*$3);

    if ((!$result) || ($result == Py_None)) {
        // new tuple3
        $result = PyTuple_New(3);
        PyTuple_SetItem($result, 0, b);
        PyTuple_SetItem($result, 1, w);
        PyTuple_SetItem($result, 2, h);
    }
    else{
        if (!PyTuple_Check($result)) {
            // new tuple4
            auto t= PyTuple_New(4);
            PyTuple_SetItem(t, 0, $result);
            PyTuple_SetItem(t, 1, b);
            PyTuple_SetItem(t, 2, w);
            PyTuple_SetItem(t, 3, h);
            $result=t;
        }
        else {
            // concat
            auto head = $result;
            auto tail = PyTuple_New(3);
            PyTuple_SetItem($result, 0, b);
            PyTuple_SetItem($result, 1, w);
            PyTuple_SetItem($result, 2, h);
            $result = PySequence_Concat(head, tail);
            Py_DECREF(head);
            Py_DECREF(tail);
        }
    }
}


%typemap(in) float col[3] (float temp[3]) {
    if (!PySequence_Check($input)) {
        PyErr_SetString(PyExc_ValueError,"Expected a sequence");
        return NULL;
    }
    if (PySequence_Length($input) < $1_dim0) {
        PyErr_SetString(PyExc_ValueError,"Size mismatch. Expected more than $1_dim0 elements");
        return NULL;
    }
    for (int i = 0; i < $1_dim0; i++) {
        PyObject *o = PySequence_GetItem($input,i);
        if (PyNumber_Check(o)) {
            temp[i] = (float) PyFloat_AsDouble(o);
        }
        else {
            PyErr_SetString(PyExc_ValueError,"Sequence elements must be numbers");
            return NULL;
        }
    }
    $1 = temp;
}
%typemap(argout) float col[3] {
    for (int i = 0; i < $1_dim0; i++) {
        PyObject *o = PyFloat_FromDouble((double) $1[i]);
        PyList_SetItem($input, i, o);
    }
}

%typemap(in, numinputs=0) (unsigned char** out_bytes, int* out_size) (unsigned char *tempP, int tempSize) {
    $1 = &tempP;
    $2 = &tempSize;
}
%typemap(argout)(unsigned char** out_bytes, int* out_size){
    auto b = PyBytes_FromStringAndSize((const char *)*$1, *$2);

    if ((!$result) || ($result == Py_None)) {
        $result = b;
    }
    else{
        if (!PyTuple_Check($result)) {
            // new tuple4
            auto t= PyTuple_New(2);
            PyTuple_SetItem(t, 0, $result);
            PyTuple_SetItem(t, 1, b);
            $result=t;
        }
        else {
            // concat
            auto head = $result;
            auto tail = PyTuple_New(1);
            PyTuple_SetItem($result, 0, b);
            $result = PySequence_Concat(head, tail);
            Py_DECREF(head);
            Py_DECREF(tail);
        }
    }
}

//////////////////////////////////////////////////////////////////////////////
%include "imgui/imgui.h"
//////////////////////////////////////////////////////////////////////////////

%extend ImGuiIO {
    void SetKeyMap(int k, int v)
    {
        ImGui::GetIO().KeyMap[k]=v;
    }

    void SetImeWindowHandle(long long v)
    {
        ImGui::GetIO().ImeWindowHandle = (void*)v;
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

%extend ImGuiIO {
    void SetRenderDrawListsFn(PyObject *pyfunc) {
        ImGui::GetIO().UserData=pyfunc;
        self->RenderDrawListsFn=PythonRenderDrawListsFn;
        Py_INCREF(pyfunc);
    }
}

%extend ImFontAtlas {
    void SetTexID(long long id) {
        self->TexID=reinterpret_cast<void*>(id);
    }
}

%extend ImDrawData {
    ImDrawList* GetCmdList(int n){
        return self->CmdLists[n];
    }
}

%template(ImVectorDrawVert) ImVector<ImDrawVert>;
%template(ImVectorDrawIdx) ImVector<ImDrawIdx>;
%template(ImVectorDrawCmd) ImVector<ImDrawCmd>;

%extend ImDrawList {
    void GetVtxBufferData(unsigned char **out_bytes, int *out_size){
        *out_bytes=(unsigned char *)self->VtxBuffer.Data;
        *out_size=self->VtxBuffer.Size * sizeof(self->VtxBuffer.Data[0]);
    }
    void GetIdxBufferData(unsigned char **out_bytes, int *out_size){
        *out_bytes=(unsigned char *)self->IdxBuffer.Data;
        *out_size=self->IdxBuffer.Size * sizeof(self->IdxBuffer.Data[0]);
    }
}

%extend ImDrawList {
    ImDrawCmd* GetCmdBuffer(int n){
        return &self->CmdBuffer[n];
    }
}

%include "cpointer.i"
%pointer_functions(float, floatp);
%pointer_functions(bool, boolp);

