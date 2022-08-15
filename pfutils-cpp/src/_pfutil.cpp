#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>
#include <pybind11/embed.h>
#include <memory>

namespace py = pybind11;

#include "FileManager.h"
#include "FutureVector.h"

PYBIND11_MODULE(_pfutil, m) {
    py::class_<FutureVector<void>, std::shared_ptr<FutureVector<void>>>(m, "VoidFutureVector")
        .def("__iter__", [](FutureVector<void> &self){
            return py::make_iterator(self.begin(), self.end());
        }, py::keep_alive<0, 1>())
        .def("__len__", &FutureVector<void>::size)
        ;
    py::class_<FileManager, std::shared_ptr<FileManager>>(m, "FileManager")
        .def(py::init<uint32_t, uint32_t>())
        .def("copy_file", &FileManager::copy_file)
        .def("remove_file", &FileManager::remove_file)
        .def("flush_and_iter", &FileManager::flush_and_iter)
        .def("__enter__", [](FileManager &self)->FileManager&{ return self; })
        .def("__exit__", [](FileManager &self, const py::object &type, const py::object &value, const py::object &traceback){})
        ;
    py::register_exception<std::filesystem::filesystem_error>(m, "FileSystemError");
}
