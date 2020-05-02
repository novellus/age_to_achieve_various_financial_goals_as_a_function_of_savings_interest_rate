import math
import matplotlib
import pprint
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict


def calc_x_inflation(x_n, n, interest_rate, annual_gross_earn_rate, annual_cost_of_living, inflation_rate, earning=False):
    # x_n+1 = x_n * 1.01 - 70000*1.03^n
    # x(n+1) = x(n) * 1.01 - 70000*1.03^n
    # x_np1 = x_n * interest_rate - annual_cost_of_living*math.pow(inflation_rate, n)
    x_np1 = x_n * interest_rate + ((annual_gross_earn_rate if earning else 0.0) - annual_cost_of_living) * (math.pow(inflation_rate, n))
    return x_np1


def calc_instantaneous_cost_of_living(n, annual_cost_of_living, inflation_rate):
    x = annual_cost_of_living * math.pow(inflation_rate, n)
    return x


def calc_instantaneous_breakeven(n, interest_rate, annual_cost_of_living, inflation_rate):
    x = calc_instantaneous_cost_of_living(n, annual_cost_of_living, inflation_rate) / (interest_rate - 1)
    return x


def calc_breakeven_with_inflation(n, interest_rate, inflation_rate, annual_cost_of_living):
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
    x = calc_instantaneous_cost_of_living(n, annual_cost_of_living, inflation_rate) / (interest_rate - inflation_rate)
    return x


def simulate_until_end_condition(initial_age, initial_money, annual_cost_of_living, annual_gross_earn_rate, interest_rate, inflation_rate, retirement_age,
                                 end_num_years_after_retirement=None, end_after_num_years_sim_time=300, 
                                 end_if_out_of_money=True, end_if_breakeven_with_inflation=True, end_at_age=None):
    n = 0  # years passed since initial_age. Used to calculate inflation adjusted values
    x = initial_money  # money at each timestep

    possible_to_breakeven_with_inflation = bool(interest_rate > inflation_rate)

    # earn money until retirement
    retired = False
    num_years_after_retirement = None
    data = defaultdict(list)
    while True:
        # calcs
        age = n + initial_age

        if possible_to_breakeven_with_inflation:
            x_breakeven_with_inflation = calc_breakeven_with_inflation(n, interest_rate, inflation_rate, annual_cost_of_living)
        else:
            x_breakeven_with_inflation = None

        # log data
        data['x'].append(x)
        data['age'].append(age)
        data['retired'].append(retired)
        data['num_years_after_retirement'].append(num_years_after_retirement)
        data['x_breakeven_with_inflation'].append(x_breakeven_with_inflation)

        # end conditions
        if end_if_out_of_money and x <= 0:
            end_condition = 'out_of_money'
            break

        if end_if_breakeven_with_inflation and possible_to_breakeven_with_inflation and x >= x_breakeven_with_inflation:
            end_condition = 'breakeven_with_inflation'
            break

        if end_after_num_years_sim_time and n >= end_after_num_years_sim_time:
            end_condition = 'num_years_sim_time'
            break

        if end_at_age and age >= end_at_age:
            end_condition = 'age'
            break

        if end_num_years_after_retirement and num_years_after_retirement is not None and num_years_after_retirement >= end_num_years_after_retirement:
            end_condition = 'num_years_after_retirement'
            break

        # simulation
        x = calc_x_inflation(x, n, interest_rate, annual_gross_earn_rate, annual_cost_of_living, inflation_rate, earning = not retired)
        n += 1

        if age == retirement_age:
            retired = True
            num_years_after_retirement = 0

        if age > retirement_age:
            num_years_after_retirement += 1

    return end_condition, data

