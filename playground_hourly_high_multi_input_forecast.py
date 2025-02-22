# -*- coding: utf-8 -*-
"""PlayGround Hourly High - multi input forecast.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CQynjfpYX4NvKwuACnFJK560yYXSG8L8

# Step #1 Load the Data
"""

#!pip install pandas==1.4

# Time Series Forecasting - Multi-output Regression for Stock Market Prediction
# A tutorial for this file is available at www.relataly.com

import math  # Mathematical functions
import numpy as np  # Fundamental package for scientific computing with Python
import pandas as pd  # Additional functions for analysing and manipulating data
from datetime import date, timedelta, datetime  # Date Functions
from pandas.plotting import (
    register_matplotlib_converters,
)  # This function adds plotting functions for calender dates
import matplotlib.pyplot as plt  # Important package for visualization - we use this to plot the market data
import matplotlib.dates as mdates  # Formatting dates
import tensorflow as tf
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)  # Packages for measuring model performance / errors
from tensorflow.keras.models import (
    Sequential,
)  # Deep learning library, used for neural networks
from tensorflow.keras.layers import (
    LSTM,
    Dense,
    Dropout,
)  # Deep learning classes for recurrent and regular densely-connected layers
from tensorflow.keras.callbacks import (
    EarlyStopping,
)  # EarlyStopping during model training
from sklearn.preprocessing import (
    RobustScaler,
    MinMaxScaler,
)  # This Scaler removes the median and scales the data according to the quantile range to normalize the price data
import seaborn as sns
import sys
import csv
print("----------------")
sns.set_style("white", {"axes.spines.right": False, "axes.spines.top": False})
# from google.colab import files
# print("jai jai",sys.argv[0])
# print("jai jai", sys.argv[1])
# Setting the timeframe for the data extraction
# end_date =  date.today().strftime("%Y-%m-%d")
# Getting NASDAQ quotes
print(sys.argv)
stockname = sys.argv[1]
symbol = sys.argv[2]
start_date = sys.argv[3]
start_time = sys.argv[4]
end_date = sys.argv[5]
end_time = sys.argv[6]
interval = sys.argv[7]

# Set the input_sequence_length length - this is the timeframe used to make a single prediction
# input_sequence_length was 360 for 15 mins
input_sequence_length = int(sys.argv[8])
# The output sequence length is the number of steps that the neural network predicts
# 30m - 10 occurance
output_sequence_length = int(sys.argv[9])
output_csv_path = sys.argv[10]

# List of considered Features
FEATURES = ["High", "Open", "Close"]  #'Open', 'High', 'Low', 'Close' #'Adj Close']
DROP_FEATURES = ["Adj Close", "Volume"]
# Convert string to datetime
start_date_time = datetime.strptime(start_date + start_time, "%Y-%m-%d%H:%M:%S")
end_date_time = datetime.strptime(end_date + end_time, "%Y-%m-%d%H:%M:%S")


import yfinance as yf

df = yf.download(symbol, end=end_date_time, start=start_date_time, interval=interval)


if df.size >= 18000:
    print(df.size)
    print("Good set of data \U0001F911")
else:
    print(df.size)
    print("Try to increase start date \U0001F61E")
    sys.exit(1)
    
df = df.drop(DROP_FEATURES, axis=1)
print(df.tail(10))

# Decomposition
# from statsmodels.tsa.seasonal import seasonal_decompose

# result = seasonal_decompose(df['High'], model='additive', period=12)
# result.plot()
# plt.show()

"""# Step #3 Preprocessing and Feature Selection"""

# Indexing Batches
df_train = df.sort_values(by=["Datetime"]).copy()
df_train.tail(5)


def prepare_data(df):

    print("FEATURE LIST")
    print([f for f in FEATURES])

    # Create the dataset with features and filter the data to the list of FEATURES
    df_filter = df[FEATURES]

    # Convert the data to numpy values
    np_filter_unscaled = np.array(df_filter)
    # np_filter_unscaled = np.reshape(np_unscaled, (df_filter.shape[0], -1))
    print(np_filter_unscaled.shape)

    np_c_unscaled = np.array(df["High"]).reshape(-1, 1)

    return np_filter_unscaled, np_c_unscaled, df_filter


