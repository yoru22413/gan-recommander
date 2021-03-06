import unittest
from dataset import MovieLensDataset
import scipy.sparse as sparse
import numpy as np
import torch

class MyTestCase(unittest.TestCase):
    def test_MovieLensDataset(self):
        dataset = MovieLensDataset(ratings_file='test_ratings.csv', movies_file='test_movies.csv')
        row  = [0,0,1,2,3,3]
        col  = [0,1,0,2,3,4]
        data = [1.,1.,1.,1.,1.,1.]

        # test for matrix equality
        expected_mat = sparse.csr_matrix((data, (row, col)), shape=(max(row) + 1, max(col) + 1))
        self.assertTrue(np.array_equal(dataset.matrix.todense(), expected_mat.todense()))

        # test for first item retrieval
        expected_retrieval = torch.tensor([1., 1., 0., 0., 0.,])
        self.assertTrue(torch.equal(dataset[0][0], expected_retrieval))

        # test for last item retrieval
        expected_retrieval = torch.tensor([0., 0., 0., 1., 1.,])
        self.assertTrue(torch.equal(dataset[-1][0], expected_retrieval))

        # test for movie retrieval
        expected_string = "#1: Toy Story (1995) ===> Adventure|Animation|Children|Comedy|Fantasy"
        self.assertTrue(dataset.get_movie(0) == expected_string)

        # test for movie list retrieval
        expected_str_list = "#1: Toy Story (1995) ===> Adventure|Animation|Children|Comedy|Fantasy\n" + \
            "#2: Jumanji (1995) ===> Adventure|Children|Fantasy"
        self.assertTrue(dataset.get_movie_list_str([0,1]) == expected_str_list)

    def test_split_train_test(self):
        dataset = MovieLensDataset(ratings_file='test_ratings.csv', movies_file='test_movies.csv')
        train, test = dataset.split_train_test(0.1)
        self.assertEqual(train.matrix.shape, dataset.matrix.shape)
        self.assertEqual(test.matrix.shape, dataset.matrix.shape)
        self.assertEqual(test.matrix.nonzero()[0].size, round(dataset.matrix.nonzero()[0].size * 0.1))
        self.assertEqual(train.matrix.nonzero()[0].size, round(dataset.matrix.nonzero()[0].size * 0.9))

        train, test = dataset.split_train_test(0.2)
        self.assertEqual(train.matrix.shape, dataset.matrix.shape)
        self.assertEqual(test.matrix.shape, dataset.matrix.shape)
        self.assertEqual(test.matrix.nonzero()[0].size, round(dataset.matrix.nonzero()[0].size * 0.2))
        self.assertEqual(train.matrix.nonzero()[0].size, round(dataset.matrix.nonzero()[0].size * 0.8))

        s = test.matrix + train.matrix
        self.assertTrue(not (s != dataset.matrix).todense().any())
        self.assertTrue(((s.todense() == 1) | (s.todense() == 0)).all())


if __name__ == '__main__':
    unittest.main()
