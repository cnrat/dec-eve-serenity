# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\inventory\filterSvc.py
from math import pi
import evetypes
from inventorycommon.util import GetItemVolume
import service
import uicls
import carbonui.const as uiconst
import uiprimitives
import uicontrols
import uix
import uiutil
import localization
import yaml
import util
import uthread
import blue
from carbon.common.script.util.commonutils import StripTags
ITEM_CATEGORY = 1
ITEM_GROUP = 2
ITEM_VOLUME = 4
ITEM_STACKSIZE = 5
ITEM_ASSEMBLED = 6
ITEM_NAME = 7
ITEM_PRICE = 8
ITEM_SLOT = 9
ITEM_METAGROUP = 10
ITEM_METALEVEL = 11
ITEM_POWER = 12
ITEM_CPU = 13
ITEM_BLUEPRINT_COPY = 14
RESULT_ALL = 1
RESULT_ANY = 2
CRIT_YES = 1
CRIT_NO = 2
CRIT_IS = 3
CRIT_ISNOT = 4
CRIT_ISLESSTHAN = 5
CRIT_ISEQUALTO = 6
CRIT_ISGREATERTHAN = 7
CRIT_STARTSWITH = 8
CRIT_NOTSTARTSWITH = 9
CRIT_CONTAINS = 10
CRIT_NOTCONTAINS = 11

