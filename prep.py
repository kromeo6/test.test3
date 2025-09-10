from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model, Metrics, ClassificationMetrics, OutputPath
from kfp import dsl, compiler


@dsl.component(base_image="tensorflow/tensorflow")
def preprocessing(x_train_artifact: Input[Dataset], 
                  metrics : Output[Metrics],
                  metrics_2: Output[Metrics],
                  x_train_transformed_artifact: Output[Dataset]):
    ''' 
    just reshape and normalize data
    '''
    import numpy as np
    import os
    import shutil
    
    # load data artifact store
    x_train = np.load(x_train_artifact.path) 
    print("shape: ", x_train.shape)

    #logging metrics using Kubeflow Artifacts
    metrics.log_metric("Train Data Shape", x_train.shape[0])

    x_train_transformed = x_train.copy()

    # metrics_2.log_metric("Train Data housing med age", x_train_transformed[:, 2] > 50)

    x_train_transformed[x_train_transformed[:, 2] > 50, 2] = 50
    print("final shape: ", x_train_transformed.shape)
    print('type is: ', type(x_train_transformed))

    # Save directly to artifact path using file handle to avoid .npy extension issue
    with open(x_train_transformed_artifact.path, 'wb') as f:
        np.save(f, x_train_transformed)
    print("✅ Saved directly to artifact path")





