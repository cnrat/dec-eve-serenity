# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\chat.py
from eve.client.script.ui.shared.comtool.lscchannel import FormatTxt
from eve.client.script.ui.shared.comtool.lscchannel import GetColor
from eve.client.script.ui.shared.comtool.lscengine import CHTERR_ACCESSDENIED
from eve.client.script.ui.shared.comtool.lscengine import CHTERR_ALREADYEXISTS
from eve.client.script.ui.shared.comtool.lscengine import CHTERR_INCORRECTPASSWORD
from eve.client.script.ui.shared.comtool.lscengine import CHTERR_NOSUCHCHANNEL
from eve.client.script.ui.shared.comtool.lscengine import CHTERR_TOOMANYCHANNELS
from eve.client.script.ui.shared.comtool.lscengine import CHTMODE_CONVERSATIONALIST
from eve.client.script.ui.shared.comtool.lscengine import CHTMODE_CREATOR
from eve.client.script.ui.shared.comtool.lscengine import CHTMODE_DISALLOWED
from eve.client.script.ui.shared.comtool.lscengine import CHTMODE_LISTENER
from eve.client.script.ui.shared.comtool.lscengine import CHTMODE_NOTSPECIFIED
from eve.client.script.ui.shared.comtool.lscengine import CHTMODE_OPERATOR
from eve.client.script.ui.shared.comtool.lscengine import CHTMODE_SPEAKER
from eve.client.script.ui.shared.comtool.lscengine import GetAccessInfo
from eve.client.script.ui.shared.comtool.lscengine import GetDisplayName