import sys 
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

NET_DIR = ROOT / "examples"

import unittest 
from network import Network

class Test_NetworkLoading(unittest.TestCase):
    def test_network_small(self):
        network = Network.from_file(NET_DIR / "small.txt")
        self.assertEqual(network.start, "lozere")
        self.assertEqual(network.end, "saclay")
        self.assertEqual(network._roads, {'lozere': [('ensae', 10, 2), ('guichet', 20, 0)], 
                                          'ensae': [('saclay', 45, 0)], 
                                          'guichet': [('ensae', 15, 1)],
                                          'saclay': []})

if __name__ == '__main__':
    unittest.main()
