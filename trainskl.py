from sklearn.linear_model import LogisticRegression
  from sklearn.datasets import make_classification
  import pickle
  X, y = make_classification(n_samples=10, n_features=2, n_informative=2, n_redundant=0, n_classes=2, random_state=42)
  model = LogisticRegression()
  model.fit(X, y)
  os.makedirs(model_trained.path, exist_ok=True)
  # save_path = os.path.join(model_trained.path, "model.keras") 
  # model.save(save_path)
  with open(f"{model_trained.path}/model.pkl", "wb") as f:
      pickle.dump(model, f)
