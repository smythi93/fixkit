import random
from typing import Callable, Tuple, List, Optional
import numpy as np
import scipy

from pyrep.logger import LOGGER


class Layer:
    def __init__(
        self,
        activation: Callable[[np.array], np.array],
        shape: Tuple[int, int],
        derivative: Optional[Callable[[np.array], np.array]] = None,
    ):
        if (
            activation not in [Layer.sigmoid, Layer.relu, Layer.tanh, Layer.linear]
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
    def linear(x):
        return x

    # noinspection PyUnusedLocal
    @staticmethod
    def linear_derivative(x):
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

    def get_grads(
        self,
        x: np.array,
        error: np.array,
        output: np.array,
    ):
        delta = error * self.derivative(output)
        return (
            np.dot(delta, self.weights.T),
            np.dot(np.atleast_2d(x).T, delta),
            np.sum(delta, axis=0),
        )

    def backward(
        self, x: np.array, error: np.array, output: np.array, learning_rate: float = 0.1
    ):
        delta, d_w, d_b = self.get_grads(x, error, output)
        self.weights -= learning_rate * d_w
        self.biases -= learning_rate * d_b
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
        self, n, encoder_activation=Layer.tanh, decoder_activation=Layer.linear
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
        x_l_pred, x_r_pred = np.split(y_pred.flatten(), 2)
        return np.linalg.norm(x_l - x_l_pred) ** 2 + np.linalg.norm(x_r - x_r_pred) ** 2

    def loss_derivative(self, y_true, y_pred):
        loss_derivative = 2 * (y_pred - y_true)
        decoder_d, decoder_dw, decoder_db = self.decoder.get_grads(
            self.outputs[1], loss_derivative, self.outputs[2]
        )
        _, encoder_dw, encoder_db = self.encoder.get_grads(
            self.outputs[0], decoder_d, self.outputs[1]
        )
        return np.concatenate(
            [encoder_dw.flatten(), decoder_dw.flatten(), encoder_db, decoder_db]
        )

    def encode(self, x_l, x_r):
        return self.encoder.forward(np.concatenate([x_l, x_r]))

    def decode(self, x):
        return np.split(self.decoder.forward(x).reshape(-1), 2)


class DeepRepairAutoEncoder(AutoEncoder):
    def __init__(self, n):
        super().__init__(
            n, encoder_activation=Layer.tanh, decoder_activation=Layer.linear
        )
        self.n = n

    def encode(self, x_l, x_r):
        return self.encoder.forward(np.array([np.concatenate([x_l, x_r])]))

    def decode(self, x):
        return np.split(self.decoder.forward(x)[0], 2)

    def flatten(self):
        return np.concatenate(
            [
                self.encoder.weights.flatten(),
                self.decoder.weights.flatten(),
                self.encoder.biases.flatten(),
                self.decoder.biases.flatten(),
            ]
        )

    def reconstruct(self, flat: np.array):
        size = 2 * self.n**2
        self.encoder.weights = flat[:size].reshape((2 * self.n, self.n))
        self.decoder.weights = flat[size : 2 * size].reshape((self.n, 2 * self.n))
        self.encoder.biases = flat[2 * size : 2 * size + self.n]
        self.decoder.biases = flat[2 * size + self.n :]

    def optimize_loss(self, flat: np.array, x_train: np.array):
        self.reconstruct(flat)
        loss = 0
        for x in x_train:
            loss += self.loss(x, self.predict(x))
        return loss // len(x_train)

    def optimize_loss_derivative(self, flat: np.array, x_train: np.array):
        self.reconstruct(flat)
        loss = np.zeros_like(flat)
        for x in x_train:
            loss += self.loss_derivative(x, self.predict(x))
        return loss // len(x_train)

    def train(self, x, epochs=50, display=10):
        x_train = []
        for data_1 in x:
            for data_2 in x:
                x_train.append(np.concatenate([data_1, data_2]))
        result, f, _ = scipy.optimize.fmin_l_bfgs_b(
            self.optimize_loss,
            self.flatten(),
            fprime=self.optimize_loss_derivative,
            args=(x_train,),
            maxiter=epochs,
            disp=display,
        )
        self.reconstruct(result)

    def recursive_encode(self, embeddings: List[np.array]) -> List[np.array]:
        if len(embeddings) > 1:
            embeddings_ = list()
            errors = list()
            for i in range(0, len(embeddings), 2):
                embeddings_.append(self.encode(embeddings[i], embeddings[i + 1])[0])
                errors.append(
                    self.loss(
                        np.concatenate([embeddings[i], embeddings[i + 1]]),
                        np.concatenate(self.decode(embeddings_[i // 2])),
                    )
                )
            if len(embeddings) % 2 == 1:
                embeddings_.append(embeddings[-1])
                errors.append(0)
            embeddings = embeddings_

            while len(embeddings) > 1:
                min_error = float("inf")
                best_position = -1
                for i in range(len(embeddings) - 1):
                    error = sum(errors[i : i + 1]) / 2
                    if error < min_error:
                        min_error = error
                        best_position = i
                embedding = self.encode(
                    embeddings[best_position], embeddings[best_position + 1]
                )[0]
                error = self.loss(
                    np.concatenate(
                        [embeddings[best_position], embeddings[best_position + 1]]
                    ),
                    np.concatenate(self.decode(embedding)),
                )
                embeddings = (
                    embeddings[:best_position]
                    + [embedding]
                    + embeddings[best_position + 2 :]
                )
                errors = errors[:best_position] + [error] + errors[best_position + 2 :]

        return embeddings[0]
