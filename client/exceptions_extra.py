# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\exceptions_extra.py
from carbon.common.lib.ccp_exceptions import ConnectionError
from carbon.common.lib.ccp_exceptions import RoleNotAssignedError
from carbon.common.lib.ccp_exceptions import SQLError
from carbon.common.lib.ccp_exceptions import UnmarshalError
from carbon.common.lib.ccp_exceptions import UserError
from carbon.common.script.net.GPSExceptions import GPSAddressOccupied
from carbon.common.script.net.GPSExceptions import GPSBadAddress
from carbon.common.script.net.GPSExceptions import GPSException
from carbon.common.script.net.GPSExceptions import GPSRemoteTransportClosed
from carbon.common.script.net.GPSExceptions import GPSTransportClosed
from carbon.common.script.net.machoNetExceptions import MachoException
from carbon.common.script.net.machoNetExceptions import MachoWrappedException
from carbon.common.script.net.machoNetExceptions import ProxyRedirect
from carbon.common.script.net.machoNetExceptions import SessionUnavailable
from carbon.common.script.net.machoNetExceptions import UberMachoException
from carbon.common.script.net.machoNetExceptions import UnMachoChannel
from carbon.common.script.net.machoNetExceptions import UnMachoDestination
from carbon.common.script.net.machoNetExceptions import WrongMachoNode
from eve.common.script.sys.eveServiceManager import DustNotEnabledError