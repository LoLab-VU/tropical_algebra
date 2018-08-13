import numpy as np
import matplotlib.pyplot as plt
import sympy
from tropical.util import parse_name, rate_2_interactions, label2rr
from future.utils import iteritems


def visualization(model, tspan, y, sp_to_vis, all_signatures, plot_type, param_values):
    mach_eps = np.finfo(float).eps
    species_ready = list(set(sp_to_vis).intersection(all_signatures.keys()))
    par_name_idx = {j.name: i for i, j in enumerate(model.parameters)}
    if not species_ready:
        raise Exception('None of the input species is a driver')

    for sp in species_ready:

        # Setting up figure
        fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True)
        fig.subplots_adjust(hspace=0.4)

        signature = all_signatures[sp][plot_type]

        axs[2].scatter(tspan, [str(s) for s in signature])
        # plt.yticks(list(set(signature)))
        axs[2].set_ylabel('Dominant terms', fontsize=12)
        axs[2].set_xlabel('Time(s)', fontsize=14)
        axs[2].set_xlim(0, tspan[-1])
        # plt.ylim(0, max(y_pos))

        reaction_rates = label2rr(model, sp)
        for rr_idx, rr in iteritems(reaction_rates):
            mon = rr
            var_to_study = [atom for atom in mon.atoms(sympy.Symbol)]
            arg_f1 = [0] * len(var_to_study)
            for idx, va in enumerate(var_to_study):
                if str(va).startswith('__'):
                    sp_idx = int(''.join(filter(str.isdigit, str(va))))
                    arg_f1[idx] = np.maximum(mach_eps, y[:, sp_idx])
                else:
                    arg_f1[idx] = param_values[par_name_idx[va.name]]

            f1 = sympy.lambdify(var_to_study, mon)
            mon_values = f1(*arg_f1)
            mon_name = rate_2_interactions(model, str(mon))
            axs[1].plot(tspan, mon_values, label='{0}: {1}'.format(rr_idx, mon_name))
        axs[1].set_ylabel(r'Rate [$\mu$M/s]', fontsize=12)
        axs[1].legend(bbox_to_anchor=(1., 0.85), ncol=3, title='Reaction rates')

        # TODO: fix this for observables.
        axs[0].plot(tspan, y[:, sp], label=parse_name(model.species[sp]))
        axs[0].set_ylabel(r'Concentration [$\mu$M]', fontsize=12)
        axs[0].legend(bbox_to_anchor=(1.32, 0.85), ncol=1)
        fig.suptitle('Discretization' + ' ' + parse_name(model.species[sp]), y=1.0)

        # plt.tight_layout()
        fig.savefig('s{0}'.format(sp) + '.pdf', format='pdf', bbox_inches='tight')
