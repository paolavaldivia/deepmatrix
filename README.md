# Deepmatrix

deep zoom images from hdf5 files

## Dependencies
* [Python Imaging Library (PIL)](http://pillow.readthedocs.io/en/3.4.x/index.html)
* [OpenSeadragon](https://openseadragon.github.io/) (for running the demo)

## Run the demo
1. Use an hdf5 file or run the script `data/image2hdf5.py` to create an hdf5 file from an image.
2. Use the script `example.py` to create Deep Zoom Images from the hdf5 file.
3. Run a http server (e.g. python, etc.).
4. Navigate to `<your_serverpath>/demo/index.html` to run the local demo.