np_filter_unscaled, np_c_unscaled, df_filter = prepare_data(df_train)

# Creating a separate scaler that works on a single column for scaling predictions
# Scale each feature to a range between 0 and 1
scaler_train = MinMaxScaler()
np_scaled = scaler_train.fit_transform(np_filter_unscaled)

# Create a separate scaler for a single column
scaler_pred = MinMaxScaler()
np_scaled_c = scaler_pred.fit_transform(np_c_unscaled)

df_train

# Prediction Index
index_Close = df_filter.columns.get_loc("High")

# Split the training data into train and train data sets
# As a first step, we get the number of rows to train the model on 80% of the data
train_data_length = math.ceil(np_scaled.shape[0] * 0.8)

# Create the training and test data
train_data = np_scaled[:train_data_length, :]
test_data = np_scaled[train_data_length - input_sequence_length :, :]


# The RNN needs data with the format of [samples, time steps, features]
# Here, we create N samples, input_sequence_length time steps per sample, and f features
def partition_dataset(input_sequence_length, output_sequence_length, data):
    x, y = [], []
    data_len = data.shape[0]
    for i in range(input_sequence_length, data_len - output_sequence_length):
        x.append(
            data[i - input_sequence_length : i, :]
        )  # contains input_sequence_length values 0-input_sequence_length * columns
        y.append(
            data[i : i + output_sequence_length, index_Close]
        )  # contains the prediction values for validation (3rd column = Close),  for single-step prediction

    # Convert the x and y to numpy arrays
    x = np.array(x)
    y = np.array(y)
    return x, y


# Generate training data and test data
x_train, y_train = partition_dataset(
    input_sequence_length, output_sequence_length, train_data
)
x_test, y_test = partition_dataset(
    input_sequence_length, output_sequence_length, test_data
)

# Print the shapes: the result is: (rows, training_sequence, features) (prediction value, )
print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)

# Validate that the prediction value and the input match up
# The last close price of the second input sample should equal the first prediction value
nrows = 1  # number of shifted plots

fig, ax = plt.subplots(nrows=nrows, ncols=1, figsize=(16, 8))
for i, ax in enumerate(fig.axes):
    print(f"x_train_{i}")
    xtrain = pd.DataFrame(x_train[i][:, index_Close], columns={f"x_train_{i}"})
    ytrain = pd.DataFrame(
        y_train[i][: output_sequence_length - 1], columns={f"y_train_{i}"}
    )
    ytrain.index = np.arange(
        input_sequence_length, input_sequence_length + output_sequence_length - 1
    )
    xtrain_ = pd.concat(
        [xtrain, ytrain[:1].rename(columns={ytrain.columns[0]: xtrain.columns[0]})]
    )
    df_merge = pd.concat([xtrain_, ytrain])
    # sns.lineplot(data = df_merge, ax=ax)
# plt.show

"""# Step #4 Model Training"""

# Configure the neural network model
model = Sequential()
n_output_neurons = output_sequence_length

# Model with n_neurons = inputshape Timestamps, each with x_train.shape[2] variables
n_input_neurons = x_train.shape[1] * x_train.shape[2]
print(n_input_neurons, x_train.shape[1], x_train.shape[2])
model.add(
    LSTM(128, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2]))
)
model.add(LSTM(64, return_sequences=False))
model.add(Dense(n_output_neurons))

# Compile the model
model.compile(optimizer="adam", loss="mse")

# Training the model
epochs = 500
batch_size = 64

early_stop = EarlyStopping(monitor="loss", patience=15, verbose=1)
history = model.fit(
    x_train,
    y_train,
    batch_size=batch_size,
    epochs=epochs,
    validation_data=(x_test, y_test),
    callbacks=[early_stop],
)

from matplotlib import pyplot

