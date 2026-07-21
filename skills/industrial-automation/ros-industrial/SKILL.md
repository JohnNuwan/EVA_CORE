---
name: ros-industrial
description: ROS/ROS2 pour la robotique industrielle — architecture, packages, bridge PLC, MoveIt, navigation2, industrial_core
---

# ROS & ROS2 pour la Robotique Industrielle

## Quand l'utiliser
Quand l'utilisateur demande de programmer un robot sous ROS/ROS2, intégrer ROS avec un automate industriel, configurer MoveIt pour un bras, ou déployer un système ROS sur cible industrielle (ROS-Industrial).

## Concepts Fondamentaux

### Architecture ROS1 vs ROS2
| Aspect | ROS1 | ROS2 |
|--------|------|------|
| Communication | TCPROS/UDPROS | DDS (FastDDS/cycloneDDS) |
| Découverte | Master centralisé | DDS Discovery (distribué) |
| QoS | Aucune | Fiabilité, durabilité, historic |
| Temps réel | Non | Oui (executor) |
| Sécurité | Non | SROS2 (auth, encrypt) |
| Multi-robot | Limitée | Native |

### Composants Clés ROS2
```
- rclcpp / rclpy     → Client libraries C++/Python
- nodes              → Processus autonomes
- topics             → Pub/sub asynchrone
- services           → Requête/réponse synchrone
- actions            → Appel asynchrone longue durée
- parameters         → Configuration dynamique
- lifecycle nodes    → États managés (unconfigured→inactive→active→finalized)
- TF2               → Arbre de transformations (frames)
- URDF              → Description unifiée du robot (XML)
- controllers       → Control loops (ros2_control)
- launch            → Lancement multi-nœuds (Python/XML/YAML)
```

## Robot Operating System — Commandes Essentielles

### ROS2 CLI
```bash
# Découverte et diagnostic
ros2 node list
ros2 topic list
ros2 service list
ros2 param list
ros2 action list

# Inspection
ros2 topic echo /topic_name
ros2 topic hz /topic_name
ros2 topic bw /topic_name
ros2 node info /node_name
ros2 interface show std_msgs/msg/String

# TF2
ros2 run tf2_tools view_frames
ros2 run tf2_echo parent_frame child_frame

# Lancement
ros2 launch package_name launch_file.py
ros2 run package_name executable
```

### Outils de Diagnostic
```bash
# RQT (GUI Qt4/5 pour ROS)
rqt_graph          # Graphe des nœuds/topics
rqt_plot           # Tracé de données en temps réel
rqt_console        # Filtrage des logs
rqt_bag            # Visualisation des bags
rqt_tf_tree        # Arbre des frames TF2

# rosbag
ros2 bag record -a -o session.bag
ros2 bag info session.bag
ros2 bag play session.bag

# RViz — visualisation 3D des capteurs/robot
rviz2
```

## ROS-Industrial (rosindustrial.org)

### Packages Clés
| Package | Rôle |
|---------|------|
| `industrial_core` | Nœud simple_message, interface robot ↔ contrôleur |
| `industrial_robot_client` | Client générique pour robots industriels |
| `industrial_robot_status_interface` | État standardisé du robot |
| `industrial_deprecated` | Compatibilité ascendante |
| `industrial_trajectory_filters` | Lissage/trappage des trajectoires |
| `industrial_utils` | Utilitaires (paramètres, conversions) |
| `motoman_driver` | Drivers Yaskawa/Motoman |
| `fanuc_driver` | Drivers Fanuc |
| `abb_driver` | Drivers ABB |
| `kuka_driver` | Drivers KUKA RSI |
| `universal_robot` | Drivers UR |

### Protocole Simple Message
```
Header (7 octets):
  - prefix (4 bytes): 0x1234
  - msg_type (1 byte): 10=JOINT_TRAJ_PT, 20=CARTESIAN_TRAJ_PT, ... 
  - comm_type (1 byte): 1=TOPIC, 2=SERVICE, 3=INFORM
  - reply_code (1 byte): 0=SUCCESS, 1=ERROR

Pallettisation des points de trajectoire :
  JointTrajPt → position[] + velocity[] + duration + sequence
```

## MoveIt2 — Planification de Mouvement

### Architecture
```
move_group node
├── Planning Scene (monde + robot)
│   ├── RobotModel (URDF/SRDF)
│   └── PlanningSceneMonitor (octomap, perception)
├── Motion Planners
│   ├── OMPL (PRM, RRT, EST, LazyPRM, ...)
│   ├── Pilz Industrial Planner (PTP, LIN, CIRC)
│   ├── STOMP
│   └── CHOMP
├── Kinematics
│   ├── KDL (défaut)
│   ├── TRAC-IK (plus robuste)
│   ├── IKFast (analytique, pré-généré)
│   └── bio_ik (optimisation multi-objectif)
├── Collision Checking
│   ├── FCL (défaut)
│   └── Self-collision (dummy links)
└── Trajectory Processing
    ├── Time parameterization (trapezoidal, cubic)
    ├── Iterative spline parameterization
    └── Cartesian interpolation
```

