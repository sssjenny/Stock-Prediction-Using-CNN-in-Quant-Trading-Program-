import configparser
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calRateOfReturn(X, actual_data, pred_data):
    origin_money = 10000  # 最初投资额
    money = 10000  # 动态钱数
    status = 0  # 持仓方向，0是未持仓，1是多头，2是空头
    money_History = []  # 钱数历史数据
    money_History.append(money)
    hasTransactionToday = False  # 当日是否开仓
    numOfHand = 0

    for i in range(1, 3791):
        if (i % 48 == 0):
            hasTransactionToday = False
        now_close = actual_data[i]  # 此5min实际价格
        last_close = actual_data[i - 1]  # 上5min实际价格
        next_pred = pred_data[i + 1]  # 上5min预测价格
        signal_1 = (now_close - last_close) / last_close  # 趋势信号1
        signal_2 = (next_pred - now_close) / now_close  # 趋势信号2

        if (status == 0):
            if (signal_2 > X):
                numOfHand = math.floor(money / now_close)
                money -= now_close * numOfHand
                money -= now_close * 0.000023 * numOfHand
                status = 1
                hasTransactionToday = True
            elif (signal_2 < -X):
                numOfHand = math.floor(money / now_close)
                money += now_close * numOfHand
                money -= now_close * 0.000023 * numOfHand
                status = 2
                hasTransactionToday = True
        elif (status == 1):
            if (signal_1 < -X and signal_2 > X):
                money += now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand
                numOfHand = math.floor(money / now_close)
                money -= now_close * numOfHand
                money -= now_close * 0.000023 * numOfHand
                hasTransactionToday = True
            elif (signal_2 < -X):
                money += now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand
                numOfHand = math.floor(money / now_close)
                money += now_close * numOfHand
                money -= now_close * 0.000023 * numOfHand
                status = 2
                hasTransactionToday = True
            elif (signal_1 < -X and signal_2 >= -X and signal_2 <= X):
                money += now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand
                status = 0
        elif (status == 2):
            if (signal_2 > X):
                money -= now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand
                numOfHand = math.floor(money / now_close)
                money -= now_close * numOfHand
                money -= now_close * 0.000023 * numOfHand
                status = 1
                hasTransactionToday = True
            if (signal_1 > X and signal_2 < -X):
                money -= now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand
                numOfHand = math.floor(money / now_close)
                money += now_close * numOfHand
                money -= now_close * 0.000023 * numOfHand
                hasTransactionToday = True
            if (signal_1 > X and signal_2 >= -X and signal_2 <= X):
                money -= now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand
                status = 0
        money_History.append(money)

        # 最后一天强制平仓
        if (i == 3790):
            if (status == 1):
                money += now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand
            elif (status == 2):
                money -= now_close * numOfHand
                if (hasTransactionToday):
                    money -= now_close * 0.000345 * numOfHand
                else:
                    money -= now_close * 0.000023 * numOfHand

    return (money - origin_money) / origin_money


def cal_X_auto():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='GB18030')

    pred_data = pd.read_csv(config.get('config', 'filename'))

    actual_data = pd.read_csv("6m.csv")

    date = pred_data["Unnamed: 0"].values
    actual_data = actual_data.loc[19200 * 0.8 + 48:19199, ["close"]]
    actual_data = actual_data["close"].values
    pred_data = pred_data["close"].values

    rateOfReturn = []
    maxReturn = 0
    currentReturn = 0
    maxReturnOfX = 0
    for i in np.arange(0.0001, 0.01, 0.0001):
        currentReturn = calRateOfReturn(i, actual_data, pred_data)
        rateOfReturn.append(currentReturn)
        if (currentReturn > maxReturn):
            maxReturn = currentReturn
            maxReturnOfX = i

    plt.plot(np.arange(0.0001, 0.01, 0.0001), rateOfReturn)
    plt.show()

    # x结果写入config.ini
    config.set('config', 'x', round(maxReturnOfX, 4).__str__())
    openConfig = open('config.ini', 'w')
    config.write(openConfig)
    openConfig.close()

    return maxReturn