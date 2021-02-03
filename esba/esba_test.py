#!/usr/bin/env python
# coding: utf-8

# I use `bayesian-optimization==0.6`, my backend pretty much stick with this version, so migrating will break the code.
from datetime import datetime

import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from bayes_opt import BayesianOptimization
import copy
import pickle
import pkg_resources
import types

#Kite MIS 
CORR_FACTOR = 0.0007
CORR_FACTOR_2 = 0

#Kite MIS 
#CORR_FACTOR = 0.0015
#CORR_FACTOR_2 = 0.35

##Kite CNC  
#CORR_FACTOR = 0.0015
#CORR_FACTOR_2 = 0.35
#D_FACTOR = 15.94

##binance
#CORR_FACTOR = 0.0008
#CORR_FACTOR_2 = 0.35



def get_imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            name = val.__name__.split('.')[0]
        elif isinstance(val, type):
            name = val.__module__.split('.')[0]
        poorly_named_packages = {'PIL': 'Pillow', 'sklearn': 'scikit-learn'}
        if name in poorly_named_packages.keys():
            name = poorly_named_packages[name]
        yield name


imports = list(set(get_imports()))
requirements = []
for m in pkg_resources.working_set:
    if m.project_name in imports and m.project_name != 'pip':
        requirements.append((m.project_name, m.version))

for r in requirements:
    print('{}=={}'.format(*r))


def get_state(data, t, n):
    d = t - n + 1
    block = data[d: t + 1] if d >= 0 else -d * [data[0]] + data[0: t + 1]
    res = []
    for i in range(n - 1):
        res.append(block[i + 1] - block[i])
    return np.array([res])


class RewardsException(Exception):
    def __init__(self, i):
        self.i = i

    def __str__(self):
        return "Rewards are equal on %d iteration" % self.i


class Deep_Evolution_Strategy:
    inputs = None

    def __init__(
            self, weights, reward_function, population_size, sigma, learning_rate
    ):
        self.weights = weights
        self.reward_function = reward_function
        self.population_size = population_size
        self.sigma = sigma
        self.learning_rate = learning_rate

    def _get_weight_from_population(self, weights, population):
        weights_population = []
        for index, i in enumerate(population):
            jittered = self.sigma * i
            weights_population.append(weights[index] + jittered)
        return weights_population

    def get_weights(self):
        return self.weights

    def train(self, data_to_train, epoch=100, print_every=1):
        lasttime = time.time()
        for i in range(epoch):
            population = []
            rewards = np.zeros(self.population_size)
            for k in range(self.population_size):
                x = []
                for w in self.weights:
                    x.append(np.random.randn(*w.shape) + np.sqrt(1 / (w.shape[0] + w.shape[1])))
                population.append(x)
            for k in range(self.population_size):
                weights_population = self._get_weight_from_population(
                    self.weights, population[k]
                )
                rewards[k] = self.reward_function(weights_population, data_to_train)
            if np.std(rewards) == 0:
                # XXX
                raise RewardsException(i)
            else:
                rewards = (rewards - np.mean(rewards)) / (np.std(rewards + 1e-30))
            for index, w in enumerate(self.weights):
                A = np.array([p[index] for p in population])
                self.weights[index] = (
                        w
                        + self.learning_rate
                        / (self.population_size * self.sigma)
                        * np.dot(A.T, rewards).T
                )
            if (i + 1) % print_every == 0:
                print(
                    'iter %d. reward: %f'
                    % (i + 1, self.reward_function(self.weights, data_to_train))
                )
        print('time taken to train:', time.time() - lasttime, 'seconds')


class Model:
    def __init__(self, input_size, layer_size, output_size):
        self.weights = [
            np.random.randn(input_size, layer_size),
            np.random.randn(layer_size, output_size),
            np.random.randn(layer_size, 1),
            np.random.randn(1, layer_size),
        ]

    def predict(self, inputs):
        feed = np.dot(inputs, self.weights[0]) + self.weights[-1]
        decision = np.dot(feed, self.weights[1])
        buy = np.dot(feed, self.weights[2])
        return decision, buy

    def get_weights(self):
        return self.weights

    def set_weights(self, weights):
        self.weights = weights


