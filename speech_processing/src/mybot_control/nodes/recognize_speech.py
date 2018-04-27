import librosa.display
from dtw import dtw
from numpy.linalg import norm

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
