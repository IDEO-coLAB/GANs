import tensorflow as tf
import numpy as np

from ops import BN, conv2d, conv2dtr, dense, lrelu, \
                flatten, reshape, sigmoid, tanh

class VAEGAN:
    ''' Generative adversarial network with encoder. '''
    def __init__(self, is_training, img_shape=(64, 64, 3), zsize=128):
        # Input image shape: x, y, channels
        self.img_shape = img_shape
        # latent (z) vector length
        self.zsize = zsize
        # is the model being trained
        self.is_training = is_training

    def encoder(self, inputs, scope='encoder', reuse=None):
        ''' Returns encoder graph. Inputs is a placeholder of size
        (None, rows, cols, channels) '''
        with tf.variable_scope(scope, reuse=reuse):

            bn = BN(self.is_training)

            t = lrelu(bn(conv2d(inputs, 64, strides=4)))
            print('25: %s' % t.get_shape())
            t = lrelu(bn(conv2d(t, 128, strides=4)))
            print('27: %s' % t.get_shape())
            t = lrelu(bn(conv2d(t, 256)))
            print('29: %s' % t.get_shape())
            
            t = flatten(t)
            print('32: %s' % t.get_shape())
            t = lrelu(bn(dense(t, 512)))
            print('34: %s' % t.get_shape())
            
            # keep means and logsigma for computing variational loss
            means = lrelu(dense(t, self.zsize))
            logsigmas = lrelu(dense(t, self.zsize))
            
            sigmas = tf.exp(0.5 * logsigmas) # see Hands on machine learning, Geron, p. 435
            sample = tf.random_normal(tf.shape(sigmas), dtype=tf.float32)
            output = sample * sigmas + means
          
            return output, logsigmas, means

    def latent_loss(self, logsigmas, means):
        with tf.variable_scope('latent_loss'):
            loss = 0.5 * tf.reduce_mean(tf.exp(logsigmas) + tf.square(means) - 1 - logsigmas)
            return loss

    def generator(self, inputs, scope='generator', reuse=None):
        with tf.variable_scope(scope, reuse=reuse):
            # deconvolution mirrors convolution, start with many filters, then
            # shrink down to a base level of filters. This is lowest number of filters
            # before wiring to 3 channel image (rgb).

            bn = BN(self.is_training)

            t = dense(inputs, 5*4*512)
            t = lrelu(bn(reshape(t, (tf.shape(t)[0], 4, 5, 512))))

            t = lrelu(bn(conv2dtr(t, 512)))
            t = lrelu(bn(conv2dtr(t, 256)))
            t = lrelu(bn(conv2dtr(t, 128)))
            t = lrelu(bn(conv2dtr(t, 64)))

            # final conv2d  transpose to get to filter depth of 3, for rgb channels
            logits = conv2dtr(t, self.img_shape[2])
            return tanh(logits)


    def discriminator(self, inputs, scope='discriminator', reuse=None):
        with tf.variable_scope(scope, reuse=reuse):

            bn = BN(self.is_training)

            t = lrelu(conv2d(inputs, 64, strides=4)) # no bn here
            t = lrelu(bn(conv2d(t, 128)))
            t = lrelu(bn(conv2d(t, 256)))
            t = lrelu(bn(conv2d(t, 512)))

            # use this vector to compare similarity of two images
            similarity = flatten(t)
            print('81: %s' % similarity.get_shape())

            # output classification: probability an image is fake
            logits = dense(similarity, 1)
            classification = sigmoid(logits)
            return classification, logits, similarity



