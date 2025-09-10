from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model, Metrics, ClassificationMetrics, OutputPath
from kfp import dsl


@dsl.component(base_image="tensorflow/tensorflow", packages_to_install=["pandas", "tensorflow"])
#def load_dataset(x_train_artifact: Output[Dataset]):
def load_dataset(x_train_artifact: Output[Dataset], 
                 x_test_artifact: Output[Dataset],
                 y_train_artifact: Output[Dataset],
                 y_test_artifact: Output[Dataset],
                 tensorboard_artifact: Output[Dataset]):
    '''
    get dataset from Keras and load it separating input from output and train from test
    '''
    import numpy as np
    import pandas as pd
    from tensorflow import keras
    import os
    import shutil
   
    (x_train, y_train), (x_test, y_test) = keras.datasets.california_housing.load_data(version="small", path="california_housing.npz", test_split=0.2, seed=109)

    y_train = (y_train > 200000).astype(int)
    y_test= (y_test > 200000).astype(int)
    
    # Save numpy arrays directly to artifact paths
    # Note: np.save automatically adds .npy extension, but we want to save to exact path
    with open(x_train_artifact.path, 'wb') as f:
        np.save(f, x_train)

    with open(y_train_artifact.path, 'wb') as f:
        np.save(f, y_train)

    with open(x_test_artifact.path, 'wb') as f:
        np.save(f, x_test)

    with open(y_test_artifact.path, 'wb') as f:
        np.save(f, y_test)

    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    df.to_csv(tensorboard_artifact.path, index=False)

# import pandas as pd

# # Collect all batches into one DataFrame
# dfs = []
# for batch in dataset.to_batches(batch_size=10000):
#     df_batch = batch.to_pandas()
#     dfs.append(df_batch)

# # Combine all batches
# full_df = pd.concat(dfs, ignore_index=True)
