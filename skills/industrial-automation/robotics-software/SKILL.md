---
name: robotics-software
description: Génie logiciel robotique — middleware, simulateurs (Gazebo, MuJoCo), real-time, frameworks, CI/CD, testing, embedded, ROS packaging
---

# Robotics Software Engineering — Génie Logiciel Robotique

## Quand l'utilisateur
Quand l'utilisateur demande de structurer un projet robotique, de choisir un middleware ou simulateur, de configurer un système temps réel, d'écrire des tests pour logiciel robotique, ou de CI/CD ROS.

## Architecture Logicielle Robotique

### Stack Logiciel Typique
```
┌─────────────────────────────────────────┐
│              Application Layer           │
│  Navigation / Manipulation / Perception │
├─────────────────────────────────────────┤
│           Behavior & Planning            │
│  State machines (SMACH, BehaviorTree)    │
├─────────────────────────────────────────┤
│           Middleware Layer                │
│  ROS2 / OROCOS / DDS / LCM / Zenoh      │
├─────────────────────────────────────────┤
│         Driver & Hardware Abstraction     │
│  ros2_control / ROS drivers / SOEM      │
├─────────────────────────────────────────┤
│              Real-time Layer              │
│  Xenomai / PREEMPT_RT / RT-Linux        │
├─────────────────────────────────────────┤
│         Operating System / Kernel         │
│  Ubuntu / Debian / Yocto Linux          │
└─────────────────────────────────────────┘
```

### Choix du Middleware

| Middleware | Communication | Temps Réel | Sécurité | Usage |
|-----------|--------------|------------|----------|-------|
| **ROS2 (DDS)** | Pub/sub, srv, action, DDS QoS | Oui (executor) | SROS2 | Standard robotique |
| **ROS1** | TCPROS/UDPROS | Non | Non | Legacy |
| **OROCOS** | RTT (Real-Time Toolkit) | Oui (réel) | Non | Contrôle temps réel |
| **LCM (Lightweight Comm. Marshalling)** | UDP multicast | Non | Non | Robotique agile (MIT) |
| **Zenoh** | Pub/sub, RPC, DDS bridge | Oui (zenoh-pico) | ACL | Edge robotics |
| **ZeroMQ (ZMQ)** | TCP/IPC/multicast | Non | CurveCP | Générique |
| **MQTT** | Broker-based | Non | TLS | IoT/Edge |

## ROS2 — Structure de Projet

### Layout Recommandé
```
my_robot_project/
├── my_robot_bringup/      # Launch files, configuration
│   ├── launch/
│   │   ├── robot.launch.py
│   │   └── simulation.launch.py
│   ├── config/
│   │   ├── robot.yaml
│   │   └── controllers.yaml
│   └── package.xml
│
├── my_robot_description/  # URDF/SRDF, meshes
│   ├── urdf/
│   │   ├── robot.urdf.xacro
│   │   └── robot.srdf
│   ├── meshes/
│   │   ├── base_link.stl
│   │   └── arm.stl
│   └── config/
│       └── joint_limits.yaml
│
├── my_robot_control/      # ros2_control
│   ├── src/
│   │   ├── robot_hardware_interface.cpp
│   │   └── joint_trajectory_controller.cpp
│   ├── config/
│   │   └── control.yaml
│   └── package.xml
│
├── my_robot_perception/   # Vision, LiDAR processing
│   ├── src/
│   │   ├── object_detector.cpp
│   │   └── pointcloud_filter.cpp
│   ├── launch/
│   │   └── perception.launch.py
│   └── package.xml
│
├── my_robot_navigation/   # Localization, path planning
│   ├── src/
│   │   ├── local_planner.cpp
│   │   └── global_planner.cpp
│   └── package.xml
│
├── my_robot_msgs/         # Messages personnalisés
│   ├── msg/
│   │   ├── RobotStatus.msg
│   │   └── JointCommand.msg
│   ├── srv/
│   │   └── GraspObject.srv
│   ├── action/
│   │   └── PickAndPlace.action
│   └── package.xml
│
├── tests/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── colcon.meta
└── setup.sh
```

