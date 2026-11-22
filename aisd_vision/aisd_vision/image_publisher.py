import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2



class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher')

        # Create a publisher for Image messages on the video_frames topic
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10)

        # Create a timer that calls timer_callback every 0.1 seconds
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Open the default webcam (camera index 0)
        self.cap = cv2.VideoCapture(0)

        # Create a converter between OpenCV images and ROS 2 Image messages
        self.br = CvBridge()


    def timer_callback(self):
        # Capture a single frame from the webcam
        ret, frame = self.cap.read()

        # Check whether the camera successfully captured the frame
        if ret == True:
            # Convert the OpenCV frame to a ROS 2 Image message
            image_msg = self.br.cv2_to_imgmsg(frame)

            # Publish the image to the video_frames topic
            self.publisher_.publish(image_msg)


def main(args=None):
    # Initialize ROS 2 communication
    rclpy.init(args=args)

    # Create an instance of the ImagePublisher node
    image_publisher = ImagePublisher()

    # Keep the node running and process timer callbacks
    rclpy.spin(image_publisher)

    # Release the webcam when the node stops
    image_publisher.cap.release()

    # Destroy the node and shut down ROS 2
    image_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