class ItemFilterSvc(service.Service):
    __guid__ = 'svc.itemFilter'

    def Run(self, *args):
        self.defaultFilters = self.GetDefaultFilters()
        self.characterSettings = sm.GetService('characterSettings')
        self.filtersByName = self.FetchFiltersFromServer()
        if self.filtersByName is None:
            self.filtersByName = self.defaultFilters
        self.tempFilter = None
        return

    def GetValue(self, condition, item):
        if condition == ITEM_CATEGORY:
            return item.categoryID
        elif condition == ITEM_GROUP:
            return item.groupID
        elif condition == ITEM_VOLUME:
            return GetItemVolume(item)
        elif condition == ITEM_PRICE:
            price = util.GetAveragePrice(item)
            if price is not None:
                price = util.RoundISK(price)
            return price
        elif condition == ITEM_STACKSIZE:
            return item.stacksize
        elif condition == ITEM_ASSEMBLED:
            return item.singleton
        elif condition == ITEM_SLOT:
            effects = cfg.dgmtypeeffects.get(item.typeID, [])
            return [ effect.effectID for effect in effects ]
        elif condition == ITEM_NAME:
            name = uix.GetItemName(item)
            return StripTags(name)
        elif condition == ITEM_METAGROUP:
            ret = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeMetaGroupID, 0))
            if not ret:
                ret = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeTechLevel, 1))
                if ret == 3:
                    ret = 14
            return ret
        elif condition == ITEM_METALEVEL:
            return int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeMetaLevel, 0))
        elif condition == ITEM_POWER:
            return int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributePower, 0))
        elif condition == ITEM_CPU:
            return int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeCpu, 0))
        elif condition == ITEM_BLUEPRINT_COPY:
            return item.singleton == const.singletonBlueprintCopy
        else:
            return

    def _Filter(self, value, criteria, critValue):
        if criteria == CRIT_IS:
            if isinstance(value, (tuple, list)):
                return critValue in value
            if isinstance(value, basestring):
                return value.lower() == critValue.lower()
            return value == critValue
        elif criteria == CRIT_ISNOT:
            if isinstance(value, (tuple, list)):
                return critValue not in value
            if isinstance(value, basestring):
                return value.lower() != critValue.lower()
            return value != critValue
        elif criteria == CRIT_ISLESSTHAN:
            return value is not None and value < critValue
        elif criteria == CRIT_ISEQUALTO:
            return value == critValue
        elif criteria == CRIT_ISGREATERTHAN:
            return value is not None and value > critValue
        elif criteria == CRIT_STARTSWITH:
            return value.lower().startswith(critValue.lower())
        elif criteria == CRIT_NOTSTARTSWITH:
            return not value.lower().startswith(critValue.lower())
        elif criteria == CRIT_CONTAINS:
            return value.lower().find(critValue.lower()) != -1
        elif criteria == CRIT_NOTCONTAINS:
            return value.lower().find(critValue.lower()) == -1
        else:
            return None

    def FilterItems(self, items, filt):
        func = lambda item: self.FilterItem(item, filt)
        return filter(func, items)

    def FilterItem(self, item, filt):
        filterName, allOrAny, conditions = filt
        if allOrAny == RESULT_ANY:
            for condition, criteria, critValue in conditions:
                value = self.GetValue(condition, item)
                if self._Filter(value, criteria, critValue):
                    return True

            return False
        if allOrAny == RESULT_ALL:
            for condition, criteria, critValue in conditions:
                value = self.GetValue(condition, item)
                if not self._Filter(value, criteria, critValue):
                    return False

            return True

    def GetDefaultFilters(self):
        ret = {}
        ret[localization.GetByLabel('UI/Inventory/FilterAmmunition')] = (localization.GetByLabel('UI/Inventory/FilterAmmunition'), RESULT_ALL, ((ITEM_CATEGORY, CRIT_IS, const.categoryCharge),))
        ret[localization.GetByLabel('UI/Inventory/FilterOreAndMaterials')] = (localization.GetByLabel('UI/Inventory/FilterOreAndMaterials'), RESULT_ANY, ((ITEM_CATEGORY, CRIT_IS, const.categoryMaterial), (ITEM_CATEGORY, CRIT_IS, const.categoryAsteroid), (ITEM_GROUP, CRIT_IS, const.groupHarvestableCloud)))
        ret[localization.GetByLabel('UI/Inventory/FilterShipModules')] = (localization.GetByLabel('UI/Inventory/FilterShipModules'), RESULT_ALL, ((ITEM_CATEGORY, CRIT_IS, const.categoryModule),))
        ret[localization.GetByLabel('UI/Inventory/FilterSkillbooks')] = (localization.GetByLabel('UI/Inventory/FilterSkillbooks'), RESULT_ALL, ((ITEM_CATEGORY, CRIT_IS, const.categorySkill),))
        ret[localization.GetByLabel('UI/Inventory/FilterValuableItems')] = (localization.GetByLabel('UI/Inventory/FilterValuableItems'), RESULT_ALL, ((ITEM_PRICE, CRIT_ISGREATERTHAN, 100000),))
        return ret

    def FetchFiltersFromServer(self):
        ret = None
        yamlStr = self.characterSettings.Get('inventoryFilters')
        if yamlStr is not None:
            ret = {}
            filters = yaml.load(yamlStr, Loader=yaml.CLoader)
            for f in filters:
                ret[f[0]] = f

        return ret

    def PersistFilters(self):
        yamlFilters = yaml.safe_dump(self.filtersByName.values())
        self.characterSettings.Save('inventoryFilters', yamlFilters)
        sm.ScatterEvent('OnInvFiltersChanged')

    def GetFilters(self):
        ret = self.filtersByName.values()
        ret.sort(key=lambda x: x[0].lower())
        return ret

    def SaveFilter(self, name, resultType, conditions, suppressWarn=False):
        if not name:
            raise UserError('SaveFilterNoName')
        if self.GetFilterByName(name) and not suppressWarn:
            if uicore.Message('SaveFilterPrompt', {}, uiconst.YESNO) != uiconst.ID_YES:
                return
        self.filtersByName[name] = [name, resultType, conditions]
        self.PersistFilters()
        uicore.Message('FilterSaved')

    def CreateFilter(self):
        FilterCreationWindow.Open()

    def EditFilter(self, name):
        filter = self.GetFilterByName(name)
        if filter:
            wnd = FilterCreationWindow.GetIfOpen()
            if wnd:
                wnd.Close()
            FilterCreationWindow.Open(filter=filter)

    def GetFilterByName(self, name):
        name = name.lower()
        for key, filter in self.filtersByName.iteritems():
            if key.lower() == name:
                return filter

    def RemoveFilter(self, name, suppressWarn=False):
        if self.GetFilterByName(name):
            if not suppressWarn and uicore.Message('RemoveFilterPrompt', {}, uiconst.YESNO) != uiconst.ID_YES:
                return
            self.filtersByName.pop(name)
            self.PersistFilters()

    def SetTempFilter(self, filter):
        self.tempFilter = filter
        sm.ScatterEvent('OnInvTempFilterChanged')

    def ApplyTempFilter(self, items):
        if self.tempFilter:
            items = self.FilterItems(items, self.tempFilter)
        return items


