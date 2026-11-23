# CST8504 Assignment 2 — ROS 2 Vision

## Project Overview

This project demonstrates how to control the Turtlesim simulator using hand gestures detected through a webcam.

The application uses **ROS 2 Humble**, **Python**, **OpenCV**, and **MediaPipe** to capture live video, detect hand landmarks, and convert fingertip positions into movement commands.

The system consists of three ROS 2 packages:

- **`aisd_msgs`** — Defines the custom `Hand` message containing the horizontal positions of the index and pinky fingertips.
- **`aisd_vision`** — Captures webcam images and processes them using MediaPipe to detect hand landmarks.
- **`aisd_motion`** — Converts detected fingertip positions into ROS 2 `Twist` messages to control Turtlesim.

The application was developed and tested using **Ubuntu Server 22.04 in Oracle VirtualBox**, with the Turtlesim graphical interface displayed on a Windows 11 host through X11 forwarding.

The project also includes a safety timeout that stops the turtle when hand detection is lost.

## System Architecture

The application consists of four ROS 2 nodes connected through three topics.

```text
                  Webcam
                     |
                     v
              ImagePublisher
                (aisd_vision)
                     |
                     | /video_frames
                     | sensor_msgs/Image
                     v
                   Hands
                (aisd_vision)
                     |
                     | /cmd_hand
                     | aisd_msgs/Hand
                     v
                    Move
                (aisd_motion)
                     |
                     | /cmd_vel
                     | geometry_msgs/Twist
                     v
                  Turtlesim
```

### ROS 2 Nodes and Topics

| Node | Subscribes To | Publishes To | Responsibility |
|---|---|---|---|
| `image_publisher` | — | `/video_frames` | Captures webcam frames and publishes ROS 2 image messages. |
| `hands` | `/video_frames` | `/cmd_hand` | Uses MediaPipe to detect the index and pinky fingertips. |
| `move` | `/cmd_hand` | `/cmd_vel` | Converts fingertip positions into linear and angular velocities. |
| `turtlesim` | `/cmd_vel` (remapped) | — | Simulates the turtle's movement. |

### Custom Hand Message

The `aisd_msgs` package defines the `Hand` message with two fields:

```text
float64 xpinky
float64 xindex
```

- `xpinky` — Normalized horizontal position of the pinky fingertip (landmark 20).
- `xindex` — Normalized horizontal position of the index fingertip (landmark 8).

Both values typically range from `0.0` to `1.0`, representing positions across the camera image.

## Hand Gesture Controls

The `Move` node subscribes to `/cmd_hand` and uses the horizontal positions of the index and pinky fingertips to control the turtle.

### Rotation

The horizontal position of the index fingertip (`xindex`) determines the turtle's rotation.

| Condition | Action | Angular Velocity (`angular.z`) |
|---|---|---|
| `xindex > 0.55` | Turn right | `-0.1` |
| `xindex < 0.45` | Turn left | `0.1` |
| `0.45 <= xindex <= 0.55` | No rotation | `0.0` |

### Forward Movement

The relative horizontal positions of the index and pinky fingertips determine forward movement.

| Condition | Action | Linear Velocity (`linear.x`) |
|---|---|---|
| `xindex > xpinky` | Move forward | `0.5` |
| `xindex <= xpinky` | No forward movement | `0.0` |

Rotation and forward movement are evaluated independently, allowing the turtle to move forward while turning.

### Automatic Stop When Hand Detection Is Lost

The `Move` node includes a safety timeout to prevent unintended movement when hand detection stops.

- Each received `Hand` message updates the time of the most recent detection.
- A ROS 2 timer checks for missing messages every `0.1` seconds.
- If no `Hand` message arrives for `1.0` second, the node publishes a `Twist` message with zero linear and angular velocities.
- When hand detection resumes, the turtle responds to new movement commands.

This improvement was tested with simulated hand messages and live webcam input.

## Development Environment

The project was developed and tested using the following environment:

| Component | Technology |
|---|---|
| Host operating system | Windows 11 |
| Virtualization | Oracle VirtualBox |
| Guest operating system | Ubuntu Server 22.04.5 LTS |
| ROS 2 distribution | ROS 2 Humble |
| Programming language | Python 3.10 |
| Computer vision | OpenCV |
| Hand tracking | MediaPipe 0.10.21 |
| ROS 2 image conversion | cv_bridge |
| Simulator | Turtlesim |
| Code editor | Visual Studio Code with Remote - SSH |
| Version control | Git and GitHub |

### Webcam and Graphical Display

The webcam is connected to the Ubuntu virtual machine using VirtualBox webcam passthrough.

Turtlesim runs inside Ubuntu, while its graphical window is displayed on the Windows host using PuTTY X11 forwarding and VcXsrv.

### Python Virtual Environment

A Python virtual environment named `.venv` is located in the ROS 2 workspace directory.