### Création d'un Package ROS2
```bash
# Python
ros2 pkg create my_robot_perception \
  --build-type ament_python \
  --dependencies rclpy sensor_msgs cv_bridge std_msgs

# C++
ros2 pkg create my_robot_control \
  --build-type ament_cmake \
  --dependencies rclcpp sensor_msgs control_msgs hardware_interface

# Interface
ros2 pkg create my_robot_msgs \
  --build-type ament_cmake \
  --dependencies std_msgs geometry_msgs action_msgs
```

### Définition de Messages Personnalisés
```bash
# msg/RobotStatus.msg
int32 joint_count
float64[] joint_positions
float64[] joint_velocities
float64[] joint_torques
bool safety_stop_active
uint32 error_code

# srv/GraspObject.srv
---
geometry_msgs/Pose grasp_pose
bool success

# action/PickAndPlace.action
geometry_msgs/Pose object_pose
---
geometry_msgs/Pose approach_pose
float64 completion_time
---
float32 progress
```

## Simulateurs Robotiques

### Gazebo (Ignition / Harmonic)
```bash
# Installation
sudo apt install ros-humble-gazebo-ros-pkgs

# Lancement d'un monde
gazebo worlds/empty.world

# ROS2 + Gazebo bridge
ros2 launch gazebo_ros gazebo.launch.py world:=worlds/my_world.world

# Spawn d'un robot
ros2 run gazebo_ros spawn_entity.py \
  -file ~/my_robot.urdf \
  -entity my_robot \
  -x 0 -y 0 -z 0.5

# Plugin SDF (pour un modèle de roue)
<plugin name="diff_drive" filename="libignition-gazebo-diff-drive-system.so">
  <left_joint>left_wheel_joint</left_joint>
  <right_joint>right_wheel_joint</right_joint>
  <wheel_separation>0.3</wheel_separation>
  <wheel_radius>0.05</wheel_radius>
  <topic>/cmd_vel</topic>
  <odom_topic>/odom</odom_topic>
</plugin>
```

### MuJoCo (Multi-Joint dynamics with Contact)
```python
import mujoco
import mujoco.viewer

# Chargement du modèle
model = mujoco.MjModel.from_xml_path('robot.xml')
data = mujoco.MjData(model)

# Simulation
with mujoco.viewer.launch_passive(model, data) as viewer:
    for _ in range(10000):
        # Commande : position cible des joints
        data.ctrl[:] = target_positions
        mujoco.mj_step(model, data)

        # Observer
        print(f"Position : {data.qpos[:6]}")
        print(f"Contact forces : {data.cfrc_ext}")

        # Viewer synchrone
        viewer.sync()
```

### MuJoCo XML — Modèle Robot
```xml
<mujoco model="robot_arm">
  <compiler angle="radian" meshdir="meshes"/>

  <option timestep="0.002" gravity="0 0 -9.81"/>

  <default>
    <joint type="hinge" axis="0 0 1" damping="0.1" armature="0.01"/>
    <geom type="mesh" condim="4" friction="0.5 0.005 0.0001"/>
  </default>

  <worldbody>
    <light pos="0 0 2"/>
    <geom type="plane" size="2 2 0.1"/>

    <body name="base" pos="0 0 0.1">
      <joint type="free"/>  <!-- base fixe -->
      <geom type="cylinder" size="0.1 0.05" rgba="0.5 0.5 0.5 1"/>

      <body name="link1" pos="0 0 0.15">
        <joint name="joint1" range="-180 180"/>
        <geom type="box" size="0.02 0.02 0.15" rgba="0.2 0.6 0.8 1"/>
        <inertial mass="1.0" inertia="0.01 0.01 0.005"/>

        <body name="link2" pos="0 0 0.15">
          <joint name="joint2" range="-120 120" axis="0 1 0"/>
          <geom type="box" size="0.02 0.02 0.2" rgba="0.8 0.2 0.2 1"/>
          <inertial mass="0.8" inertia="0.008 0.008 0.004"/>
        </body>
      </body>
    </body>
  </worldbody>

  <actuator>
    <motor name="motor1" joint="joint1" gear="100" ctrlrange="-10 10"/>
    <motor name="motor2" joint="joint2" gear="100" ctrlrange="-10 10"/>
  </actuator>
</mujoco>
```

