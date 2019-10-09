# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for simplifying work with Pytorch.
"""

import collections
import logging
import subprocess

import torch.cuda

log = logging.getLogger(__name__)


def select_device():
    """Automatically choose a Torch device to be used for subsequent computation.

    Automatically chooses GPUs over CPUs, prioritizing GPUs that are lightly loaded.

    .. note::
        Always returns a valid device, but there is no guarantee that a given device will have
        sufficient resources for a given computation.
    """
    if torch.cuda.is_available():
        GPU = collections.namedtuple("GPU", ["index", "name", "temperature", "utilization", "allocated", "total"])

        command = ["nvidia-smi", "--query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"]
        results = subprocess.check_output(command).decode("utf-8")
        lines = [[value.strip() for value in line.split(",")] for line in results.strip().split("\n")]

        gpus = []
        for index, name, temperature, utilization, allocated, total in lines:
            gpus.append(GPU(index=int(index), name=name, temperature=float(temperature), utilization=float(utilization), allocated=int(allocated), total=int(total)))
        gpus = sorted(gpus, key=lambda gpu: (gpu.allocated, gpu.temperature))

        for gpu in gpus:
            log.info("GPU [{}] {} | {}degC, {}% | {} / {} MB".format(gpu.index, gpu.name, gpu.temperature, gpu.utilization, gpu.allocated, gpu.total))

        gpu = gpus[0]
        device = torch.device("cuda:{}".format(gpu.index))
    else:
        device = torch.device("cpu")

    log.info("Selected device: {}".format(device))
    return device

