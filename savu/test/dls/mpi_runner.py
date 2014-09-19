# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: mpi_runner
   :platform: Unix
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
# First to pick up the DLS controls environment and versioned libraries
from pkg_resources import require
require('mpi4py==1.3.1')
require('h5py==2.2.0')
require('numpy')  # h5py need to be able to import numpy
require('scipy')

import logging
import optparse
import socket
import tempfile

from mpi4py import MPI

import savu.plugins.utils as pu
import savu.test.test_utils as tu
from savu.data.structures import RawTimeseriesData

if __name__ == '__main__':

    usage = "%prog [options]"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU1,CPU2,CPU3,CPU4,CPU5,CPU6,CPU7,CPU8",
                      type='string')
    parser.add_option("-p", "--plugin", dest="plugin", help="Plugin name",
                      default="savu.plugins.timeseries_field_corrections",
                      type='string')
    parser.add_option("-d", "--dir", dest="directory",
                      help="Temp direcotry name",
                      default="/dls/tmp/ssg37927/cluster",
                      type='string')
    (options, args) = parser.parse_args()

    RANK_NAMES = {}
    count = 0
    for name in options.names.split(','):
        RANK_NAMES[count] = name
        count += 1

    RANK = MPI.COMM_WORLD.rank
    SIZE = MPI.COMM_WORLD.size
    MACHINES = SIZE/len(RANK_NAMES)
    MACHINE_RANK = RANK/MACHINES
    MACHINE_RANK_NAME = RANK_NAMES[MACHINE_RANK]
    MACHINE_NUMBER = RANK % MACHINES
    MACHINE_NUMBER_STRING = "%03i" % (MACHINE_NUMBER)

    logging.basicConfig(level=0, format='L %(asctime)s.%(msecs)03d M' +
                        MACHINE_NUMBER_STRING + ' ' + MACHINE_RANK_NAME +
                        ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

    MPI.COMM_WORLD.barrier()

    logging.info("Starting the test process")

    IP = socket.gethostbyname(socket.gethostname())

    logging.debug("ip address is : %s", IP)

    MPI.COMM_WORLD.barrier()

    global_data = None

    if RANK == 0:
        temp_file = tempfile.NamedTemporaryFile(dir=options.directory,
                                                suffix='.h5', delete=False)
        logging.debug("Created output file name is  : %s", temp_file.name)
        global_data = {'file_name': temp_file.name}

    global_data = MPI.COMM_WORLD.bcast(global_data, root=0)

    logging.debug("Output file name is  : %s", global_data['file_name'])

    if 'CPU' in MACHINE_RANK_NAME:
        logging.debug("Loading plugin %s", options.plugin)
        plugin = pu.load_plugin(None, options.plugin)
        logging.debug("Loaded  plugin %s", options.plugin)

        # load appropriate data
        logging.debug("Loading test data")
        data = None
        if plugin.required_data_type() == RawTimeseriesData:
            data = tu.get_nexus_test_data()

        if data is None:
            logging.error("Data is None")

        # generate somewhere for the data to go
        logging.debug("Sorting out output data")
        output = \
            tu.get_temp_projection_data(plugin.name, data, mpi=MPI,
                                        file_name=global_data['file_name'])
        logging.debug("processing")
        plugin.process(data, output, SIZE, RANK)

        logging.debug("Processed to file : %s", output.backing_file.filename)

        data.complete()
        output.complete()

        logging.debug("All files closed")

    MPI.COMM_WORLD.barrier()