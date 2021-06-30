from . import xaal_sensfloor
from xaal.lib import helpers
from xaal.lib.asyncio import AsyncEngine

#helpers.run_package(xaal_sensfloor.PACKAGE_NAME,xaal_sensfloor.setup)
helpers.setup_console_logger(xaal_sensfloor.PACKAGE_NAME)
xaal_sensfloor.run()
