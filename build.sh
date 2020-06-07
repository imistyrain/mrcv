if [ ! -d build ] ; then
    mkdir build
fi
cd build
cmake ..
make -j4
mv export modelinfo