### ISSAC Sim (NVIDIA) — Simulateur Industrielle
```python
from omni.isaac.core import World
from omni.isaac.core.objects import VisualCuboid
import numpy as np

my_world = World(stage_units_in_meters=1.0)
my_world.scene.add_default_ground_plane()

# Chargement d'un robot UR10
from omni.isaac.core.robots import Robot
robot = my_world.scene.add(Robot(
    prim_path="/World/UR10",
    name="UR10",
    usd_path="ur10.usd"
))

my_world.reset()
for i in range(1000):
    # Mise à jour
    joint_positions = np.array([0.1*i for _ in range(6)])
    robot.set_joint_positions(joint_positions)
    my_world.step(render=True)
```

## Temps Réel Robotique

### PREEMPT_RT Kernel
```bash
# Installation du noyau temps réel
sudo apt install linux-image-rt-amd64  # Debian
# ou
sudo apt install linux-lowlatency       # Ubuntu

# Vérification
uname -a | grep rt  # doit contenir "rt" ou "preempt"
```

### Xenomai (Dual-kernel)
```bash
# Installation Xenomai 3
git clone git://xenomai.org/xenomai-3.git
./configure --with-core=cobalt --enable-pshared
make -j$(nproc)
sudo make install

# Test de latence
sudo /usr/xenomai/bin/latency -t 0 -T 1000
# Résultat typique : < 10μs sur matériel dédié
```

### Real-Time ROS2 Executor
```cpp
#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors/static_single_threaded_executor.hpp>

class RTControlNode : public rclcpp::Node {
public:
    RTControlNode() : Node("rt_control") {
        // Priorité temps réel
        set_priority(95, SCHED_FIFO);

        // Timer à haute fréquence
        timer_ = this->create_wall_timer(
            std::chrono::microseconds(1000),  // 1kHz
            [this]() { this->control_loop(); }
        );
    }

private:
    void set_priority(int priority, int policy) {
        struct sched_param sched;
        sched.sched_priority = priority;
        if (sched_setscheduler(0, policy, &sched) != 0) {
            RCLCPP_WARN(get_logger(), "Échec priorité RT (pas root?)");
        }
    }

    void control_loop() {
        // Lecture capteurs (lecture directe mémoire / DMA)
        // Calcul loi de commande (100μs max)
        // Écriture actionneurs (via SOEM / EtherCAT)
    }

    rclcpp::TimerBase::SharedPtr timer_;
};
```

### Isolation CPU (NO_HZ)
```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX="isolcpus=1-3 nohz_full=1-3 rcu_nocbs=1-3"

# Affinité des threads ROS2
taskset -c 1-3 ros2 run my_robot_control rt_control_node

# Vérification
htop  # CPU 0 = OS, CPU 1-3 = contrôle dédié
```

## ros2_control — Hardware Interface

