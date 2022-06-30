#!/usr/bin/python3
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

from inspect import ClosureVars
import sys
import algo

class Bot:
    def __init__(self):
        self.botState = BotState()
        self.signal = 0

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            self.parse(reading)

    def parse(self, info: str):
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        if tmp[0] == "action":
            unit1 = self.botState.list_of_pairs[0]
            unit2 = self.botState.list_of_pairs[1]
            pair = unit1 + "_" + unit2
            CloseValues = self.botState.charts[pair].closes
            lastCloseValue = CloseValues[-1]
            mean = algo.SMA(CloseValues, 20)
            #band bollingers
            highBand, lowBand = algo.BollingerBands(CloseValues, mean, 20)
            #rsi
            rsi = algo.RSI(CloseValues[len(CloseValues) - 15:], 14)
            print(f'rsi: {rsi}', file=sys.stderr)
            #macd
            macd = algo.MACD(CloseValues)
            print(f'macd: {macd}', file=sys.stderr)
            print('', file=sys.stderr)
            print('', file=sys.stderr)
            
            #strategy
            moneyOut = self.botState.stacks[unit2] * lastCloseValue
            moneyStack = self.botState.stacks[unit1] / lastCloseValue
            buyValue = ((lowBand - lastCloseValue) / 50) * moneyStack
            sellValue = ((lastCloseValue - highBand) / 30) * self.botState.stacks[unit2]
            print(f'lastCloseValue: {lastCloseValue} \n mean: {mean} \n highBand: {highBand} \n lowBand: {lowBand} \n buyValue: {buyValue} \n sellValue: {sellValue} \n moneyStack: {moneyStack}', file=sys.stderr)
            print(f'{unit2}: {self.botState.stacks[unit2]} \n initialStack: {self.botState.initialStack} \n {unit1}: {self.botState.stacks["USDT"]}', file=sys.stderr)
            print('', file=sys.stderr)
            print('', file=sys.stderr)
            if (macd < -400 and rsi < 30 and moneyStack > 0.0001):
                print(f'buy {pair} {moneyStack}', flush=True)
                self.signal = 1
                print("macd buy", file=sys.stderr)
                print('', file=sys.stderr)
                print('', file=sys.stderr)
            #elif (rsi >= 80 and macd < -200 and moneyStack > 0.0001):
            #    print(f'buy {pair} {moneyStack}', flush=True)
            #    self.signal = 1
            #    print("rsi buy", file=sys.stderr)
            elif ((macd > 400 or (rsi <= 30 and moneyOut > self.botState.initialStack + 100)) and self.botState.stacks[unit2] > 0.0001):
                print(f'sell {pair} {self.botState.stacks[unit2]}', flush=True)
                self.signal = -1
                print("macd sell", file=sys.stderr)
                print('', file=sys.stderr)
                print('', file=sys.stderr)
            elif (lastCloseValue < lowBand and moneyStack > buyValue and buyValue > 0.0001 and self.signal != 1):
                print(f'buy {pair} {buyValue}', flush=True)
                print("Band buy", file=sys.stderr)
                self.signal = 1

            elif (lastCloseValue > highBand and self.botState.stacks[unit2] >= sellValue and sellValue > 0.0001 and self.signal != -1):
                print(f'sell {pair} {self.botState.stacks[unit2]}', flush=True)
                self.signal = -1
            elif moneyOut > self.botState.initialStack + 100:
                print(f'sell {pair} {self.botState.stacks[unit2]}', flush=True)
                self.signal = -1
            else:
                print("no_moves", flush=True)
            print(f'____________________________________________________________', file=sys.stderr)

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)


class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)
    
    def get_date(self):
        return self.dates
    
    def get_open(self):
        return self.opens
    
    def get_high(self):
        return self.highs
    
    def get_low(self):
        return self.lows
    
    def get_close(self):
        return self.closes
    
    def get_volume(self):
        return self.volumes

class BotState:
    def __init__(self):
        self.player_names = []
        self.your_bot = ""
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()
        self.list_of_pairs = []

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)
        # split pair delim by _
        # add pair to list of pairs if not already in list
        unit = pair.split("_")
        if not (unit[0] in self.list_of_pairs):
            self.list_of_pairs.append(unit[0])
        if not (unit[1] in self.list_of_pairs):
            self.list_of_pairs.append(unit[1])

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "player_names":
            self.player_names = value.rstrip("\n\r").split(",")
        if key == "your_bot":
            self.your_bot = value
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
