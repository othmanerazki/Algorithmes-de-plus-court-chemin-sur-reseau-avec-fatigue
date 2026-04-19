import sys 
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

NET_DIR = ROOT / "examples"

import pytest
from network import Network

def test_network_small():
    # Setup
    network = Network.from_file(NET_DIR / "small.txt")
    
    # Assertions
    assert network.start == "lozere"
    assert network.end == "saclay"
    assert network._roads == {
        'lozere': [('ensae', 10, 2), ('guichet', 20, 0)], 
        'ensae': [('saclay', 45, 0)], 
        'guichet': [('ensae', 15, 1)],
        'saclay': []
    }