// esp32_stub.ino
// Micro-ROS stub for ESP32 motor controller
// This firmware runs on the physical robot bases, receiving Twist commands
// from the Pi 5 and returning Odometry/Battery telemetry.

#include <micro_ros_arduino.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <geometry_msgs/msg/twist.h>
#include <nav_msgs/msg/odometry.h>
#include <sensor_msgs/msg/battery_state.h>

rcl_subscription_t subscriber;
rcl_publisher_t odom_publisher;
rcl_publisher_t batt_publisher;

geometry_msgs__msg__Twist msg_twist;
nav_msgs__msg__Odometry msg_odom;
sensor_msgs__msg__BatteryState msg_batt;

rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

void error_loop(){
  while(1){
    delay(100);
  }
}

// Simulated physical state
float current_x = 0.0;
float current_y = 0.0;
float current_theta = 0.0;
float current_v = 0.0;
float current_w = 0.0;
float battery_level = 100.0;

void cmd_vel_callback(const void * msgin)
{  
  const geometry_msgs__msg__Twist * msg = (const geometry_msgs__msg__Twist *)msgin;
  // Apply velocity commands to motor drivers (L298N, MDD10A, etc.)
  current_v = msg->linear.x;
  current_w = msg->angular.z;
  
  // Battery drops slightly with movement
  battery_level -= (abs(current_v) + abs(current_w)) * 0.001;
}

void setup() {
  Serial.begin(115200);
  set_microros_transports();
  
  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  RCCHECK(rclc_node_init_default(&node, "vyuha_base_r1", "", &support));

  // Subscriber: cmd_vel
  RCCHECK(rclc_subscription_init_default(
    &subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Twist),
    "/r1/cmd_vel"));

  // Publisher: odom
  RCCHECK(rclc_publisher_init_default(
    &odom_publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(nav_msgs, msg, Odometry),
    "/r1/odom"));

  // Publisher: battery
  RCCHECK(rclc_publisher_init_default(
    &batt_publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, BatteryState),
    "/r1/battery"));

  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_subscription(&executor, &subscriber, &msg_twist, &cmd_vel_callback, ON_NEW_DATA));
}

void loop() {
  RCCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
  
  // 1. Simulate kinematics integration for mock testing
  float dt = 0.1; // 10Hz loop
  current_theta += current_w * dt;
  current_x += current_v * cos(current_theta) * dt;
  current_y += current_v * sin(current_theta) * dt;

  // 2. Publish Odometry
  msg_odom.pose.pose.position.x = current_x;
  msg_odom.pose.pose.position.y = current_y;
  
  // Approximate quaternion from theta
  msg_odom.pose.pose.orientation.z = sin(current_theta / 2.0);
  msg_odom.pose.pose.orientation.w = cos(current_theta / 2.0);
  
  RCSOFTCHECK(rcl_publish(&odom_publisher, &msg_odom, NULL));

  // 3. Publish Battery
  msg_batt.percentage = battery_level / 100.0;
  RCSOFTCHECK(rcl_publish(&batt_publisher, &msg_batt, NULL));

  delay(100);
}
