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

        nn.fit(x, y, epochs=10000, learning_rate=0.5)

        for data, label in zip(x, y):
            self.assertAlmostEqual(nn.predict(data)[0], label, delta=0.1)

    def test_deep_repair_encoder(self):
        random.seed(0)
        encoder = DeepRepairAutoEncoder(2)
        x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        encoder.train(x, epochs=50)
        for data_1 in x:
            for data_2 in x:
                close = np.isclose(
                    np.array([data_1, data_2]),
                    encoder.decode(encoder.encode(data_1, data_2)),
                    atol=0.7,
                )
                self.assertTrue(close.all())
        encoding = encoder.recursive_encode(
            [[0, 0], [0, 1], [1, 0], [1, 1], [1, 0], [1, 1]]
        )
