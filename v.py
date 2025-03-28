from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model, Metrics, ClassificationMetrics, OutputPath
from kfp import dsl, compiler


@dsl.component(base_image="tensorflow/tensorflow", packages_to_install=['scikit-learn'])
def model_validation(
    x_test_artifact : Input[Dataset], 
    # x_test_processed: Input[Dataset],
    # y_train_artifact : Input[Dataset], 
    y_test_artifact :Input[Dataset],
    # hyperparameters : dict, 
    metrics: Output[Metrics], 
    classification_metrics: Output[ClassificationMetrics], 
    model_trained_artifact: Input[Model]
    ):
    """
    Build the model with Keras API
    Export model metrics
    """
    from tensorflow import keras
    import tensorflow as tf
    import numpy as np
    import os
    import glob
    from sklearn.metrics import confusion_matrix
    
    #load dataset
    x_test = np.load(x_test_artifact.path)
    # x_test = np.load(x_test_processed.path)
    y_test = np.load(y_test_artifact.path)
    # y_test = np.load(y_test_artifact.path)
    
    #load model structure
    save_path = os.path.join(model_trained_artifact.path, "model.keras") 
    model = keras.models.load_model(save_path)

    
    loss, acc = model.evaluate(x=x_test,y=y_test)
    print("loss is:", loss)
    print("acc is:", acc)

    y_predict = model.predict(x=x_test)
    y_predict = np.argmax(y_predict, axis=1)
    cmatrix = confusion_matrix(y_test, y_predict)
    cmatrix = cmatrix.tolist()
    numbers_list = ['0','1']
    #log confusione matrix
    classification_metrics.log_confusion_matrix(numbers_list,cmatrix)


    #Kubeflox metrics export
    # metrics.log_metric("Test loss", loss)
    metrics.log_metric("Test accuracy", acc)