# pyplot.plot(history.history['loss'])
# pyplot.plot(history.history['val_loss'])
pyplot.title("model train vs validation loss")
pyplot.ylabel("loss")
pyplot.xlabel("epoch")
pyplot.legend(["train", "validation"], loc="upper right")
# pyplot.show()

"""# Step #5 Evaluate Model Performance"""

# Get the predicted values
y_pred_scaled = model.predict(x_test)

# Unscale the predicted values
y_pred = scaler_pred.inverse_transform(y_pred_scaled)
y_test_unscaled = scaler_pred.inverse_transform(y_test).reshape(
    -1, output_sequence_length
)

# Mean Absolute Error (MAE)
MAE = mean_absolute_error(y_test_unscaled, y_pred)
print(f"Median Absolute Error (MAE): {np.round(MAE, 2)}")

# Mean Absolute Percentage Error (MAPE)
MAPE = np.mean((np.abs(np.subtract(y_test_unscaled, y_pred) / y_test_unscaled))) * 100
print(f"Mean Absolute Percentage Error (MAPE): {np.round(MAPE, 2)} %")

# Median Absolute Percentage Error (MDAPE)
MDAPE = (
    np.median((np.abs(np.subtract(y_test_unscaled, y_pred) / y_test_unscaled))) * 100
)
print(f"Median Absolute Percentage Error (MDAPE): {np.round(MDAPE, 2)} %")


def prepare_df(i, x, y, y_pred_unscaled):
    # Undo the scaling on x, reshape the testset into a one-dimensional array, so that it fits to the pred scaler
    x_test_unscaled_df = pd.DataFrame(
        scaler_pred.inverse_transform((x[i]))[:, index_Close]
    ).rename(columns={0: "x_test"})

    y_test_unscaled_df = []
    # Undo the scaling on y
    if type(y) == np.ndarray:
        y_test_unscaled_df = pd.DataFrame(scaler_pred.inverse_transform(y)[i]).rename(
            columns={0: "y_test"}
        )

    # Create a dataframe for the y_pred at position i, y_pred is already unscaled
    y_pred_df = pd.DataFrame(y_pred_unscaled[i]).rename(columns={0: "y_pred"})
    return x_test_unscaled_df, y_pred_df, y_test_unscaled_df


def plot_multi_test_forecast(x_test_unscaled_df, y_test_unscaled_df, y_pred_df, title):
    # Package y_pred_unscaled and y_test_unscaled into a dataframe with columns pred and true
    if type(y_test_unscaled_df) == pd.core.frame.DataFrame:
        df_merge = y_pred_df.join(y_test_unscaled_df, how="left")
    else:
        df_merge = y_pred_df.copy()

    # Merge the dataframes
    df_merge_ = pd.concat([x_test_unscaled_df, df_merge]).reset_index(drop=True)

    # Plot the linecharts
    fig, ax = plt.subplots(figsize=(20, 8))
    plt.title(title, fontsize=12)
    ax.set(ylabel=stockname + "_stock_price_quotes")
    sns.lineplot(data=df_merge_, linewidth=2.0, ax=ax)
    print(df_merge_)


# Creates a linechart for a specific test batch_number and corresponding test predictions
batch_number = 50
x_test_unscaled_df, y_pred_df, y_test_unscaled_df = prepare_df(
    i, x_test, y_test, y_pred
)
title = f"Predictions vs y_test - test batch number {batch_number}"
plot_multi_test_forecast(x_test_unscaled_df, y_test_unscaled_df, y_pred_df, title)

"""# Step #6 Create a new Forecast"""

# Get the latest input batch from the test dataset, which is contains the price values for the last ten trading days
x_test_latest_batch = np_scaled[-input_sequence_length:, :].reshape(
    1, input_sequence_length, len(FEATURES)
)

# Predict on the batch
y_pred_scaled = model.predict(x_test_latest_batch)
y_pred_unscaled = scaler_pred.inverse_transform(y_pred_scaled)