class Agent:
    def __init__(
            self,
            population_size,
            sigma,
            learning_rate,
            model,
            money,
            max_buy,
            max_sell,
            skip,
            window_size,
    ):
        self.window_size = window_size
        self.skip = skip
        self.POPULATION_SIZE = population_size
        self.SIGMA = sigma
        self.LEARNING_RATE = learning_rate
        self.model = model
        self.initial_money = money
        self.max_buy = max_buy
        self.max_sell = max_sell
        self.es = Deep_Evolution_Strategy(
            self.model.get_weights(),
            self.get_reward,
            self.POPULATION_SIZE,
            self.SIGMA,
            self.LEARNING_RATE,
        )

    def act(self, sequence):
        decision, buy = self.model.predict(np.array(sequence))
        return np.argmax(decision[0]), int(buy[0])

    def get_reward(self, weights, close):
        initial_money = self.initial_money
        starting_money = initial_money
        self.model.weights = weights
        state = get_state(close, 0, self.window_size + 1)
        inventory = []
        quantity = 0
        for t in range(0, len(close) - 1, self.skip):
            action, buy = self.act(state)
            next_state = get_state(close, t + 1, self.window_size + 1)
            if action == 1 and initial_money >= close[t]:
                if buy < 0:
                    buy = 1
                if buy > self.max_buy:
                    buy_units = self.max_buy
                else:
                    buy_units = buy
                # Changed the total_buy and add correction_factor = 0.01
                total_buy = buy_units * close[t] * (1 + CORR_FACTOR)
                initial_money -= total_buy
                inventory.append(total_buy)
                quantity += buy_units
    ## Can we add a condition for the sell to execute like 1. if the bought_price < (1 + CORR_FACTOR) * cost(t) or the current cost(t) > ((1 + CORR_FACTOR)* ( bought_price or buy_price )  )         
            elif action == 2 and len(inventory) > 0:
                if quantity > self.max_sell:
                    sell_units = self.max_sell
                else:
                    sell_units = quantity
                quantity -= sell_units
                # Changed the total_sell and add correction_factor = 0.01
                total_sell = sell_units * close[t] * (1 - CORR_FACTOR)
                ##For kite CNC
               # total_sell = (sell_units * close[t] * (1 - CORR_FACTOR)) - D_FACTOR
                initial_money += total_sell

            state = next_state
      ## Added the COOR_FACTOR to the rewards so that rewards ar always positive A reward >= +CORR_FACTOR_2 
        reward = (((initial_money - starting_money) / starting_money) * 100) - CORR_FACTOR_2
        return reward

    def fit(self, data_to_train, iterations, checkpoint):
        self.es.train(data_to_train, iterations, print_every=checkpoint)

    def buy(self, close, start=0):
        initial_money = self.initial_money
        state = get_state(close, start, self.window_size + 1)
        starting_money = initial_money
        states_sell = []
        states_buy = []
        inventory = []
        quantity = 0
        for t in range(start, len(close) - 1, self.skip):
            action, buy = self.act(state)
            next_state = get_state(close, t + 1, self.window_size + 1)
            if action == 1 and initial_money >= close[t]:
                if buy < 0:
                    buy = 1
                if buy > self.max_buy:
                    buy_units = self.max_buy
                else:
                    buy_units = buy
                # Changed the total_buy and add correction_factor = 0.01
                total_buy = buy_units * close[t] * (1 + CORR_FACTOR)
                initial_money -= total_buy
                inventory.append(total_buy)
                quantity += buy_units
                states_buy.append(t)
                print(
                    'day %d: buy %d units at price %f, total balance %f'
                    % (t, buy_units, total_buy, initial_money)
                )
    ## Can we add a condition for the sell to execute like 1. if the bought_price < (1 + CORR_FACTOR) * current cost(t) or the current cost(t) > ((1 + CORR_FACTOR)* (bought_price or buy_price ) )                        
            elif action == 2 and len(inventory) > 0:
                bought_price = inventory.pop(0)
                if quantity > self.max_sell:
                    sell_units = self.max_sell
                else:
                    sell_units = quantity
                if sell_units < 1:
                    continue
                quantity -= sell_units
                # Changed the total_sell and add correction_factor = 0.01
                total_sell = (sell_units * close[t] * (1 - CORR_FACTOR))
               ##For kite CNC
               # total_sell = (sell_units * close[t] * (1 - CORR_FACTOR)) - D_FACTOR
                initial_money += total_sell
                states_sell.append(t)
                try:
                    invest = ((total_sell - bought_price) / bought_price) * 100
                except:
                    invest = 0
                print(
                    'day %d, sell %d units at price %f, investment %f %%, total balance %f,'
                    % (t, sell_units, total_sell, invest, initial_money)
                )
            state = next_state

        ## Added the COOR_FACTOR to the invest so that invest ar always positive & invest >= +CORR_FACTOR_2 
        invest = (((initial_money - starting_money) / starting_money) * 100) - CORR_FACTOR_2

        print(
            '\ntotal gained %f, total investment %f %%'
            % (initial_money - starting_money, invest)
        )
        plt.figure(figsize=(20, 10))
        plt.plot(close, label='true close', c='g')
        plt.plot(
            close, 'X', label='predict buy', markevery=states_buy, c='b'
        )
        plt.plot(
            close, 'o', label='predict sell', markevery=states_sell, c='r'
        )
        plt.legend()
        plt.savefig('figures/buy.png')
        # plt.show(block=True)

    def predict(self, data):
        state = get_state(data, self.window_size, self.window_size + 1)

        action, buy = self.act(state)
        return action, buy