class FilterCreationWindow(uicontrols.Window):
    default_topParentHeight = 0
    default_windowID = 'FilterCreationWindow'
    default_height = 170
    default_width = 380
    default_caption = 'UI/Inventory/Filters/ItemFilterCaption'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.MakeUnMinimizable()
        self.MakeUncollapseable()
        filter = attributes.get('filter', None)
        if filter:
            self.filterName, self.allOrAny, conditions = filter
            self.originalName = self.filterName
        else:
            self.filterName = ''
            self.allOrAny = RESULT_ALL
            conditions = None
            self.originalName = None
        self.entryCont = uicls.ScrollContainer(name='entryCont', parent=self.sr.main, align=uiconst.TOALL, padding=(10, 10, 10, 0))
        bottomPar = uiprimitives.Container(name='bottomPar', parent=self.sr.main, align=uiconst.TOBOTTOM, height=75, idx=0)
        uicontrols.GradientSprite(bgParent=bottomPar, rotation=-pi / 2, rgbData=[(0, (0.3, 0.3, 0.3))], alphaData=[(0, 0.3), (0.9, 0.0)])
        uiprimitives.Line(parent=bottomPar, align=uiconst.TOTOP, color=(0.3, 0.3, 0.3, 0.3))
        buttonCont1 = uicontrols.ContainerAutoSize(name='bottomCont1', parent=bottomPar, align=uiconst.CENTERTOP, top=20, height=20)
        buttonCont2 = uicontrols.ContainerAutoSize(name='bottomCont2', parent=bottomPar, align=uiconst.CENTERTOP, top=50, height=20)
        uicontrols.EveLabelSmall(parent=uiprimitives.Container(align=uiconst.TOLEFT, parent=buttonCont1, width=1), left=3, top=-14, text=localization.GetByLabel('UI/Inventory/Filters/Match'))
        uicontrols.Checkbox(parent=buttonCont1, text=localization.GetByLabel('UI/Inventory/Filters/All'), wrapLabel=False, groupname='allOrAny', align=uiconst.TOLEFT, checked=self.allOrAny == RESULT_ALL, callback=self.OnRadioButtonsChanged, retval=RESULT_ALL)
        self.radiButtons = uicontrols.Checkbox(parent=buttonCont1, text=localization.GetByLabel('UI/Inventory/Filters/Any'), wrapLabel=False, groupname='allOrAny', align=uiconst.TOLEFT, checked=self.allOrAny == RESULT_ANY, callback=self.OnRadioButtonsChanged, retval=RESULT_ANY)
        self.nameEdit = uicontrols.SinglelineEdit(name='nameEdit', parent=buttonCont1, align=uiconst.TOLEFT, label=localization.GetByLabel('UI/Inventory/Filters/FilterName'), width=120, padLeft=20, setvalue=self.filterName)
        uicontrols.Button(label=localization.GetByLabel('UI/Common/Buttons/Save'), parent=buttonCont2, align=uiconst.TOLEFT, func=self.Save, padLeft=4)
        uicontrols.Button(label=localization.GetByLabel('UI/Common/Buttons/Close'), parent=buttonCont2, align=uiconst.TOLEFT, func=self.Close, padLeft=4)
        if conditions:
            for condition in conditions:
                self.AddEntry(isRemovable=True, condition=condition)

        self.AddEntry(isRemovable=False)
        return

    def LoadFilter(self, filter):
        name, allOrAny, criterias = filter
        self.nameEdit.SetText(name)
        self.allOrAny = allOrAny

    def OnRadioButtonsChanged(self, button):
        self.allOrAny = button.data['value']
        self.ApplyFilter()

    def AddEntry(self, isRemovable=False, condition=None):
        entry = uicls.CriteriaEntry(parent=self.entryCont, condition=condition, controller=self, isRemovable=isRemovable, opacity=0.0)
        uicore.animations.FadeIn(entry)

    def ApplyFilter(self, *args):
        sm.GetService('itemFilter').SetTempFilter(self.GetFilter())

    def Close(self, *args, **kw):
        sm.GetService('itemFilter').SetTempFilter(None)
        uicontrols.Window.Close(self, *args, **kw)
        return

    def GetFilter(self):
        criterias = []
        for entry in self.entryCont.mainCont.children:
            criteria = entry.GetValue()
            if criteria:
                criterias.append(criteria)

        if criterias:
            return (self.nameEdit.GetValue(), self.allOrAny, criterias)

    def Save(self, *args):
        filter = self.GetFilter()
        if filter:
            if self.originalName:
                sm.GetService('itemFilter').RemoveFilter(self.originalName, suppressWarn=True)
                sm.GetService('itemFilter').SaveFilter(suppressWarn=True, *filter)
            else:
                sm.GetService('itemFilter').SaveFilter(*filter)
            self.originalName = filter[0]
        else:
            uicore.Message('CannotSaveBlankFilter')

    def Confirm(self, *args):
        self.ApplyFilter()


