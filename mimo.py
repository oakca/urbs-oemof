##########################################################################
# IMPORTS
##########################################################################

# oemof
import oemofm
import oemof.solph as solph
import oemof.outputlib as outputlib

# urbs
import urbs
from pyomo.opt.base import SolverFactory

# misc.
import logging
import os
import pandas as pd
from datetime import datetime

##########################################################################
# Helper Functions
##########################################################################


def comparison(u_model, o_model):
    """
    Function for comparing urbs & oemof

    Args:
        u_model: urbs model instance use create_um() to generate
        o_model: oemof model instance use create_om() to generate

    Returns:
        None
    """

    # check objective difference
    if u_model.obj() != o_model.objective():
        print('urbs\t', u_model.obj())
        print('oemof\t', o_model.objective())
        print('Diff\t', u_model.obj() - o_model.objective())


##########################################################################
# urbs Model
##########################################################################

# create urbs model
def create_um(input_file, timesteps):
    """
    Creates an urbs model for given input, time steps

    Args:
        input_file: input file
        timesteps: simulation timesteps

    Returns:
        model instance
    """

    # scenario name, read and modify data for scenario
    data = urbs.read_excel(input_file)

    # create model
    model = urbs.create_model(data, 1, timesteps)

    # solve model and read results
    optim = SolverFactory('glpk')
    result = optim.solve(model, tee=False)

    # write LP file
    filename = os.path.join(os.path.dirname(__file__), 'mimo_urbs.lp')
    model.write(filename, io_options={'symbolic_solver_labels': True})

    return model


##########################################################################
# oemof Model
##########################################################################

# create oemof model
def create_om(input_file, timesteps):
    """
    Creates an oemof model for given input, time steps

    Args:
        input_file: input file
        timesteps: simulation timesteps

    Returns:
        model instance
    """

    # read input file
    data = pd.read_csv(input_file)

    # create oemof model
    model = oemofm.create_model(data, timesteps)

    # solve model and read results
    model = solph.Model(model)
    model.solve(solver='glpk', solve_kwargs={'tee': False})

    # write LP file
    filename = os.path.join(os.path.dirname(__file__), 'mimo_oemof.lp')
    model.write(filename, io_options={'symbolic_solver_labels': True})

    return model


if __name__ == '__main__':
    # Input Files
    input_file_urbs = 'mimo.xlsx'
    input_file_oemof = 'mimo.csv'

    # simulation timesteps
    (offset, length) = (0, 100)  # time step selection
    timesteps = range(offset, offset + length + 1)

    # create models
    print('----------------------------------------------------')
    print('CREATING urbs MODEL')
    urbs_model = create_um(input_file_urbs, timesteps)
    print('CREATING oemof MODEL')
    oemof_model = create_om(input_file_oemof, timesteps)
    print('----------------------------------------------------')

    comparison(urbs_model, oemof_model)
