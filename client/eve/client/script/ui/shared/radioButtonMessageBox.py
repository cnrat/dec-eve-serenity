# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\radioButtonMessageBox.py
import uiprimitives
import uicontrols
import uiutil
import uthread
import form
import uicls
import carbonui.const as uiconst
import localization

class RadioButtonMessageBox(form.MessageBox):
    __guid__ = 'form.RadioButtonMessageBox'
    __nonpersistvars__ = ['suppress']

    def Execute(self, text, title, buttons, radioOptions, icon, suppText, customicon=None, height=None, width=None, default=None, modal=True):
        height = height or 230
        width = width or 340
        self.HideHeader()
        self.SetMinSize([width, height])
        self.width = width
        self.height = height
        self.DefineIcons(icon, customicon)
        if title is None:
            title = localization.GetByLabel('UI/Common/Information')
        self.sr.main = uiutil.FindChild(self, 'main')
        push = uiprimitives.Container(name='push', align=uiconst.TOLEFT, parent=self.sr.topParent, width=64)
        caption = uicontrols.CaptionLabel(text=title, align=uiconst.CENTERLEFT, parent=self.sr.topParent, left=64, width=270)
        self.SetTopparentHeight(max(56, caption.textheight + 16))
        self.sr.radioContainer = uiprimitives.Container(name='radioContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, left=6, top=const.defaultPadding, width=const.defaultPadding, height=40)
        push = uiprimitives.Container(name='push', align=uiconst.TOLEFT, parent=self.sr.radioContainer, width=4)
        self.sr.radioContainer2 = uiprimitives.Container(name='radioContainer', parent=self.sr.radioContainer, align=uiconst.TOALL, pos=(6,
         const.defaultPadding,
         6,
         const.defaultPadding))
        self.sr.textContainer = uiprimitives.Container(name='textContainer', parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        if text:
            edit = uicls.EditPlainText(parent=self.sr.textContainer, padding=const.defaultPadding, readonly=1)
            self.edit = edit
            uthread.new(self.SetText, text)
        h = 0
        if radioOptions:
            self.radioboxID = 'radioButtonMessageBox_%s' % repr(title)
            radioSelection = settings.user.ui.Get(self.radioboxID, 'radioboxOption1Selected')
            for index, label in enumerate(radioOptions):
                checkBox = uicontrols.Checkbox(text=label, parent=self.sr.radioContainer, configName=self.radioboxID, retval='radioboxOption%dSelected' % (index + 1), checked='radioboxOption%dSelected' % (index + 1) == radioSelection, groupname=self.radioboxID, callback=self.OnCheckboxChange)
                h += checkBox.height

        self.sr.radioContainer.height = h
        if suppText:
            self.ShowSupp(suppText)
        self.DefineButtons(buttons, default=default)
        if modal:
            uicore.registry.SetFocus(self)
        return

    def ShowSupp(self, text):
        bottom = uiprimitives.Container(name='suppressContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, height=20, idx=0)
        self.sr.suppCheckbox = uicontrols.Checkbox(text=text, parent=bottom, configName='suppress', retval=0, checked=0, groupname=None, callback=self.ChangeSupp, align=uiconst.TOPLEFT, pos=(6, 0, 320, 0))
        return

    def OnCheckboxChange(self, checkbox, *args):
        config = checkbox.data['config']
        if checkbox.data.has_key('value'):
            if checkbox.data['value'] is None:
                settings.user.ui.Set(config, checkbox.checked)
            else:
                settings.user.ui.Set(config, checkbox.data['value'])
        return

    def GetRadioSelection(self):
        return settings.user.ui.Get(self.radioboxID, 'radioboxOption1Selected')