### Configuration URDF/SRDF
```xml
<!-- URDF: modèle cinématique -->
<link name="shoulder_link">
  <visual><geometry><mesh filename="shoulder.stl"/></geometry></visual>
  <collision><geometry><mesh filename="shoulder.stl"/></geometry></collision>
</link>
<joint name="shoulder_pan_joint" type="revolute">
  <parent link="base_link"/>
  <child link="shoulder_link"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-3.14" upper="3.14" effort="330" velocity="2.0"/>
</joint>

<!-- SRDF: groupes et configurations -->
<group name="manipulator">
  <joint name="shoulder_pan_joint"/>
  <joint name="shoulder_lift_joint"/>
  <joint name="elbow_joint"/>
  <joint name="wrist_1_joint"/>
  <joint name="wrist_2_joint"/>
  <joint name="wrist_3_joint"/>
</group>
<group name="gripper">
  <joint name="finger_joint1"/>
  <joint name="finger_joint2"/>
</group>
<group_state name="home" group="manipulator">
  <joint name="shoulder_pan_joint" value="0"/>
  <joint name="shoulder_lift_joint" value="-1.57"/>
  <joint name="elbow_joint" value="1.57"/>
  <joint name="wrist_1_joint" value="0"/>
  <joint name="wrist_2_joint" value="0"/>
  <joint name="wrist_3_joint" value="0"/>
</group_state>
<disable_default_collisions/>
```

### MoveIt C++ API
```cpp
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>

// Initialisation
moveit::planning_interface::MoveGroupInterface move_group("manipulator");
moveit::planning_interface::PlanningSceneInterface planning_scene;

// Mouvement articulaire (joint space)
std::vector<double> joint_target = {0.0, -1.57, 1.57, 0.0, 0.0, 0.0};
move_group.setJointValueTarget(joint_target);
moveit::planning_interface::MoveGroupInterface::Plan plan;
bool success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
move_group.execute(plan);

// Mouvement cartésien (task space)
geometry_msgs::msg::Pose target_pose;
target_pose.orientation.w = 1.0;
target_pose.position.x = 0.5;
target_pose.position.y = 0.2;
target_pose.position.z = 0.3;
move_group.setPoseTarget(target_pose);
success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);

// Trajectoire cartésienne avec interpolation
std::vector<geometry_msgs::msg::Pose> waypoints;
waypoints.push_back(start_pose);
waypoints.push_back(mid_pose);
waypoints.push_back(end_pose);

moveit_msgs::msg::RobotTrajectory trajectory;
double eef_step = 0.01;    // résolution cartésienne (m)
double jump_threshold = 0.0;  // désactiver le saut (préférer eef_step)
double fraction = move_group.computeCartesianPath(waypoints, eef_step, jump_threshold, trajectory);
// fraction = 1.0 = 100% du chemin trouvé

// Collision objects
moveit_msgs::msg::CollisionObject collision_object;
collision_object.header.frame_id = "world";
collision_object.id = "obstacle_1";
shape_msgs::msg::SolidPrimitive primitive;
primitive.type = primitive.BOX;
primitive.dimensions = {0.2, 0.3, 0.5};
geometry_msgs::msg::Pose pose;
pose.orientation.w = 1.0;
pose.position.x = 0.3;
pose.position.y = -0.2;
pose.position.z = 0.25;
collision_object.primitives.push_back(primitive);
collision_object.primitive_poses.push_back(pose);
collision_object.operation = collision_object.ADD;
std::vector<moveit_msgs::msg::CollisionObject> objects = {collision_object};
planning_scene.applyCollisionObjects(objects);
```

## Navigation2 — Mobile Robot

### Pipeline
```
SLAM (slam_toolbox / cartographer)
  → Map (occupancy grid)
  → Global Planner (NavFn, Smac Planner, A*)
    → Path
    → Local Planner (DWB, MPPI, TEB)
      → Velocity Commands (Twist)
        → Diff/Omni drive controller
```

