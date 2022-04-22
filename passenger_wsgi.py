import sys
project_home = u'/home/onlymyli/public_html/life2'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path
from website import create_app
application = create_app()