### Implémentation Hardware Interface
```cpp
#include <hardware_interface/system_interface.hpp>
#include <hardware_interface/types/hardware_interface_type_values.hpp>

class MyRobotHardware : public hardware_interface::SystemInterface {
public:
    CallbackReturn on_init(const hardware_interface::HardwareInfo &info) override {
        // Initialisation des canaux
        joint_positions_.resize(info.joints.size(), 0.0);
        joint_velocities_.resize(info.joints.size(), 0.0);
        joint_efforts_.resize(info.joints.size(), 0.0);
        return CallbackReturn::SUCCESS;
    }

    std::vector<hardware_interface::StateInterface> export_state_interfaces() override {
        std::vector<hardware_interface::StateInterface> interfaces;
        for (size_t i = 0; i < joint_positions_.size(); i++) {
            interfaces.emplace_back(
                info_.joints[i].name,
                hardware_interface::HW_IF_POSITION,
                &joint_positions_[i]);
            // ... velocity, effort
        }
        return interfaces;
    }

    std::vector<hardware_interface::CommandInterface> export_command_interfaces() override {
        // Similar for command interfaces
    }

    return_type read(const rclcpp::Time &time, const rclcpp::Duration &period) override {
        // Lecture matérielle (EtherCAT, CAN, Modbus, etc.)
        // joint_positions_ = read_encoders();
        return return_type::OK;
    }

    return_type write(const rclcpp::Time &time, const rclcpp::Duration &period) override {
        // Écriture actionneurs
        // write_motor_commands(joint_efforts_);
        return return_type::OK;
    }

private:
    std::vector<double> joint_positions_;
    std::vector<double> joint_velocities_;
    std::vector<double> joint_efforts_;
};
```

## Tests et Validation

### Tests Unitaires ROS2
```python
import pytest
import rclpy
from my_robot_msgs.srv import GraspObject
from my_robot_perception.object_detector import ObjectDetector

@pytest.fixture
def detector():
    rclpy.init()
    node = ObjectDetector()
    yield node
    node.destroy_node()
    rclpy.shutdown()

class TestObjectDetector:
    def test_detect_no_image(self, detector):
        with pytest.raises(ValueError):
            detector.detect(None)

    def test_detect_single_object(self, detector, test_image):
        result = detector.detect(test_image)
        assert len(result.objects) >= 1  # au moins 1 objet
        assert result.objects[0].confidence > 0.5

    def test_detect_multiple_objects(self, detector, test_scene):
        result = detector.detect(test_scene)
        assert len(result.objects) >= 3  # 3+ objets
```

### Intégration Continue (GitHub Actions ROS2)
```yaml
# .github/workflows/ci.yaml
name: ROS2 CI

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-22.04
    container:
      image: ros:humble-ros-base-jammy

    steps:
    - uses: actions/checkout@v4
      with:
        path: src/my_robot

    - name: Install dependencies
      run: |
        rosdep update
        rosdep install --from-paths src --ignore-src -r -y

    - name: Build
      run: |
        colcon build --event-handlers console_cohesion+

    - name: Lint (ament)
      run: |
        source install/setup.bash
        ament_cpplint src/my_robot
        ament_flake8 src/my_robot

    - name: Run tests
      run: |
        source install/setup.bash
        colcon test --packages-select my_robot_perception
        colcon test-result --verbose
```

### Hardware-in-the-Loop (HIL)
```python
class HILTesting:
    """Test avec vrai matériel via EtherCAT"""
    def test_joint_movement(self, robot_hardware):
        """Vérifie que chaque joint bouge correctement"""
        for joint_id in range(6):
            # Envoi consigne
            robot_hardware.set_joint_target(joint_id, 0.5)

            # Attente stabilisation
            time.sleep(0.5)

            # Vérification retour capteur
            actual = robot_hardware.get_joint_position(joint_id)
            assert abs(actual - 0.5) < 0.01  # erreur < 1°

            # Retour à zéro
            robot_hardware.set_joint_target(joint_id, 0.0)
```

## Communication EtherCAT (SOEM)

