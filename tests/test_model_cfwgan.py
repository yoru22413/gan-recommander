import unittest

import numpy as np
import torch
from torch.utils.data import random_split

from dataset import MovieLensDataset
from model_cfwgan import MLPTower, MLPRepeat, Generator, Discriminator, CFWGAN
import pytorch_lightning as pl


class MyTestCase(unittest.TestCase):
    def test_mlpTower(self):
        model = MLPTower(16, 2, 3)
        out = model(torch.tensor(np.random.rand(5, 16), dtype=torch.float))
        self.assertEqual(out.shape, (5, 2))
        l = [(x.in_features, x.out_features) for x in model.sequential if isinstance(x, torch.nn.Linear)]
        self.assertEqual(l, [(16, 8), (8, 4), (4, 2), (2, 2)])

    def test_repeatMLP(self):
        model = MLPRepeat(16, 8, 12, 3)
        out = model(torch.tensor(np.random.rand(5, 16), dtype=torch.float))
        self.assertEqual(out.shape, (5, 8))
        l = [(x.in_features, x.out_features) for x in model.sequential if isinstance(x, torch.nn.Linear)]
        self.assertEqual(l, [(16, 12), (12, 12), (12, 12), (12, 8)])

    def test_generator(self):
        model = Generator(50)
        x = torch.tensor(np.random.rand(8, 50)).float()
        out = model(x)
        self.assertEqual(out.shape, (8, 50))

    def test_discriminator(self):
        model = Discriminator(50, 3)
        x = torch.tensor(np.random.rand(8, 50)).float()
        out = model(x, x)
        self.assertEqual(out.shape, (8, 1))

    def test_precision_at_n(self):
        items = torch.tensor([[0, 1, 0, 1, 0, 1],
                              [0, 0, 0, 1, 1, 1],
                              [1, 1, 0, 0, 1, 1]])
        items_predicted = torch.tensor([[1.2, -0.1, 2, 1.1, 1.8, 2],
                                        [0.26514016, 0.25176894, 0.41136022, 0.39306909, 0.13250113, 0.84741624],
                                        [0.14425929, 0.2018705, 0.15223548, 0.73594551, 0.76860745, 0.70887101]])
        precision = CFWGAN.precision_at_n(items_predicted, items, n=2)
        self.assertAlmostEqual(precision, (1 / 2 + 1 / 2 + 1 / 2) / 3)
        precision = CFWGAN.precision_at_n(items_predicted, items, n=3)
        self.assertAlmostEqual(precision, (1 / 3 + 2 / 3 + 2 / 3) / 3)

    # def test_precision_at_n_few_pos(self):
    #     items = torch.tensor([[0, 1, 0, 0, 0, 1],
    #                           [0, 0, 0, 1, 0, 1],
    #                           [0, 0, 1, 0, 1, 1]])
    #     items_predicted = torch.tensor([[1.2, 3, 2, 1.1, 1.8, 2.1],
    #                                     [0.26514016, 0.25176894, 0.41136022, 0.39306909, 0.13250113, 0.84741624],
    #                                     [0.14425929, 0.2018705, 0.15223548, 0.73594551, 0.76860745, 0.70887101]])
    #     precision = CFWGAN.precision_at_n(items_predicted, items, n=3)
    #     self.assertAlmostEqual(precision.item(), (2 / 2 + 2 / 2 + 2 / 3) / 3)
    #
    #     items = torch.tensor([[0, 1, 0, 0, 0, 0],
    #                           [0, 0, 0, 0, 0, 0],
    #                           [0, 0, 1, 0, 1, 1]])
    #     items_predicted = torch.tensor([[1.2, 3, 2, 1.1, 1.8, 2.1],
    #                                     [0.26514016, 0.25176894, 0.41136022, 0.39306909, 0.13250113, 0.84741624],
    #                                     [0.14425929, 0.2018705, 0.15223548, 0.73594551, 0.76860745, 0.70887101]])
    #     precision = CFWGAN.precision_at_n(items_predicted, items, n=3)
    #     self.assertAlmostEqual(precision.item(), (1 / 1 + 2 / 3) / 2)

    def test_negative_sampling(self):
        class Test:
            def __init__(self, s_zr=0.6, s_pm=0.6):
                self.s_zr = s_zr
                self.s_pm = s_pm
                self.negative_sampling = CFWGAN.negative_sampling

        test = Test(s_zr=0.6, s_pm=0.6)
        items = torch.tensor([[1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                              [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]])
        zr, pm = test.negative_sampling(test, items)
        for i in range(items.shape[0]):
            self.assertEqual(zr[i].sum(), 3)
            self.assertEqual(pm[i].sum(), 3)
        t = zr + items
        self.assertTrue(((t == 0) | (t == 1)).all())

        t = pm + items
        self.assertTrue(((t == 0) | (t == 1)).all())

        test.s_pm = 0
        test.s_zr = 0

        zr, pm = test.negative_sampling(test, items)
        for i in range(items.shape[0]):
            self.assertEqual(zr[i].sum(), 0)
            self.assertEqual(pm[i].sum(), 0)

        test.s_pm = 1.0
        test.s_zr = 1.0

        zr, pm = test.negative_sampling(test, items)
        for i in range(items.shape[0]):
            self.assertEqual(zr[i].sum(), 5)
            self.assertEqual(pm[i].sum(), 5)

    def test_ndcg(self):
        from math import log2
        items_predicted = torch.tensor([[1, 0.9, 0.8, 0.7, 0], [0, 0.1, 0.2, 0.3, 1]])
        items = torch.tensor([[0, 1, 0, 1.0, 0], [1, 0, 1, 0, 1]])

        ndcg1 = (0/log2(2) + 1/log2(3) + 0/log2(4) + 1/log2(5)) / (1/log2(2) + 1/log2(3) + 0/log2(4) + 0/log2(5))
        ndcg2 = (1/log2(2) + 0/log2(3) + 1/log2(4) + 0/log2(5)) / (1/log2(2) + 1/log2(3) + 1/log2(4) + 0/log2(5))
        real_ndcg = (ndcg1 + ndcg2)/2

        ndcg = CFWGAN.ndcg(items_predicted, items, n=4).item()
        self.assertAlmostEqual(ndcg, real_ndcg)

        items_predicted = torch.tensor([[1, 0.9, 0.8, 0.7, 0], [0, 0.1, 0.2, 0.3, 1]])
        items = torch.tensor([[0, 0, 0, 0, 0], [1, 0, 1.0, 0, 1]])
        real_ndcg = (1 / log2(2) + 0 / log2(3) + 1 / log2(4) + 0 / log2(5)) / (
                    1 / log2(2) + 1 / log2(3) + 1 / log2(4) + 0 / log2(5))

        ndcg = CFWGAN.ndcg(items_predicted, items, n=4).item()
        self.assertAlmostEqual(ndcg, real_ndcg)

    def test_recall_at_n(self):
        items_predicted = torch.tensor([[1, 0.9, 0.8, 0.7, 0], [0, 0.1, 0.2, 0.3, 1]])
        items = torch.tensor([[0, 1, 0, 1.0, 0], [1, 0, 1, 0, 1]])

        real_recall = (2/2 + 2/3)/2
        recall = CFWGAN.recall_at_n(items_predicted, items, n=4).item()
        self.assertAlmostEqual(recall, real_recall)

        real_recall = (1/2 + 2/3)/2
        recall = CFWGAN.recall_at_n(items_predicted, items, n=3).item()
        self.assertAlmostEqual(recall, real_recall)

        items_predicted = torch.tensor([[1, 0.9, 0.8, 0.7, 0], [0, 0.1, 0.2, 0.3, 1]])
        items = torch.tensor([[0, 0, 0, 0, 0], [1, 0, 1.0, 0, 1]])
        real_recall = 2/3
        recall = CFWGAN.recall_at_n(items_predicted, items, n=4).item()
        self.assertAlmostEqual(recall, real_recall)


if __name__ == '__main__':
    unittest.main()
