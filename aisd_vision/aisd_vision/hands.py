import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp

# Access the MediaPipe Hands solution
mp_hands = mp.solutions.hands

# Import our custom ROS 2 Hand message
from aisd_msgs.msg import Hand


class Hands(Node):

    def __init__(self):
        # Initialize the ROS 2 node with the name 'hands'
        super().__init__('hands')

        # Subscribe to Image messages from the video_frames topic
        self.subscription = self.create_subscription(
            Image,
            'video_frames',
            self.listener_callback,
            10
        )

        # Create a converter between ROS 2 and OpenCV images
        self.br = CvBridge()

        # Publish custom Hand messages to the cmd_hand topic
        self.hand_publisher = self.create_publisher(
            Hand,
            'cmd_hand',
            10
        )


    def listener_callback(self, msg):
        # Convert the incoming ROS 2 Image message into an OpenCV image
        image = self.br.imgmsg_to_cv2(msg)

        # MediaPipe landmark numbers for the two fingertips
        PINKY_FINGER_TIP = 20
        INDEX_FINGER_TIP = 8

        # Initialize MediaPipe's hand detection and tracking model
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as myhands:

            # Mark the image as not writeable to improve performance
            image.flags.writeable = False

            # Convert the image from OpenCV BGR format to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Analyze the image and detect hand landmarks
            results = myhands.process(image)

            # Check whether at least one hand was detected
            if results.multi_hand_landmarks:

                # Create a custom ROS 2 Hand message
                hand_msg = Hand()

                # Get the normalized horizontal position of the pinky tip
                hand_msg.xpinky = results.multi_hand_landmarks[0].landmark[
                    PINKY_FINGER_TIP
                ].x

                # Get the normalized horizontal position of the index tip
                hand_msg.xindex = results.multi_hand_landmarks[0].landmark[
                    INDEX_FINGER_TIP
                ].x

                # Publish only when another node is subscribed
                if self.hand_publisher.get_subscription_count() > 0:
                    self.hand_publisher.publish(hand_msg)
                else:
                    self.get_logger().info('waiting for subscriber')


def main(args=None):
    # Initialize ROS 2 communication
    rclpy.init(args=args)

    # Create an instance of the Hands node
    hands = Hands()

    try:
        # Keep the node running to process incoming image messages
        rclpy.spin(hands)

    except KeyboardInterrupt:
        # Handle Ctrl+C when stopping the node
        pass

    finally:
        # Release resources and destroy the ROS 2 node
        hands.destroy_node()

        # Shut down ROS 2 communication
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
