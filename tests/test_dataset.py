import unittest
from dataset import MovieLensDataset
import scipy.sparse as sparse
import numpy as np

class MyTestCase(unittest.TestCase):
    def test_MovieLensDataset(self):
        dataset = MovieLensDataset('test_ratings.csv')
        row  = [0,0,1,2,3,3]
        col  = [4,3,4,2,1,0]
        data = [1.,1.,1.,1.,1.,1.]
        expected_mat = sparse.csr_matrix((data, (row, col)), shape=(max(row) + 1, max(col) + 1))
        self.assertTrue(np.array_equal(dataset.matrix.todense(), expected_mat.todense()))

if __name__ == '__main__':
    unittest.main()