def best_agent(
        data_to_train, window_size, skip, population_size, sigma, learning_rate, size_network
):
    model = Model(window_size, size_network, 3)
    agent = Agent(
        population_size,
        sigma,
        learning_rate,
        model,
        100000,
        150,
        150,
        skip,
        window_size,
    )
    try:
        agent.fit(data_to_train, 100, 50)
        return agent, agent.es.reward_function(agent.es.weights, data_to_train)
    except:
        return None, 0


def find_best_agent(data_to_train):
    def _find_best_agent(
            window_size, skip, population_size, sigma, learning_rate, size_network
    ):
        global accbest , best_model_agent
        param = {
            'window_size': int(np.around(window_size)),
            'skip': int(np.around(skip)),
            'population_size': int(np.around(population_size)),
            'sigma': max(min(sigma, 1), 0.0001),
            'learning_rate': max(min(learning_rate, 0.5), 0.000001),
            'size_network': int(np.around(size_network)),
        }
        print('\nSearch parameters %s' % (param))
        model, investment = best_agent(data_to_train, **param)
        print('stop after 100 iteration with investment %f' % (investment))
        if investment > accbest:
            best_model_agent = copy.deepcopy(model)
            accbest = investment
        return investment

    return _find_best_agent


def new_agent(NN_BAYESIAN):
    model = Model(input_size=int(np.around(NN_BAYESIAN.res['max']['max_params']['window_size'])),
                  layer_size=int(np.around(NN_BAYESIAN.res['max']['max_params']['size_network'])),
                  output_size=3)
    agent = Agent(population_size=int(np.around(NN_BAYESIAN.res['max']['max_params']['population_size'])),
                  sigma=NN_BAYESIAN.res['max']['max_params']['sigma'],
                  learning_rate=NN_BAYESIAN.res['max']['max_params']['learning_rate'],
                  model=model,
                  money=100000,
                  max_buy=150,
                  max_sell=150,
                  skip=int(np.around(NN_BAYESIAN.res['max']['max_params']['skip'])),
                  window_size=int(np.around(NN_BAYESIAN.res['max']['max_params']['window_size'])))
    return agent


def load_model(path):
    with open(path, 'rb') as fopen:
        model = pickle.load(fopen)

    return model


