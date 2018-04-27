# ros
#! /usr/bin/python
import rospy
from geometry_msgs.msg import Twist
import time
# lib for record
import pyaudio
import wave
# lib for recognize speech
import librosa.display
from dtw import dtw
from numpy.linalg import norm

class QBot():
    def __init__(self):
        # initiliaze
        rospy.init_node('Move', anonymous=False)

    	# tell user how to stop QBot
    	rospy.loginfo("To stop QBot CTRL + C")

        # What function to call when you ctrl + c
        rospy.on_shutdown(self.shutdown)

        # Create a publisher which can "talk" to QBot and tell it to move
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)



        # Twist is a datatype for velocity
        move_cmd = Twist()
    	# let's go forward at 0.2 m/s
        move_cmd.linear.x = 0
    	# let's turn at 0 radians/s
    	move_cmd.angular.z = 0

    	# as long as you haven't ctrl + c keeping doing...
        # while not rospy.is_shutdown():
        #     # publish the velocity
        #     self.cmd_vel.publish(move_cmd)
        #     # wait for 0.1 seconds (10 HZ) and publish again
        #     r.sleep()

    def move_bot(self, x, z):
        # Twist is a datatype for velocity
        move_cmd = Twist()
    	# let's go forward at 0.2 m/s
        move_cmd.linear.x = x
    	# let's turn at 0 radians/s
    	move_cmd.angular.z = z
        self.cmd_vel.publish(move_cmd)
        #QBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
        r = rospy.Rate(1)
        # wait for 0.1 seconds (10 HZ) and publish again
        r.sleep()

    def shutdown(self):
        # stop QBot
        rospy.loginfo("Stop QBot")
	    # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop QBot
        self.cmd_vel.publish(Twist())
	    # sleep just makes sure QBot receives the stop command prior to shutting down the script
        rospy.sleep(1)
#end ros
bot = QBot()
x = 0
z = 0

while not rospy.is_shutdown():
    # strart record
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 1
    WAVE_OUTPUT_FILENAME = "samples/test.wav"
    #
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    # end record

    # recognize speech
    y_test, sr_test = librosa.load('samples/test.wav')
    y_forward, sr_forward = librosa.load('samples/forward.wav')
    y_left, sr_left = librosa.load('samples/left.wav')
    y_right, sr_right = librosa.load('samples/right.wav')
    y_back, sr_back = librosa.load('samples/back.wav')
    y_stop, sr_stop = librosa.load('samples/stop.wav')
    #
    # plt.subplot(1, 2, 1)
    mfcc_test = librosa.feature.mfcc(y_test, sr_test)
    mfcc_forward = librosa.feature.mfcc(y_forward, sr_forward)
    mfcc_left = librosa.feature.mfcc(y_left, sr_left)
    mfcc_right = librosa.feature.mfcc(y_right, sr_right)
    mfcc_back = librosa.feature.mfcc(y_back, sr_back)
    mfcc_stop = librosa.feature.mfcc(y_stop, sr_stop)

    dist_forward, cost_forward, acc_cost_forward, path_forward = dtw(mfcc_forward.T, mfcc_test.T, dist=lambda x, y: norm(x - y, ord=1))
    dist_left, cost_left, acc_cost_left, path_left = dtw(mfcc_left.T, mfcc_test.T, dist=lambda x, y: norm(x - y, ord=1))
    dist_right, cost_right, acc_cost_right, path_right = dtw(mfcc_right.T, mfcc_test.T, dist=lambda x, y: norm(x - y, ord=1))
    dist_back, cost_back, acc_cost_back, path_back = dtw(mfcc_back.T, mfcc_test.T, dist=lambda x, y: norm(x - y, ord=1))
    dist_stop, cost_stop, acc_cost_stop, path_stop = dtw(mfcc_stop.T, mfcc_test.T, dist=lambda x, y: norm(x - y, ord=1))
    # print 'Normalized distance between the two sounds:', dist

    print "dist_forward: ", dist_forward
    print "dist_left: ", dist_left
    print "dist_right: ", dist_right
    print "dist_back: ", dist_back
    print "dist_stop: ", dist_stop

    label = 0
    # label = 0 => forward
    # label = 1 => left
    # label = 2 => right
    # label = 3 => back
    # label = 4 => stop

    dist = dist_forward

    if dist > dist_left :
        label = 1
        dist = dist_left
    if dist > dist_right :
        label = 2
        dist = dist_right
    if dist > dist_back :
        label = 3
        dist = dist_back
    if dist > dist_stop :
        label = 4
        dist = dist_stop

    # print "Label: ", label
    # print "Dist: ", dist

    if(dist < 100) :
        if label == 0 :
            print "forward"
            bot.move_bot(0.2, 0)
            x = 0.2
            z = 0
        elif label == 1 :
            print "left"
            bot.move_bot(0, 0.2)
            x = 0
            z = 0.2
        elif label == 2 :
            print "right"
            bot.move_bot(0, -0.2)
            x = 0
            z = -0.2
        elif label == 3 :
            print "back"
            bot.move_bot(-0.2, 0)
            x = -0.2
            z = 0
        elif label == 4 :
            print "stop"
            bot.move_bot(0, 0)
            x = 0
            z = 0
    else :
        bot.move_bot(x, z)
    time.sleep(1)
