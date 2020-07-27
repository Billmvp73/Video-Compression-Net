import tensorflow.compat.v1 as tf
from utils.network import VideoCompressor
import numpy as np
from PIL import Image
import os
import pickle as pkl
import math

if __name__ == "__main__":
    net = VideoCompressor()
    chkfile = "checkpoints/tfvideocomp.chk"
    pklfile = "checkpoints/tfvideocomp.pkl"
    checkpointFrequency = 25
    direc = "vimeo_septuplet/sequences/"
    subdircount = 0

    for item in os.listdir(direc):
        subdircount += 1

    tfprvs = tf.placeholder(tf.float32, shape=[4, 256, 448, 3], name="first_frame")
    tfnext = tf.placeholder(tf.float32, shape=[4, 256, 448, 3], name="second_frame")

    l_r = tf.placeholder(tf.float32, shape=[], name='learning_rate')
    lamda = tf.placeholder(tf.int16, shape=[], name="train_lambda")

    _, mse, bpp = net(tfprvs, tfnext)
    train_loss = tf.cast(lamda, tf.float32) * mse + bpp
    train = tf.train.AdamOptimizer(learning_rate=l_r).minimize(train_loss)

    train_epoch = tf.get_variable("train_epoch", initializer=tf.constant(0))
    tfvideo_batch = tf.get_variable("tfvideo_batch", initializer=tf.constant(0))
    increment_video_batch = tf.assign(tfvideo_batch, tfvideo_batch + 1)
    directory = tf.get_variable("directory", initializer=tf.constant(1))

    increment_directory = tf.assign(directory, directory + 1)
    init_video_batch_updater = tf.assign(tfvideo_batch, 0)
    init_directory_updater = tf.assign(directory, 1)
    increment_epoch = tf.assign(train_epoch, train_epoch + 1)
    init_epoch_updater = tf.assign(train_epoch, 0)

    init = tf.global_variables_initializer()

    saver = tf.train.Saver()

    starting = False

    with tf.Session() as sess:
        sess.run(init)
        # with open("checkpoints/spymodeltf.pkl", "rb") as f:
        #     net.ofnet.set_weights(pkl.load(f))
        if starting:
            saver.restore(sess, chkfile)

        load_epoch = train_epoch.eval() if starting else 0
        lr = 1e-4
        lmda = 8192

        for epoch in range(load_epoch, 21):
            print("lr={}, lambda = {}".format(lr, lmda))
            load_dir = directory.eval() if starting else 1

            for i in range(load_dir, subdircount + 1):
                subdir = direc + str(i).zfill(5) + '/'
                subsubdircount = 0
                for item in os.listdir(subdir):
                    subsubdircount += 1

                start_video_batch = tfvideo_batch.eval() if starting else 0

                num_video_batch = math.floor(subsubdircount / 4)
                starting = False

                for video_batch in range(start_video_batch, 1):
                    for batch in range(1, 8):
                        bat = subdir + str(4 * video_batch + 1).zfill(4) + '/im' + str(batch) + '.png'
                        bat = np.array(Image.open(bat)).astype(np.float32) * (1.0 / 255.0)
                        bat = np.expand_dims(bat, axis=0)
                        for item in range(2, 5):
                            img = subdir + str(4 * video_batch + item).zfill(4) + '/im' + str(batch) + '.png'
                            img = np.array(Image.open(img)).astype(np.float32) * (1.0 / 255.0)
                            img = np.expand_dims(img, axis=0)
                            bat = np.concatenate((bat, img), axis=0)

                        if batch == 1:
                            prevReconstructed = bat

                        else:
                            recloss, rate, _ = sess.run([mse, bpp, train],
                                                        feed_dict={tfprvs: prevReconstructed, tfnext: bat, l_r: lr,
                                                                   lamda: lmda})
                            prevReconstructed = bat

                    increment_video_batch.op.run()
                    print("recon loss = {:.8f}, bpp = {:.8f}, video = {}, directory = {}, epoch = {}".format(recloss,
                                                                                                             rate,
                                                                                                             video_batch,
                                                                                                             i, epoch))
                    # print(tfvideo_batch.eval(), directory.eval())
                    if video_batch % checkpointFrequency == 0:
                        weights = net.get_weights()
                        # pkl.dump(weights, open(pklfile, "wb"))
                        # saver.save(sess, chkfile)

                init_video_batch_updater.op.run()
                increment_directory.op.run()

            init_directory_updater.op.run()
            increment_epoch.op.run()
            if epoch == 0:
                lr = 1e-5

            elif epoch == 1:
                lr = 1e-6

            elif epoch == 2:
                lr = 1e-7

            elif epoch == 3:
                weights = net.get_weights()
                pkl.dump(weights, open("checkpoints/videocompressor8192.pkl", "wb"))
                saver.save(sess, "checkpoints/videocompressor8192.chk")
                lr = 1e-5
                lmda = 4096

            elif epoch == 4:
                lr = 1e-6

            elif epoch == 5:
                lr = 1e-7

            elif epoch == 6:
                weights = net.get_weights()
                pkl.dump(weights, open("checkpoints/videocompressor4096.pkl", "wb"))
                saver.save(sess, "checkpoints/videocompressor4096.chk")
                lr = 1e-5
                lmda = 2048

            elif epoch == 7:
                lr = 1e-6

            elif epoch == 8:
                lr = 1e-7

            elif epoch == 9:
                weights = net.get_weights()
                pkl.dump(weights, open("checkpoints/videocompressor2048.pkl", "wb"))
                saver.save(sess, "checkpoints/videocompressor2048.chk")
                lr = 1e-5
                lmda = 1024

            elif epoch == 10:
                lr = 1e-6

            elif epoch == 11:
                lr = 1e-7

            elif epoch == 12:
                weights = net.get_weights()
                pkl.dump(weights, open("checkpoints/videocompressor1024.pkl", "wb"))
                saver.save(sess, "checkpoints/videocompressor1024.chk")
                lr = 1e-5
                lmda = 512

            elif epoch == 13:
                lr = 1e-6

            elif epoch == 14:
                lr = 1e-7

            elif epoch == 15:
                weights = net.get_weights()
                pkl.dump(weights, open("checkpoints/videocompressor512.pkl", "wb"))
                saver.save(sess, "checkpoints/videocompressor512.chk")
                lr = 1e-5
                lmda = 256

            elif epoch == 16:
                lr = 1e-6

            elif epoch == 17:
                lr = 1e-7

            elif epoch == 18:
                weights = net.get_weights()
                pkl.dump(weights, open("checkpoints/videocompressor256.pkl", "wb"))
                saver.save(sess, "checkpoints/videocompressor256.chk")
                lr = 1e-5
                lmda = 128

            elif epoch == 19:
                lr = 1e-6

            elif epoch == 20:
                lr = 1e-7
                pklfile = "checkpoints/tfvideocomp128.pkl"
                chkfile = "checkpoints/videocompressor128.chk"

        init_epoch_updater.op.run()