It was created with access to system Python packages to support ROS 2 dependencies:

```bash
cd ~/ros2_ws
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

The environment uses these Python package versions:

```text
mediapipe==0.10.21
numpy==1.26.4
opencv-contrib-python==4.11.0.86
```

The virtual environment is not committed to GitHub. It must be recreated when setting up the project on another machine.

## Building and Running the Application

### 1. Clone the GitHub Repository

Clone the project into the `src` directory of a ROS 2 workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone git@github.com:shap0011/assignment-2-ros-2-and-vision-olga.git
```

### 2. Set Up the Python Environment

Install the required system dependencies, including ROS 2 Humble, Turtlesim, `cv_bridge`, and OpenCV.

Create and activate a Python virtual environment:

```bash
cd ~/ros2_ws
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python3 -m pip install mediapipe==0.10.21 numpy==1.26.4 opencv-contrib-python==4.11.0.86
```

### 3. Build the ROS 2 Workspace

Make sure ROS 2 Humble and the virtual environment are activated:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/.venv/bin/activate
```

Build the packages:

```bash
cd ~/ros2_ws
python3 -m colcon build --symlink-install
```

Source the workspace:

```bash
source ~/ros2_ws/install/setup.bash
```

### 4. Launch Turtlesim

Open a terminal with X11 forwarding enabled and run:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 run turtlesim turtlesim_node --ros-args -r /turtle1/cmd_vel:=/cmd_vel
```

The Turtlesim window should appear on the graphical desktop.

### 5. Launch the ImagePublisher Node

In a new terminal:

```bash
source ~/ros2_ws/.venv/bin/activate
source ~/ros2_ws/install/setup.bash

ros2 run aisd_vision image_publisher
```

This node captures frames from the webcam and publishes them to `/video_frames`.

### 6. Launch the Move Node

In another terminal:

```bash
source ~/ros2_ws/.venv/bin/activate
source ~/ros2_ws/install/setup.bash

ros2 run aisd_motion move
```

This node subscribes to `/cmd_hand` and publishes movement commands to `/cmd_vel`.

### 7. Launch the Hands Node

In another terminal:

```bash
source ~/ros2_ws/.venv/bin/activate
source ~/ros2_ws/install/setup.bash

ros2 run aisd_vision hands
```

This node processes webcam frames using MediaPipe and publishes detected fingertip coordinates to `/cmd_hand`.

### 8. Test the Application

Hold your hand in front of the webcam.

- Move your index finger toward the left or right side of the camera image to control rotation.
- Change the relative horizontal positions of your index and pinky fingertips to control forward movement.
- Remove your hand from the camera to activate the automatic stopping mechanism.
- Show your hand again to resume control.

### 9. Stop the Application

Press **Ctrl+C** in each terminal running a ROS 2 node.

To reset Turtlesim to its starting position, run:

```bash
ros2 service call /reset std_srvs/srv/Empty "{}"
```

## Testing and Results

The application was tested on Ubuntu Server 22.04 running ROS 2 Humble inside Oracle VirtualBox.

### Functional Testing

| Test | Expected Result | Actual Result |
|---|---|---|
| Webcam capture | ImagePublisher captures webcam frames | Passed |
| ROS 2 image publishing | Images are published to `/video_frames` | Passed |
| MediaPipe hand detection | Index and pinky fingertips are detected | Passed |
| Custom Hand message | Fingertip coordinates are published to `/cmd_hand` | Passed |
| Right rotation | Index fingertip position greater than `0.55` produces `angular.z = -0.1` | Passed |
| Forward movement | `xindex > xpinky` produces `linear.x = 0.5` | Passed |
| Automatic stopping | Missing hand messages cause zero velocity commands | Passed |
| Hand detection recovery | Turtle resumes responding when the hand returns | Passed |
| Turtlesim integration | Turtle responds to webcam-based hand gestures | Passed |

### ROS 2 Topic Verification

The following commands were used to inspect ROS 2 communication:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /cmd_hand
ros2 topic echo /cmd_vel
ros2 topic hz /video_frames
```

The `/cmd_hand` topic successfully published changing fingertip coordinates while a hand was visible.

The `/cmd_vel` topic produced the expected linear and angular velocities during simulated hand-message tests.

### Safety Timeout Verification

The safety timeout was tested using simulated `Hand` messages and the live webcam.

The test confirmed that:

1. The turtle moves when valid hand coordinates are received.
2. When hand messages stop, the `Move` node publishes zero velocities after approximately one second.
3. The turtle resumes responding when hand detection returns.

### Observations

Turtlesim movement is relatively slow because the assignment uses small movement velocities (`linear.x = 0.5` and `angular.z = ±0.1`).

The original movement values were preserved to remain consistent with the assignment requirements.

MediaPipe initialization was optimized so that the hand-tracking model is created once when the `Hands` node starts, rather than being recreated for every incoming webcam frame.
