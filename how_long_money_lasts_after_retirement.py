# program parameters
interest_rate = 1.01  # earned on savings
inflation_rate = 1.0323
annual_cost_of_living = 38000  # at time of initial design, and sustained *times inflation rates*
annual_gross_earn_rate = 75000 # while working, and sustained *times inflation rates*
initial_money = 300000
initial_age = 28
assumed_death_age = 120


# static data and functions
import math
import pprint
import numpy as np
from matplotlib import pyplot as plt


program_descriptor = f'''interest_rate = {interest_rate}, inflation_rate = {inflation_rate}
initial_money = {initial_money}, annual_gross_earn_rate = {annual_gross_earn_rate}, annual_cost_of_living = {annual_cost_of_living}
initial_age = {initial_age}, assumed_death_age = {assumed_death_age}'''

possible_to_breakeven_with_inflation = bool(interest_rate > inflation_rate)


def calc_x_inflation(x_n, n, earning=False):
    # x_n+1 = x_n * 1.01 - 70000*1.03^n
    # x(n+1) = x(n) * 1.01 - 70000*1.03^n
    # x_np1 = x_n * interest_rate - annual_cost_of_living*math.pow(inflation_rate, n)
    x_np1 = x_n * interest_rate + ((annual_gross_earn_rate if earning else 0.0) - annual_cost_of_living) * (math.pow(inflation_rate, n))
    return x_np1


def calc_instantaneous_cost_of_living(n):
    x = annual_cost_of_living * math.pow(inflation_rate, n)
    return x


def calc_instantaneous_breakeven(n):
    x = calc_instantaneous_cost_of_living(n) / (interest_rate - 1)
    return x


def calc_breakeven_with_inflation(n):
    '''have 1.45e8
    cost of living 3.28e6
    breakeven 8.17e7
    age 149
    retired at 118
    interest 0.04
    inflation 0.0323

    earned with interest = 0.04 * 1.45e8 = 5.8e6
    spent = 3.28e6
    net earn = 5.8e6 - 3.28e6 = 2.52e6
    amount net earn to offset inflation = 0.0323 * 1.45e8 = 4.6835e6
    want: earned with interest = spent + amount net earn to offset inflation
    x * (interest_rate - 1) = calc_instantaneous_cost_of_living + x * (inflation_rate - 1)
    => x * (interest_rate - inflation_rate) = calc_instantaneous_cost_of_living
    => x = calc_instantaneous_cost_of_living / (interest_rate - inflation_rate)'''
    x = calc_instantaneous_cost_of_living(n) / (interest_rate - inflation_rate)
    return x


# simulation
data_summary = []
data_runs = []
data_runs_descriptor = []
data_runs_end_conditions = []
for retirement_age in range(initial_age, assumed_death_age + 1):
    n = 0  # years passed since initial_age. Used to calculate inflation adjusted values
    x = initial_money  # money at each timestep
    data_runs.append([])
    data_runs[-1].append([])
    data_runs[-1][-1].append(n + initial_age)  # 0
    data_runs[-1][-1].append(x)                # 1
    data_runs_descriptor.append('retirement_age = ' + str(retirement_age))

    # earn money until retirement
    while n + initial_age < retirement_age and (x < calc_breakeven_with_inflation(n) if possible_to_breakeven_with_inflation else True):
        x = calc_x_inflation(x, n, earning=True)
        n += 1
        data_runs[-1].append([])
        data_runs[-1][-1].append(n + initial_age)  # 0
        data_runs[-1][-1].append(x)                # 1

    # retire, and calculate age that we run out of money
    # but don't calculate forever if we exceed breakeven
    while x > 0 and (x < calc_breakeven_with_inflation(n) if possible_to_breakeven_with_inflation else True) and n < 300:
        x = calc_x_inflation(x, n)
        n += 1
        data_runs[-1].append([])
        data_runs[-1][-1].append(n + initial_age)  # 0
        data_runs[-1][-1].append(x)                # 1

    # calculate end of run condition
    age_end_of_run = n + initial_age
    data_runs_end_conditions.append([])
    data_runs_end_conditions[-1].append(age_end_of_run)  # 0
    if not possible_to_breakeven_with_inflation or x < calc_breakeven_with_inflation(n):
        age_run_out_of_money = age_end_of_run
        years_survive_after_retiring = age_run_out_of_money - retirement_age
        data_runs_end_conditions[-1].append(False)       # 1
    else:
        age_run_out_of_money = float('inf')
        years_survive_after_retiring = float('inf')
        data_runs_end_conditions[-1].append(True)        # 1

    data_summary.append([])
    data_summary[-1].append(retirement_age)                 # 0
    data_summary[-1].append(age_run_out_of_money)           # 1
    data_summary[-1].append(years_survive_after_retiring)   # 2


