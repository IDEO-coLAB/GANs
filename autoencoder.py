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

  def encoder(self, inputs, training, scope='encoder', reuse=None):
    ''' Returns encoder graph. Inputs is a placeholder of size
    (None, rows, cols, channels) '''
     
    with tf.variable_scope(scope, reuse=reuse):
      # 64 filters of 5x5 field with stride 2
      t = tf.layers.conv2d(inputs, 64, 5, strides=2)

      # Batch normalize per channel (per the paper) and channels are last dim.
      # This means find average accross the batch and apply it to the inputs, 
      # but do it separately for each channel. Also note that in the input layer,
      # we call them channels (red, green, blue) but in deeper layers each channel
      # is the output of a convolution filter.
      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)

      t = tf.layers.conv2d(t, 128, 5, strides=2)   
      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)

      t = tf.layers.conv2d(t, 256, 5, strides=2)   
      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)

      t = tf.contrib.layers.flatten(t)
      t = tf.layers.dense(t, 512, kernel_initializer=he_init())
      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)

      # In a variational autoencoder, the encoder outputs a mean and sigma vector
      # from which samples are drawn. In practice, treat the second output as
      # log(sigma**2), but we'll call it logsigma. Each of mean and logsigma are
      # zsize vectors, but here we pack them into a single zsize*2 vector.
      self.means = tf.layers.dense(t, self.zsize, activation=tf.nn.elu, kernel_initializer=he_init())
      self.logsigmas = tf.layers.dense(t, self.zsize, activation=tf.nn.elu, kernel_initializer=he_init())
      # keep means and logsigma for computing variational loss
      sigmas = tf.exp(0.5 * self.logsigmas) # see Hands on machine learning, Geron, p. 435

      sample = tf.random_normal(tf.shape(sigmas), dtype=tf.float32)
    return sample * sigmas + self.means

  def latent_loss(self):
    with tf.variable_scope('latent_loss'):
      loss = 0.5 * tf.reduce_mean(tf.exp(self.logsigmas) + tf.square(self.means) - 1 - self.logsigmas)
    return loss

  def decoder(self, inputs, training, scope='decoder', reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
      # deconvolution mirrors convolution, start with many filters, then
      # shrink down to a base level of filters. This is lowest number of filters
      # before wiring to 3 channel image (rgb).

      t = tf.layers.dense(inputs, 4*4*1024, kernel_initializer=he_init())
      # densely connect z vector to enough units to supply first deconvolution layer.
      # That's rows*cols and at this layer use 8 times the base number of filters.

      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)
      t = tf.reshape(t, (tf.shape(t)[0], 4, 4, 1024))
      # for 64x64 images, this is 4x4 by 512 filters
      
      t = tf.layers.conv2d_transpose(t, 512, 5, strides=2, padding='same')

      # Because of the way the kernel slides accross
      # the input, and b/c we're using stride 2, output is double the input
      # rows/cols plus a few more due to width of kernel. Just crop out extras
      # before moving on.
      # e.g. for input image of size 4x4, with 5x5 kernel and stride of 2, 
      # we get output of 11x11, but want 8x8. Crop off bottom and right of image.

      # crop the whole batch
      # t = t[:, :rows[1], :cols[1], :]
     
      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)

      t = tf.layers.conv2d_transpose(t, 256, 5, strides=2, padding='same')
      #t = t[:, :rows[2], :cols[2], :]
      # for 64x64 images, this is 16x16 by 128 filters
      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)

      t = tf.layers.conv2d_transpose(t, 128, 5, strides=2, padding='same')
      #t = t[:, :rows[3], :cols[3], :]
      # for 64x64 images, this is 32x32 by 64 filters
      t = tf.layers.batch_normalization(t, axis=-1, training=training)
      t = tf.nn.elu(t)

      self.logits = tf.layers.conv2d(t, self.img_shape[2], 5, strides=2, padding='same')
      # for 64x64 rgb images, this is 64x64 by 3 channels

      t = tf.tanh(self.logits)

    return t



