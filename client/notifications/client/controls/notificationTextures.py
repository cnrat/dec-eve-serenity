# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\controls\notificationTextures.py
import eve.common.script.util.notificationconst as nConst
texturePath = 'res:/UI/Texture/Icons/notifications/notificationIcon_%s.png'
NOTIFICATION_TYPE_TO_TEXTURE = {1234: 'res:/UI/Texture/icons/50_64_11.png',
 nConst.notificationTypeCharTerminationMsg: texturePath % 2,
 nConst.notificationTypeAllMaintenanceBillMsg: texturePath % 4,
 nConst.notificationTypeAllWarDeclaredMsg: texturePath % 5,
 nConst.notificationTypeAllWarSurrenderMsg: texturePath % 6,
 nConst.notificationTypeAllWarRetractedMsg: texturePath % 7,
 nConst.notificationTypeAllWarInvalidatedMsg: texturePath % 8,
 nConst.notificationTypeCharBillMsg: texturePath % 9,
 nConst.notificationTypeCorpAllBillMsg: texturePath % 10,
 nConst.notificationTypeBillOutOfMoneyMsg: texturePath % 11,
 nConst.notificationTypeBountyClaimMsg: texturePath % 14,
 nConst.notificationTypeCloneActivationMsg: texturePath % 15,
 nConst.notificationTypeCorpAppNewMsg: texturePath % 16,
 nConst.notificationTypeCorpTaxChangeMsg: texturePath % 19,
 nConst.notificationTypeCharLeftCorpMsg: texturePath % 21,
 nConst.notificationTypeCorpNewCEOMsg: texturePath % 22,
 nConst.notificationTypeCorpDividendMsg: texturePath % 23,
 nConst.notificationTypeCorpVoteMsg: texturePath % 25,
 nConst.notificationTypeCorpVoteCEORevokedMsg: texturePath % 26,
 nConst.notificationTypeCorpWarDeclaredMsg: texturePath % 27,
 nConst.notificationTypeCorpWarSurrenderMsg: texturePath % 29,
 nConst.notificationTypeCorpWarRetractedMsg: texturePath % 30,
 nConst.notificationTypeCorpWarInvalidatedMsg: texturePath % 31,
 nConst.notificationTypeContainerPasswordMsg: texturePath % 32,
 nConst.notificationTypeCustomsMsg: texturePath % 33,
 nConst.notificationTypeInsuranceFirstShipMsg: texturePath % 34,
 nConst.notificationTypeInsurancePayoutMsg: texturePath % 35,
 nConst.notificationTypeInsuranceInvalidatedMsg: texturePath % 36,
 nConst.notificationTypeSovAllClaimFailMsg: texturePath % 37,
 nConst.notificationTypeSovCorpClaimFailMsg: texturePath % 38,
 nConst.notificationTypeSovAllBillLateMsg: texturePath % 39,
 nConst.notificationTypeSovCorpBillLateMsg: texturePath % 40,
 nConst.notificationTypeSovAllClaimLostMsg: texturePath % 41,
 nConst.notificationTypeSovCorpClaimLostMsg: texturePath % 42,
 nConst.notificationTypeSovAllClaimAquiredMsg: texturePath % 43,
 nConst.notificationTypeSovCorpClaimAquiredMsg: texturePath % 44,
 nConst.notificationTypeAllAnchoringMsg: texturePath % 45,
 nConst.notificationTypeAllStructVulnerableMsg: texturePath % 46,
 nConst.notificationTypeAllStrucInvulnerableMsg: texturePath % 47,
 nConst.notificationTypeSovDisruptorMsg: texturePath % 48,
 nConst.notificationTypeCorpStructLostMsg: texturePath % 49,
 nConst.notificationTypeCorpOfficeExpirationMsg: texturePath % 50,
 nConst.notificationTypeCloneRevokedMsg1: texturePath % 51,
 nConst.notificationTypeCloneMovedMsg: texturePath % 52,
 nConst.notificationTypeCloneRevokedMsg2: texturePath % 53,
 nConst.notificationTypeInsuranceExpirationMsg: texturePath % 54,
 nConst.notificationTypeInsuranceIssuedMsg: texturePath % 55,
 nConst.notificationTypeJumpCloneDeletedMsg1: texturePath % 56,
 nConst.notificationTypeJumpCloneDeletedMsg2: texturePath % 57,
 nConst.notificationTypeFWCorpJoinMsg: texturePath % 58,
 nConst.notificationTypeFWCorpLeaveMsg: texturePath % 59,
 nConst.notificationTypeFWCorpKickMsg: texturePath % 60,
 nConst.notificationTypeFWCharKickMsg: texturePath % 61,
 nConst.notificationTypeFWCorpWarningMsg: texturePath % 62,
 nConst.notificationTypeFWCharWarningMsg: texturePath % 63,
 nConst.notificationTypeFWCharRankLossMsg: texturePath % 64,
 nConst.notificationTypeFWCharRankGainMsg: texturePath % 65,
 nConst.notificationTypeAgentMoveMsg: texturePath % 66,
 nConst.notificationTypeTransactionReversalMsg: texturePath % 67,
 nConst.notificationTypeReimbursementMsg: texturePath % 68,
 nConst.notificationTypeLocateCharMsg: texturePath % 69,
 nConst.notificationTypeResearchMissionAvailableMsg: texturePath % 70,
 nConst.notificationTypeMissionOfferExpirationMsg: texturePath % 71,
 nConst.notificationTypeMissionTimeoutMsg: texturePath % 72,
 nConst.notificationTypeStoryLineMissionAvailableMsg: texturePath % 73,
 nConst.notificationTypeTowerAlertMsg: texturePath % 75,
 nConst.notificationTypeTowerResourceAlertMsg: texturePath % 76,
 nConst.notificationTypeStationAggressionMsg1: texturePath % 77,
 nConst.notificationTypeStationStateChangeMsg: texturePath % 78,
 nConst.notificationTypeStationConquerMsg: texturePath % 79,
 nConst.notificationTypeStationAggressionMsg2: texturePath % 80,
 nConst.notificationTypeFacWarCorpJoinRequestMsg: texturePath % 81,
 nConst.notificationTypeFacWarCorpLeaveRequestMsg: texturePath % 82,
 nConst.notificationTypeFacWarCorpJoinWithdrawMsg: texturePath % 83,
 nConst.notificationTypeFacWarCorpLeaveWithdrawMsg: texturePath % 84,
 nConst.notificationTypeCorpLiquidationMsg: texturePath % 85,
 nConst.notificationTypeSovereigntyTCUDamageMsg: texturePath % 86,
 nConst.notificationTypeSovereigntySBUDamageMsg: texturePath % 87,
 nConst.notificationTypeSovereigntyIHDamageMsg: texturePath % 88,
 nConst.notificationTypeContactAdd: texturePath % 89,
 nConst.notificationTypeContactEdit: texturePath % 90,
 nConst.notificationTypeIncursionCompletedMsg: texturePath % 91,
 nConst.notificationTypeCorpKicked: texturePath % 92,
 nConst.notificationTypeOrbitalAttacked: texturePath % 93,
 nConst.notificationTypeOrbitalReinforced: texturePath % 94,
 nConst.notificationTypeOwnershipTransferred: texturePath % 95,
 nConst.notificationTypeFWAllianceWarningMsg: texturePath % 96,
 nConst.notificationTypeFWAllianceKickMsg: texturePath % 97,
 nConst.notificationTypeAllWarCorpJoinedAllianceMsg: texturePath % 98,
 nConst.notificationTypeAllyJoinedWarDefenderMsg: texturePath % 99,
 nConst.notificationTypeAllyJoinedWarAggressorMsg: texturePath % 100,
 nConst.notificationTypeAllyJoinedWarAllyMsg: texturePath % 101,
 nConst.notificationTypeMercOfferedNegotiationMsg: texturePath % 102,
 nConst.notificationTypeWarSurrenderOfferMsg: texturePath % 103,
 nConst.notificationTypeWarSurrenderDeclinedMsg: texturePath % 104,
 nConst.notificationTypeFacWarLPPayoutKill: texturePath % 105,
 nConst.notificationTypeFacWarLPPayoutEvent: texturePath % 106,
 nConst.notificationTypeFacWarLPDisqualifiedEvent: texturePath % 107,
 nConst.notificationTypeFacWarLPDisqualifiedKill: texturePath % 108,
 nConst.notificationTypeAllyContractCancelled: texturePath % 109,
 nConst.notificationTypeWarAllyOfferDeclinedMsg: texturePath % 110,
 nConst.notificationTypeBountyYourBountyClaimed: texturePath % 111,
 nConst.notificationTypeBountyPlacedChar: texturePath % 112,
 nConst.notificationTypeBountyPlacedCorp: texturePath % 113,
 nConst.notificationTypeBountyPlacedAlliance: texturePath % 114,
 nConst.notificationTypeKillRightAvailable: texturePath % 115,
 nConst.notificationTypeKillRightAvailableOpen: texturePath % 116,
 nConst.notificationTypeKillRightEarned: texturePath % 117,
 nConst.notificationTypeKillRightUsed: texturePath % 118,
 nConst.notificationTypeKillRightUnavailable: texturePath % 119,
 nConst.notificationTypeKillRightUnavailableOpen: texturePath % 120,
 nConst.notificationTypeDeclareWar: texturePath % 121,
 nConst.notificationTypeOfferedSurrender: texturePath % 122,
 nConst.notificationTypeAcceptedSurrender: texturePath % 123,
 nConst.notificationTypeMadeWarMutual: texturePath % 124,
 nConst.notificationTypeRetractsWar: texturePath % 125,
 nConst.notificationTypeOfferedToAlly: texturePath % 126,
 nConst.notificationTypeAcceptedAlly: texturePath % 127,
 nConst.notificationTypeDistrictAttacked: texturePath % 132,
 nConst.notificationTypeBattlePunishFriendlyFire: texturePath % 133,
 nConst.notificationTypeBountyESSTaken: texturePath % 134,
 nConst.notificationTypeBountyESSShared: texturePath % 135,
 nConst.notificationTypeIndustryTeamAuctionWon: texturePath % 136,
 nConst.notificationTypeIndustryTeamAuctionLost: texturePath % 137,
 nConst.notificationTypeCloneActivationMsg2: texturePath % 138,
 nConst.notificationTypeCCPDevNews: texturePath % 170,
 nConst.notificationTypeCCPServerNews: texturePath % 171,
 nConst.notificationTypeCCPGameNews: texturePath % 172,
 nConst.notificationTypeCCPOutOfGameNews: texturePath % 173,
 nConst.notificationTypeServerShutdown: texturePath % 180,
 nConst.notificationTypeStructureFuelAlert: texturePath % 'StructureFuelAlert',
 nConst.notificationTypeStructureAnchoring: texturePath % 'StructureAnchoring',
 nConst.notificationTypeStructureUnanchoring: texturePath % 'StructureUnanchoring',
 nConst.notificationTypeStructureUnderAttack: texturePath % 'StructureUnderAttack',
 nConst.notificationTypeStructureOnline: texturePath % 'StructureOnline',
 nConst.notificationTypeStructureLostShields: texturePath % 'StructureLostShields',
 nConst.notificationTypeStructureLostArmor: texturePath % 'StructureLostArmor',
 nConst.notificationTypeStructureDestroyed: texturePath % 'StructureDestroyed',
 nConst.notificationTypeStructureItemsToAssetSafety: texturePath % 'StructureItemsToAssetSafety',
 nConst.notificationTypeStructureItemsNeedAttention: texturePath % 'StructureItemsNeedAttention',
 nConst.notificationTypeStructureMarketOrdersCancelled: texturePath % 'StructureMarketOrdersCancelled',
 nConst.notificationTypeStructureLostDockingAccess: texturePath % 'StructureLostDockingAccess',
 nConst.notificationTypeStructureOfficeRentalBill: texturePath % 'StructureOfficeRentalBill',
 nConst.notificationTypeStructureServicesOffline: texturePath % 'StructureServicesOffline',
 nConst.notificationTypeStructureItemsDelivered: texturePath % 'StructureItemsDelivered',
 nConst.notificationTypeSkillFinished: texturePath % 1000,
 nConst.notificationTypeSkillEmptyQueue: texturePath % 1002,
 nConst.notificationTypeMailSummary: texturePath % 1003,
 nConst.notificationTypeUnusedSkillPoints: texturePath % 1005,
 nConst.notificationTypeContractAssigned: texturePath % 1006,
 nConst.notificationTypeContractNeedsAttention: texturePath % 1006,
 nConst.notificationTypeAchievementTaskFinished: texturePath % 1010,
 nConst.notificationTypeOpportunityFinished: texturePath % 1011,
 nConst.notificationTypeNewRedeemableItem: texturePath % 1020,
 nConst.notificationTypeGameTimeReceived: texturePath % 1030,
 nConst.notificationTypeQuestComplete: texturePath % 1040,
 nConst.notificationTypeGameTimeSent: texturePath % 1031,
 nConst.notificationTypeContactSignedOn: texturePath % 2001,
 nConst.notificationTypeContactSignedOff: texturePath % 2002}