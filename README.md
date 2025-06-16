# Installation Guide for Intel RealSense T265 with ROS 2

## 1. Install Intel® RealSense™ SDK 2.0 (Debian Packages)

### Register the server's public key:
```bash
sudo mkdir -p /etc/apt/keyrings
curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | sudo tee /etc/apt/keyrings/librealsense.pgp > /dev/null
```

### Install HTTPS support for apt
```bash
sudo apt-get install apt-transport-https
```

### Add the server to the list of repositories
```bash
echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/librealsense.list
sudo apt-get update
```

### Install core packages
```bash
sudo apt-get install librealsense2-dkms
sudo apt-get install librealsense2-utils
```

## 2. Install librealsense v2.51.1 (Recommended for T265)

### Install dependencies
```bash
sudo apt update && sudo apt install -y \
    git cmake libssl-dev libusb-1.0-0-dev \
    libudev-dev pkg-config libgtk-3-dev \
    libglfw3-dev libgl1-mesa-dev
```

### Clone and checkout stable version
```bash
git clone https://github.com/IntelRealSense/librealsense.git ~/librealsense
cd ~/librealsense
git checkout v2.51.1
```

### Build with T265 support
```bash
mkdir build && cd build
cmake .. \
    -DBUILD_EXAMPLES=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DFORCE_LIBUVC=ON \
    -DBUILD_WITH_CUDA=OFF
make -j$(nproc)
sudo make install
```

## 3. Set Up T265 Permissions

### USB permissions
```bash
sudo cp ~/librealsense/config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### User groups
```bash
sudo usermod -a -G video,dialout $USER
sudo reboot
```

### Verify installation
```bash
realsense-viewer --version
```

## 4. Install ROS 2 Wrapper v4.51.1

### Create workspace
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

### Clone matching wrapper version
```bash
git clone -b 4.51.1 https://github.com/IntelRealSense/realsense-ros.git
```

### Install dependencies
```bash
cd ~/ros2_ws
rosdep install -y --from-paths src --ignore-src
```

### Build with T265 support
```bash
colcon build --symlink-install --cmake-args -DFORCE_LIBUVC=ON
```

### Source workspace (add to .bashrc)
```bash
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Launching the T265 Node
```bash
ros2 launch realsense2_camera rs_launch.py enable_t265:=true
```

## References
- https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md#installing-the-packages  
- https://github.com/IntelRealSense/librealsense/releases/tag/v2.51.1  
- https://github.com/IntelRealSense/realsense-ros  
- https://github.com/IntelRealSense/realsense-ros/releases/tag/4.51.1