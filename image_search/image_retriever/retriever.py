import pandas as pd
from pymilvus import connections, Collection, utility
import towhee
from towhee.types.image_utils import from_pil

class Retriever:
    def __init__(self, host, port, collection_name):
        #df = pd.read_csv('image_search/data/image_100x10/files_to_train.csv')

        #id_img = df.set_index('id')['path'].to_dict()

        connections.connect(host=host, port=port)

        if utility.has_collection(collection_name):
            self.collection = Collection(collection_name)
            #print(self.collection.load())
            print('Total number of entities in {} is {}.'.format(collection_name, self.collection.num_entities))

        with towhee.api() as api:
            self.search = (
                api.runas_op(func=lambda img: from_pil(img))
                .image_embedding.timm(model_name='resnet50')
                .tensor_normalize()
                .milvus_search(collection=self.collection, limit=5, output_fields=['id', 'label'])
                .runas_op(func=lambda res: [[x.id, x.score, x.label] for x in res])
                .as_function()
            )

        print('Retriever is ready.')

    def search(self, pil_img):
        return self.search(pil_img)


