import random
from typing import Callable, Tuple, List, Optional
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow import keras

from pyrep.logger import LOGGER


class Layer:
    def __init__(
        self,
        activation: Callable[[np.array], np.array],
        shape: Tuple[int, int],
        derivative: Optional[Callable[[np.array], np.array]] = None,
    ):
        if (
            activation not in [Layer.sigmoid, Layer.relu, Layer.tanh, Layer.identity]
            and derivative is None
        ):
            raise ValueError("Invalid activation function")
        self.activation = activation
        self.derivative = derivative or getattr(
            Layer, f"{activation.__name__}_derivative"
        )
        self.shape = shape
        self.weights = np.random.randn(*shape) / np.sqrt(shape[0])
        self.biases = np.random.randn(shape[1])

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def sigmoid_derivative(x):
        return x * (1 - x)

    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    @staticmethod
    def relu_derivative(x):
        return np.where(x > 0, 1, 0)

    @staticmethod
    def tanh(x):
        return np.tanh(x)

    @staticmethod
    def tanh_derivative(x):
        return 1 - np.tanh(x) ** 2

    @staticmethod
    def identity(x):
        return x

    @staticmethod
    def identity_derivative(x):
        return 1

    @staticmethod
    def softmax(x):
        exps = np.exp(x - np.max(x))
        return exps / np.sum(exps, axis=0)

    @staticmethod
    def softmax_derivative(x):
        return Layer.softmax(x) * (1 - Layer.softmax(x))

    def forward(self, x):
        return self.activation(np.dot(np.atleast_2d(x), self.weights) + self.biases)

    def backward(
        self, x: np.array, error: np.array, output: np.array, learning_rate: float = 0.1
    ):
        delta = error * self.derivative(output)
        self.weights -= learning_rate * np.dot(np.atleast_2d(x).T, delta)
        self.biases -= learning_rate * np.sum(delta, axis=0)
        return delta


class NeuralNetwork:
    def __init__(
        self,
        layers: List[Layer],
        loss: Callable[[np.array, np.array], np.array],
        derivative: Optional[Callable[[np.array, np.array], np.array]] = None,
    ):
        if (
            loss
            not in [
                NeuralNetwork.mean_squared_error,
                NeuralNetwork.cross_entropy,
                NeuralNetwork.binary_cross_entropy,
            ]
            and derivative is None
        ):
            raise ValueError("Invalid loss function")
        self.loss = loss
        self.derivative = derivative or getattr(
            NeuralNetwork, f"{loss.__name__}_derivative"
        )
        self.layers = layers
        self.outputs = list()

    @staticmethod
    def mean_squared_error(y_true, y_pred):
        return np.mean((y_pred - y_true) ** 2)

    @staticmethod
    def mean_squared_error_derivative(y_true, y_pred):
        return y_pred - y_true

    @staticmethod
    def cross_entropy(y_true, y_pred):
        return -np.sum(y_true * np.log(y_pred))

    @staticmethod
    def cross_entropy_derivative(y_true, y_pred):
        return y_pred - y_true

    @staticmethod
    def binary_cross_entropy(y_true, y_pred):
        return -np.sum(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))

    @staticmethod
    def binary_cross_entropy_derivative(y_true, y_pred):
        return (y_pred - y_true) / (y_pred * (1 - y_pred))

    def forward(self, x):
        self.outputs = [x]
        for layer in self.layers:
            x = layer.forward(x)
            self.outputs.append(x)
        return x

    def backward(self, x, y, learning_rate):
        output = self.forward(x)
        error = self.derivative(y, output)
        for layer, output, input_ in zip(
            reversed(self.layers),
            reversed(self.outputs[1:]),
            reversed(self.outputs[:-1]),
        ):
            error = layer.backward(input_, error, output, learning_rate)

    def predict(self, x):
        return self.forward(x)

    def fit(
        self,
        x_train,
        y_train,
        epochs: int = 1000,
        batch_size: int = 100,
        learning_rate: float = 0.1,
        display: int = 100,
    ):
        for epoch in range(1, epochs + 1):
            loss = 0
            sample = zip(x_train, y_train)
            if batch_size < len(x_train):
                sample = random.sample(list(sample), k=batch_size)
            for x, y in sample:
                self.backward(x, y, learning_rate)
                if epoch % display == 0:
                    loss += self.loss(y, self.predict(x))
            if epoch % display == 0:
                LOGGER.info(f"Epoch {epoch}: loss {loss / len(x_train)}")

    def train(self, *args, **kwargs):
        self.fit(*args, **kwargs)

    def evaluate(self, x_test, y_test):
        return np.mean([self.loss(y, self.predict(x)) for x, y in zip(x_test, y_test)])


