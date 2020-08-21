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
    amount net earn to offset inflation = 0.0323 * 1.45e8 = 4.4835e6
    want: earned with interest = spent + amount net earn to offset inflation
    x * (interest_rate - 1) = calc_instantaneous_cost_of_living + x * (inflation_rate - 1)
    => x * (interest_rate - inflation_rate) = calc_instantaneous_cost_of_living
    => x = calc_instantaneous_cost_of_living / (interest_rate - inflation_rate)'''
    x = calc_instantaneous_cost_of_living(n, annual_cost_of_living, inflation_rate) / (interest_rate - inflation_rate)
    return x


def simulate_until_end_condition(initial_age, initial_money, annual_cost_of_living, annual_gross_earn_rate, interest_rate, inflation_rate, retirement_age,
                                 end_num_years_after_retirement=None, end_after_num_years_sim_time=300, 
                                 end_if_out_of_money=True, end_if_breakeven_with_inflation=True, end_at_age=None,
                                 n=None):
    if n is None:
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

        if age >= retirement_age:
            retired = True
            num_years_after_retirement = age - retirement_age

        if possible_to_breakeven_with_inflation:
            x_breakeven_with_inflation = calc_breakeven_with_inflation(n, interest_rate, inflation_rate, annual_cost_of_living)
            broke_even_with_inflation = (x >= x_breakeven_with_inflation)
        else:
            x_breakeven_with_inflation = None
            broke_even_with_inflation = False

        # log data
        data['n'].append(n)
        data['x'].append(x)
        data['age'].append(age)
        data['retired'].append(retired)
        data['num_years_after_retirement'].append(num_years_after_retirement)
        data['x_breakeven_with_inflation'].append(x_breakeven_with_inflation)
        data['broke_even_with_inflation'].append(broke_even_with_inflation)

        # end conditions
        if end_if_out_of_money and x <= 0:
            end_condition = 'out_of_money'
            break

        if end_if_breakeven_with_inflation and possible_to_breakeven_with_inflation and broke_even_with_inflation:
            end_condition = 'breakeven_with_inflation'
            break

        if end_after_num_years_sim_time is not None and n >= end_after_num_years_sim_time:
            end_condition = 'num_years_sim_time'
            break

        if end_at_age is not None and age >= end_at_age:
            end_condition = 'age'
            break

        if end_num_years_after_retirement is not None and num_years_after_retirement is not None and num_years_after_retirement >= end_num_years_after_retirement:
            end_condition = 'num_years_after_retirement'
            break

        # simulation
        x = calc_x_inflation(x, n, interest_rate, annual_gross_earn_rate, annual_cost_of_living, inflation_rate, earning = not retired)
        n += 1

        # repeated end conditions
        if end_if_out_of_money and x <= 0:
            end_condition = 'out_of_money'
            break

    return end_condition, data

if __name__ == '__main__':
    # params
    initial_age = 29
    # retirement_age = initial_age
    # initial_money = 435000
    initial_money = 300000
    annual_cost_of_living = 38000  # at time of initial design, and sustained *times inflation rates*
    annual_gross_earn_rate = 69000 # while working, and sustained *times inflation rates*
    # annual_gross_earn_rate = 38000 # while working, and sustained *times inflation rates*
    # annual_gross_earn_rate = 100000 # while working, and sustained *times inflation rates*
    inflation_rate = 1.0323
    # inflation_rate = 1.0
    maximum_death_age = 124
    # interest_rate = 1.02  # earned on savings
    working_happiness = -0.7971938776 # on a 0-10 scale, minus 7 to center scale at 0
    free_happiness = 0.6653911565

    # plot setup
    descriptor = (f'Integrated happiness over lifetime and death age as a function of savings interest rate and retirement age. (evaluated at discrete 1-year intervals)\n' +
                  f'Comparing retirement strategies: immediate retirement, optimal retirement age (maximizes integrated happiness), immediate retirement + run out of money + work again + optimal 2nd retirement (maximizes integrated happiness), and static retirement at age where integrated happiness least squares fits to optimal.\n' +
                  f'initial_age = {initial_age}, maximum_death_age = {maximum_death_age+1}, inflation_rate = {(inflation_rate-1)*100:.3}% (annual), initial_money = {initial_money}, annual_gross_earn_rate = {annual_gross_earn_rate}, annual_cost_of_living = {annual_cost_of_living}\n' +
                  f'working_happiness = {working_happiness}, free_happiness = {free_happiness} (integrated value for one year, zero centered)')

    # assuming immediate retirement
    # maximizing integrated happiness over lifetime

    plt.figure()
    # plt.gca().xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1.0))
    # 'working_happiness (scale out of 10)'
    plt.xlabel('savings annual interest or depreciation')
    plt.ylabel('age')
    plt.title(descriptor)
    plt.minorticks_on()
    plt.grid(b=True, which='major', color='black', linestyle='-')
    plt.grid(b=True, which='minor', color='red', linestyle='--')
    plt.gca().xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda val, pos: f'{(val-1)*100:.3}%'))
    plt.xlim(0.7, 1.3)
    plt.ylim(initial_age - 1, maximum_death_age + 4)

    # colors = ['red', 'green', 'blue', 'orange', 'yellow', 'black', 'brown', 'gray', 'cyan', 'magenta']
    colors = ['red', 'green', 'blue', 'orange', 'black', 'brown', 'gray', 'cyan', 'magenta']

    # # reference indicating enopugh capital accrued to surive to maximum_death_age
    region_patches = []
    # previous_y = None
    # for i_region, difference in enumerate(np.linspace(0, 80, 5)):
    #     x, y = [initial_age, maximum_death_age], [maximum_death_age - initial_age - difference, 0 - difference]
        
    #     if previous_y is None:
    #         upper_bound = 100
    #     else:
    #         upper_bound = previous_y
    #     previous_y = y
        
    #     plt.fill_between(x, y, upper_bound, facecolor=colors[(i_region)%len(colors)], alpha=0.1)
    #     region_patch = matplotlib.patches.Patch(color=colors[(i_region)%len(colors)], label=f'enough savings to survive until age {int(maximum_death_age - difference)}')
    #     region_patches.append(region_patch)

    # # reference slopes indicating ratio of years free to years working
    # for i_plot, slope in enumerate([2/5.0, 1.0, 1.2, 5/2.0]):
    #     # slope is years free / years worked
    #     plt.plot([initial_age, maximum_death_age], [8, 8 + slope * (maximum_death_age - initial_age)], c=colors[(i_plot+1)%len(colors)], marker=None, linestyle='--', label=f'reference slope {slope:.3}')

    # siumulation setup
    # interest_rates = [1.035]
    # interest_rates = np.linspace(1, 1.13, 14)
    # interest_rates = np.geomspace(1, 1.13, 15)
    # interest_rates = list(interest_rates) + [inflation_rate, 1.046]
    # interest_rates = list(np.geomspace(1, inflation_rate, 4, endpoint=False)) + list(np.geomspace(inflation_rate, 1.045, 6, endpoint=False)) + list(np.geomspace(1.045, 1.13, 4))
    # interest_rates = [1.04 - x for x in np.geomspace(1, 1.04, 11)]
    # interest_rates = [1.04-(x-1)*10/9.0*0.004 for x in np.geomspace(1,10,20)]
    # interest_rates = [1.023]
    interest_rates = list(np.linspace(0.7, 1.30, 3000))
    interest_rates = list(sorted(interest_rates))

    # working_happinesses = list(np.linspace(0.0, 10.0, 100))
    # working_happinesses = list(reversed(sorted(working_happinesses)))

    # simulation 1 - immediate retirement
    data_immediate_retirement_interest_rate_meta = defaultdict(list)
    retirement_age = initial_age
    for interest_rate in interest_rates:
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
                                                                end_at_age = maximum_death_age + 1)
                                                                # end_at_age = 10000)

        # log data
        # print(f'\tinterest_rate {interest_rate} -> end_condition {end_condition}, {run_data["num_years_after_retirement"][-1]}')
        data_immediate_retirement_interest_rate_meta['interest_rate'].append(interest_rate)
        data_immediate_retirement_interest_rate_meta['retirement_age'].append(retirement_age)
        data_immediate_retirement_interest_rate_meta['broke_even_with_inflation'].append(run_data['broke_even_with_inflation'][-1])
        data_immediate_retirement_interest_rate_meta['death_age'].append(run_data['age'][-1])

        if working_happiness >= free_happiness:
            data_immediate_retirement_interest_rate_meta['integrated_happiness'].append(working_happiness*run_data['age'][-1])
        # elif run_data['broke_even_with_inflation'][-1]:
        #     data_immediate_retirement_interest_rate_meta['integrated_happiness'].append(free_happiness)
        else:
            data_immediate_retirement_interest_rate_meta['integrated_happiness'].append(float(retirement_age)*working_happiness + run_data['num_years_after_retirement'][-1]*free_happiness)

    # simulation 2 - compute optimal retirement age, maximizing integrated happiness
    data_optimal_retirement_interest_rate_meta = defaultdict(list)
    for interest_rate in interest_rates:
        data_run_meta = defaultdict(list)

        for retirement_age in range(initial_age, maximum_death_age + 1):
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
                                                                    end_at_age = maximum_death_age + 1)
                                                                    # end_at_age = 10000)

            # log data
            data_run_meta['retirement_age'].append(retirement_age)
            data_run_meta['broke_even_with_inflation'].append(run_data['broke_even_with_inflation'][-1])
            data_run_meta['death_age'].append(run_data['age'][-1])

            if working_happiness >= free_happiness:
                data_run_meta['integrated_happiness'].append(working_happiness*run_data['age'][-1])
            # elif run_data['broke_even_with_inflation'][-1]:
            #     data_run_meta['integrated_happiness'].append(free_happiness)
            else:
                data_run_meta['integrated_happiness'].append(float(retirement_age)*working_happiness + run_data['num_years_after_retirement'][-1]*free_happiness)

        # compute optimal retirement age
        max_happiness, retirement_age_for_max_happiness = -float('inf'), None
        broke_even_with_inflation = None
        death_age = None
        for i_integrated_happiness, integrated_happiness in enumerate(data_run_meta['integrated_happiness']):
            if integrated_happiness >= max_happiness or math.isclose(integrated_happiness, max_happiness):  # prefer latest retirement to maximize secondary oppurtunities
                max_happiness = integrated_happiness
                retirement_age_for_max_happiness = data_run_meta['retirement_age'][i_integrated_happiness]
                broke_even_with_inflation = data_run_meta['broke_even_with_inflation'][i_integrated_happiness]
                death_age = data_run_meta['death_age'][i_integrated_happiness]

        data_optimal_retirement_interest_rate_meta['interest_rate'].append(interest_rate)
        data_optimal_retirement_interest_rate_meta['max_happiness'].append(max_happiness)
        data_optimal_retirement_interest_rate_meta['retirement_age_for_max_happiness'].append(retirement_age_for_max_happiness)
        data_optimal_retirement_interest_rate_meta['broke_even_with_inflation'].append(broke_even_with_inflation)
        data_optimal_retirement_interest_rate_meta['death_age'].append(death_age)

    # simulation 3 - immediate retirement, then go back to work once we run out of money computing optimal retirement age from there
    initial_retirement_age = initial_age
    data_double_retirement_interest_rate_meta = defaultdict(list)
    for interest_rate in interest_rates:
        # retire immediately and simulate until run out of money or maximum_death_age
        end_condition_1, run_data_1  = simulate_until_end_condition(initial_age = initial_age,
                                                                    initial_money = initial_money,
                                                                    annual_cost_of_living = annual_cost_of_living,
                                                                    annual_gross_earn_rate = annual_gross_earn_rate,
                                                                    interest_rate = interest_rate,
                                                                    inflation_rate = inflation_rate,
                                                                    retirement_age = initial_retirement_age,
                                                                    end_num_years_after_retirement = None,
                                                                    end_after_num_years_sim_time = None, 
                                                                    end_if_out_of_money = True,
                                                                    end_if_breakeven_with_inflation = False,
                                                                    end_at_age = maximum_death_age + 1)
                                                                    # end_at_age = 10000)


        # now that we've run out of money, go back to work and compute new optimal retirement age
        if end_condition_1 == 'age':
            # skip secondary simlation and data logging if we already made it to maximum_death_age
            continue

        data_run_meta = defaultdict(list)
        for retirement_age in range(run_data_1['age'][-1], maximum_death_age + 1):
            end_condition_2, run_data_2  = simulate_until_end_condition(initial_age = initial_age,
                                                                        n = run_data_1['n'][-1],
                                                                        initial_money = run_data_1['x'][-1],
                                                                        annual_cost_of_living = annual_cost_of_living,
                                                                        annual_gross_earn_rate = annual_gross_earn_rate,
                                                                        interest_rate = interest_rate,
                                                                        inflation_rate = inflation_rate,
                                                                        retirement_age = retirement_age,
                                                                        end_num_years_after_retirement = None,
                                                                        end_after_num_years_sim_time = None, 
                                                                        end_if_out_of_money = True,
                                                                        end_if_breakeven_with_inflation = False,
                                                                        end_at_age = maximum_death_age + 1)
                                                                        # end_at_age = 10000)

            # log data
            data_run_meta['retirement_age'].append(retirement_age)
            data_run_meta['broke_even_with_inflation'].append(run_data_2['broke_even_with_inflation'][-1])
            data_run_meta['death_age'].append(run_data_2['age'][-1])

            if working_happiness >= free_happiness:
                data_run_meta['integrated_happiness'].append(working_happiness*run_data_2['age'][-1])
            # elif run_data_2['broke_even_with_inflation'][-1]:
            #     data_run_meta['integrated_happiness'].append(free_happiness)
            else:
                data_run_meta['integrated_happiness'].append(float(initial_retirement_age) * working_happiness + run_data_1['num_years_after_retirement'][-1]*free_happiness +
                                                             float(retirement_age - run_data_1['age'][-1]) * working_happiness + run_data_2['num_years_after_retirement'][-1]*free_happiness)

        # compute optimal retirement age
        max_happiness, retirement_age_for_max_happiness = -float('inf'), None
        broke_even_with_inflation = None
        death_age = None
        for i_integrated_happiness, integrated_happiness in enumerate(data_run_meta['integrated_happiness']):
            if integrated_happiness >= max_happiness or math.isclose(integrated_happiness, max_happiness):  # prefer latest retirement to maximize secondary oppurtunities
                max_happiness = integrated_happiness
                retirement_age_for_max_happiness = data_run_meta['retirement_age'][i_integrated_happiness]
                broke_even_with_inflation = data_run_meta['broke_even_with_inflation'][i_integrated_happiness]
                death_age = data_run_meta['death_age'][i_integrated_happiness]

        data_double_retirement_interest_rate_meta['interest_rate'].append(interest_rate)
        data_double_retirement_interest_rate_meta['max_happiness'].append(max_happiness)
        data_double_retirement_interest_rate_meta['retirement_age_for_max_happiness'].append(retirement_age_for_max_happiness)
        data_double_retirement_interest_rate_meta['broke_even_with_inflation'].append(broke_even_with_inflation)
        data_double_retirement_interest_rate_meta['death_age'].append(death_age)

    # simulation 4 - late retirement, compute satatic retirement age which is nearest optimal happiness across the whole graph range via least squares regression.
    #                enable picking a new optimal solution if run out of money from retiring early
    data_late_retirement_initial_retirement_age_meta = defaultdict(list)

    for initial_retirement_age in range(initial_age, maximum_death_age + 1):
        data_late_retirement_interest_rate_meta = defaultdict(list)
        for interest_rate in interest_rates:
            # retire immediately and simulate until run out of money or maximum_death_age
            end_condition_1, run_data_1  = simulate_until_end_condition(initial_age = initial_age,
                                                                        initial_money = initial_money,
                                                                        annual_cost_of_living = annual_cost_of_living,
                                                                        annual_gross_earn_rate = annual_gross_earn_rate,
                                                                        interest_rate = interest_rate,
                                                                        inflation_rate = inflation_rate,
                                                                        retirement_age = initial_retirement_age,
                                                                        end_num_years_after_retirement = None,
                                                                        end_after_num_years_sim_time = None, 
                                                                        end_if_out_of_money = True,
                                                                        end_if_breakeven_with_inflation = False,
                                                                        end_at_age = maximum_death_age + 1)
                                                                        # end_at_age = 10000)

            data_late_retirement_interest_rate_meta['interest_rate'].append(interest_rate)
            data_late_retirement_interest_rate_meta['initial_retirement_age'].append(initial_retirement_age)
            data_late_retirement_interest_rate_meta['initial_retirement_end'].append(run_data_1['age'][-1])

            # if we made it to maximum_death_age, then log that as the end state of the simulation
            # Otherwise, now that we've run out of money, go back to work and compute new optimal retirement age
            if end_condition_1 == 'age':
                data_late_retirement_interest_rate_meta['2nd_retirement_age'].append(None)
                data_late_retirement_interest_rate_meta['broke_even_with_inflation'].append(run_data_1['broke_even_with_inflation'][-1])
                data_late_retirement_interest_rate_meta['death_age'].append(run_data_1['age'][-1])

                if working_happiness >= free_happiness:
                    data_late_retirement_interest_rate_meta['integrated_happiness'].append(working_happiness*run_data_1['age'][-1])
                # elif run_data_1['broke_even_with_inflation'][-1]:
                #     data_late_retirement_interest_rate_meta['integrated_happiness'].append(free_happiness)
                else:
                    data_late_retirement_interest_rate_meta['integrated_happiness'].append(float(initial_retirement_age) * working_happiness + run_data_1['num_years_after_retirement'][-1]*free_happiness)

            else:
                data_run_meta = defaultdict(list)
                for retirement_age in range(run_data_1['age'][-1], maximum_death_age + 1):
                    end_condition_2, run_data_2  = simulate_until_end_condition(initial_age = initial_age,
                                                                                n = run_data_1['n'][-1],
                                                                                initial_money = run_data_1['x'][-1],
                                                                                annual_cost_of_living = annual_cost_of_living,
                                                                                annual_gross_earn_rate = annual_gross_earn_rate,
                                                                                interest_rate = interest_rate,
                                                                                inflation_rate = inflation_rate,
                                                                                retirement_age = retirement_age,
                                                                                end_num_years_after_retirement = None,
                                                                                end_after_num_years_sim_time = None, 
                                                                                end_if_out_of_money = True,
                                                                                end_if_breakeven_with_inflation = False,
                                                                                end_at_age = maximum_death_age + 1)
                                                                                # end_at_age = 10000)

                    # log data
                    data_run_meta['retirement_age'].append(retirement_age)
                    data_run_meta['broke_even_with_inflation'].append(run_data_2['broke_even_with_inflation'][-1])
                    data_run_meta['death_age'].append(run_data_2['age'][-1])

                    if working_happiness >= free_happiness:
                        data_run_meta['integrated_happiness'].append(working_happiness*run_data_2['age'][-1])
                    # elif run_data_2['broke_even_with_inflation'][-1]:
                    #     data_run_meta['integrated_happiness'].append(free_happiness)
                    else:
                        data_run_meta['integrated_happiness'].append(float(initial_retirement_age) * working_happiness + run_data_1['num_years_after_retirement'][-1]*free_happiness +
                                                                     float(retirement_age - run_data_1['age'][-1]) * working_happiness + run_data_2['num_years_after_retirement'][-1]*free_happiness)

                # compute optimal retirement age
                max_happiness, retirement_age_for_max_happiness = -float('inf'), None
                broke_even_with_inflation = None
                death_age = None
                for i_integrated_happiness, integrated_happiness in enumerate(data_run_meta['integrated_happiness']):
                    if integrated_happiness >= max_happiness or math.isclose(integrated_happiness, max_happiness):  # prefer latest retirement to maximize secondary oppurtunities
                        max_happiness = integrated_happiness
                        retirement_age_for_max_happiness = data_run_meta['retirement_age'][i_integrated_happiness]
                        broke_even_with_inflation = data_run_meta['broke_even_with_inflation'][i_integrated_happiness]
                        death_age = data_run_meta['death_age'][i_integrated_happiness]

                data_late_retirement_interest_rate_meta['integrated_happiness'].append(max_happiness)
                data_late_retirement_interest_rate_meta['2nd_retirement_age'].append(retirement_age_for_max_happiness)
                data_late_retirement_interest_rate_meta['broke_even_with_inflation'].append(broke_even_with_inflation)
                data_late_retirement_interest_rate_meta['death_age'].append(death_age)

        data_late_retirement_initial_retirement_age_meta['initial_retirement_age'].append(initial_retirement_age)
        data_late_retirement_initial_retirement_age_meta['interest_rate_meta'].append(data_late_retirement_interest_rate_meta)

        # compute summed squared distance to optimal
        summed_squared_distance_to_optimal = 0.0
        for i, _ in enumerate(data_late_retirement_interest_rate_meta['interest_rate']):
            assert math.isclose(data_late_retirement_interest_rate_meta['interest_rate'][i], data_optimal_retirement_interest_rate_meta['interest_rate'][i])  # verify parse order matches
            summed_squared_distance_to_optimal += math.pow(data_optimal_retirement_interest_rate_meta['max_happiness'][i] - data_late_retirement_interest_rate_meta['integrated_happiness'][i], 2)
        data_late_retirement_initial_retirement_age_meta['summed_squared_distance_to_optimal'].append(summed_squared_distance_to_optimal)

    # find the least squares solution
    data_optimal_late_retirement_interest_rate_meta = None
    optimal_late_retirement_age = None
    least_squared_distance_to_optimal = float('inf')
    for i, squared_distance_to_optimal in enumerate(data_late_retirement_initial_retirement_age_meta['summed_squared_distance_to_optimal']):
        if squared_distance_to_optimal <= least_squared_distance_to_optimal or math.isclose(squared_distance_to_optimal, least_squared_distance_to_optimal):  # prefer latest retirement to maximize secondary oppurtunities
            least_squared_distance_to_optimal = squared_distance_to_optimal
            data_optimal_late_retirement_interest_rate_meta = data_late_retirement_initial_retirement_age_meta['interest_rate_meta'][i]
            optimal_late_retirement_age = data_late_retirement_initial_retirement_age_meta['initial_retirement_age'][i]


    # plot data
    plt.plot([inflation_rate, inflation_rate], plt.gca().get_ybound(), c='magenta', linestyle='--', linewidth=3, label=f'inflation_rate')
    plt.plot([1.2232, 1.2232], plt.gca().get_ybound(), c='black', linestyle='--', linewidth=3, label=f'SpaceX stock value rate of change, 4-pt fit 3/2018 to 7/2020')
    plt.plot([1.2888, 1.2888], plt.gca().get_ybound(), c='grey', linestyle='--', linewidth=3, label=f'SpaceX stock value rate of change, 17-pt fit 6/2014 to 7/2020')

    # plt.plot(data_immediate_retirement_interest_rate_meta['interest_rate'], data_immediate_retirement_interest_rate_meta['retirement_age'], c='red', marker=None, label=f'retirement age')
    # plt.plot(data_immediate_retirement_interest_rate_meta['interest_rate'], data_immediate_retirement_interest_rate_meta['death_age'], c='blue', marker=None, label=f'death age, given retirement age and corresponding savings')
    
    plt.fill_between(data_immediate_retirement_interest_rate_meta['interest_rate'], data_immediate_retirement_interest_rate_meta['retirement_age'], data_immediate_retirement_interest_rate_meta['death_age'], facecolor='blue', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='blue', alpha=0.3, label=f'free life (retirement to death), with immediate retirement')
    region_patches.append(region_patch)

    plt.fill_between(data_immediate_retirement_interest_rate_meta['interest_rate'],
                     data_immediate_retirement_interest_rate_meta['death_age'],
                     (plt.ylim()[1],) * len(data_immediate_retirement_interest_rate_meta['interest_rate']),
                     where=data_immediate_retirement_interest_rate_meta['broke_even_with_inflation'],
                     facecolor='blue', hatch='xxx', edgecolor='#0000A0', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='blue', alpha=0.3, hatch='xxx', edgecolor='#0000A0', label=f'savings break even with inflation, will not drive death date')
    region_patches.append(region_patch)
    
    # plt.plot(data_optimal_retirement_interest_rate_meta['interest_rate'], data_optimal_retirement_interest_rate_meta['retirement_age_for_max_happiness'], c='red', marker=None, label=f'optimal retirement age')
    # plt.plot(data_optimal_retirement_interest_rate_meta['interest_rate'], data_optimal_retirement_interest_rate_meta['death_age'], c='blue', marker=None, label=f'death age, given retirement age and corresponding savings')
    
    plt.fill_between(data_optimal_retirement_interest_rate_meta['interest_rate'], data_optimal_retirement_interest_rate_meta['retirement_age_for_max_happiness'], data_optimal_retirement_interest_rate_meta['death_age'], facecolor='red', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='red', alpha=0.3, label=f'free life (retirement to death), with optimal retirement age (maximizes integrated happiness)')
    region_patches.append(region_patch)

    plt.fill_between(data_optimal_retirement_interest_rate_meta['interest_rate'],
                     data_optimal_retirement_interest_rate_meta['death_age'],
                     (plt.ylim()[1],) * len(data_optimal_retirement_interest_rate_meta['interest_rate']),
                     where=data_optimal_retirement_interest_rate_meta['broke_even_with_inflation'],
                     facecolor='red', hatch='xxx', edgecolor='#0000A0', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='red', alpha=0.3, hatch='xxx', edgecolor='#0000A0', label=f'savings break even with inflation, will not drive death date')
    region_patches.append(region_patch)
    
    # plt.plot(data_double_retirement_interest_rate_meta['interest_rate'], data_double_retirement_interest_rate_meta['retirement_age_for_max_happiness'], c='red', marker=None, label=f'2nd retirement age')
    # plt.plot(data_double_retirement_interest_rate_meta['interest_rate'], data_double_retirement_interest_rate_meta['death_age'], c='blue', marker=None, label=f'death age, given retirement age and corresponding savings')

    plt.fill_between(data_double_retirement_interest_rate_meta['interest_rate'], data_double_retirement_interest_rate_meta['retirement_age_for_max_happiness'], data_double_retirement_interest_rate_meta['death_age'], facecolor='green', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='green', alpha=0.3, label=f'free life (2nd retirement to death), with immediate initial retirement until out of money then back to work and optimal 2nd retirement age (maximizes integrated happiness)')
    region_patches.append(region_patch)

    plt.fill_between(data_double_retirement_interest_rate_meta['interest_rate'],
                     data_double_retirement_interest_rate_meta['death_age'],
                     (plt.ylim()[1],) * len(data_double_retirement_interest_rate_meta['interest_rate']),
                     where=data_double_retirement_interest_rate_meta['broke_even_with_inflation'],
                     facecolor='green', hatch='xxx', edgecolor='#0000A0', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='green', alpha=0.3, hatch='xxx', edgecolor='#0000A0', label=f'savings break even with inflation, will not drive death date')
    region_patches.append(region_patch)
    
    # plt.plot(data_optimal_late_retirement_interest_rate_meta['interest_rate'], data_optimal_late_retirement_interest_rate_meta['initial_retirement_age'], c='red', marker=None, label=f'initial retirement age')
    # plt.plot(data_optimal_late_retirement_interest_rate_meta['interest_rate'], data_optimal_late_retirement_interest_rate_meta['initial_retirement_end'], c='red', marker=None, label=f'initial retirement end')
    # plt.plot(data_optimal_late_retirement_interest_rate_meta['interest_rate'], data_optimal_late_retirement_interest_rate_meta['2nd_retirement_age'], c='red', marker=None, label=f'2nd retirement age')
    # plt.plot(data_optimal_late_retirement_interest_rate_meta['interest_rate'], data_optimal_late_retirement_interest_rate_meta['death_age'], c='blue', marker=None, label=f'death age, given retirement age and corresponding savings')

    plt.fill_between(data_optimal_late_retirement_interest_rate_meta['interest_rate'], data_optimal_late_retirement_interest_rate_meta['initial_retirement_age'], data_optimal_late_retirement_interest_rate_meta['initial_retirement_end'], facecolor='black', alpha=0.1)
    plt.fill_between(data_optimal_late_retirement_interest_rate_meta['interest_rate'],
                     [age or 0 for age in data_optimal_late_retirement_interest_rate_meta['2nd_retirement_age']],
                     data_optimal_late_retirement_interest_rate_meta['death_age'],
                     where=[age is not None for age in data_optimal_late_retirement_interest_rate_meta['2nd_retirement_age']],
                     facecolor='black', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='black', alpha=0.3, label=f'free life (not working), initial retirement at age {optimal_late_retirement_age}, and possible secondary retirement, which least squares fits to optimal for all initial static retirement ages')
    region_patches.append(region_patch)

    plt.fill_between(data_optimal_late_retirement_interest_rate_meta['interest_rate'],
                     data_optimal_late_retirement_interest_rate_meta['death_age'],
                     (plt.ylim()[1],) * len(data_optimal_late_retirement_interest_rate_meta['interest_rate']),
                     where=data_optimal_late_retirement_interest_rate_meta['broke_even_with_inflation'],
                     facecolor='black', hatch='xxx', edgecolor='#0000A0', alpha=0.1)
    region_patch = matplotlib.patches.Patch(facecolor='black', alpha=0.3, hatch='xxx', edgecolor='#0000A0', label=f'savings break even with inflation, will not drive death date')
    region_patches.append(region_patch)

    plt.gca().set_yticks(np.linspace(*plt.gca().get_ybound(), 11))
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(loc=2, handles = handles + region_patches)
    # plt.legend(loc=2)

    plt.twinx()
    plt.ylabel('integrated happiness (zero centered)')
    plt.ylim(-60, 80)

    plt.plot(data_immediate_retirement_interest_rate_meta['interest_rate'], data_immediate_retirement_interest_rate_meta['integrated_happiness'], c='blue', marker=None, label=f'integrated happiness over lifetime, immediate retirement')
    plt.plot(data_optimal_retirement_interest_rate_meta['interest_rate'], data_optimal_retirement_interest_rate_meta['max_happiness'], c='red', marker=None, label=f'integrated happiness over lifetime, optimal retirement')
    plt.plot(data_double_retirement_interest_rate_meta['interest_rate'], data_double_retirement_interest_rate_meta['max_happiness'], c='green', marker=None, label=f'integrated happiness over lifetime, 2nd retirement')
    plt.plot(data_optimal_late_retirement_interest_rate_meta['interest_rate'], data_optimal_late_retirement_interest_rate_meta['integrated_happiness'], c='black', marker=None, label=f'integrated happiness over lifetime, retirement at age {optimal_late_retirement_age}')

    # compute difference datasets
    difference_data = defaultdict(list)
    for i, _ in enumerate(data_double_retirement_interest_rate_meta['interest_rate']):  # data_double_retirement_interest_rate_meta is shorter, but matches parse order until it ends
        assert math.isclose(data_double_retirement_interest_rate_meta['interest_rate'][i], data_optimal_retirement_interest_rate_meta['interest_rate'][i])  # verify parse order matches
        if not math.isclose(data_double_retirement_interest_rate_meta['max_happiness'][i], data_optimal_retirement_interest_rate_meta['max_happiness'][i]):
            difference_data['interest_rate'].append(data_double_retirement_interest_rate_meta['interest_rate'][i])
            difference_data['difference'].append(data_optimal_retirement_interest_rate_meta['max_happiness'][i] - data_double_retirement_interest_rate_meta['max_happiness'][i])
    plt.plot(difference_data['interest_rate'], difference_data['difference'], c='orange', marker=None, label=f'difference between optimal and 2nd retirement integrated happinesses over lifetime')

    difference_data = defaultdict(list)
    for i, _ in enumerate(data_optimal_late_retirement_interest_rate_meta['interest_rate']):
        assert math.isclose(data_optimal_late_retirement_interest_rate_meta['interest_rate'][i], data_optimal_retirement_interest_rate_meta['interest_rate'][i])  # verify parse order matches
        difference_data['interest_rate'].append(data_optimal_late_retirement_interest_rate_meta['interest_rate'][i])
        difference_data['difference'].append(data_optimal_retirement_interest_rate_meta['max_happiness'][i] - data_optimal_late_retirement_interest_rate_meta['integrated_happiness'][i])
    plt.plot(difference_data['interest_rate'], difference_data['difference'], c='yellow', marker=None, label=f'difference between optimal and retirement at {optimal_late_retirement_age} integrated happinesses over lifetime')

    plt.plot(plt.gca().get_xbound(), [0.0, 0.0], c='cyan', linestyle='--', linewidth=3, label=f'minimum happiness to count as "worth it"')

    plt.gca().set_yticks(np.linspace(*plt.gca().get_ybound(), 11))
    plt.legend(loc=1)

    # ', at interest_rate = {(interest_rate-1)*100:.3}%'
    # colors[i_plot%len(colors)]

    # plot least squares distance vs retirement age to sanity check
    plt.figure()
    plt.title('least squares distance to optimal integrated happiness over the domain of interest rates between -30% and +30%')
    plt.xlabel('initial_retirement_age')
    plt.ylabel('least squares distance to optimal integrated happiness')
    plt.plot(data_late_retirement_initial_retirement_age_meta['initial_retirement_age'], data_late_retirement_initial_retirement_age_meta['summed_squared_distance_to_optimal'], c='blue', marker=None)


    plt.show()
