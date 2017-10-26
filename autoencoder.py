import tensorflow as tf
import numpy as np

he_init = tf.contrib.layers.variance_scaling_initializer

class Autoencoder():
  ''' Autoencoder including encode, decode networks. '''
  def __init__(self, img_shape=(64, 64, 3), zsize=128):
    # Input image shape: x, y, channels
    self.img_shape = img_shape
    # latent (z) vector length
    self.zsize = zsize

  def encoder(self, inputs, scope='encoder', reuse=None):
    ''' Returns encoder graph. Inputs is a placeholder of size
    (None, rows, cols, channels) '''
     
    with tf.variable_scope(scope, reuse=reuse):
      # Base number of 2D convolution filters. 64 is from paper.
      filters = 64
      # 64 filters of 5x5 field with stride 2
      t0 = tf.layers.conv2d(inputs, filters, 5, strides=2)

      # Batch normalize per channel (per the paper) and channels are last dim.
      # This means find average accross the batch and apply it to the inputs, 
      # but do it separately for each channel. Also note that in the input layer,
      # we call them channels (red, green, blue) but in deeper layers each channel
      # is the output of a convolution filter.
      t1 = tf.layers.batch_normalization(t0, axis=-1)
      t2 = tf.nn.elu(t1)

      t3 = tf.layers.conv2d(t2, filters*2, 5, strides=2)   
      t4 = tf.layers.batch_normalization(t3, axis=-1)
      t5 = tf.nn.elu(t4)

      t6 = tf.layers.conv2d(t5, filters*2, 5, strides=2)   
      t7 = tf.layers.batch_normalization(t6, axis=-1)
      t8 = tf.nn.elu(t7)

      t9 = tf.contrib.layers.flatten(t8)
       
      # In a variational autoencoder, the encoder outputs a mean and sigma vector
      # from which samples are drawn. In practice, treat the second output as
      # log(sigma**2), but we'll call it logsigma. Each of mean and logsigma are
      # zsize vectors, but here we pack them into a single zsize*2 vector.
      self.means = tf.layers.dense(t9, self.zsize, activation=tf.nn.elu, kernel_initializer=he_init())
      self.logsigmas = tf.layers.dense(t9, self.zsize, activation=tf.nn.elu, kernel_initializer=he_init())
      # keep means and logsigma for computing variational loss
      sigmas = tf.exp(0.5 * self.logsigmas) # see Hands on machine learning, Geron, p. 435

      sample = tf.random_normal(tf.shape(sigmas), dtype=tf.float32)
    return sample * sigmas + self.means

  def latent_loss(self):
    with tf.variable_scope('latent_loss'):
      loss = 0.5 * tf.reduce_mean(tf.exp(self.logsigmas) + tf.square(self.means) - 1 - self.logsigmas)
    return loss

  def decoder(self, inputs, scope='decoder', reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
      filters = 64
      # deconvolution mirrors convolution, start with many filters, then
      # shrink down to a base level of filters. This is lowest number of filters
      # before wiring to 3 channel image (rgb).

      rows = [int(np.ceil(self.img_shape[0] / i)) for i in [16., 8., 4., 2.]]
      cols = [int(np.ceil(self.img_shape[1] / i)) for i in [16., 8., 4., 2.]]
      # What size should image be as we create larger and larger images with
      # each conv transpose layer.

      t0 = tf.layers.dense(inputs, rows[0]*cols[0]*filters*8, kernel_initializer=he_init())
      # densely connect z vector to enough units to supply first deconvolution layer.
      # That's rows*cols and at this layer use 8 times the base number of filters.

      t1 = tf.reshape(t0, (tf.shape(t)[0], rows[0], cols[0], filters*8))
      # for 64x64 images, this is 4x4 by 512 filters
      t2 = tf.layers.batch_normalization(t1, axis=-1)
      t3 = tf.nn.elu(t2)

      t4 = tf.layers.conv2d_transpose(t3, filters*4, 5, strides=2)

      # Because of the way the kernel slides accross
      # the input, and b/c we're using stride 2, output is double the input
      # rows/cols plus a few more due to width of kernel. Just crop out extras
      # before moving on.
      # e.g. for input image of size 4x4, with 5x5 kernel and stride of 2, 
      # we get output of 11x11, but want 8x8. Crop off bottom and right of image.

      # crop the whole batch
      t5 = t4[:, :rows[1], :cols[1], :]
     
      t6 = tf.layers.batch_normalization(t5, axis=-1)
      t7 = tf.nn.elu(t6)

      t8 = tf.layers.conv2d_transpose(t7, filters*2, 5, strides=2)
      t9 = t8[:, :rows[2], :cols[2], :]
      # for 64x64 images, this is 16x16 by 128 filters
      t10 = tf.layers.batch_normalization(t9, axis=-1)
      t11 = tf.nn.elu(t10)

      t12 = tf.layers.conv2d_transpose(t11, filters, 5, strides=2)
      t13 = t12[:, :rows[3], :cols[3], :]
      # for 64x64 images, this is 32x32 by 64 filters
      t14 = tf.layers.batch_normalization(t13, axis=-1)
      t15 = tf.nn.elu(t14)

      t16 = tf.layers.conv2d_transpose(t15, self.img_shape[2], 5, strides=2)
      self.logits = t16[:, :self.img_shape[0], :self.img_shape[1], :]
      # for 64x64 rgb images, this is 64x64 by 3 channels

      t17 = tf.sigmoid(self.logits)

    return t17



