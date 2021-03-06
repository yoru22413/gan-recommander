import torch
import numpy as np
from dataset import MovieLensDataset
from model_cfwgan import CFWGAN

class Recommender():
    def __init__(self, path_to_model=None, ratings_file=None, movies_file=None):
        self.dataset = MovieLensDataset(ratings_file=ratings_file, movies_file=movies_file)
        self.model = self.load_model(path_to_model)

    def load_model(self, path):
        if path is None or path == '':
            return None
        model = CFWGAN.load_from_checkpoint(path, num_items=len(self.dataset))
        return model

    def generate(self, vector):
        return self.model.forward(torch.tensor(vector))

    def filter_vector(self, input, output):
        filtered = input * output
        return filtered

    def top_k(self, vector, k=1):
        values = torch.sort(vector, descending=True)
        string = self.dataset.get_movie_list_str(list(values[1].detach().numpy()[:k]))
        top = list(values[0][:k].detach().numpy())
        probs = ", ".join([str(t) for t in top])
        return string + "\n\nprobs: [" + probs + "]"

    def vector_to_movies(self, vector):
        filtered = [(i+1)*vector[i] for i in range(len(vector)) if vector[i] != 0]
        filtered = list(np.array(filtered) - 1)
        filtered.reverse()
        return self.dataset.get_movie_list_str(filtered)
