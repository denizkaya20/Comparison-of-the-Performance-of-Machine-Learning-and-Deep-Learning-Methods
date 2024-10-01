# -*- coding: utf-8 -*-
"""Esnek_Hesaplama_Proje_Son.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10qrCQHKMiIji7vecR0lsq5D1CRnGtdZb
"""

from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

!pip install yfinance

start_date = '2014-12-01'

end_date = '2023-05-20'

ticker ="TSLA"

data = yf.download(ticker, start_date, end_date)

data["Date"] = data.index

data = data[["Date", "Open", "High",

             "Low", "Close", "Adj Close", "Volume"]]
data.reset_index(drop=True, inplace=True)

print(data.tail())

#data.to_excel("Stock_price.xlsx")

data.describe()

data.info()

import time
import math
import pandas_datareader as web
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use("fivethirtyeight")
sns.set_style('whitegrid')
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense,LSTM
from sklearn.preprocessing import StandardScaler, MinMaxScaler

stock = yf.Ticker(ticker)

hist = stock.history(start="2014-12-01", end="2023-05-20")

FullData = hist["Close"].values.reshape(-1, 1)
print(FullData[0:5])

sc = MinMaxScaler()

FullData_scaled = sc.fit_transform(FullData)

hist.tail(10)

def Data_Process(stock):
    TimeSteps=10
    FutureTimeSteps=5

    start_date = datetime(2014,12,1)
    end_date = datetime(2023,5,20)

    data = yf.download(stock, start=start_date, end=end_date)
    data['TradeDate'] = data.index

    FullData = data[['Close']].values
    sc = MinMaxScaler()

    DataScaler = sc.fit(FullData)
    X = DataScaler.transform(FullData)

    X = X.reshape(X.shape[0],)

    X_samples = list()
    y_samples = list()

    NumerOfRows = len(X)

    for i in range(TimeSteps , NumerOfRows-FutureTimeSteps , 1):
        x_sample = X[i-TimeSteps:i]
        y_sample = X[i:i+FutureTimeSteps]
        X_samples.append(x_sample)
        y_samples.append(y_sample)

    X_data = np.array(X_samples)
    X_data = X_data.reshape(X_data.shape[0], X_data.shape[1], 1)

    y_data = np.array(y_samples)

    TestingRecords = 5

    X_train=X_data[:-TestingRecords]
    X_test=X_data[-TestingRecords:]
    y_train=y_data[:-TestingRecords]
    y_test=y_data[-TestingRecords:]
    TimeSteps=X_train.shape[1]
    TotalFeatures=X_train.shape[2]

    return X_train, y_train, X_test, y_test, TotalFeatures,TimeSteps,data,DataScaler,FullData

def Data_Process_Linear_Regression():
  pass


def create_model(X_train,X_test,y_train,y_test,TotalFeatures,TimeSteps,epochs):

    FutureTimeSteps=5
    regressor = Sequential()


    regressor.add(LSTM(units = 10, activation = 'relu', input_shape = (TimeSteps, TotalFeatures), return_sequences=True))



    regressor.add(LSTM(units = 5, activation = 'relu', input_shape = (TimeSteps, TotalFeatures), return_sequences=True))


    regressor.add(LSTM(units = 5, activation = 'relu', return_sequences=False ))

    regressor.add(Dense(units = FutureTimeSteps))
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

    StartTime=time.time()

    # Fitting the RNN to the Training set
    regressor.fit(X_train, y_train, batch_size = 5, epochs = epochs)

    EndTime=time.time()
    return regressor

def making_predictions(X_test,y_test,regressor,DataScaler):
  predicted_Price = regressor.predict(X_test)
  predicted_Price = DataScaler.inverse_transform(predicted_Price)
  orig=y_test
  orig=DataScaler.inverse_transform(y_test)
  return orig,predicted_Price

def draw_graphics(orig,predicted_Price):
  FutureTimeSteps=5
  TestingRecords=5
  for i in range(len(orig)):
    Prediction=predicted_Price[i]
    Original=orig[i]

    # Visualising the results
    plt.plot(Prediction, color = 'blue', label = 'Predicted Volume')
    plt.plot(Original, color = 'lightblue', label = 'Original Volume')

    plt.title('### Accuracy of the predictions:'+ str(100 - (100*(abs(Original-Prediction)/Original)).mean().round(2))+'% ###')
    plt.xlabel('Trading Date')

    startDateIndex=(FutureTimeSteps*TestingRecords)-FutureTimeSteps*(i+1)
    endDateIndex=(FutureTimeSteps*TestingRecords)-FutureTimeSteps*(i+1) + FutureTimeSteps
    TotalRows=data.shape[0]

    plt.xticks(range(FutureTimeSteps), data.iloc[TotalRows-endDateIndex : TotalRows-(startDateIndex) , :]['TradeDate'])
    plt.ylabel('Stock Price')

    plt.legend()
    fig=plt.gcf()
    fig.set_figwidth(20)
    fig.set_figheight(3)
    plt.show()

def visualize_full_data_predictions(X_train,X_test,regressor,DataScaler):
  TrainPredictions=DataScaler.inverse_transform(regressor.predict(X_train))
  TestPredictions=DataScaler.inverse_transform(regressor.predict(X_test))

  FullDataPredictions=np.append(TrainPredictions, TestPredictions)
  FullDataOrig=FullData[TimeSteps:]

