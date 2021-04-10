from pytorch_lightning.callbacks import ModelCheckpoint
from torch.utils.data import random_split, DataLoader

from model_cfwgan import CFWGAN
from dataset import MovieLensDataset
import torch
import pytorch_lightning as pl


pl.seed_everything(12323)

batch_size = 16

dataset = MovieLensDataset('movielens/ml-latest-small/ratings.csv', 'movielens/ml-latest-small/movies.csv')
train, test = dataset.split_train_test(test_size=0.2)

test_size = int(len(test)*0.5)

test, val = random_split(dataset, [test_size, len(test)-test_size], generator=torch.Generator().manual_seed(1234))

model = CFWGAN(dataset.item_count, alpha=0.1, s_zr=0.7, s_pm=0.7)

model_checkpoint = ModelCheckpoint(monitor='precision_at_5', save_top_k=5, save_weights_only=True, mode='max')

trainer = pl.Trainer(max_epochs=10, callbacks=[model_checkpoint])
trainer.fit(model, DataLoader(train, batch_size, shuffle=True), DataLoader(val, batch_size*2))
trainer.test(model, DataLoader(test, batch_size*2))