class CriteriaEntry(uiprimitives.Container):
    __guid__ = 'uicls.CriteriaEntry'
    default_align = uiconst.TOTOP
    default_height = 22
    default_padBottom = 5

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.filterType = None
        self.criteriaValue = None
        self.controller = attributes.controller
        condition = attributes.get('condition', None)
        self.isRemovable = attributes.get('isRemovable', False)
        self.removeButton = uicontrols.ButtonIcon(name='removeButton', parent=self, align=uiconst.TOLEFT, width=16, iconSize=9, texturePath='res:/UI/Texture/Icons/Minus.png', func=self.OnRemoveBtn)
        self.SetRemovable(self.isRemovable)
        self.filterTypeCombo = uicontrols.Combo(name='filterOptionsCombo', align=uiconst.TOLEFT_PROP, parent=self, width=0.3, padLeft=4, options=self.GetFilterTypeComboOptions(), callback=self.OnFilterTypeCombo)
        self.filterDetailCont = uiprimitives.Container(name='filterDetailCont', parent=self)
        if condition:
            self.SetFilterType(*condition)
        return

    def GetFilterTypeComboOptions(self):
        options = [('', 0),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionAssembled'), ITEM_ASSEMBLED),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionGroup'), ITEM_CATEGORY),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionSlotType'), ITEM_SLOT),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionStackSize'), ITEM_STACKSIZE),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionVolume'), ITEM_VOLUME),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionUnitPrice'), ITEM_PRICE),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionName'), ITEM_NAME),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionMetaGroup'), ITEM_METAGROUP),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionMetaLevel'), ITEM_METALEVEL),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionPowerUsage'), ITEM_POWER),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionCpuUsage'), ITEM_CPU),
         (localization.GetByLabel('UI/Inventory/Filters/ConditionBlueprintCopy'), ITEM_BLUEPRINT_COPY)]
        options.sort(key=lambda x: x[0])
        return options

    def OnRemoveBtn(self, *args):
        wnd = uiutil.GetWindowAbove(self)
        if self.isRemovable:
            self.Close()
        if wnd:
            wnd.ApplyFilter()

    def GetClassByFilterType(self, value):
        return {ITEM_ASSEMBLED: CriteriaValueBool,
         ITEM_CATEGORY: CriteriaValueCategory,
         ITEM_GROUP: CriteriaValueCategory,
         ITEM_SLOT: CriteriaValueSlot,
         ITEM_STACKSIZE: CriteriaValueInt,
         ITEM_VOLUME: CriteriaValueFloat,
         ITEM_PRICE: CriteriaValueFloat,
         ITEM_NAME: CriteriaValueString,
         ITEM_METAGROUP: CriteriaValueMetaGroup,
         ITEM_METALEVEL: CriteriaValueInt,
         ITEM_POWER: CriteriaValueFloat,
         ITEM_CPU: CriteriaValueFloat,
         ITEM_BLUEPRINT_COPY: CriteriaValueBool}.get(value)

    def OnFilterTypeCombo(self, combo, label, filterType):
        self.SetFilterType(filterType)
        if filterType > 0 and not self.isRemovable:
            self.controller.AddEntry()
            self.SetRemovable(True)
        wnd = uiutil.GetWindowAbove(self)
        if wnd:
            wnd.ApplyFilter()

    def SetFilterType(self, filterType, criteria=None, value=None):
        if not filterType:
            return
        self.filterType = filterType
        self.filterDetailCont.Flush()
        if filterType == ITEM_GROUP:
            self.filterTypeCombo.SelectItemByValue(ITEM_CATEGORY)
        else:
            self.filterTypeCombo.SelectItemByValue(filterType)
        cls = self.GetClassByFilterType(filterType)
        self.criteriaValue = cls(parent=self.filterDetailCont, filterType=filterType, criteria=criteria, value=value)

    def SetRemovable(self, removable):
        self.isRemovable = removable
        if removable:
            self.removeButton.Enable()
        else:
            self.removeButton.Disable()

    def GetValue(self):
        if not self.filterType or not self.criteriaValue:
            return None
        else:
            return self.criteriaValue.GetValue()


