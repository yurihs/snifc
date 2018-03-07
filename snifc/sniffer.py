"""
Captura e filtragem de pacotes
"""

from datetime import datetime
import pyshark
from typing import Generator, Tuple

def capturar_continuosamente(interface: str) -> Generator[Tuple, None, None]:
    capture = pyshark.LiveCapture(interface=interface, bpf_filter='udp src port 53')

    start = datetime.now()
    for pacote in capture.sniff_continuously():
        if pacote.dns:
            yield (
                (pacote.sniff_time - start).total_seconds(),
                pacote.ip.src,
                pacote.ip.dst,
                pacote.dns.qry_name
            )
