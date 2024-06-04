import random
import unittest

import numpy as np

from pyrep.embeddings.encoder import NeuralNetwork, Layer, DeepRepairAutoEncoder


class TestNN(unittest.TestCase):
    def test_nn(self):
        random.seed(0)
        x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        y = np.array([[0], [1], [1], [0]])

        nn = NeuralNetwork(
            [Layer(Layer.sigmoid, (2, 2)), Layer(Layer.sigmoid, (2, 1))],
            NeuralNetwork.mean_squared_error,
        )

        nn.fit(x, y, epochs=5000, learning_rate=0.5)

        for data, label in zip(x, y):
            self.assertAlmostEqual(nn.predict(data)[0], label, delta=0.05)

    def test_deep_repair_encoder(self):
        random.seed(0)
        encoder = DeepRepairAutoEncoder(2)
        x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        encoder.train(x, epochs=50)
        for data_1 in x:
            for data_2 in x:
                array = np.concatenate([data_1, data_2])
                loss = encoder.loss(array, encoder.predict(array))
                self.assertGreaterEqual(10, loss)
        encoding = encoder.recursive_encode(
            [[0, 0], [0, 1], [1, 0], [1, 1], [1, 0], [1, 1]]
        )
        print(encoding)