### Configuration Nav2
```yaml
# navigation.yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: true

controller_server:
  ros__parameters:
    controller_plugins: ["FollowPath"]
    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller/RegulatedPurePursuitController"
      desired_linear_vel: 0.3
      max_linear_accel: 2.5
      lookahead_dist: 1.0
      use_velocity_scaled_lookahead: true
      min_approach_linear_velocity: 0.05

local_costmap:
  local_costmap:
    ros__parameters:
      robot_radius: 0.3
      inflation_radius: 0.5
      resolution: 0.05
      map_type: costmap
      observation_sources: laser_scan_sensor
      laser_scan_sensor:
        topic: /scan
        max_obstacle_height: 2.0
        clearing: true
        marking: true

global_costmap:
  global_costmap:
    ros__parameters:
      robot_radius: 0.3
      global_frame: map
      robot_base_frame: base_link
      resolution: 0.05
      track_unknown_space: true
```

## Communication ROS ↔ PLC (Bridge Industriel)

### Modbus TCP Bridge
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Bool
from pymodbus.client import ModbusTcpClient

class ModbusROSBridge(Node):
    def __init__(self):
        super().__init__('modbus_ros_bridge')
        self.client = ModbusTcpClient('192.168.1.100', port=502)
        self.client.connect()

        # Publisher capteurs PLC → ROS
        self.pub_temp = self.create_publisher(Float64, '/plc/temperature', 10)
        self.pub_status = self.create_publisher(Bool, '/plc/motor_running', 10)

        # Timer de lecture
        self.timer = self.create_timer(0.1, self.read_plc)

        # Subscriber ROS → PLC
        self.sub_setpoint = self.create_subscription(
            Float64, '/plc/setpoint', self.write_setpoint, 10)

    def read_plc(self):
        temp = self.client.read_holding_registers(100, 1)
        if temp.isError():
            self.get_logger().error('Erreur lecture Modbus')
            return
        msg = Float64()
        msg.data = temp.registers[0] / 10.0  # scaling
        self.pub_temp.publish(msg)

    def write_setpoint(self, msg):
        scaled = int(msg.data * 10)
        self.client.write_register(200, scaled)
```

### OPC UA Bridge (open62541)
```bash
# Compilation bridge OPC UA ↔ ROS
ros2 run ros2_opc_ua opcua_bridge_exe
# lit les variables OPC UA → les publie en topics ROS2
# écrit les topics ROS2 → les écrit en variables OPC UA
```

### EtherCAT via SOEM (Simple Open EtherCAT Master)
- Package `ethercat_manager` pour ROS2
- Lecture/écriture des PDO cycliques
- Synchronisation avec le cycle de contrôle (1-10 kHz)

## Industrial Robot Clients

### Exemple : driver Fanuc
```python
import rclpy
from industrial_robot_client.joint_trajectory_streamer import JointTrajectoryStreamer

rclpy.init()
streamer = JointTrajectoryStreamer()
# Envoi de la trajectoire articulaire au contrôleur Fanuc
points = [
    JointTrajectoryPoint(positions=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                         velocities=[0.0]*6,
                         time_from_start=Duration(seconds=2)),
    JointTrajectoryPoint(positions=[0.5, -0.3, 0.8, 0.0, 0.2, 0.0],
                         velocities=[0.0]*6,
                         time_from_start=Duration(seconds=4)),
]
streamer.send_joint_trajectory(points)
rclpy.spin(streamer)
```

## Pièges et Bonnes Pratiques

- **Ne jamais lancer `ros2 run` sans un workspace source** : utiliser `colcon build --symlink-install` et `source install/setup.bash`.
- **Problèmes DDS découverte** : si nœuds ne se voient pas, vérifier `ROS_DOMAIN_ID` (même ID) et `RMW_IMPLEMENTATION` (même implémentation DDS). Test : `ros2 run demo_nodes_cpp talker` / `listener`.
- **TF2 manquant** : toute transformation requiert une chaîne complète de parent à enfant. Publier obligatoirement `map→odom→base_link→...`. Utiliser `view_frames` pour diagnostiquer les trous.
- **Real-time ROS2** : isoler les cœurs CPU (`isolcpus=1-3` kernel param), utiliser `realtime_cmake` + `rclcpp::Executor::add_node` sur thread dédié, éviter les callbacks bloquants.
- **MoveIt ne planifie pas** : vérifier que le robot est en dehors de collisions (self-collision), que la scène ne contient pas d'obstacle englobant, et que le groupe est bien défini dans le SRDF.
- **Performances rosbag** : éviter `-a` (all topics) si seuls quelques topics sont nécessaires. Préférer `--topics /tf /joint_states` pour réduire la taille des fichiers.

## Références

- Documentation officielle ROS2 : https://docs.ros.org/
- ROS-Industrial : https://rosindustrial.org/
- MoveIt2 : https://moveit.picknik.ai/
- Nav2 : https://navigation.ros.org/
- ROS2 Control : https://control.ros.org/
