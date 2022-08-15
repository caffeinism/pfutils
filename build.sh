rm package -r
py3clean .
python3 setup.py sdist

for MANYLINUX_VERSION in $(jq -r 'keys[]' manylinux-info.json)
do
    PYTHON_VERSIONS=$(jq -r "."$MANYLINUX_VERSION"[]" manylinux-info.json)
    docker run -it --rm \
        -v `pwd`:/src \
        -v `pwd`/package:/wheels \
        --workdir=/src \
        -e MANYLINUX_VERSION="$MANYLINUX_VERSION" \
        -e PYTHON_VERSIONS="$PYTHON_VERSIONS" \
        -e BUILD_CPP="true" \
        quay.io/pypa/$MANYLINUX_VERSION bash build_wheel.sh
done

mv dist/*.tar.gz package
rm dist pfutils.egg-info build -r
chown caffeinism:caffeinism package -R