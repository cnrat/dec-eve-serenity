# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\const.py
import os
import localization
RESROOT = os.path.dirname(__file__) + '\\res\\'

class Texts:
    NextGroupButtonLabel = 'Next Group'
    PreviousGroupButtonLabel = 'Previous Group'
    RankLabel = 'Rank: '
    ScoreLabel = ' Discovery Credits'
    SelectionsLabel = 'Selections'
    SubmitButtonLabel = 'Submit'
    TaskImageLabel = 'Jovian Tissue Sample'


class Events:
    CategoryChanged = 'OnCitizenScienceCategoryChanged'
    ClickMainImage = 'OnClickMainImage'
    CloseResult = 'OnProjectDiscoveryResultClosed'
    CloseWindow = 'OnProjectDiscoveryClosed'
    ContinueFromResult = 'OnCitizenScienceContinueFromResult'
    ContinueFromReward = 'OnProjectDiscoveryContinueFromReward'
    ContinueFromTrainingResult = 'OnCitizenScienceContinueFromTrainingResult'
    EnableUI = 'OnUIEnabled'
    ExcludeCategories = 'OnCitizenScienceExcludeCategories'
    ResetAndGetNewTask = 'OnProjectDiscoveryResetAndGetNewTask'
    HoverMainImage = 'OnHoverMainImage'
    MainImageLoaded = 'OnMainImageLoaded'
    MouseEnterMainImage = 'OnMouseEnterMainImage'
    MouseExitMainImage = 'OnMouseExitMainImage'
    NewTask = 'OnCitizenScienceNewTask'
    NewTrainingTask = 'OnCitizenScienceNewTrainingTask'
    NoConnectionToAPI = 'OnNoConnectionToAPIError'
    PercentageCountFinished = 'OnProjectDiscoveryPercentageCountFinished'
    PlayTutorial = 'OnCitizenSciencePlayTutorial'
    ProcessingViewFinished = 'OnProcessingViewFinished'
    ProjectDiscoveryStarted = 'OnProjectDiscoveryStarted'
    QuitTutorialTooltips = 'OnProjectDiscoveryQuitTutorialTooltips'
    RestartWindow = 'OnRestartWindow'
    ResultReceived = 'OnCitizenScienceResultReceived'
    RewardViewFadeOut = 'OnRewardViewFadeOut'
    StartTutorial = 'OnProjectDiscoveryStartTutorial'
    SubmitSolution = 'OnCitizenScienceSubmitSolution'
    SkipTutorial = 'OnProjectDiscoverySkipTutorial'
    TrainingResultReceived = 'OnCitizenScienceTrainingResultReceived'
    TransmissionFinished = 'OnTransmissionFinished'
    TooltipTextureChanged = 'OnTooltipTextureChanged'
    UpdateAnalysisKredits = 'OnProjectDiscoveryAnalysisKreditsUpdated'
    UpdateScoreBar = 'OnCitizenScienceUpdateScoreBar'


class Settings:
    ProjectDiscoveryIntroductionShown = 'ProjectDiscoveryIntroductionShown'
    ProjectDiscoveryTutorialPlayed = 'ProjectDiscoveryTutorialPlayed'


class Sounds:
    AnalysisDonePlay = 'wise:/project_discovery_analysis_done_play'
    AnalysisWindowMovePlay = 'wise:/project_discovery_analysis_window_move_play'
    CategorySelectPlay = 'wise:/project_discovery_category_select_play'
    ColorSelectPlay = 'wise:/project_discovery_color_select_play'
    MainImageLoadPlay = 'wise:/project_discovery_main_image_calculation_loop_play'
    MainImageLoadStop = 'wise:/project_discovery_main_image_calculation_loop_stop'
    MainImageLoopPlay = 'wise:/project_discovery_main_image_loop_play'
    MainImageLoopStop = 'wise:/project_discovery_main_image_loop_stop'
    MainImageOpenPlay = 'wise:/project_discovery_main_image_open_play'
    ProcessingPlay = 'wise:/project_discovery_analysis_calculation_loop_play'
    ProcessingStop = 'wise:/project_discovery_analysis_calculation_loop_stop'
    RewardsWindowClosePlay = 'wise:/project_discovery_analysis_window_close_play'
    RewardsWindowLoopPlay = 'wise:/project_discovery_analysis_window_loop_play'
    RewardsWindowLoopStop = 'wise:/project_discovery_analysis_window_loop_stop'
    RewardsWindowOpenPlay = 'wise:/project_discovery_analysis_window_open_play'


def get_training_task_list(project_id):
    training_tasks = [{'tasksToFinishLevel': 2,
      get_task_number_by_project_id(4, project_id): get_localization_for_task(4),
      get_task_number_by_project_id(9, project_id): get_localization_for_task(9),
      get_task_number_by_project_id(22, project_id): get_localization_for_task(22)},
     {'tasksToFinishLevel': 2,
      get_task_number_by_project_id(20, project_id): get_localization_for_task(20),
      get_task_number_by_project_id(19, project_id): get_localization_for_task(19),
      get_task_number_by_project_id(15, project_id): get_localization_for_task(15)},
     {'tasksToFinishLevel': 1,
      get_task_number_by_project_id(13, project_id): get_localization_for_task(13),
      get_task_number_by_project_id(3, project_id): get_localization_for_task(3),
      get_task_number_by_project_id(2, project_id): get_localization_for_task(2)},
     {'tasksToFinishLevel': 1,
      get_task_number_by_project_id(7, project_id): get_localization_for_task(7),
      get_task_number_by_project_id(23, project_id): get_localization_for_task(23),
      get_task_number_by_project_id(0, project_id): get_localization_for_task(0)},
     {'tasksToFinishLevel': 1,
      get_task_number_by_project_id(8, project_id): get_localization_for_task(8),
      get_task_number_by_project_id(12, project_id): get_localization_for_task(12),
      get_task_number_by_project_id(14, project_id): get_localization_for_task(14)},
     {'tasksToFinishLevel': 1,
      get_task_number_by_project_id(16, project_id): get_localization_for_task(16),
      get_task_number_by_project_id(17, project_id): get_localization_for_task(17),
      get_task_number_by_project_id(18, project_id): get_localization_for_task(18)},
     {'tasksToFinishLevel': 1,
      get_task_number_by_project_id(10, project_id): get_localization_for_task(10),
      get_task_number_by_project_id(11, project_id): get_localization_for_task(11),
      get_task_number_by_project_id(5, project_id): get_localization_for_task(5)},
     {'tasksToFinishLevel': 1,
      get_task_number_by_project_id(1, project_id): get_localization_for_task(1),
      get_task_number_by_project_id(6, project_id): get_localization_for_task(6),
      get_task_number_by_project_id(21, project_id): get_localization_for_task(21)}]
    return training_tasks


def get_task_number_by_project_id(task_id, project_id):
    prefix = project_id * 10000000
    return prefix + task_id


def get_localization_for_task(task_id):
    return localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/TutorialExplanations/%02d' % task_id)