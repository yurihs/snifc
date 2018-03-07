"""
Utilidades
"""

import os
from pyshark.tshark.tshark import get_process_path, check_output
from typing import List

def get_tshark_interface_names(tshark_path=None: str) -> List[str]:
    """
    Retorna uma lista dos nomes de interface de rede.
    """
    parameters = [get_process_path(tshark_path), '-D']
    with open(os.devnull, 'w') as null:
        tshark_interfaces = check_output(parameters, stderr=null).decode("ascii")

    return [line.split('. ')[1] for line in tshark_interfaces.splitlines()]
