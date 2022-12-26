# People detection application with Deepstream SDK

## Requirements

1. Make sure you have CUDA, Docker and Docker-NVIDIA Toolkit installed.
2. Ensure you are using the OpenGL libs of NVIDIA, you can verify this with:

The output should be:

```
OpenGL vendor string: NVIDIA Corporation
OpenGL renderer string: Quadro T2000 with Max-Q Design/PCIe/SSE2
OpenGL core profile version string: 4.6.0 NVIDIA 515.43.04
OpenGL core profile shading language version string: 4.60 NVIDIA
OpenGL core profile context flags: (none)
OpenGL core profile profile mask: core profile
OpenGL core profile extensions:
OpenGL version string: 4.6.0 NVIDIA 515.43.04
OpenGL shading language version string: 4.60 NVIDIA
OpenGL context flags: (none)
OpenGL profile mask: (none)
OpenGL extensions:
OpenGL ES profile version string: OpenGL ES 3.2 NVIDIA 515.43.04
OpenGL ES profile shading language version string: OpenGL ES GLSL ES 3.20
OpenGL ES profile extensions:
```
If not do this:
```
sudo prime-select nvidia
sudo reboot
```

## How to run it
1. Clone the project

2. Pull deepstream python bindings docker
```
docker pull serge3006/deepstream-python-bindings:0.0.1
```
3. Allow external applications to connect to the host’s X display:
```
xhost +
```
4. Set the DISPLAY environment variable

```
export DISPLAY=:1
```
5. Run the container in interactive mode
```
docker run --gpus all -it --rm --net=host --privileged -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/deepstream-restricted-zone-detection/app/:/app/ -e DISPLAY=$DISPLAY -w /app/ serge3006/deepstream-python-bindings:0.0.1
```
6. Install requirements
```
pip install -r requirements.txt
```
7. Run the app
```
cd /app
python3 main.py
```