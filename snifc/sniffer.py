"""
Captura e filtragem de pacotes
"""

from datetime import datetime
import pyshark
from typing import Generator, Tuple

def capturar_continuosamente(interface: str) -> Generator[Tuple, None, None]:
    capture = pyshark.LiveCapture(interface=interface)

    start = datetime.now()
    for pacote in capture.sniff_continuously():
        if hasattr(pacote, 'ip'):
            print(dir(pacote))
            yield (
                (pacote.sniff_time - start).total_seconds(),
                pacote.ip.src,
                pacote.ip.dst,
                ' / '.join(layer.layer_name for layer in pacote.layers),
                pacote.length
            )
