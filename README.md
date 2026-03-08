# Secure Voice Media Controller

A secure, voice‑controlled media assistant with multi‑layer authentication and distance‑optimized speech recognition.

The Secure Voice Media Controller enables real‑time, hands‑free media control while prioritizing security, accuracy, and environmental adaptability. It combines wake‑word activation, voice‑based authentication, and dynamic microphone calibration to deliver a reliable voice interface suitable for desktops, smart‑home systems, and embedded devices.

# Features

Voice‑Driven Media Control
Control system media functions such as:

Play / Pause

Volume Up / Down

Mute

Next / Previous Track

# Multi‑Layer Security

Wake‑word activation prevents accidental triggers

Voice password authentication ensures only authorized users can start a session

Session‑based command execution

Automatic session timeout for added protection

# Adaptive Audio Processing

Distance‑optimized microphone sensitivity

Real‑time noise handling

Automatic calibration on startup

# Intelligent Session Management
Tracks authentication state

Enables or blocks commands based on session status

Logs session events for debugging or auditing

# secure-voice-media-controller
.
├── docs/                  # architecture notes, diagrams, experiment logs
├── src/                   # ROS 2 packages (description, bringup, autonomy, mapping)
│   ├── mtrebot_description/
│   ├── <ugv_bringup_pkg>/
│   ├── <uav_bringup_pkg>/
│   ├── <multi_robot_coordination_pkg>/
│   └── <mapping_fusion_pkg>/
├── worlds/                # Gazebo worlds and assets
├── launch/                # top-level launch files (simulation + stack)
├── scripts/               # utilities: setup, logging, evaluation
└── README.md
│   ├── train_model.py
│   └── preprocess_dataset.py