if __name__ == "__main__":
    # TSLA Time Period: **Mar 23, 2018 - Mar 23, 2019**

    # LOAD DATA
    print('Load the data ---------------------')
    df = pd.read_csv('data/data_10_sbin_1min_22_jun_28_aug.csv')
    df.replace([np.inf, -np.inf], np.nan)
    ## This code will convert the inf with NaN drop Nan values
    df[df == np.inf] = np.nan
    ## This code will replace the NAN values with mean
    df.fillna(df.mean(), inplace=True)
    df.head()
    ## show the float values in the data 
    df.info()
    
    close = df.Close.values.tolist()
    window_size = 32
    skip = 5

    # FIND BEST PARAMS WITH BAYESIAN OPTIM
    print('Find the best params with bayesian optim ---------------------')
    # Random_state is set for the repetitive experiment.
    accbest = 0.0
    best_model_agent = None

    np.random.seed(42)
    NN_BAYESIAN = BayesianOptimization(
        find_best_agent(close),
        {
            'window_size': (1280, 7040),
            'skip': (1, 15),
            'population_size': (1, 50),
            'sigma': (0.01, 0.99),
            'learning_rate': (0.000001, 0.49),
            'size_network': (10, 1000),
        },
        random_state=42
    )

    NN_BAYESIAN.maximize(init_points=30, n_iter=50, acq='ei', xi=0.0)
    print('Best AGENT accuracy value: %f' % NN_BAYESIAN.res['max']['max_val'])
    print('Best AGENT parameters: ', NN_BAYESIAN.res['max']['max_params'])

    # Save parameters.
    print('Save bayesian params ---------------------')
    copy_model = copy.deepcopy(NN_BAYESIAN.res)
    with open('models/bayesian_parameters_10_sbin_1min_22_jun_28_aug_commission_0007.pkl', 'wb') as fopen:
        pickle.dump(copy_model, fopen)

    # TRAIN THE MODEL WITH BEST PARAMS
    print('Train the model with best params ---------------------')
    with open('models/bayesian_parameters_10_sbin_1min_22_jun_28_aug_commission_0007.pkl', 'rb') as fopen:
        NN_BAYESIAN.res = pickle.load(fopen)
    agent = new_agent(NN_BAYESIAN)
    
    epochs = 375
    checkpoints = 25
    try:
        agent.fit(close, epochs, checkpoints)
    except RewardsException as err:
        print(err)
        print("Run with %d iterations" % err.i)
        agent = new_agent(NN_BAYESIAN)
        agent.fit(close, err.i, checkpoints)

    # EXPORT the model
#    print('Exporting best_agent_model ---------------------')
#    copy_model = copy.deepcopy(best_model_agent.model)
#    with open('models/model_test_10_sbin_1min_22_jun_28_aug_commission_0007.pkl', 'wb') as fopen:
#        pickle.dump(copy_model, fopen)
#    print('model exported')
    print('Exporting best_agent_model ---------------------')
    copy_model = copy.deepcopy(best_model_agent)
    with open('models/agent_test_10_sbin_1min_22_jun_28_aug_commission_0007_commission_007.pkl', 'wb') as fopen:
        pickle.dump(copy_model, fopen)
    print('best_agent_model exported')
    
#    best_model_agent.buy(close)
    
    # EXPORT the model
#    print('Exporting Agent.model Swapnil plz Wait---------------------')
#    copy_model = copy.deepcopy(agent.model)
#    with open('models/agent_model_test_10_sbin_1min_22_jun_28_aug_commission_0007.pkl', 'wb') as fopen:
#        pickle.dump(copy_model, fopen)
#    print('agent.model exported')
    
    print('Exporting Agent_Fit Swapnil plz Wait---------------------')
    copy_model = copy.deepcopy(agent)
    with open('models/agent_fit_test_10_sbin_1min_22_jun_28_aug_commission_0007_commission_007.pkl', 'wb') as fopen:
        pickle.dump(copy_model, fopen)
    print('agent exported')
    
#    agent.buy(close)
    

