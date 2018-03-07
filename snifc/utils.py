"""
Utilidades
"""

import os
import sys
from pathlib import Path
from pyshark.tshark.tshark import get_process_path, check_output
from typing import List

def get_tshark_interface_names(tshark_path: str = None) -> List[str]:
    """
    Retorna uma lista dos nomes de interface de rede.
    """
    parameters = [get_process_path(tshark_path), '-D']
    with open(os.devnull, 'w') as null:
        tshark_interfaces = check_output(parameters, stderr=null).decode("ascii")

    return [line.split('. ')[1] for line in tshark_interfaces.splitlines()]

def get_project_dir() -> Path:
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = Path(sys._MEIPASS)
    else:
        # we are running in a normal Python environment
        bundle_dir = Path(__file__).absolute().parent
    return bundle_dir