# stats about runs
max_age_across_runs = 0
max_money_across_runs = 0
for i_run, run in enumerate(data_runs):
    for point in run:
        max_age_across_runs = max(max_age_across_runs, point[0])
        max_money_across_runs = max(max_money_across_runs, point[1])

achieved_breakeven_with_inflation = False
age_breakeven_with_inflation = None
money_at_breakeven_with_inflation = None
for i_run, end_conditions in enumerate(data_runs_end_conditions):
    if end_conditions[1]:
        achieved_breakeven_with_inflation = True
        age_breakeven_with_inflation = end_conditions[0]
        try:
            money_at_breakeven_with_inflation = data_runs[i_run][-1][1]
        except:
            print(i_run)
            print(data_runs[i_run])
            raise
        print(f'Achieve breakeven with inflation at age {age_breakeven_with_inflation}')
        print(money_at_breakeven_with_inflation)
        break
else:
    print('Never achieve breakeven with inflation')


# stats agnostic to which data run it is
data_run_stats = []
for n in range(max_age_across_runs - initial_age + 1):
    data_run_stats.append([n + initial_age])                          # 0
    data_run_stats[-1].append(calc_instantaneous_breakeven(n))        # 1
    data_run_stats[-1].append(calc_instantaneous_cost_of_living(n))   # 2
    data_run_stats[-1].append(calc_breakeven_with_inflation(n))       # 3


# zipping
zd_summary = list(zip(*data_summary))
zd_runs = [list(zip(*data_runs_entry)) for data_runs_entry in data_runs]
zd_run_stats = list(zip(*data_run_stats))


# plots
plt.figure()
plt.plot(zd_summary[0], zd_summary[1], c='green', marker='x', markersize=2)
plt.xlabel('age of retirement')
plt.ylabel('age of running out of money')


plt.figure()
plt.plot(zd_summary[0], zd_summary[2], c='blue', marker='x', markersize=2)
plt.xlabel('age of retirement')
plt.ylabel('years survive after retiring')


colors = ['red', 'green', 'blue', 'orange', 'yellow', 'black', 'brown', 'gray', 'cyan', 'magenta']
plt.figure()
for i_plot, i_data_runs_index in enumerate(range(0, len(data_runs), 10)):
    plt.plot(zd_runs[i_data_runs_index][0], zd_runs[i_data_runs_index][1], c=colors[i_plot%len(colors)], marker='x', markersize=2, label=data_runs_descriptor[i_data_runs_index])
# plt.plot(zd_run_stats[0], zd_run_stats[1], c='#00AAAA', marker='x', markersize=2, label='instantaneous breakeven cash')
plt.plot(zd_run_stats[0], zd_run_stats[2], c='#00FF00', marker='x', markersize=2, label='instantaneous cost of living')
if possible_to_breakeven_with_inflation:
    plt.plot(zd_run_stats[0], zd_run_stats[3], c='#AAAA00', marker='x', markersize=2, label='breakeven with inflation')
plt.xlabel('age')
plt.ylabel('money')
if achieved_breakeven_with_inflation:
    plt.xlim(initial_age, age_breakeven_with_inflation)
    plt.ylim(0, money_at_breakeven_with_inflation)
else:
    plt.xlim(initial_age, max_age_across_runs)
    plt.ylim(0, max_money_across_runs)
plt.legend(loc=1)
plt.title(program_descriptor)



plt.show()