# Prepare the data and plot the input data and the predictions
x_test_unscaled_df, y_test_unscaled_df, _ = prepare_df(
    0, x_test_latest_batch, "", y_pred_unscaled
)
plot_multi_test_forecast(
    x_test_unscaled_df, "", y_test_unscaled_df, "x_new Vs. y_new_pred"
)

Predicted_High = y_test_unscaled_df["y_pred"].max()
# print(Predicted_High)

"""# Summary"""

# Mean Absolute Error (MAE)
MAE = mean_absolute_error(y_test_unscaled, y_pred)

# Mean Absolute Percentage Error (MAPE)
MAPE = np.mean((np.abs(np.subtract(y_test_unscaled, y_pred) / y_test_unscaled))) * 100

# Median Absolute Percentage Error (MDAPE)
MDAPE = (
    np.median((np.abs(np.subtract(y_test_unscaled, y_pred) / y_test_unscaled))) * 100
)

# for hourly prediction
base_time = datetime.strptime(end_time, '%H:%M:%S')
next_interval = base_time  + timedelta(hours=1)
next_interval_string = next_interval.strftime('%H:%M:%S')

# Convert string to datetime
start_date_time = datetime.strptime(end_date + end_time, "%Y-%m-%d%H:%M:%S")
end_date_time = datetime.strptime(end_date + next_interval_string , "%Y-%m-%d%H:%M:%S")
actualDf = yf.download(
    symbol, end=end_date_time, start=start_date_time, interval=interval
)
print(actualDf)
Vaidation_df = pd.DataFrame()
Vaidation_df["Date"] = actualDf.index
Vaidation_df["ActualHigh"] = actualDf["High"].values
Vaidation_df["PredictedHigh"] = y_test_unscaled_df["y_pred"]
Vaidation_df["Residuals"] = Vaidation_df["ActualHigh"] - Vaidation_df["PredictedHigh"]
ActualHigh = Vaidation_df["ActualHigh"].values.max()
Predicted_High = Vaidation_df["PredictedHigh"].values.max()

print(Vaidation_df)
print(f"Prediction Date: {end_date}")
print(f"Median Absolute Error (MAE): {np.round(MAE, 2)}")
print(f"Mean Absolute Percentage Error (MAPE): {np.round(MAPE, 2)} %")
print(f"Median Absolute Percentage Error (MDAPE): {np.round(MDAPE, 2)} %")
print(f"Predicted High =", Predicted_High)
print(f"Actual High =", actualDf["High"].values.max())
print(f"Actual Difference =", ActualHigh.max() - Predicted_High)


if np.round(MAE, 2) <= 40.00 and np.round(MAPE, 2) <= 0.20 and np.round(MDAPE, 2) <=  0.15:
    print("Working \U0001F911")
    print(f"Writing to {output_csv_path}")
    # Open the file in write mode and create a csv.writer object
    with open(output_csv_path, mode="a", newline='') as file:
        writer = csv.writer(file)
        # Write the data to the CSV file
        data = [
            [
                end_date+" "+end_time,
                actualDf["High"].values.max(),
                Predicted_High,
                actualDf["High"].values.max() - Predicted_High,
                np.round(MAE, 2),
                np.round(MAPE, 2),
                np.round(MDAPE, 2),
            ],

        ]

        writer.writerows(data)

else:
    print("Not-Working \U0001F61E")

# Prediction Date: 2024-07-01
# Median Absolute Error (MAE): 99.19
# Mean Absolute Percentage Error (MAPE): 0.44 %
# Median Absolute Percentage Error (MDAPE): 0.31 %
# Predicted High = 24173.744
# Actual High = 24163.349609375
# Actual Difference = -10.39453125


# Prediction Date: 2024-07-01
# Median Absolute Error (MAE): 128.26
# Mean Absolute Percentage Error (MAPE): 0.57 %
# Median Absolute Percentage Error (MDAPE): 0.49 %
# Predicted High = 24146.496
# Actual High = 24163.349609375
# Actual Difference = 16.853515625
