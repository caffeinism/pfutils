for PYTHON_VERSION in $PYTHON_VERSIONS
do
    echo $PYTHON_VERSION
    $PYTHON_VERSION -m pip install pybind11
    $PYTHON_VERSION setup.py build bdist_wheel --dist-dir=/dist
done

for it in $(ls /dist | grep whl)
do
    auditwheel repair /dist/$it -w /wheels
done