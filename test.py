import sys
import os
print os.path.dirname(__file__)
print os.path.join(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__) + '/resources'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__) + '/resources/lib'))
print sys.path

import nose
nose.main()
