#coding=utf-8

import os
import math
import numpy as np
import tensorflow as tf
from data_util_3 import data_batch

import matplotlib.pyplot as plt  

lr = 0.001
iter_num = 1000000
batch_num = 128

dataset_dir = './data_3'
ckpt_name = 'cnn_data_4.ckpt'

image_width = 160
image_height = 60
digits_num = 4
digits_size = 62
channel_num = 1

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

def weight_variable(shape):
    initial = 0.01 * tf.random_normal(shape)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = 0.1 * tf.random_normal(shape)
    return tf.Variable(initial)

images = tf.placeholder(tf.float32,[None,image_height*image_width])
labels = tf.placeholder(tf.float32,[None,digits_num*digits_size])
keep_prob = tf.placeholder(tf.float32)



#   Convolutional Layer 1
feature_map_num_1 = 32
filter_size_1 = 3

x_image = tf.reshape(images, [-1, image_width, image_height, channel_num])
W_conv1 = weight_variable([filter_size_1, filter_size_1 , channel_num, feature_map_num_1])
b_conv1 = bias_variable([feature_map_num_1])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)
h_pool1 = tf.nn.dropout(h_pool1, keep_prob)

#   Convolutional Layer 2
feature_map_num_2 = 64
filter_size_2 = 3

W_conv2 = weight_variable([filter_size_2, filter_size_2, feature_map_num_1, feature_map_num_2])
b_conv2 = bias_variable([feature_map_num_2])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)
h_pool2 = tf.nn.dropout(h_pool2, keep_prob)

#   Convolutional Layer 3
feature_map_num_3 = 64
filter_size_3 = 3

W_conv3 = weight_variable([filter_size_3, filter_size_3, feature_map_num_2, feature_map_num_3])
b_conv3 = bias_variable([feature_map_num_3])
h_conv3 = tf.nn.relu(conv2d(h_pool2, W_conv3) + b_conv3)
h_pool3 = max_pool_2x2(h_conv3)
h_pool3 = tf.nn.dropout(h_pool3, keep_prob)


# Densely Connected Layer
height = int(math.ceil(image_height/2.0/2.0/2.0))
width = int(math.ceil(image_width/2.0/2.0/2.0))

W_fc1 = weight_variable([height * width * feature_map_num_3, 1024])
b_fc1 = bias_variable([1024])
h_pool3_flat = tf.reshape(h_pool3, [-1, height * width * feature_map_num_3])
h_fc1 = tf.nn.relu(tf.matmul(h_pool3_flat, W_fc1) + b_fc1)

# Dropout
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

W_fc2 = weight_variable([1024, digits_num*digits_size])
b_fc2 = bias_variable([digits_num*digits_size])

# results = tf.reshape(results,[-1,digits_size])
# results = tf.nn.softmax(results)
# results = tf.reshape(results,[-1,digits_num*digits_size])
# labels_ = tf.reshape(labels,[-1,digits_size])

# results=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
# cross_entropy = -tf.reduce_sum(labels*tf.log(results))


results = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
# cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=results)
cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=results)
cross_entropy = tf.reduce_mean(cross_entropy)
# train_step = tf.train.GradientDescentOptimizer(lr).minimize(cross_entropy)


train_step = tf.train.AdamOptimizer(lr).minimize(cross_entropy)
# train_step = tf.train.GradientDescentOptimizer(lr).minimize(cross_entropy)


labels_ = tf.reshape(labels,[-1,digits_num,digits_size])
results = tf.reshape(results,[-1,digits_num,digits_size])

correct_prediction = tf.equal(tf.argmax(results,2), tf.argmax(labels_,2))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))




saver = tf.train.Saver()

config_gpu = tf.ConfigProto()  
config_gpu.gpu_options.allow_growth=True  

with tf.Session(config=config_gpu) as sess:
    init = tf.global_variables_initializer()
    sess.run(init)
    saver.restore(session, './models_res'+ckpt_name)
    max_acc = 0
    for i in range(iter_num):
        (a,b) = data_batch(dataset_dir+'/train',digits_num,digits_size,batch_num,iter_num)
        # print a[1],b[1]
        # im = a[2].reshape(60,160)
        # fig = plt.figure()

        # plt.imshow(im , cmap='gray')
        # bb = b[2].reshape(4,62)
        # print np.argmax(bb,1)
        # plt.show()


        if(i%100==0):

            images_test,labels_test  = data_batch(dataset_dir+'/train',digits_num,digits_size,batch_num,iter_num)
            valid_acc = sess.run(accuracy, feed_dict={images: images_test, labels:labels_test,keep_prob:1.0})
            print " valid : ", valid_acc
            if valid_acc>max_acc:
                max_acc = valid_acc
                path = saver.save(sess, os.path.join(os.path.dirname(__file__), 'models_res', ckpt_name))
                print("Model saved... :", path)

        loss,_ = sess.run([cross_entropy,train_step],feed_dict={images:a,labels:b, keep_prob: 0.75})
        if i%10 ==0:
            print "iter:",i," ",loss

    images_test,labels_test  = data_batch(dataset_dir+'/train',digits_num,digits_size,batch_num,iter_num)
    valid_acc = sess.run(accuracy, feed_dict={images: images_test, labels:labels_test,keep_prob:1.0})
    print " valid : ", valid_acc    
    if valid_acc>max_acc:
        max_acc = valid_acc
        path = saver.save(sess, os.path.join(os.path.dirname(__file__), 'models_res', ckpt_name))
        print("Model saved... :", path)
