# src/models/lstm_model.py

from keras.models import Sequential, load_model
from keras.layers import Input, LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt


class LSTMModel:
    def __init__(self, input_shape, output_size, model_path=None):
        if model_path:
            print("Carregando o modelo salvo...")
            self.model = load_model(model_path)
        else:
            self.model = Sequential()
            self.model.add(Input(shape=input_shape))
            # Camadas LSTM com Dropout
            self.model.add(LSTM(units=64, return_sequences=True))
            self.model.add(Dropout(0.2))
            self.model.add(LSTM(units=64))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(units=output_size))
            self.model.compile(
                optimizer="adam",
                loss="mean_squared_error",
                metrics=["mean_absolute_error"],
            )

    def train(
        self,
        X_train,
        Y_train,
        X_val=None,
        Y_val=None,
        epochs=500,
        batch_size=32,
        model_save_path="lstm_model.keras",
    ):
        print("Iniciando o treinamento do modelo...")

        # Callbacks para EarlyStopping e ModelCheckpoint
        early_stopping = EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True, verbose=1
        )
        checkpoint = ModelCheckpoint(
            filepath="model_weights_epoch_{epoch:02d}.h5",
            save_weights_only=True,
            monitor="val_loss",
            mode="min",
            save_best_only=False,
            verbose=1,
        )

        callbacks = [early_stopping, checkpoint]

        history = self.model.fit(
            X_train,
            Y_train,
            validation_data=(X_val, Y_val) if X_val is not None else None,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
        )
        print("Treinamento concluído.")

        # Salvar o modelo treinado
        self.model.save(model_save_path)
        print(f"Modelo salvo em {model_save_path}.")
        return history

    def predict(self, X):
        print("Realizando previsões...")
        return self.model.predict(X)

    def load_weights(self, weights_path):
        print(f"Carregando pesos do modelo de {weights_path}...")
        self.model.load_weights(weights_path)

    def plot_training_history(self, history):
        plt.figure(figsize=(8, 4))
        plt.plot(history.history["loss"], label="Loss de Treinamento")
        if "val_loss" in history.history:
            plt.plot(history.history["val_loss"], label="Loss de Validação")
        plt.title("Histórico de Treinamento")
        plt.xlabel("Épocas")
        plt.ylabel("Loss")
        plt.legend()
        plt.show()

    def plot_predictions(self, Y_test, Y_pred, scaler):
        # Reverter a normalização para os valores reais
        Y_test_scaled = scaler.inverse_transform(Y_test.reshape(-1, 1))
        Y_pred_scaled = scaler.inverse_transform(Y_pred.reshape(-1, 1))

        # Plotar os valores reais vs. previsões
        plt.figure(figsize=(10, 6))
        plt.plot(Y_test_scaled, color="blue", label="Valores Reais")
        plt.plot(Y_pred_scaled, color="red", linestyle="--", label="Previsões")
        plt.title("Previsões vs Valores Reais")
        plt.xlabel("Período")
        plt.ylabel("Preço BTC (USD)")
        plt.legend()
        plt.show()
