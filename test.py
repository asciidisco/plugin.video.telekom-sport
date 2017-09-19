import sys
import os
print os.path.dirname(os.path.abspath(__file__))
print os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/resources')
print os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/resources/lib')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/resources'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/resources/lib'))
print sys.path

import nose
nose.main()
