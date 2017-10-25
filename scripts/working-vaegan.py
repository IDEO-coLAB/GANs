img_directory = '/home/ec2-user/img_align_celeba'
model_save_directory = '/home/ec2-user/vaegan-celeba.ckpt'
log_directory = '/home/ec2-user/tf-log'
img_save_directory = '/home/ec2-user/vaegan-celeba-out'
batch_size = 64
training_set_size = 2048
img_size = 128
zsize = 128

import sys
sys.path.append('/home/ec2-user/autoencoder-vaegan')
sys.stdout.flush()

import numpy as np
import scipy as sp
import os
from utils import imshow, resize_crop, load_img

print('loading and resizing training data')
print(img_directory)

# load training data
training = np.array([resize_crop(load_img(i+1, img_directory), (img_size, img_size)) for i in range(training_set_size)])

# create models

import tensorflow as tf
from autoencoder import Autoencoder
from discriminator import Discriminator

tf.reset_default_graph()

print('building graph')

# input images feed
X = tf.placeholder(tf.float32, [None, img_size, img_size, 3])

# for feeding random draws of z (latent variable)
Z = tf.placeholder(tf.float32, [None, zsize])

# encoder, decoder that will be connected to a discriminator
vae = Autoencoder(img_shape=(img_size, img_size, 3), zsize=zsize)
encoder = vae.encoder(X)
decoder = vae.decoder(encoder)

# a second decoder for decoding samplings of z
decoder_z_obj = Autoencoder(img_shape=(img_size, img_size, 3), zsize=zsize)
decoder_z = decoder_z_obj.decoder(Z, reuse=True)

# discriminator attached to vae output
disc_vae_obj = Discriminator(img_shape=(img_size, img_size, 3))
disc_vae_obj.disc(decoder)
disc_vae_logits = disc_vae_obj.logits

# discriminator attached to X input
# shares weights with other discriminator
disc_x_obj = Discriminator(img_shape=(img_size, img_size, 3))
disc_x_obj.disc(X, reuse=True)
disc_x_logits = disc_x_obj.logits

# discriminator attached to random Zs passed through decoder
# shares weights with other discriminator
disc_z_obj = Discriminator(img_shape=(img_size, img_size, 3))
disc_z_obj.disc(decoder_z, reuse=True)
disc_z_logits = disc_z_obj.logits


print('building losses')
# Loss functions and optimizers

learning_rate = 0.0001

# set up loss functions and training_ops

# latent loss used for training encoder
latent_loss = vae.latent_loss()

# loss that uses decoder to determine similarity between
# actual input images and output images from the vae
similarity_xentropy = tf.nn.sigmoid_cross_entropy_with_logits(
    labels=disc_x_obj.similarity, 
    logits=disc_vae_obj.similarity)
similarity_loss = tf.reduce_sum(similarity_xentropy)

# losses for the discriminator's output. Labes are real: 0, fake: 1.
# cross entropy with 1 labes, since training prob that image is fake
disc_vae_loss = tf.reduce_sum(tf.nn.sigmoid_cross_entropy_with_logits(
    labels=tf.ones_like(disc_vae_logits),
    logits=disc_vae_logits))

# cross entropy with 0 labes, since training prob that image is fake
disc_x_loss = tf.reduce_sum(tf.nn.sigmoid_cross_entropy_with_logits(
    labels=tf.zeros_like(disc_x_logits),
    logits=disc_x_logits))

# cross entropy with 1 labes, since training prob that image is fake
disc_z_loss = tf.reduce_sum(tf.nn.sigmoid_cross_entropy_with_logits(
    labels=tf.ones_like(disc_z_logits),
    logits=disc_z_logits))

# how to weight decoder reconstruction vs fooling discriminator
gamma = 0.001
# minimize these with optimizer
disc_loss = disc_vae_loss + disc_x_loss + disc_z_loss
encoder_loss = latent_loss + similarity_loss
decoder_loss = gamma * similarity_loss - disc_loss

# get weights to train for each of encoder, decoder, etc.
# pass this to optimizer so it only trains w.r.t the network
# we want to train and just uses other parts of the network as is
# (for example use the discriminator to compute a loss during training
# of the encoder, but don't adjust weights of the discriminator)

encoder_vars = [i for i in tf.trainable_variables() if 'encoder' in i.name]
decoder_vars = [i for i in tf.trainable_variables() if 'decoder' in i.name]
disc_vars = [i for i in tf.trainable_variables() if 'discriminator' in i.name]

train_encoder = tf.train.AdamOptimizer(learning_rate=learning_rate)     .minimize(encoder_loss, var_list=encoder_vars)
    
train_decoder = tf.train.AdamOptimizer(learning_rate=learning_rate)     .minimize(decoder_loss, var_list=decoder_vars)
    
train_disc = tf.train.AdamOptimizer(learning_rate=learning_rate)     .minimize(disc_loss, var_list=disc_vars)

saver = tf.train.Saver()

# create summary nodes
disc_loss_summary = tf.summary.scalar('disc loss', disc_loss)
encoder_loss_summary = tf.summary.scalar('encoder loss', encoder_loss)
decoder_loss_summary = tf.summary.scalar('decoder loss', decoder_loss)
merged_summary = tf.summary.merge_all()

sess = tf.InteractiveSession()
try:
    print("trying to restore session at %s" % model_save_directory)
    saver.restore(sess, model_save_directory)
except:
    print("could't restore model, creating new session")
    tf.global_variables_initializer().run()

writer = tf.summary.FileWriter(log_directory, sess.graph)

# Train

print('training')

import math
batches = int(float(training_set_size) / batch_size)
epochs = 1000000

for epoch in range(epochs):
    print ('epoch %s ' % epoch, end='', flush=True)
    zdraws = np.random.normal(size=(training_set_size, zsize))
    
    # train discriminator
    for batch in range(batches):
        xfeed = training[batch*batch_size:(batch+1)*batch_size]
        zfeed = zdraws[batch*batch_size:(batch+1)*batch_size]
        sess.run(train_disc, feed_dict={X: xfeed, Z: zfeed})
        print('.', end='', flush=True)
         
    # train encoder
    for batch in range(batches):
        xfeed = training[batch*batch_size:(batch+1)*batch_size]
        sess.run(train_encoder, feed_dict={X: xfeed})
        print('.', end='', flush=True)
        
    # train decoder
    for batch in range(batches):
        xfeed = training[batch*batch_size:(batch+1)*batch_size]
        zfeed = zdraws[batch*batch_size:(batch+1)*batch_size]
        sess.run(train_decoder, feed_dict={X: xfeed, Z: zfeed})
        print('.', end='', flush=True)
    
    if (epoch % 1 == 0):
            # report loss on the first batch
        xfeed = training[:batch_size]
        zfeed = zdraws[:batch_size]
        summary = merged_summary.eval(feed_dict={X: xfeed, Z: zfeed})
        writer.add_summary(summary, epoch) 

        example = decoder.eval(feed_dict={X: training[:1]})
        img_save_path = os.path.join(img_save_directory, '%06d.jpg' % epoch)
        sp.misc.imsave(img_save_path, example[0])

        print('saving session', flush=True)
        saver.save(sess, model_save_directory)