if __name__ == '__main__':
    # params
    initial_age = 28
    initial_money = 300000
    annual_cost_of_living = 38000  # at time of initial design, and sustained *times inflation rates*
    annual_gross_earn_rate = 75000 # while working, and sustained *times inflation rates*
    # annual_gross_earn_rate = 38000 # while working, and sustained *times inflation rates*
    # annual_gross_earn_rate = 125000 # while working, and sustained *times inflation rates*
    inflation_rate = 1.0323
    # inflation_rate = 1.0
    likely_death_age = 120
    # interest_rate = earned on savings

    # plot setup
    descriptor = (f'Years of survival after retirement as a function of age of retirement and annual interest rate. (evaluated at 1-year intervals)\n' + 
                  f'initial_age = {initial_age}, inflation_rate = {(inflation_rate-1)*100:.3}% (annual), initial_money = {initial_money}, annual_gross_earn_rate = {annual_gross_earn_rate}, annual_cost_of_living = {annual_cost_of_living}')

    plt.figure()
    # plt.gca().xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1.0))
    plt.xlabel('age of retirement')
    plt.ylabel('average happiness (scale out of 10)')
    plt.title(descriptor)
    plt.minorticks_on()
    plt.grid(b=True, which='major', color='black', linestyle='-')
    plt.grid(b=True, which='minor', color='red', linestyle='--')
    plt.xlim(initial_age, likely_death_age)
    # plt.ylim(0, 100)
    plt.ylim(6.202806122, 7.665391156)

    # colors = ['red', 'green', 'blue', 'orange', 'yellow', 'black', 'brown', 'gray', 'cyan', 'magenta']
    colors = ['red', 'green', 'blue', 'orange', 'black', 'brown', 'gray', 'cyan', 'magenta']

    # # reference indicating enopugh capital accrued to surive to likely_death_age
    # region_patches = []
    # previous_y = None
    # for i_region, difference in enumerate(np.linspace(0, 80, 5)):
    #     x, y = [initial_age, likely_death_age], [likely_death_age - initial_age - difference, 0 - difference]
        
    #     if previous_y is None:
    #         upper_bound = 100
    #     else:
    #         upper_bound = previous_y
    #     previous_y = y
        
    #     plt.fill_between(x, y, upper_bound, facecolor=colors[(i_region)%len(colors)], alpha=0.1)
    #     region_patch = matplotlib.patches.Patch(color=colors[(i_region)%len(colors)], label=f'enough savings to survive until age {int(likely_death_age - difference)}')
    #     region_patches.append(region_patch)

    # # reference slopes indicating ratio of years free to years working
    # for i_plot, slope in enumerate([2/5.0, 1.0, 1.2, 5/2.0]):
    #     # slope is years free / years worked
    #     plt.plot([initial_age, likely_death_age], [8, 8 + slope * (likely_death_age - initial_age)], c=colors[(i_plot+1)%len(colors)], marker=None, linestyle='--', label=f'reference slope {slope:.3}')

    # siumulation setup
    # interest_rates = np.linspace(1, 1.13, 14)
    # interest_rates = np.geomspace(1, 1.13, 15)
    # interest_rates = list(interest_rates) + [inflation_rate, 1.046]
    # interest_rates = list(np.geomspace(1, inflation_rate, 4, endpoint=False)) + list(np.geomspace(inflation_rate, 1.045, 6, endpoint=False)) + list(np.geomspace(1.045, 1.13, 4))
    interest_rates = [1.0, 1.001, 1.002]
    interest_rates = reversed(sorted(interest_rates))

    # siumulation
    for i_plot, interest_rate in enumerate(interest_rates):
        data = defaultdict(list)
        # print(f'processing {interest_rate}')

        for retirement_age in range(initial_age, likely_death_age + 1):
            end_condition, run_data  = simulate_until_end_condition(initial_age = initial_age,
                                                                    initial_money = initial_money,
                                                                    annual_cost_of_living = annual_cost_of_living,
                                                                    annual_gross_earn_rate = annual_gross_earn_rate,
                                                                    interest_rate = interest_rate,
                                                                    inflation_rate = inflation_rate,
                                                                    retirement_age = retirement_age,
                                                                    end_num_years_after_retirement = None,
                                                                    end_after_num_years_sim_time = None, 
                                                                    end_if_out_of_money = True,
                                                                    end_if_breakeven_with_inflation = False,
                                                                    # end_at_age = 121)
                                                                    end_at_age = 10000)

            # log data
            # print(f'\tretirement_age {retirement_age} -> end_condition {end_condition}, {run_data["num_years_after_retirement"][-1]}')
            data['retirement_age'].append(retirement_age)
            data['num_years_survived_after_retirement'].append(run_data['num_years_after_retirement'][-1])
            data['ratio_num_years_survived_after_retirement'].append(run_data['num_years_after_retirement'][-1]/float(retirement_age))
            data['average_happiness'].append((float(retirement_age)*6.202806122 + run_data['num_years_after_retirement'][-1]*7.665391156)/(float(retirement_age) + run_data['num_years_after_retirement'][-1]))

        plt.plot(data['retirement_age'], data['average_happiness'], c=colors[i_plot%len(colors)], marker='x', markersize=2, label=f'average happiness, at interest_rate = {(interest_rate - 1.0) * 100 :.3}%')

    handles, labels = plt.gca().get_legend_handles_labels()
    # plt.legend(loc=1, handles = region_patches + handles)
    plt.legend(loc=1)
    plt.show()
