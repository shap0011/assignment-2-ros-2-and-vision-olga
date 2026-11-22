import rclpy
from rclpy.node import Node
from aisd_msgs.msg import Hand
from geometry_msgs.msg import Twist


class Move(Node):

    def __init__(self):
        # Initialize the ROS 2 node with the name 'move'
        super().__init__('move')

        # Subscribe to Hand messages published by the Hands node
        self.subscription = self.create_subscription(
            Hand,
            'cmd_hand',
            self.listener_callback,
            10
        )

        # Create a publisher for robot movement commands
        self.vel_publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )


    def listener_callback(self, msg):
        # Initialize angular and linear velocities to zero
        angle = 0.0
        linear = 0.0

        # Determine rotation using the index fingertip's x-coordinate
        if msg.xindex > 0.55:
            # Index finger is on the right side of the image
            self.get_logger().info('right')
            angle = -0.1

        elif msg.xindex < 0.45:
            # Index finger is on the left side of the image
            self.get_logger().info('left')
            angle = 0.1

        else:
            # Index finger is near the centre: no rotation
            angle = 0.0

        # Determine forward movement by comparing fingertip positions
        if msg.xindex > msg.xpinky:
            # Index fingertip is to the right of the pinky fingertip
            self.get_logger().info('come')
            linear = 0.5

        else:
            # Otherwise, the turtle stays in place
            self.get_logger().info('stay')
            linear = 0.0

        # Create a Twist message containing the movement velocities
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angle

        # Publish the movement command if a subscriber is connected
        if self.vel_publisher.get_subscription_count() > 0:
            self.vel_publisher.publish(twist)

        else:
            self.get_logger().info('waiting for subscriber')


def main(args=None):
    # Initialize ROS 2 communication
    rclpy.init(args=args)

    # Create an instance of the Move node
    move = Move()

    try:
        # Keep the node running to receive Hand messages
        rclpy.spin(move)

    except KeyboardInterrupt:
        # Handle Ctrl+C when stopping the node
        pass

    finally:
        # Destroy the node and release its resources
        move.destroy_node()

        # Shut down ROS 2 communication
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