class CriteriaValueBase(uiprimitives.Container):
    __guid__ = 'filterEntry.CriteriaValueBase'
    default_value = None
    default_criteria = None

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.filterType = attributes.filterType
        self.criteria = attributes.Get('criteria', self.default_criteria)
        self.value = attributes.Get('value', self.default_value)
        self.applyFilterPending = False
        self.applyFilterThread = None
        return

    def CreateCombo(self, options, width=0.5, select=None):
        return uicontrols.Combo(align=uiconst.TOLEFT_PROP, parent=self, width=width, padLeft=const.defaultPadding, options=options, select=None, callback=self.ApplyFilter)

    def ApplyFilter(self, *args):
        if not self.applyFilterThread:
            self.applyFilterThread = uthread.new(self._ApplyFilter)
        else:
            self.applyFilterPending = True

    def _ApplyFilter(self):
        wnd = uiutil.GetWindowAbove(self)
        if wnd:
            wnd.ApplyFilter()
            blue.synchro.Sleep(500)
            if self.applyFilterPending:
                self.applyFilterThread = uthread.new(self._ApplyFilter)
            else:
                self.applyFilterThread = None
            self.applyFilterPending = False
        return


class CriteriaValueBool(CriteriaValueBase):
    __guid__ = 'filterEntry.CriteriaValueBool'
    default_criteria = CRIT_ISNOT
    default_value = True

    def ApplyAttributes(self, attributes):
        CriteriaValueBase.ApplyAttributes(self, attributes)
        options = ((localization.GetByLabel('UI/Inventory/Filters/CritIsTrue'), CRIT_IS), (localization.GetByLabel('UI/Inventory/Filters/CritIsFalse'), CRIT_ISNOT))
        self.criteriaCombo = self.CreateCombo(options)
        self.criteriaCombo.SelectItemByValue(self.criteria)

    def GetValue(self):
        return [self.filterType, self.criteriaCombo.GetValue(), True]