# plotting the full data
  plt.plot(FullDataPredictions, color = 'blue', label = 'Predicted Price')
  plt.plot(FullDataOrig , color = 'lightblue', label = 'Original Price')


  plt.title('Stock Price Predictions')
  plt.xlabel('Trading Date')
  plt.ylabel('Stock Price')
  plt.legend()
  fig=plt.gcf()
  fig.set_figwidth(20)
  fig.set_figheight(8)
  plt.show()

def PredictPrice(data,DataScaler):
    Last10DaysPrices=data['Close'].tail(10).values
    Last10DaysPrices=Last10DaysPrices.reshape(-1, 1)
    X_test=DataScaler.transform(Last10DaysPrices)
    NumberofSamples=1
    TimeSteps=X_test.shape[0]
    NumberofFeatures=X_test.shape[1]
    X_test=X_test.reshape(NumberofSamples,TimeSteps,NumberofFeatures)
    Next5DaysPrice = regressor.predict(X_test)
    Next5DaysPrice = DataScaler.inverse_transform(Next5DaysPrice)
    return Next5DaysPrice.flatten()

X_train, y_train, X_test, y_test, TotalFeatures,TimeSteps,data,DataScaler,FullData=Data_Process(ticker)

regressor=create_model(X_train,X_test,y_train,y_test,TotalFeatures,TimeSteps,epochs=100)

orig,predicted_Price=making_predictions(X_test,y_test,regressor,DataScaler)
# Accuracy of the predictions
accuracy=100 - (100*(abs(orig-predicted_Price)/orig)).mean()
print(f'Accuracy:', accuracy,'\n')
Next5DaysPrice=PredictPrice(data,DataScaler)

print('\n#### Next5DaysPrice ####')
print(Next5DaysPrice,'\n')

print('\n#### Original Prices ####')
print(orig,'\n')
print('#### Predicted Prices ####')
print(predicted_Price)

draw_graphics(orig,predicted_Price)

Predicted5DaysPrice=PredictPrice(data,DataScaler)
print("Predicted Prices:\n",Predicted5DaysPrice)

import yfinance as yf

start_date = '2023-05-21'
end_date = '2023-05-27'
ticker = ticker

data = yf.download(ticker, start_date, end_date)

data["Date"] = data.index
data = data[["Date", "Close"]]
actual_prices = data.reset_index(drop=True)

print("Actual Next 5 Days Prices:")
print(actual_prices)

predicted_prices = []

for price in Predicted5DaysPrice:
  predicted_prices.append(price)

prices_df = pd.DataFrame({'Date': actual_prices["Date"], 'Actual Price': actual_prices["Close"],
                          'Predicted Price': predicted_prices})

print("\nActual and Predicted Prices for the Next 5 Days:")
print(prices_df)

# Visualize the actual and predicted price changes
plt.figure(figsize=(10, 6))
plt.plot(prices_df["Date"], prices_df["Actual Price"], label='Actual Price', marker='o')
plt.plot(prices_df["Date"], prices_df["Predicted Price"], label='Predicted Price', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Actual and Predicted Price Changes')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

!pip install pycaret

from pycaret.regression import *
s = setup(data=hist, target='Close', session_id=123)

# functional API
best = compare_models()

print(best)

#Lineer Regresyon Modeli
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from sklearn import metrics
from sklearn.model_selection import train_test_split

stock = yf.Ticker("TSLA")

# get historical market data
df = stock.history(start="2014-12-01", end="2023-05-20")

X = df[['High','Low','Open','Volume']].values
y = df['Close'].values

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3, random_state=1)

regressor = LinearRegression()
regressor.fit(X_train, y_train)
LinearRegression()

print(regressor.coef_)

print(regressor.intercept_)

predicted_lineer = regressor.predict(X_test)
print(predicted_lineer)

data1 = pd.DataFrame({'Actual': y_test.flatten(), 'Predicted' : predicted_lineer.flatten()})

data1.head(10)

import math
print('Mean Absolute Error:', metrics.mean_absolute_error(y_test,predicted_lineer))
print('Mean Squared Error:', metrics.mean_squared_error(y_test,predicted_lineer))
print('Root Mean Squared Error:', math.sqrt(metrics.mean_squared_error(y_test,predicted_lineer)))
r2 = metrics.r2_score(y_test, predicted_lineer)
print('R-squared Score:', r2)

graph = data1.head(20)
graph.plot(kind='bar')

print("Actual Next 5 Days Prices:")
print(actual_prices)

start_date = datetime(2023, 5, 22)
end_date = datetime(2023, 5, 26)

date_range = pd.date_range(start=start_date, end=end_date)
predicted_df = pd.DataFrame({'Date': date_range})

future_features = df[['High', 'Low', 'Open', 'Volume']].tail(5)
predicted_prices = regressor.predict(future_features)

predicted_df['Predicted Price'] = predicted_prices

print("Predicted Prices for the Next 5 Days:")
print(predicted_df)

comparison_df = pd.concat([actual_prices, predicted_df.set_index('Date')], axis=1)
print("Actual and Predicted Prices for the Next 5 Days:")
print(comparison_df)

plt.plot(actual_prices['Date'], actual_prices['Close'], label='Actual Prices')
plt.plot(predicted_df['Date'], predicted_df['Predicted Price'], label='Predicted Prices')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Actual vs Predicted Prices')
plt.legend()
plt.show()