```c
// Simple Open EtherCAT Master (SOEM)
#include <soem/ethercat.h>

#define EC_TIMEOUTMON 5000

int main() {
    // Initialisation
    if (ec_init("eno1")) {
        printf("Initialisation EtherCAT réussie\n");

        // Scan du bus
        if (ec_config_init(FALSE) > 0) {
            printf("%d esclaves trouvés\n", ec_slavecount);

            // Configuration PDO
            ec_config_map(&IOmap);
            ec_configdc();

            // Boucle de communication cyclique
            while (1) {
                // Envoi requête
                ec_send_processdata();

                // Réception
                int wkc = ec_receive_processdata(EC_TIMEOUTRET);

                if (wkc > 0) {
                    // Lecture des entrées (encoders)
                    int32_t pos = *(int32_t*)(ec_slave[0].inputs);
                    uint16_t status = *(uint16_t*)(ec_slave[0].inputs + 4);

                    // Écriture des sorties (moteurs)
                    int32_t target = 50000;
                    memcpy(ec_slave[0].outputs, &target, 4);
                }

                usleep(1000);  // 1 kHz
            }
        }
    }
}
```

## Gestion de Dépendances

### Repositories ROS2 (vcstool / rosinstall)
```yaml
# my_robot.repos
repositories:
  my_robot_control:
    type: git
    url: https://github.com/myorg/my_robot_control.git
    version: humble-devel

  my_robot_description:
    type: git
    url: https://github.com/myorg/my_robot_description.git
    version: main

  # Dépendance externe
  ros2_controllers:
    type: git
    url: https://github.com/ros-controls/ros2_controllers.git
    version: humble
```

```bash
# Setup du workspace
mkdir -p my_robot_ws/src
cd my_robot_ws
vcs import src < my_robot.repos
rosdep install --from-paths src --ignore-src -r -y
colcon build
```

## Pièges et Bonnes Pratiques

- **Ne pas mélanger ROS1 et ROS2** : les protocoles sont incompatibles. Si bridge nécessaire, utiliser `ros1_bridge` (package de bridge ROS1↔ROS2).
- **Timeouts DDS** : les nœuds ROS2 qui ne se découvrent pas : vérifier `ROS_DOMAIN_ID` et le firewall. Les middlewares DDS (FastDDS, CycloneDDS) ne sont pas compatibles entre eux — utiliser un seul RMW.
- **Tests de régression** : un test sur une vraie trajectoire (rosbag playback + comparaison) vaut 100 tests unitaires. Toujours inclure des tests de scénario.
- **Simulation vs réel** : le gap simulation→réel est un problème majeur. Tester le transfert tôt. Modèles de contact et de friction mal calibrés = comportement différent en réel. Ajouter des perturbations simulées pour robustesse.
- **Performances ROS2** : les callbacks sont séquentiels dans l'executor par défaut. Pour la haute fréquence (>1kHz), utiliser l'executor multithread ou static single-thread avec un nœud dédié.
- **Safety** : tout système robotique en contact humain doit avoir une couche de sécurité indépendante du logiciel principal (hardware E-stop, limit switches, torque limiting).
- **Logs structurés** : utiliser le système de logging ROS2 (`RCLCPP_INFO`, `rclpy.logging`), pas des `printf`. Configurer les niveaux de log par nœud.

## Références

- ROS2 Documentation officielle : https://docs.ros.org/en/humble/
- ros2_control : https://control.ros.org/
- Gazebo Sim : https://gazebosim.org/
- MuJoCo : https://mujoco.org/
- OROCOS : https://www.orocos.org/
- Zenoh : https://zenoh.io/
- SOEM : https://github.com/OpenEtherCATsociety/SOEM
- Xenomai : https://xenomai.org/
- PREEMPT_RT : https://wiki.linuxfoundation.org/realtime/start
- ROS2 Testing : https://docs.ros.org/en/humble/Tutorials/Intermediate/Testing/CLI.html
- Featherstone, R. (2008). *Rigid Body Dynamics Algorithms*. Springer.
- Todorov, E. (2014). MuJoCo: A physics engine for model-based control. *IEEE IROS 2014*.
- Koenig, N. & Howard, A. (2004). Design and Use Paradigms for Gazebo. *IEEE ICRA 2004*.