class AutoEncoder(NeuralNetwork):
    def __init__(
        self, n, encoder_activation=Layer.tanh, decoder_activation=Layer.identity
    ):
        self.n = n
        self.encoder = Layer(encoder_activation, (2 * n, n))
        self.decoder = Layer(decoder_activation, (n, 2 * n))
        super().__init__(
            [self.encoder, self.decoder], AutoEncoder.loss, AutoEncoder.loss_derivative
        )

    @staticmethod
    def loss(y_true, y_pred):
        x_l, x_r = np.split(y_true, 2)
        x_l_pred, x_r_pred = np.split(y_pred, 2)
        return np.linalg.norm(x_l - x_l_pred) ** 2 + np.linalg.norm(x_r - x_r_pred) ** 2

    @staticmethod
    def loss_derivative(y_true, y_pred):
        return y_pred - y_true

    def encode(self, x_l, x_r):
        return self.encoder.forward(np.concatenate([x_l, x_r]))

    def decode(self, x):
        return np.split(self.decoder.forward(x).reshape(-1), 2)


class DeepRepairAutoEncoder:
    def __init__(self, n):
        self.n = n
        self.encoder_layer = keras.layers.Dense(n, activation="tanh")
        self.decoder_layer = keras.layers.Dense(2 * n, activation="linear")
        self.encoder = keras.Sequential([keras.Input((2 * n,)), self.encoder_layer])
        self.decoder = keras.Sequential([keras.Input((n,)), self.decoder_layer])
        self.loss = keras.losses.MeanSquaredError()
        self.model = keras.Sequential(
            [keras.Input((2 * n,)), self.encoder_layer, self.decoder_layer]
        )
        self.model.compile(loss=self.loss)
        self.encoder.compile(loss=self.loss)
        self.decoder.compile(loss=self.loss)

    def encode(self, x_l, x_r):
        return self.encoder.predict(np.array([np.concatenate([x_l, x_r])]))

    def decode(self, x):
        return np.split(self.decoder.predict(x)[0], 2)

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def function_factory(self, x_train):
        shapes = tf.shape_n(self.model.trainable_variables)
        n_tensors = len(shapes)

        count = 0
        idx = list()
        part = list()

        for i, shape in enumerate(shapes):
            n = np.prod(shape)
            idx.append(tf.reshape(tf.range(count, count + n, dtype=tf.int32), shape))
            part.extend([i] * n)
            count += n

        part = tf.constant(part)

        @tf.function
        def assign_new_model_parameters(params_1d):
            params = tf.dynamic_partition(params_1d, part, n_tensors)
            for i, (shape, param) in enumerate(zip(shapes, params)):
                self.model.trainable_variables[i].assign(tf.reshape(param, shape))

        @tf.function
        def f(params_1d):
            with tf.GradientTape() as tape:
                assign_new_model_parameters(params_1d)
                loss_value = self.loss(self.model(x_train, training=True), x_train)
            grads = tape.gradient(loss_value, self.model.trainable_variables)
            grads = tf.dynamic_stitch(idx, grads)
            f.iter.assign_add(1)
            tf.print("Iter:", f.iter, "loss:", loss_value)
            tf.py_function(f.history.append, inp=[loss_value], Tout=[])
            return loss_value, grads

        f.iter = tf.Variable(0)
        f.idx = idx
        f.part = part
        f.shapes = shapes
        f.assign_new_model_parameters = assign_new_model_parameters
        f.history = []

        return f

    def train(self, x, epochs=50):
        x_train = []
        for data_1 in x:
            for data_2 in x:
                x_train.append(np.concatenate([data_1, data_2]))
        func = self.function_factory(np.array(x_train))
        init_params = tf.dynamic_stitch(func.idx, self.model.trainable_variables)
        results = tfp.optimizer.lbfgs_minimize(
            func,
            initial_position=init_params,
            max_iterations=epochs,
        )
        func.assign_new_model_parameters(results.position)
