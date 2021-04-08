import unittest
from model_cfwgan import MLPTower, RepeatMLP
import torch
import numpy as np

class MyTestCase(unittest.TestCase):
    def test_mlpTower(self):
        model = MLPTower(16, 2, 3)
        out = model(torch.tensor(np.random.rand(5,16), dtype=torch.float))
        self.assertEqual(out.shape, (5, 2))
        l = [(x.in_features, x.out_features) for x in model.sequential if isinstance(x, torch.nn.Linear)]
        self.assertEqual(l, [(16, 8), (8, 4), (4,2), (2, 2)])

    def test_repeatMLP(self):
        model = RepeatMLP(16, 8, 12, 3)
        out = model(torch.tensor(np.random.rand(5, 16), dtype=torch.float))
        self.assertEqual(out.shape, (5, 8))
        l = [(x.in_features, x.out_features) for x in model.sequential if isinstance(x, torch.nn.Linear)]
        self.assertEqual(l, [(16, 12), (12, 12), (12, 12), (12, 8)])


if __name__ == '__main__':
    unittest.main()
