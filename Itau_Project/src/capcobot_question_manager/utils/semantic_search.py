import logging
import os
import tarfile

import numpy as np
import tensorflow_hub as hub
from sklearn.neighbors import NearestNeighbors

from src.capcobot_question_manager.utils.file_utils import (
    get_file_from_s3,
)

logger = logging.getLogger("CapcoBot")


class SemanticSearch:
    def __init__(self):
        self.get_model_tensorflow()
        self.use = hub.load("model_tensorflow")
        logger.info("Carga do modelo do tensorflow realizada com sucesso")
        self.fitted = False

    def get_model_tensorflow(self):
        if not os.path.exists(os.path.join("model_tensorflow", "saved_model.pb")):
            if not os.path.exists("model_tensorflow"):
                os.mkdir("model_tensorflow")
            logger.info("Extaindo arquivo tar.gz")
            file = tarfile.open(
                fileobj=get_file_from_s3(
                    filename="universal-sentence-encoder_4.tar.gz",
                    folder="model_tensorflow",
                ),
                mode="r:gz",
            )
            file.extractall("./model_tensorflow")
            file.close()
            logger.info("Arquivo extraído com sucesso")
        else:
            logger.info("Arquivo já existente. Não baixado novamente.")

    def fit(self, data, batch=1000, n_neighbors=5):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True

    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]

        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors

    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i : (i + batch)]
            emb_batch = self.use(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings
