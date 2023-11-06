# Copyright 2022 Siddharth Saha
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from teleop_msgs.msg import VehicleControlData
from teleop_msgs.srv import EmergencyStop
class TeleopPy(Node):
    estop_state = False
    def __init__(self):
        super().__init__("teleop_py_node")
        self.declare_parameters('',[
            ('Steering', rclpy.Parameter.Type.INTEGER),
            ('Brake', rclpy.Parameter.Type.INTEGER),
            ('Throttle', rclpy.Parameter.Type.INTEGER),
            ('EstopButton', rclpy.Parameter.Type.INTEGER)
        ]) #load paramter values into node
        self.subscription = self.create_subscription(Joy,'joy',self.__callback,10)
        self.create_service(EmergencyStop,'estop_service',self.__estop__service)
        self.pub = self.create_publisher(VehicleControlData,'output_teleop',10)

    def __callback(self,msg:Joy):
        message = VehicleControlData(throttle=msg._axes[self.get_parameter('Throttle').get_parameter_value()._integer_value],brake=msg._axes[self.get_parameter('Brake').get_parameter_value()._integer_value],steering=msg._axes[self.get_parameter('Steering').get_parameter_value()._integer_value], estop=msg._buttons[self.get_parameter('EstopButton').get_parameter_value().integer_value] == 1)
        #self.get_logger().info("MESSAGE: %s" %message.__repr__())
        if message.estop == True:
            message.brake = -1.0
            message.throttle = 0.0
            message.steering = 0.0
        elif self.estop_state == True:
            message.brake = -1.0
            message.throttle = 0.0
            message.steering = 0.0
            message.estop = True
        self.pub.publish(message)
        
    def __estop__service(self, request:EmergencyStop.Request, response:EmergencyStop.Response):
        response.estop_state = self.estop_state
        if request._set_estop == True and self.estop_state == False:
            response.estop_state = True
            self.estop_state = True
        elif request._set_estop == False and self.estop_state == True:
            response.estop_state = False
            self.estop_state = False
        return response
    
def main(args=None):
    rclpy.init(args=args)
    teleop_py = TeleopPy()
    rclpy.spin(teleop_py)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    