class CriteriaValueInt(CriteriaValueBase):
    __guid__ = 'filterEntry.CriteriaValueInt'
    ints = (0, 1000000000000000.0)
    floats = None
    default_criteria = CRIT_ISGREATERTHAN
    default_value = 0

    def ApplyAttributes(self, attributes):
        CriteriaValueBase.ApplyAttributes(self, attributes)
        options = ((localization.GetByLabel('UI/Inventory/Filters/CritLessThan'), CRIT_ISLESSTHAN), (localization.GetByLabel('UI/Inventory/Filters/CritEqualTo'), CRIT_ISEQUALTO), (localization.GetByLabel('UI/Inventory/Filters/CritGreaterThan'), CRIT_ISGREATERTHAN))
        self.criteriaCombo = self.CreateCombo(options)
        self.criteriaCombo.SelectItemByValue(self.criteria)
        self.valueEdit = uicontrols.SinglelineEdit(name='valueEdit', parent=self, align=uiconst.TOLEFT_PROP, ints=self.ints, floats=self.floats, setvalue=self.value, padLeft=4, width=0.5, OnFocusLost=self.ApplyFilter, OnReturn=self.ApplyFilter, OnChange=self.ApplyFilter)

    def GetValue(self):
        return [self.filterType, self.criteriaCombo.GetValue(), self.valueEdit.GetValue()]


class CriteriaValueFloat(CriteriaValueInt):
    __guid__ = 'filterEntry.CriteriaValueFloat'
    ints = None
    floats = (0.0, 1000000000000000.0)
    default_value = 0.0


class CriteriaValueString(CriteriaValueBase):
    __guid__ = 'filterEntry.CriteriaValueString'
    default_criteria = CRIT_STARTSWITH
    default_value = ''

    def ApplyAttributes(self, attributes):
        CriteriaValueBase.ApplyAttributes(self, attributes)
        options = ((localization.GetByLabel('UI/Inventory/Filters/CritStartsWith'), CRIT_STARTSWITH),
         (localization.GetByLabel('UI/Inventory/Filters/CritNotStartsWith'), CRIT_NOTSTARTSWITH),
         (localization.GetByLabel('UI/Inventory/Filters/CritIs'), CRIT_IS),
         (localization.GetByLabel('UI/Inventory/Filters/CritIsNot'), CRIT_ISNOT),
         (localization.GetByLabel('UI/Inventory/Filters/CritContains'), CRIT_CONTAINS),
         (localization.GetByLabel('UI/Inventory/Filters/CritNotContains'), CRIT_NOTCONTAINS))
        self.criteriaCombo = self.CreateCombo(options)
        self.criteriaCombo.SelectItemByValue(self.criteria)
        self.valueEdit = uicontrols.SinglelineEdit(name='valueEdit', parent=self, align=uiconst.TOLEFT_PROP, setvalue=self.value, padLeft=4, width=0.5, OnFocusLost=self.ApplyFilter, OnReturn=self.ApplyFilter, OnChange=self.ApplyFilter)

    def GetValue(self):
        return [self.filterType, self.criteriaCombo.GetValue(), self.valueEdit.GetValue()]


