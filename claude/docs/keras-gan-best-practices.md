# Keras Framework: GANs and Best Practices Guide

## Table of Contents
1. [Introduction to Keras and GANs](#introduction)
2. [GAN Architecture Fundamentals](#gan-architecture)
3. [Implementing GANs in Keras](#implementing-gans)
4. [Training Best Practices](#training-best-practices)
5. [Callbacks and Monitoring](#callbacks-and-monitoring)
6. [Hyperparameter Tuning](#hyperparameter-tuning)
7. [Advanced Techniques](#advanced-techniques)
8. [Common Pitfalls and Solutions](#common-pitfalls)

---

## Introduction to Keras and GANs

### What is Keras?
Keras is a high-level deep learning API that provides an intuitive interface for building and training neural networks across various domains including computer vision, NLP, and time series data. It supports TensorFlow as its backend and emphasizes:
- **Ease of use**: Simple, consistent APIs
- **Modularity**: Building blocks that can be easily combined
- **Extensibility**: Custom layers, losses, and training loops

### Generative Adversarial Networks (GANs)
GANs consist of two neural networks trained in opposition:
- **Generator**: Creates synthetic data from random noise
- **Discriminator**: Distinguishes real data from generated data

### Available GAN Implementations in Keras
- [DCGAN](https://keras.io/examples/generative/dcgan_overriding_train_step) - Deep Convolutional GAN
- [StyleGAN](https://keras.io/examples/generative/stylegan) - High-quality image synthesis
- [Conditional GAN](https://keras.io/examples/generative/conditional_gan) - Class-conditioned generation
- [CycleGAN](https://keras.io/examples/generative/cyclegan) - Unpaired image-to-image translation
- [Data-efficient GANs](https://keras.io/examples/generative/gan_ada) - Training with limited data
- [GauGAN](https://keras.io/examples/generative/gaugan) - Semantic image synthesis

---

## GAN Architecture Fundamentals

### Generator Network Architecture

The generator transforms random noise into realistic samples. A typical DCGAN generator structure:

```python
import keras
from keras import layers

def get_generator(noise_size=64, width=128, depth=4):
    """
    DCGAN generator architecture
    Args:
        noise_size: Dimension of input noise vector
        width: Base number of filters
        depth: Number of upsampling layers
    """
    noise_input = keras.Input(shape=(noise_size,))

    # Initial dense layer to create spatial dimensions
    x = layers.Dense(4 * 4 * width, use_bias=False)(noise_input)
    x = layers.BatchNormalization(scale=False)(x)
    x = layers.ReLU()(x)
    x = layers.Reshape(target_shape=(4, 4, width))(x)

    # Progressive upsampling with transposed convolutions
    for _ in range(depth - 1):
        x = layers.Conv2DTranspose(
            width,
            kernel_size=4,
            strides=2,
            padding="same",
            use_bias=False,
        )(x)
        x = layers.BatchNormalization(scale=False)(x)
        x = layers.ReLU()(x)

    # Final layer to produce RGB image
    image_output = layers.Conv2DTranspose(
        3,
        kernel_size=4,
        strides=2,
        padding="same",
        activation="sigmoid",
    )(x)

    return keras.Model(noise_input, image_output, name="generator")
```

**Key Design Principles:**
- Use BatchNormalization (without bias in preceding layers)
- ReLU activation in generator, except output layer
- Sigmoid or Tanh for final activation (depends on data normalization)
- Transposed convolutions for upsampling

### Discriminator Network Architecture

The discriminator classifies images as real or fake:

```python
from tensorflow import keras
from tensorflow.keras import layers

def get_discriminator(image_size=64, width=128, depth=4,
                     leaky_relu_slope=0.2, dropout_rate=0.4):
    """
    DCGAN discriminator architecture
    Args:
        image_size: Input image resolution
        width: Base number of filters
        depth: Number of downsampling layers
        leaky_relu_slope: Negative slope for LeakyReLU
        dropout_rate: Dropout probability for regularization
    """
    discriminator = keras.Sequential([
        keras.Input(shape=(image_size, image_size, 3)),
        layers.Conv2D(width, kernel_size=3, strides=2, padding="same"),
        layers.LeakyReLU(negative_slope=leaky_relu_slope),
        layers.Dropout(dropout_rate),
    ], name="discriminator")

    # Progressive downsampling
    for i in range(depth - 1):
        discriminator.add(
            layers.Conv2D(width * (2 ** (i + 1)),
                         kernel_size=3,
                         strides=2,
                         padding="same")
        )
        discriminator.add(layers.LeakyReLU(negative_slope=leaky_relu_slope))
        discriminator.add(layers.Dropout(dropout_rate))

    discriminator.add(layers.GlobalMaxPooling2D())
    discriminator.add(layers.Dense(1))

    return discriminator
```

**Key Design Principles:**
- LeakyReLU activation (typically slope=0.2)
- Dropout for regularization (0.3-0.5)
- No BatchNormalization in discriminator's first layer
- Strided convolutions for downsampling (avoid pooling)

---

## Implementing GANs in Keras

### Custom Training Loop Implementation

Keras allows you to override the `train_step` method for full control over GAN training:

```python
class GAN(keras.Model):
    def __init__(self, discriminator, generator, latent_dim):
        super().__init__()
        self.discriminator = discriminator
        self.generator = generator
        self.latent_dim = latent_dim
        self.seed_generator = keras.random.SeedGenerator(1337)

    def compile(self, d_optimizer, g_optimizer, loss_fn):
        super().compile()
        self.d_optimizer = d_optimizer
        self.g_optimizer = g_optimizer
        self.loss_fn = loss_fn
        self.d_loss_metric = keras.metrics.Mean(name="d_loss")
        self.g_loss_metric = keras.metrics.Mean(name="g_loss")

    @property
    def metrics(self):
        return [self.d_loss_metric, self.g_loss_metric]

    def train_step(self, real_images):
        batch_size = ops.shape(real_images)[0]

        # Generate random latent vectors
        random_latent_vectors = keras.random.normal(
            shape=(batch_size, self.latent_dim),
            seed=self.seed_generator
        )

        # Generate fake images
        generated_images = self.generator(random_latent_vectors)

        # Combine real and fake images
        combined_images = ops.concatenate([generated_images, real_images], axis=0)

        # Create labels (1 for real, 0 for fake)
        labels = ops.concatenate(
            [ops.ones((batch_size, 1)), ops.zeros((batch_size, 1))], axis=0
        )

        # IMPORTANT: Add noise to labels (improves training stability)
        labels += 0.05 * tf.random.uniform(tf.shape(labels))

        # Train discriminator
        with tf.GradientTape() as tape:
            predictions = self.discriminator(combined_images)
            d_loss = self.loss_fn(labels, predictions)

        grads = tape.gradient(d_loss, self.discriminator.trainable_weights)
        self.d_optimizer.apply_gradients(
            zip(grads, self.discriminator.trainable_weights)
        )

        # Train generator
        random_latent_vectors = keras.random.normal(
            shape=(batch_size, self.latent_dim),
            seed=self.seed_generator
        )

        # Create "all real" labels for generator training
        misleading_labels = ops.zeros((batch_size, 1))

        with tf.GradientTape() as tape:
            predictions = self.discriminator(self.generator(random_latent_vectors))
            g_loss = self.loss_fn(misleading_labels, predictions)

        grads = tape.gradient(g_loss, self.generator.trainable_weights)
        self.g_optimizer.apply_gradients(
            zip(grads, self.generator.trainable_weights)
        )

        # Update metrics
        self.d_loss_metric.update_state(d_loss)
        self.g_loss_metric.update_state(g_loss)

        return {
            "d_loss": self.d_loss_metric.result(),
            "g_loss": self.g_loss_metric.result(),
        }
```

### Alternative: Using @tf.function for Performance

For better performance, wrap the training step in `@tf.function`:

```python
@tf.function
def train_step(real_images):
    batch_size = tf.shape(real_images)[0]
    random_latent_vectors = tf.random.normal(shape=(batch_size, latent_dim))
    generated_images = generator(random_latent_vectors)
    combined_images = tf.concat([generated_images, real_images], axis=0)

    labels = tf.concat(
        [tf.ones((batch_size, 1)), tf.zeros((batch_size, 1))], axis=0
    )
    labels += 0.05 * tf.random.uniform(labels.shape)

    # Discriminator training
    with tf.GradientTape() as tape:
        predictions = discriminator(combined_images)
        d_loss = loss_fn(labels, predictions)
    grads = tape.gradient(d_loss, discriminator.trainable_weights)
    d_optimizer.apply(grads, discriminator.trainable_weights)

    # Generator training
    random_latent_vectors = tf.random.normal(shape=(batch_size, latent_dim))
    misleading_labels = tf.zeros((batch_size, 1))

    with tf.GradientTape() as tape:
        predictions = discriminator(generator(random_latent_vectors))
        g_loss = loss_fn(misleading_labels, predictions)
    grads = tape.gradient(g_loss, generator.trainable_weights)
    g_optimizer.apply(grads, generator.trainable_weights)

    return d_loss, g_loss, generated_images
```

---

## Training Best Practices

### 1. Hyperparameter Configuration

```python
# Data parameters
num_epochs = 100  # Start with 100, increase to 400+ for production
image_size = 64   # Common sizes: 64, 128, 256
batch_size = 128  # Larger is better for stability (32-256)
padding = 0.25

# Architecture parameters
noise_size = 64    # Latent dimension (64-512)
depth = 4          # Network depth
width = 128        # Base filter count
leaky_relu_slope = 0.2
dropout_rate = 0.4

# Optimization parameters
learning_rate = 2e-4  # Standard DCGAN learning rate
beta_1 = 0.5          # NOT 0.9! Important for GAN training
ema = 0.99           # Exponential moving average coefficient
```

### 2. Optimizer Setup

**Critical Best Practice:** Use the same learning rate for both networks initially:

```python
from tensorflow.keras.optimizers import Adam

# Recommended: Same learning rate for both (DCGAN standard)
generator_optimizer = Adam(learning_rate=2e-4, beta_1=0.5)
discriminator_optimizer = Adam(learning_rate=2e-4, beta_1=0.5)

# Advanced: Different learning rates (if you have sufficient resources)
# Lower generator LR can sometimes improve stability
# generator_optimizer = Adam(learning_rate=1e-4, beta_1=0.5)
# discriminator_optimizer = Adam(learning_rate=2e-4, beta_1=0.5)
```

**Key Points:**
- `beta_1=0.5` is crucial (default 0.9 often fails for GANs)
- `learning_rate=2e-4` is the DCGAN standard
- Start with equal learning rates, adjust only if needed

### 3. Loss Functions

**Binary Cross-Entropy (Most Common):**
```python
loss_fn = keras.losses.BinaryCrossentropy(from_logits=True)
```

**Wasserstein Loss (for WGAN):**
```python
def wasserstein_loss(y_true, y_pred):
    return -tf.reduce_mean(y_true * y_pred)
```

### 4. Label Smoothing and Noise

**One-sided label smoothing** improves stability:

```python
# Instead of perfect 0s and 1s
real_labels = tf.ones((batch_size, 1)) * 0.9  # Smooth to 0.9
fake_labels = tf.zeros((batch_size, 1))

# Add random noise to labels
labels += 0.05 * tf.random.uniform(tf.shape(labels))
```

### 5. Data Preprocessing

```python
def preprocess_images(images):
    """Normalize images to [-1, 1] or [0, 1] based on generator output"""
    images = tf.cast(images, tf.float32)
    # For tanh activation in generator
    images = (images - 127.5) / 127.5  # Scale to [-1, 1]
    # OR for sigmoid activation
    # images = images / 255.0  # Scale to [0, 1]
    return images
```

### 6. Training Loop Best Practices

```python
# Compile and train
gan = GAN(discriminator=discriminator, generator=generator, latent_dim=latent_dim)
gan.compile(
    d_optimizer=keras.optimizers.Adam(learning_rate=2e-4, beta_1=0.5),
    g_optimizer=keras.optimizers.Adam(learning_rate=2e-4, beta_1=0.5),
    loss_fn=keras.losses.BinaryCrossentropy(from_logits=True),
)

# Use callbacks for monitoring and checkpointing
history = gan.fit(
    train_dataset,
    epochs=num_epochs,
    callbacks=[checkpoint_callback, image_callback]
)
```

---

## Callbacks and Monitoring

### 1. Model Checkpointing

**Save Best Model Based on Metrics:**

```python
checkpoint_callback = keras.callbacks.ModelCheckpoint(
    filepath="gan_model.weights.h5",
    save_weights_only=True,
    monitor="val_kid",  # Kernel Inception Distance
    mode="min",
    save_best_only=True,
    verbose=1
)
```

**Epoch-based Checkpointing:**

```python
checkpoint_callback = keras.callbacks.ModelCheckpoint(
    filepath="model_{epoch}.keras",
    save_best_only=False,
    save_freq='epoch'
)
```

### 2. Early Stopping

```python
early_stopping_callback = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True,
    verbose=1
)
```

### 3. Learning Rate Scheduling

**Exponential Decay:**

```python
initial_learning_rate = 2e-4
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate,
    decay_steps=1000,
    decay_rate=0.96,
    staircase=True
)

optimizer = keras.optimizers.Adam(learning_rate=lr_schedule, beta_1=0.5)
```

**Reduce on Plateau:**

```python
reduce_lr_callback = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=1e-7,
    verbose=1
)
```

### 4. Custom Image Generation Callback

```python
class GANMonitor(keras.callbacks.Callback):
    def __init__(self, num_img=3, latent_dim=128):
        self.num_img = num_img
        self.latent_dim = latent_dim

    def on_epoch_end(self, epoch, logs=None):
        random_latent_vectors = tf.random.normal(
            shape=(self.num_img, self.latent_dim)
        )
        generated_images = self.model.generator(random_latent_vectors)
        generated_images *= 255
        generated_images.numpy()

        for i in range(self.num_img):
            img = keras.preprocessing.image.array_to_img(generated_images[i])
            img.save(f"generated_img_{epoch}_{i}.png")

# Use in training
gan.fit(
    dataset,
    epochs=epochs,
    callbacks=[GANMonitor(num_img=10, latent_dim=latent_dim)]
)
```

### 5. TensorBoard Logging

```python
tensorboard_callback = keras.callbacks.TensorBoard(
    log_dir="./logs",
    histogram_freq=1,
    write_graph=True,
    write_images=True,
    update_freq='epoch'
)
```

### 6. CSV Logging

```python
csv_logger = keras.callbacks.CSVLogger(
    'training_log.csv',
    separator=',',
    append=False
)
```

### Complete Callback Setup

```python
callbacks = [
    keras.callbacks.ModelCheckpoint(
        "best_gan.weights.h5",
        save_weights_only=True,
        monitor="val_kid",
        mode="min",
        save_best_only=True
    ),
    keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=15,
        restore_best_weights=True
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='g_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7
    ),
    GANMonitor(num_img=10, latent_dim=latent_dim),
    keras.callbacks.TensorBoard(log_dir="./logs"),
    keras.callbacks.CSVLogger('training.csv')
]

model.fit(train_dataset, epochs=num_epochs, callbacks=callbacks)
```

---

## Hyperparameter Tuning

### Critical Hyperparameters Ranked by Impact

1. **Learning Rate** (Most Critical)
   - Start: 2e-4 (DCGAN standard)
   - Range: 1e-5 to 5e-4
   - Equal for G and D initially

2. **Batch Size**
   - Start: 128
   - Range: 32-256
   - Larger = more stable training

3. **Beta_1 (Adam momentum)**
   - Use: 0.5 (NOT 0.9!)
   - Critical for GAN stability

4. **Architecture Depth and Width**
   - Depth: 4-6 layers
   - Width: 64-256 base filters

5. **Dropout Rate** (Discriminator)
   - Range: 0.3-0.5
   - Higher = more regularization

6. **Label Smoothing**
   - Real labels: 0.9 instead of 1.0
   - Noise: ±0.05

### Adaptive Discriminator Augmentation (ADA)

For training with limited data:

```python
# ADA-specific hyperparameters
max_translation = 0.125
max_rotation = 0.125
max_zoom = 0.25
target_accuracy = 0.85      # Target discriminator accuracy
integration_steps = 1000    # Steps to adjust augmentation
```

### Resolution and Dataset Settings

```python
# Image resolution (power of 2)
image_size = 64  # 64, 128, 256, 512

# Kernel Inception Distance measurement resolution
kid_image_size = 75

# Data augmentation padding
padding = 0.25
```

---

## Advanced Techniques

### 1. Progressive Growing (StyleGAN)

```python
class StyleGAN(tf.keras.Model):
    def grow_model(self, res):
        """Progressively grow model to higher resolution"""
        tf.keras.backend.clear_session()
        res_log2 = log2(res)
        self.generator = self.g_builder.grow(res_log2)
        self.discriminator = self.d_builder.grow(res_log2)
        self.current_res_log2 = res_log2
        print(f"\nModel resolution: {res}x{res}")

    def compile(self, steps_per_epoch, phase, res, d_optimizer, g_optimizer):
        self.steps_per_epoch = steps_per_epoch
        if res != 2 ** self.current_res_log2:
            self.grow_model(res)
        self.phase = phase  # 'TRANSITION' or 'STABLE'
        # ... rest of compilation
```

### 2. Gradient Penalty (WGAN-GP)

```python
def gradient_loss(self, grad):
    """Gradient penalty for WGAN-GP"""
    loss = tf.square(grad)
    loss = tf.reduce_sum(loss, axis=tf.range(1, tf.size(tf.shape(loss))))
    loss = tf.sqrt(loss)
    loss = tf.reduce_mean(tf.square(loss - 1))
    return loss

# In train_step
with tf.GradientTape() as gradient_tape:
    epsilon = tf.random.uniform((batch_size, 1, 1, 1))
    interpolates = epsilon * real_images + (1 - epsilon) * fake_images
    gradient_tape.watch(interpolates)
    pred_interpolates = self.discriminator(interpolates)

gradients = gradient_tape.gradient(pred_interpolates, [interpolates])
gradient_penalty = 10.0 * self.gradient_loss(gradients)
```

### 3. Exponential Moving Average (EMA)

```python
ema = 0.99

# During training
if hasattr(self, 'ema_generator'):
    for ema_weight, weight in zip(
        self.ema_generator.weights,
        self.generator.weights
    ):
        ema_weight.assign(ema * ema_weight + (1 - ema) * weight)
```

### 4. Spectral Normalization

```python
from tensorflow_addons.layers import SpectralNormalization

# Apply to discriminator layers
discriminator = keras.Sequential([
    SpectralNormalization(layers.Conv2D(64, 3, strides=2, padding='same')),
    layers.LeakyReLU(0.2),
    # ... more layers
])
```

### 5. Self-Attention Layers

```python
class SelfAttention(layers.Layer):
    def __init__(self, channels):
        super().__init__()
        self.channels = channels
        self.query = layers.Conv2D(channels // 8, 1)
        self.key = layers.Conv2D(channels // 8, 1)
        self.value = layers.Conv2D(channels, 1)
        self.gamma = tf.Variable(0.0, trainable=True)

    def call(self, x):
        batch, height, width, channels = x.shape

        # Calculate attention
        query = self.query(x)
        query = tf.reshape(query, [batch, -1, channels // 8])

        key = self.key(x)
        key = tf.reshape(key, [batch, -1, channels // 8])

        attention = tf.nn.softmax(tf.matmul(query, key, transpose_b=True))

        value = self.value(x)
        value = tf.reshape(value, [batch, -1, channels])

        out = tf.matmul(attention, value)
        out = tf.reshape(out, [batch, height, width, channels])

        return self.gamma * out + x
```

---

## Common Pitfalls and Solutions

### 1. Mode Collapse

**Symptoms:** Generator produces limited variety of outputs

**Solutions:**
- Use mini-batch discrimination
- Add diversity term to loss
- Try Unrolled GAN
- Use feature matching
- Reduce generator learning rate

```python
# Feature matching loss
def feature_matching_loss(real_features, fake_features):
    return tf.reduce_mean(tf.abs(
        tf.reduce_mean(real_features, axis=0) -
        tf.reduce_mean(fake_features, axis=0)
    ))
```

### 2. Training Instability

**Symptoms:** Loss oscillates wildly, no convergence

**Solutions:**
- Check `beta_1=0.5` (not 0.9!)
- Reduce learning rate
- Add label noise/smoothing
- Use gradient clipping
- Check data normalization

```python
# Gradient clipping
grads = tape.gradient(loss, trainable_weights)
grads = [tf.clip_by_norm(g, 1.0) for g in grads]
optimizer.apply_gradients(zip(grads, trainable_weights))
```

### 3. Discriminator Too Strong

**Symptoms:** Generator loss increases, discriminator accuracy > 95%

**Solutions:**
- Reduce discriminator training frequency
- Add more dropout to discriminator
- Reduce discriminator capacity
- Add noise to discriminator inputs

```python
# Train discriminator less frequently
if step % 2 == 0:  # Train D every other step
    # ... discriminator training
```

### 4. Vanishing Gradients

**Symptoms:** Generator loss stuck, no learning

**Solutions:**
- Use Wasserstein loss instead of BCE
- Add batch normalization
- Use LeakyReLU instead of ReLU
- Check for dead neurons

### 5. Poor Image Quality

**Symptoms:** Blurry or low-quality outputs

**Solutions:**
- Train longer (400+ epochs)
- Increase model capacity
- Improve data quality/diversity
- Use progressive growing
- Add perceptual loss

### 6. Memory Issues

**Solutions:**
```python
# Use mixed precision training
from tensorflow.keras import mixed_precision
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)

# Reduce batch size
batch_size = 32  # Instead of 128

# Enable memory growth
gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
```

---

## Evaluation Metrics

### 1. Kernel Inception Distance (KID)

```python
# Lower is better
# Used in modern GAN papers
# More robust than FID for small datasets
```

### 2. Fréchet Inception Distance (FID)

```python
# Lower is better
# Industry standard
# Requires many samples (>10k)
```

### 3. Inception Score (IS)

```python
# Higher is better
# Measures quality and diversity
# Can be gamed
```

### 4. Visual Inspection

Always manually inspect generated samples at regular intervals!

---

## Quick Start Checklist

- [ ] Set `beta_1=0.5` in Adam optimizer
- [ ] Use `learning_rate=2e-4` for both G and D
- [ ] Add label noise/smoothing
- [ ] Use LeakyReLU in discriminator
- [ ] Use ReLU in generator
- [ ] Add BatchNormalization (generator) and Dropout (discriminator)
- [ ] Normalize images to [-1, 1] or [0, 1]
- [ ] Set up ModelCheckpoint callback
- [ ] Monitor both losses during training
- [ ] Generate sample images every few epochs
- [ ] Start with batch_size=128
- [ ] Train for at least 100 epochs initially

---

## Resources

- [Keras GAN Examples](https://keras.io/examples/generative/)
- [DCGAN Paper](https://arxiv.org/abs/1511.06434)
- [GAN Training Tips](https://github.com/soumith/ganhacks)
- [Keras Documentation](https://keras.io/)

---

## Conclusion

Training GANs requires patience and careful hyperparameter tuning. Start with the DCGAN baseline settings, monitor training closely, and make incremental adjustments. The most critical factors are:

1. **Optimizer settings** (beta_1=0.5, lr=2e-4)
2. **Architecture balance** (similar capacity for G and D)
3. **Regularization** (dropout, label smoothing, batch norm)
4. **Monitoring** (callbacks, visual inspection, metrics)

Remember: GANs are notoriously difficult to train. Don't be discouraged by initial failures. Systematic debugging and following best practices will lead to success.
