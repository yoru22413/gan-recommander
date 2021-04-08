from torch.utils.data import random_split, DataLoader

from model_cfwgan import CFWGAN
from dataset import MovieLensDataset
import torch
import pytorch_lightning as pl

batch_size = 16

dataset = MovieLensDataset()
train_size = int(len(dataset)*0.8)
train, val = random_split(dataset, [train_size, len(dataset)-train_size], generator=torch.Generator().manual_seed(1234))

model = CFWGAN(dataset.num_items)
trainer = pl.Trainer(max_epochs=10)
trainer.fit(model, DataLoader(train, batch_size, shuffle=True), DataLoader(val, batch_size*2, shuffle=True))