class CriteriaValueCategory(CriteriaValueBase):
    __guid__ = 'filterEntry.CriteriaValueCategory'
    default_criteria = CRIT_IS
    default_value = None

    def ApplyAttributes(self, attributes):
        CriteriaValueBase.ApplyAttributes(self, attributes)
        options = ((localization.GetByLabel('UI/Inventory/Filters/CritIs'), CRIT_IS), (localization.GetByLabel('UI/Inventory/Filters/CritIsNot'), CRIT_ISNOT))
        self.criteriaCombo = self.CreateCombo(options, width=0.2)
        self.criteriaCombo.SelectItemByValue(self.criteria)
        self.categoryCombo = self.CreateCombo(self.GetCategoryValueOptions(), width=0.4)
        self.categoryCombo.OnChange = self.OnCategoryComboChange
        self.groupCombo = self.CreateCombo(self.GetGroupValueOptions(), width=0.4)
        if self.value:
            if self.filterType == ITEM_CATEGORY:
                self.categoryCombo.SelectItemByValue(self.value)
                self.OnCategoryComboChange()
            elif self.filterType == ITEM_GROUP:
                categoryID = evetypes.GetCategoryIDByGroup(self.value)
                self.categoryCombo.SelectItemByValue(categoryID)
                self.OnCategoryComboChange()
                self.groupCombo.SelectItemByValue(self.value)

    def GetCategoryValueOptions(self):
        options = []
        for categoryID in evetypes.IterateCategories():
            if evetypes.IsCategoryPublishedByCategory(categoryID):
                options.append((evetypes.GetCategoryNameByCategory(categoryID), categoryID))

        options.sort(key=lambda x: x[0])
        return options

    def GetGroupValueOptions(self):
        categoryID = self.categoryCombo.GetValue()
        options = []
        for groupID in evetypes.IterateGroups():
            if evetypes.IsGroupPublishedByGroup(groupID) and evetypes.GetCategoryIDByGroup(groupID) == categoryID:
                options.append((evetypes.GetGroupNameByGroup(groupID), groupID))

        options.sort(key=lambda x: x[0])
        options.insert(0, (localization.GetByLabel('UI/Common/All'), 0))
        return options

    def OnCategoryComboChange(self, *args):
        self.groupCombo.Close()
        self.groupCombo = self.CreateCombo(self.GetGroupValueOptions(), width=0.4)
        self.ApplyFilter()

    def GetValue(self):
        if self.groupCombo.GetValue():
            return [ITEM_GROUP, self.criteriaCombo.GetValue(), self.groupCombo.GetValue()]
        else:
            return [ITEM_CATEGORY, self.criteriaCombo.GetValue(), self.categoryCombo.GetValue()]


class CriteriaValueSlot(CriteriaValueBase):
    __guid__ = 'filterEntry.CriteriaValueSlot'
    default_criteria = CRIT_IS

    def ApplyAttributes(self, attributes):
        CriteriaValueBase.ApplyAttributes(self, attributes)
        options = ((localization.GetByLabel('UI/Inventory/Filters/CritIs'), CRIT_IS), (localization.GetByLabel('UI/Inventory/Filters/CritIsNot'), CRIT_ISNOT))
        self.criteriaCombo = self.CreateCombo(options)
        self.criteriaCombo.SelectItemByValue(self.criteria)
        options = ((localization.GetByLabel('UI/Inventory/Filters/SlotLowPower'), const.effectLoPower),
         (localization.GetByLabel('UI/Inventory/Filters/SlotMedPower'), const.effectMedPower),
         (localization.GetByLabel('UI/Inventory/Filters/SlotHighPower'), const.effectHiPower),
         (localization.GetByLabel('UI/Inventory/Filters/SlotRig'), const.effectRigSlot))
        self.valueCombo = self.CreateCombo(options)
        self.valueCombo.SelectItemByValue(self.value)

    def GetValue(self):
        return [self.filterType, self.criteriaCombo.GetValue(), self.valueCombo.GetValue()]


class CriteriaValueMetaGroup(CriteriaValueBase):
    __guid__ = 'filterEntry.CriteriaValueMetaGroup'
    default_criteria = CRIT_IS

    def ApplyAttributes(self, attributes):
        CriteriaValueBase.ApplyAttributes(self, attributes)
        options = ((localization.GetByLabel('UI/Inventory/Filters/CritIs'), CRIT_IS), (localization.GetByLabel('UI/Inventory/Filters/CritIsNot'), CRIT_ISNOT))
        self.criteriaCombo = self.CreateCombo(options)
        self.criteriaCombo.SelectItemByValue(self.criteria)
        options = []
        for i in (1, 2, 3, 4, 5, 6, 14):
            metaObj = cfg.invmetagroups.Get(i)
            options.append((metaObj.name, i))

        options.sort(key=lambda x: x[0])
        self.valueCombo = self.CreateCombo(options)
        self.valueCombo.SelectItemByValue(self.value)

    def GetValue(self):
        return [self.filterType, self.criteriaCombo.GetValue(), self.valueCombo.GetValue()]