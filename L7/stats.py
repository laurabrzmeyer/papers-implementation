"""
RETECS METHOD
* This script is from Helge Spieker's stats.py code 
* Accessed in March 2023
* Available at: https://bitbucket.org/HelgeS/retecs/src/master/stats.py

Last modification: 18-12-2024

References:
    H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, 
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration," 
    26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, 
    doi: 10.1145/3092703.3092709.
    Available at: https://dl.acm.org/doi/10.1145/3092703.3092709

"""

import numpy as np
import pandas as pd
import os

def load_stats_dataframe(files, aggregated_results=None):
    if os.path.exists(aggregated_results) and all([os.path.getmtime(f) < os.path.getmtime(aggregated_results) for f in files]):
        return pd.read_pickle(aggregated_results)

    df = pd.DataFrame()

    for f in files:
        tmp_dict = pd.read_pickle(f)
        tmp_dict['iteration'] = f.split('_')[-2]

        if 'comparison' in tmp_dict:
            for (cmp_key, cmp_dict) in tmp_dict['comparison'].items():
                cmp_dict['iteration'] = tmp_dict['iteration']
                cmp_dict['env'] = tmp_dict['env']
                cmp_dict['step'] = tmp_dict['step']
                cmp_dict['agent'] = cmp_key
                cmp_dict['sched_time'] = tmp_dict['sched_time'] if 'sched_time' in tmp_dict else 0.5
                cmp_dict['history_length'] = tmp_dict['history_length'] if 'history_length' in tmp_dict else 4
                cmp_df = pd.DataFrame.from_dict(cmp_dict)
                df = pd.concat([df, cmp_df], sort=True)

            del tmp_dict['comparison']

        del tmp_dict['result']

        tmp_df = pd.DataFrame.from_dict(tmp_dict)
        df = pd.concat([df, tmp_df], sort=True)

    if aggregated_results:
        df.to_pickle(aggregated_results)

    return df


def plot_result_difference_bars(stats, metric,  qax, x):
    baseline = np.asarray(stats[metric])
    x = np.asarray(x)
    colors = ('g', 'b', 'r')

    if 'comparison' in stats:
        bar_width = 0.35

        for (offset, key) in enumerate(stats['comparison'].keys()):
            cmp_val = np.asarray(stats['comparison'][key][metric])
            cmp_val -= baseline
            qax.bar(x+offset*bar_width, cmp_val, bar_width, label=key, color=colors[offset])

    qax.legend(ncol=2)
    qax.set_xlim([1, max(x)])
