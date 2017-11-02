import tensorflow as tf

# he initialization for dense layers
he_init = tf.contrib.layers.variance_scaling_initializer

def conv2d(inputs, filters):
  return tf.layers.conv2d(inputs, filters, 5, strides=2, padding='same')

# conv2d transpose
def conv2dtr(inputs, filters):
  return tf.layers.conv2d_transpose(inputs, filters, 5, strides=2, padding='same')

def dense(inputs, units):
  return tf.layers.dense(inputs, units, kernel_initializer=he_init())

# batch normalization
class bn:
  def __init__(self, is_training):
    self.is_training = is_training

  def __call__(self, inputs):
    return tf.contrib.layers.batch_norm(inputs, updates_collections=None, is_training=self.is_training)