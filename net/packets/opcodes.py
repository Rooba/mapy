from enum import Enum

class OpCodes(Enum):
    pass

class CRecvOps(OpCodes):
    CP_CheckPassword = 0x1
    CP_GuestIDLogin = 0x2
    CP_AccountInfoRequest = 0x3
    CP_WorldInfoRequest = 0x4
    CP_SelectWorld = 0x5
    CP_CheckUserLimit = 0x6
    CP_ConfirmEULA = 0x7
    CP_SetGender = 0x8
    CP_CheckPinCode = 0x9
    CP_UpdatePinCode = 0xA
    CP_WorldRequest = 0xB
    CP_LogoutWorld = 0xC
    CP_ViewAllChar = 0xD
    CP_SelectCharacterByVAC = 0xE
    CP_VACFlagSet = 0xF
    CP_CheckNameChangePossible = 0x10
    CP_RegisterNewCharacter = 0x11
    CP_CheckTransferWorldPossible = 0x12
    CP_SelectCharacter = 0x13
    CP_MigrateIn = 0x14
    CP_CheckDuplicatedID = 0x15
    CP_CreateNewCharacter = 0x16
    CP_CreateNewCharacterInCS = 0x17
    CP_DeleteCharacter = 0x18
    CP_AliveAck = 0x19
    CP_ExceptionLog = 0x1A
    CP_SecurityPacket = 0x1B
    CP_EnableSPWRequest = 0x1C
    CP_CheckSPWRequest = 0x1D
    CP_EnableSPWRequestByACV = 0x1E
    CP_CheckSPWRequestByACV = 0x1F
    CP_CheckOTPRequest = 0x20
    CP_CheckDeleteCharacterOTP = 0x21
    CP_CreateSecurityHandle = 0x22
    CP_SSOErrorLog = 0x23
    CP_ClientDumpLog = 0x24
    CP_CheckExtraCharInfo = 0x25
    CP_CreateNewCharacter_Ex = 0x26
    CP_END_SOCKET = 0x27
    CP_BEGIN_USER = 0x28
    CP_UserTransferFieldRequest = 0x29
    CP_UserTransferChannelRequest = 0x2A
    CP_UserMigrateToCashShopRequest = 0x2B
    CP_UserMove = 0x2C
    CP_UserSitRequest = 0x2D
    CP_UserPortableChairSitRequest = 0x2E
    CP_UserMeleeAttack = 0x2F
    CP_UserShootAttack = 0x30
    CP_UserMagicAttack = 0x31
    CP_UserBodyAttack = 0x32
    CP_UserMovingShootAttackPrepare = 0x33
    CP_UserHit = 0x34
    CP_UserAttackUser = 0x35
    CP_UserChat = 0x36
    CP_UserADBoardClose = 0x37
    CP_UserEmotion = 0x38
    CP_UserActivateEffectItem = 0x39
    CP_UserUpgradeTombEffect = 0x3A
    CP_UserHP = 0x3B
    CP_Premium = 0x3C
    CP_UserBanMapByMob = 0x3D
    CP_UserMonsterBookSetCover = 0x3E
    CP_UserSelectNpc = 0x3F
    CP_UserRemoteShopOpenRequest = 0x40
    CP_UserScriptMessageAnswer = 0x41
    CP_UserShopRequest = 0x42
    CP_UserTrunkRequest = 0x43
    CP_UserEntrustedShopRequest = 0x44
    CP_UserStoreBankRequest = 0x45
    CP_UserParcelRequest = 0x46
    CP_UserEffectLocal = 0x47
    CP_ShopScannerRequest = 0x48
    CP_ShopLinkRequest = 0x49
    CP_AdminShopRequest = 0x4A
    CP_UserGatherItemRequest = 0x4B
    CP_UserSortItemRequest = 0x4C
    CP_UserChangeSlotPositionRequest = 0x4D
    CP_UserStatChangeItemUseRequest = 0x4E
    CP_UserStatChangeItemCancelRequest = 0x4F
    CP_UserStatChangeByPortableChairRequest = 0x50
    CP_UserMobSummonItemUseRequest = 0x51
    CP_UserPetFoodItemUseRequest = 0x52
    CP_UserTamingMobFoodItemUseRequest = 0x53
    CP_UserScriptItemUseRequest = 0x54
    CP_UserConsumeCashItemUseRequest = 0x55
    CP_UserDestroyPetItemRequest = 0x56
    CP_UserBridleItemUseRequest = 0x57
    CP_UserSkillLearnItemUseRequest = 0x58
    CP_UserSkillResetItemUseRequest = 0x59
    CP_UserShopScannerItemUseRequest = 0x5A
    CP_UserMapTransferItemUseRequest = 0x5B
    CP_UserPortalScrollUseRequest = 0x5C
    CP_UserUpgradeItemUseRequest = 0x5D
    CP_UserHyperUpgradeItemUseRequest = 0x5E
    CP_UserItemOptionUpgradeItemUseRequest = 0x5F
    CP_UserUIOpenItemUseRequest = 0x60
    CP_UserItemReleaseRequest = 0x61
    CP_UserAbilityUpRequest = 0x62
    CP_UserAbilityMassUpRequest = 0x63
    CP_UserChangeStatRequest = 0x64
    CP_UserChangeStatRequestByItemOption = 0x65
    CP_UserSkillUpRequest = 0x66
    CP_UserSkillUseRequest = 0x67
    CP_UserSkillCancelRequest = 0x68
    CP_UserSkillPrepareRequest = 0x69
    CP_UserDropMoneyRequest = 0x6A
    CP_UserGivePopularityRequest = 0x6B
    CP_UserPartyRequest = 0x6C
    CP_UserCharacterInfoRequest = 0x6D
    CP_UserActivatePetRequest = 0x6E
    CP_UserTemporaryStatUpdateRequest = 0x6F
    CP_UserPortalScriptRequest = 0x70
    CP_UserPortalTeleportRequest = 0x71
    CP_UserMapTransferRequest = 0x72
    CP_UserAntiMacroItemUseRequest = 0x73
    CP_UserAntiMacroSkillUseRequest = 0x74
    CP_UserAntiMacroQuestionResult = 0x75
    CP_UserClaimRequest = 0x76
    CP_UserQuestRequest = 0x77
    CP_UserCalcDamageStatSetRequest = 0x78
    CP_UserThrowGrenade = 0x79
    CP_UserMacroSysDataModified = 0x7A
    CP_UserSelectNpcItemUseRequest = 0x7B
    CP_UserLotteryItemUseRequest = 0x7C
    CP_UserItemMakeRequest = 0x7D
    CP_UserSueCharacterRequest = 0x7E
    CP_UserUseGachaponBoxRequest = 0x7F
    CP_UserUseGachaponRemoteRequest = 0x80
    CP_UserUseWaterOfLife = 0x81
    CP_UserRepairDurabilityAll = 0x82
    CP_UserRepairDurability = 0x83
    CP_UserQuestRecordSetState = 0x84
    CP_UserClientTimerEndRequest = 0x85
    CP_UserFollowCharacterRequest = 0x86
    CP_UserFollowCharacterWithdraw = 0x87
    CP_UserSelectPQReward = 0x88
    CP_UserRequestPQReward = 0x89
    CP_SetPassenserResult = 0x8A
    CP_BroadcastMsg = 0x8B
    CP_GroupMessage = 0x8C
    CP_Whisper = 0x8D
    CP_CoupleMessage = 0x8E
    CP_Messenger = 0x8F
    CP_MiniRoom = 0x90
    CP_PartyRequest = 0x91
    CP_PartyResult = 0x92
    CP_ExpeditionRequest = 0x93
    CP_PartyAdverRequest = 0x94
    CP_GuildRequest = 0x95
    CP_GuildResult = 0x96
    CP_Admin = 0x97
    CP_Log = 0x98
    CP_FriendRequest = 0x99
    CP_MemoRequest = 0x9A
    CP_MemoFlagRequest = 0x9B
    CP_EnterTownPortalRequest = 0x9C
    CP_EnterOpenGateRequest = 0x9D
    CP_SlideRequest = 0x9E
    CP_FuncKeyMappedModified = 0x9F
    CP_RPSGame = 0xA0
    CP_MarriageRequest = 0xA1
    CP_WeddingWishListRequest = 0xA2
    CP_WeddingProgress = 0xA3
    CP_GuestBless = 0xA4
    CP_BoobyTrapAlert = 0xA5
    CP_StalkBegin = 0xA6
    CP_AllianceRequest = 0xA7
    CP_AllianceResult = 0xA8
    CP_FamilyChartRequest = 0xA9
    CP_FamilyInfoRequest = 0xAA
    CP_FamilyRegisterJunior = 0xAB
    CP_FamilyUnregisterJunior = 0xAC
    CP_FamilyUnregisterParent = 0xAD
    CP_FamilyJoinResult = 0xAE
    CP_FamilyUsePrivilege = 0xAF
    CP_FamilySetPrecept = 0xB0
    CP_FamilySummonResult = 0xB1
    CP_ChatBlockUserReq = 0xB2
    CP_GuildBBS = 0xB3
    CP_UserMigrateToITCRequest = 0xB4
    CP_UserExpUpItemUseRequest = 0xB5
    CP_UserTempExpUseRequest = 0xB6
    CP_NewYearCardRequest = 0xB7
    CP_RandomMorphRequest = 0xB8
    CP_CashItemGachaponRequest = 0xB9
    CP_CashGachaponOpenRequest = 0xBA
    CP_ChangeMaplePointRequest = 0xBB
    CP_TalkToTutor = 0xBC
    CP_RequestIncCombo = 0xBD
    CP_MobCrcKeyChangedReply = 0xBE
    CP_RequestSessionValue = 0xBF
    CP_UpdateGMBoard = 0xC0
    CP_AccountMoreInfo = 0xC1
    CP_FindFriend = 0xC2
    CP_AcceptAPSPEvent = 0xC3
    CP_UserDragonBallBoxRequest = 0xC4
    CP_UserDragonBallSummonRequest = 0xC5
    CP_BEGIN_PET = 0xC6
    CP_PetMove = 0xC7
    CP_PetAction = 0xC8
    CP_PetInteractionRequest = 0xC9
    CP_PetDropPickUpRequest = 0xCA
    CP_PetStatChangeItemUseRequest = 0xCB
    CP_PetUpdateExceptionListRequest = 0xCC
    CP_END_PET = 0xCD
    CP_BEGIN_SUMMONED = 0xCE
    CP_SummonedMove = 0xCF
    CP_SummonedAttack = 0xD0
    CP_SummonedHit = 0xD1
    CP_SummonedSkill = 0xD2
    CP_Remove = 0xD3
    CP_END_SUMMONED = 0xD4
    CP_BEGIN_DRAGON = 0xD5
    CP_DragonMove = 0xD6
    CP_END_DRAGON = 0xD7
    CP_QuickslotKeyMappedModified = 0xD8
    CP_PassiveskillInfoUpdate = 0xD9
    CP_UpdateScreenSetting = 0xDA
    CP_UserAttackUser_Specific = 0xDB
    CP_UserPamsSongUseRequest = 0xDC
    CP_QuestGuideRequest = 0xDD
    CP_UserRepeatEffectRemove = 0xDE
    CP_END_USER = 0xDF
    CP_BEGIN_FIELD = 0xE0
    CP_BEGIN_LIFEPOOL = 0xE1
    CP_BEGIN_MOB = 0xE2
    CP_MobMove = 0xE3
    CP_MobApplyCtrl = 0xE4
    CP_MobDropPickUpRequest = 0xE5
    CP_MobHitByObstacle = 0xE6
    CP_MobHitByMob = 0xE7
    CP_MobSelfDestruct = 0xE8
    CP_MobAttackMob = 0xE9
    CP_MobSkillDelayEnd = 0xEA
    CP_MobTimeBombEnd = 0xEB
    CP_MobEscortCollision = 0xEC
    CP_MobRequestEscortInfo = 0xED
    CP_MobEscortStopEndRequest = 0xEE
    CP_END_MOB = 0xEF
    CP_BEGIN_NPC = 0xF0
    CP_NpcMove = 0xF1
    CP_NpcSpecialAction = 0xF2
    CP_END_NPC = 0xF3
    CP_END_LIFEPOOL = 0xF4
    CP_BEGIN_DROPPOOL = 0xF5
    CP_DropPickUpRequest = 0xF6
    CP_END_DROPPOOL = 0xF7
    CP_BEGIN_REACTORPOOL = 0xF8
    CP_ReactorHit = 0xF9
    CP_ReactorTouch = 0xFA
    CP_RequireFieldObstacleStatus = 0xFB
    CP_END_REACTORPOOL = 0xFC
    CP_BEGIN_EVENT_FIELD = 0xFD
    CP_EventStart = 0xFE
    CP_SnowBallHit = 0xFF
    CP_SnowBallTouch = 0x100
    CP_CoconutHit = 0x101
    CP_TournamentMatchTable = 0x102
    CP_PulleyHit = 0x103
    CP_END_EVENT_FIELD = 0x104
    CP_BEGIN_MONSTER_CARNIVAL_FIELD = 0x105
    CP_MCarnivalRequest = 0x106
    CP_END_MONSTER_CARNIVAL_FIELD = 0x107
    CP_CONTISTATE = 0x108
    CP_BEGIN_PARTY_MATCH = 0x109
    CP_INVITE_PARTY_MATCH = 0x10A
    CP_CANCEL_INVITE_PARTY_MATCH = 0x10B
    CP_END_PARTY_MATCH = 0x10C
    CP_RequestFootHoldInfo = 0x10D
    CP_FootHoldInfo = 0x10E
    CP_END_FIELD = 0x10F
    CP_BEGIN_CASHSHOP = 0x110
    CP_CashShopChargeParamRequest = 0x111
    CP_CashShopQueryCashRequest = 0x112
    CP_CashShopCashItemRequest = 0x113
    CP_CashShopCheckCouponRequest = 0x114
    CP_CashShopGiftMateInfoRequest = 0x115
    CP_END_CASHSHOP = 0x116
    CP_CheckSSN2OnCreateNewCharacter = 0x117
    CP_CheckSPWOnCreateNewCharacter = 0x118
    CP_FirstSSNOnCreateNewCharacter = 0x119
    CP_BEGIN_RAISE = 0x11A
    CP_RaiseRefesh = 0x11B
    CP_RaiseUIState = 0x11C
    CP_RaiseIncExp = 0x11D
    CP_RaiseAddPiece = 0x11E
    CP_END_RAISE = 0x11F
    CP_SendMateMail = 0x120
    CP_RequestGuildBoardAuthKey = 0x121
    CP_RequestConsultAuthKey = 0x122
    CP_RequestClassCompetitionAuthKey = 0x123
    CP_RequestWebBoardAuthKey = 0x124
    CP_BEGIN_ITEMUPGRADE = 0x125
    CP_GoldHammerRequest = 0x126
    CP_GoldHammerComplete = 0x127
    CP_ItemUpgradeComplete = 0x128
    CP_END_ITEMUPGRADE = 0x129
    CP_BEGIN_BATTLERECORD = 0x12A
    CP_BATTLERECORD_ONOFF_REQUEST = 0x12B
    CP_END_BATTLERECORD = 0x12C
    CP_BEGIN_MAPLETV = 0x12D
    CP_MapleTVSendMessageRequest = 0x12E
    CP_MapleTVUpdateViewCount = 0x12F
    CP_END_MAPLETV = 0x130
    CP_BEGIN_ITC = 0x131
    CP_ITCChargeParamRequest = 0x132
    CP_ITCQueryCashRequest = 0x133
    CP_ITCItemRequest = 0x134
    CP_END_ITC = 0x135
    CP_BEGIN_CHARACTERSALE = 0x136
    CP_CheckDuplicatedIDInCS = 0x137
    CP_END_CHARACTERSALE = 0x138
    CP_LogoutGiftSelect = 0x139
    CP_NO = 0x13A

class CSendOps(OpCodes):
    LP_CheckPasswordResult = 0x0
    LP_GuestIDLoginResult = 0x1
    LP_AccountInfoResult = 0x2
    LP_CheckUserLimitResult = 0x3
    LP_SetAccountResult = 0x4
    LP_ConfirmEULAResult = 0x5
    LP_CheckPinCodeResult = 0x6
    LP_UpdatePinCodeResult = 0x7
    LP_ViewAllCharResult = 0x8
    LP_SelectCharacterByVACResult = 0x9
    LP_WorldInformation = 0xA
    LP_SelectWorldResult = 0xB
    LP_SelectCharacterResult = 0xC
    LP_CheckDuplicatedIDResult = 0xD
    LP_CreateNewCharacterResult = 0xE
    LP_DeleteCharacterResult = 0xF
    LP_MigrateCommand = 0x10
    LP_AliveReq = 0x11
    LP_AuthenCodeChanged = 0x12
    LP_AuthenMessage = 0x13
    LP_SecurityPacket = 0x14
    LP_EnableSPWResult = 0x15
    LP_DeleteCharacterOTPRequest = 0x16
    LP_CheckCrcResult = 0x17
    LP_LatestConnectedWorld = 0x18
    LP_RecommendWorldMessage = 0x19
    LP_CheckExtraCharInfoResult = 0x1A
    LP_CheckSPWResult = 0x1B
    # LP_END_SOCKET = 0x1B
    # LP_BEGIN_CHARACTERDATA = 0x1C
    LP_InventoryOperation = 0x1C
    LP_InventoryGrow = 0x1D
    LP_StatChanged = 0x1E
    LP_TemporaryStatSet = 0x1F
    LP_TemporaryStatReset = 0x20
    LP_ForcedStatSet = 0x21
    LP_ForcedStatReset = 0x22
    LP_ChangeSkillRecordResult = 0x23
    LP_SkillUseResult = 0x24
    LP_GivePopularityResult = 0x25
    LP_Message = 0x26
    LP_SendOpenFullClientLink = 0x27
    LP_MemoResult = 0x28
    LP_MapTransferResult = 0x29
    LP_AntiMacroResult = 0x2A
    LP_InitialQuizStart = 0x2B
    LP_ClaimResult = 0x2C
    LP_SetClaimSvrAvailableTime = 0x2D
    LP_ClaimSvrStatusChanged = 0x2E
    LP_SetTamingMobInfo = 0x2F
    LP_QuestClear = 0x30
    LP_EntrustedShopCheckResult = 0x31
    LP_SkillLearnItemResult = 0x32
    LP_SkillResetItemResult = 0x33
    LP_GatherItemResult = 0x34
    LP_SortItemResult = 0x35
    LP_RemoteShopOpenResult = 0x36
    LP_SueCharacterResult = 0x37
    LP_MigrateToCashShopResult = 0x38
    LP_TradeMoneyLimit = 0x39
    LP_SetGender = 0x3A
    LP_GuildBBS = 0x3B
    LP_PetDeadMessage = 0x3C
    LP_CharacterInfo = 0x3D
    LP_PartyResult = 0x3E
    LP_ExpeditionRequest = 0x3F
    LP_ExpeditionNoti = 0x40
    LP_FriendResult = 0x41
    LP_GuildRequest = 0x42
    LP_GuildResult = 0x43
    LP_AllianceResult = 0x44
    LP_TownPortal = 0x45
    LP_OpenGate = 0x46
    LP_BroadcastMsg = 0x47
    LP_IncubatorResult = 0x48
    LP_ShopScannerResult = 0x49
    LP_ShopLinkResult = 0x4A
    LP_MarriageRequest = 0x4B
    LP_MarriageResult = 0x4C
    LP_WeddingGiftResult = 0x4D
    LP_MarriedPartnerMapTransfer = 0x4E
    LP_CashPetFoodResult = 0x4F
    LP_SetWeekEventMessage = 0x50
    LP_SetPotionDiscountRate = 0x51
    LP_BridleMobCatchFail = 0x52
    LP_ImitatedNPCResult = 0x53
    LP_ImitatedNPCData = 0x54
    LP_LimitedNPCDisableInfo = 0x55
    LP_MonsterBookSetCard = 0x56
    LP_MonsterBookSetCover = 0x57
    LP_HourChanged = 0x58
    LP_MiniMapOnOff = 0x59
    LP_ConsultAuthkeyUpdate = 0x5A
    LP_ClassCompetitionAuthkeyUpdate = 0x5B
    LP_WebBoardAuthkeyUpdate = 0x5C
    LP_SessionValue = 0x5D
    LP_PartyValue = 0x5E
    LP_FieldSetVariable = 0x5F
    LP_BonusExpRateChanged = 0x60
    LP_PotionDiscountRateChanged = 0x61
    LP_FamilyChartResult = 0x62
    LP_FamilyInfoResult = 0x63
    LP_FamilyResult = 0x64
    LP_FamilyJoinRequest = 0x65
    LP_FamilyJoinRequestResult = 0x66
    LP_FamilyJoinAccepted = 0x67
    LP_FamilyPrivilegeList = 0x68
    LP_FamilyFamousPointIncResult = 0x69
    LP_FamilyNotifyLoginOrLogout = 0x6A
    LP_FamilySetPrivilege = 0x6B
    LP_FamilySummonRequest = 0x6C
    LP_NotifyLevelUp = 0x6D
    LP_NotifyWedding = 0x6E
    LP_NotifyJobChange = 0x6F
    LP_IncRateChanged = 0x70
    LP_MapleTVUseRes = 0x71
    LP_AvatarMegaphoneRes = 0x72
    LP_AvatarMegaphoneUpdateMessage = 0x73
    LP_AvatarMegaphoneClearMessage = 0x74
    LP_CancelNameChangeResult = 0x75
    LP_CancelTransferWorldResult = 0x76
    LP_DestroyShopResult = 0x77
    LP_FAKEGMNOTICE = 0x78
    LP_SuccessInUseGachaponBox = 0x79
    LP_NewYearCardRes = 0x7A
    LP_RandomMorphRes = 0x7B
    LP_CancelNameChangeByOther = 0x7C
    LP_SetBuyEquipExt = 0x7D
    LP_SetPassenserRequest = 0x7E
    LP_ScriptProgressMessage = 0x7F
    LP_DataCRCCheckFailed = 0x80
    LP_CakePieEventResult = 0x81
    LP_UpdateGMBoard = 0x82
    LP_ShowSlotMessage = 0x83
    LP_WildHunterInfo = 0x84
    LP_AccountMoreInfo = 0x85
    LP_FindFirend = 0x86
    LP_StageChange = 0x87
    LP_DragonBallBox = 0x88
    LP_AskUserWhetherUsePamsSong = 0x89
    LP_TransferChannel = 0x8A
    LP_DisallowedDeliveryQuestList = 0x8B
    LP_MacroSysDataInit = 0x8C
    # LP_END_CHARACTERDATA = 0x8C
    # LP_BEGIN_STAGE = 0x8D
    LP_SetField = 0x8D
    LP_SetITC = 0x8E
    LP_SetCashShop = 0x8F
    # LP_END_STAGE = 0x8F
    # LP_BEGIN_MAP = 0x90
    LP_SetBackgroundEffect = 0x90
    LP_SetMapObjectVisible = 0x91
    LP_ClearBackgroundEffect = 0x92
    # LP_END_MAP = 0x92
    # LP_BEGIN_FIELD = 0x93
    LP_TransferFieldReqIgnored = 0x93
    LP_TransferChannelReqIgnored = 0x94
    LP_FieldSpecificData = 0x95
    LP_GroupMessage = 0x96
    LP_Whisper = 0x97
    LP_CoupleMessage = 0x98
    LP_MobSummonItemUseResult = 0x99
    LP_FieldEffect = 0x9A
    LP_FieldObstacleOnOff = 0x9B
    LP_FieldObstacleOnOffStatus = 0x9C
    LP_FieldObstacleAllReset = 0x9D
    LP_BlowWeather = 0x9E
    LP_PlayJukeBox = 0x9F
    LP_AdminResult = 0xA0
    LP_Quiz = 0xA1
    LP_Desc = 0xA2
    LP_Clock = 0xA3
    LP_CONTIMOVE = 0xA4
    LP_CONTISTATE = 0xA5
    LP_SetQuestClear = 0xA6
    LP_SetQuestTime = 0xA7
    LP_Warn = 0xA8
    LP_SetObjectState = 0xA9
    LP_DestroyClock = 0xAA
    LP_ShowArenaResult = 0xAB
    LP_StalkResult = 0xAC
    LP_MassacreIncGauge = 0xAD
    LP_MassacreResult = 0xAE
    LP_QuickslotMappedInit = 0xAF
    LP_FootHoldInfo = 0xB0
    LP_RequestFootHoldInfo = 0xB1
    LP_FieldKillCount = 0xB2
    # LP_BEGIN_USERPOOL = 0xB3
    LP_UserEnterField = 0xB3
    LP_UserLeaveField = 0xB4
    # LP_BEGIN_USERCOMMON = 0xB5
    LP_UserChat = 0xB5
    LP_UserChatNLCPQ = 0xB6
    LP_UserADBoard = 0xB7
    LP_UserMiniRoomBalloon = 0xB8
    LP_UserConsumeItemEffect = 0xB9
    LP_UserItemUpgradeEffect = 0xBA
    LP_UserItemHyperUpgradeEffect = 0xBB
    LP_UserItemOptionUpgradeEffect = 0xBC
    LP_UserItemReleaseEffect = 0xBD
    LP_UserItemUnreleaseEffect = 0xBE
    LP_UserHitByUser = 0xBF
    LP_UserTeslaTriangle = 0xC0
    LP_UserFollowCharacter = 0xC1
    LP_UserShowPQReward = 0xC2
    LP_UserSetPhase = 0xC3
    LP_SetPortalUsable = 0xC4
    LP_ShowPamsSongResult = 0xC5
    # LP_BEGIN_PET = 0xC6
    LP_PetActivated = 0xC6
    LP_PetEvol = 0xC7
    LP_PetTransferField = 0xC8
    LP_PetMove = 0xC9
    LP_PetAction = 0xCA
    LP_PetNameChanged = 0xCB
    LP_PetLoadExceptionList = 0xCC
    LP_PetActionCommand = 0xCD
    # LP_END_PET = 0xCD
    # LP_BEGIN_DRAGON = 0xCE
    LP_DragonEnterField = 0xCE
    LP_DragonMove = 0xCF
    LP_DragonLeaveField = 0xD0
    # LP_END_DRAGON = 0xD0
    LP_END_USERCOMMON = 0xD1
    # LP_BEGIN_USERREMOTE = 0xD2
    LP_UserMove = 0xD2
    LP_UserMeleeAttack = 0xD3
    LP_UserShootAttack = 0xD4
    LP_UserMagicAttack = 0xD5
    LP_UserBodyAttack = 0xD6
    LP_UserSkillPrepare = 0xD7
    LP_UserMovingShootAttackPrepare = 0xD8
    LP_UserSkillCancel = 0xD9
    LP_UserHit = 0xDA
    LP_UserEmotion = 0xDB
    LP_UserSetActiveEffectItem = 0xDC
    LP_UserShowUpgradeTombEffect = 0xDD
    LP_UserSetActivePortableChair = 0xDE
    LP_UserAvatarModified = 0xDF
    LP_UserEffectRemote = 0xE0
    LP_UserTemporaryStatSet = 0xE1
    LP_UserTemporaryStatReset = 0xE2
    LP_UserHP = 0xE3
    LP_UserGuildNameChanged = 0xE4
    LP_UserGuildMarkChanged = 0xE5
    LP_UserThrowGrenade = 0xE6
    # LP_END_USERREMOTE = 0xE6
    # LP_BEGIN_USERLOCAL = 0xE7
    LP_UserSitResult = 0xE7
    LP_UserEmotionLocal = 0xE8
    LP_UserEffectLocal = 0xE9
    LP_UserTeleport = 0xEA
    LP_Premium = 0xEB
    LP_MesoGive_Succeeded = 0xEC
    LP_MesoGive_Failed = 0xED
    LP_Random_Mesobag_Succeed = 0xEE
    LP_Random_Mesobag_Failed = 0xEF
    LP_FieldFadeInOut = 0xF0
    LP_FieldFadeOutForce = 0xF1
    LP_UserQuestResult = 0xF2
    LP_NotifyHPDecByField = 0xF3
    LP_UserPetSkillChanged = 0xF4
    LP_UserBalloonMsg = 0xF5
    LP_PlayEventSound = 0xF6
    LP_PlayMinigameSound = 0xF7
    LP_UserMakerResult = 0xF8
    LP_UserOpenConsultBoard = 0xF9
    LP_UserOpenClassCompetitionPage = 0xFA
    LP_UserOpenUI = 0xFB
    LP_UserOpenUIWithOption = 0xFC
    LP_SetDirectionMode = 0xFD
    LP_SetStandAloneMode = 0xFE
    LP_UserHireTutor = 0xFF
    LP_UserTutorMsg = 0x100
    LP_IncCombo = 0x101
    LP_UserRandomEmotion = 0x102
    LP_ResignQuestReturn = 0x103
    LP_PassMateName = 0x104
    LP_SetRadioSchedule = 0x105
    LP_UserOpenSkillGuide = 0x106
    LP_UserNoticeMsg = 0x107
    LP_UserChatMsg = 0x108
    LP_UserBuffzoneEffect = 0x109
    LP_UserGoToCommoditySN = 0x10A
    LP_UserDamageMeter = 0x10B
    LP_UserTimeBombAttack = 0x10C
    LP_UserPassiveMove = 0x10D
    LP_UserFollowCharacterFailed = 0x10E
    LP_UserRequestVengeance = 0x10F
    LP_UserRequestExJablin = 0x110
    LP_UserAskAPSPEvent = 0x111
    LP_QuestGuideResult = 0x112
    LP_UserDeliveryQuest = 0x113
    LP_SkillCooltimeSet = 0x114
    # LP_END_USERLOCAL = 0x114
    # LP_END_USERPOOL = 0x115
    # LP_BEGIN_SUMMONED = 0x116
    LP_SummonedEnterField = 0x116
    LP_SummonedLeaveField = 0x117
    LP_SummonedMove = 0x118
    LP_SummonedAttack = 0x119
    LP_SummonedSkill = 0x11A
    LP_SummonedHit = 0x11B
    # LP_END_SUMMONED = 0x11B
    # LP_BEGIN_MOBPOOL = 0x11C
    LP_MobEnterField = 0x11C
    LP_MobLeaveField = 0x11D
    LP_MobChangeController = 0x11E
    # LP_BEGIN_MOB = 0x11F
    LP_MobMove = 0x11F
    LP_MobCtrlAck = 0x120
    LP_MobCtrlHint = 0x121
    LP_MobStatSet = 0x122
    LP_MobStatReset = 0x123
    LP_MobSuspendReset = 0x124
    LP_MobAffected = 0x125
    LP_MobDamaged = 0x126
    LP_MobSpecialEffectBySkill = 0x127
    LP_MobHPChange = 0x128
    LP_MobCrcKeyChanged = 0x129
    LP_MobHPIndicator = 0x12A
    LP_MobCatchEffect = 0x12B
    LP_MobEffectByItem = 0x12C
    LP_MobSpeaking = 0x12D
    LP_MobChargeCount = 0x12E
    LP_MobSkillDelay = 0x12F
    LP_MobRequestResultEscortInfo = 0x130
    LP_MobEscortStopEndPermmision = 0x131
    LP_MobEscortStopSay = 0x132
    LP_MobEscortReturnBefore = 0x133
    LP_MobNextAttack = 0x134
    LP_MobAttackedByMob = 0x135
    # LP_END_MOB = 0x135
    LP_END_MOBPOOL = 0x136
    # LP_BEGIN_NPCPOOL = 0x137
    LP_NpcEnterField = 0x137
    LP_NpcLeaveField = 0x138
    LP_NpcChangeController = 0x139
    # LP_BEGIN_NPC = 0x13A
    LP_NpcMove = 0x13A
    LP_NpcUpdateLimitedInfo = 0x13B
    LP_NpcSpecialAction = 0x13C
    # LP_END_NPC = 0x13C
    # LP_BEGIN_NPCTEMPLATE = 0x13D
    LP_NpcSetScript = 0x13D
    # LP_END_NPCTEMPLATE = 0x13D
    LP_END_NPCPOOL = 0x13E
    # LP_BEGIN_EMPLOYEEPOOL = 0x13F
    LP_EmployeeEnterField = 0x13F
    LP_EmployeeLeaveField = 0x140
    LP_EmployeeMiniRoomBalloon = 0x141
    # LP_END_EMPLOYEEPOOL = 0x141
    # LP_BEGIN_DROPPOOL = 0x142
    LP_DropEnterField = 0x142
    LP_DropReleaseAllFreeze = 0x143
    LP_DropLeaveField = 0x144
    # LP_END_DROPPOOL = 0x144
    # LP_BEGIN_MESSAGEBOXPOOL = 0x145
    LP_CreateMessgaeBoxFailed = 0x145
    LP_MessageBoxEnterField = 0x146
    LP_MessageBoxLeaveField = 0x147
    # LP_END_MESSAGEBOXPOOL = 0x147
    # LP_BEGIN_AFFECTEDAREAPOOL = 0x148
    LP_AffectedAreaCreated = 0x148
    LP_AffectedAreaRemoved = 0x149
    # LP_END_AFFECTEDAREAPOOL = 0x149
    # LP_BEGIN_TOWNPORTALPOOL = 0x14A
    LP_TownPortalCreated = 0x14A
    LP_TownPortalRemoved = 0x14B
    # LP_END_TOWNPORTALPOOL = 0x14B
    # LP_BEGIN_OPENGATEPOOL = 0x14C
    LP_OpenGateCreated = 0x14C
    LP_OpenGateRemoved = 0x14D
    # LP_END_OPENGATEPOOL = 0x14D
    # LP_BEGIN_REACTORPOOL = 0x14E
    LP_ReactorChangeState = 0x14E
    LP_ReactorMove = 0x14F
    LP_ReactorEnterField = 0x150
    LP_ReactorLeaveField = 0x151
    # LP_END_REACTORPOOL = 0x151
    # LP_BEGIN_ETCFIELDOBJ = 0x152
    LP_SnowBallState = 0x152
    LP_SnowBallHit = 0x153
    LP_SnowBallMsg = 0x154
    LP_SnowBallTouch = 0x155
    LP_CoconutHit = 0x156
    LP_CoconutScore = 0x157
    LP_HealerMove = 0x158
    LP_PulleyStateChange = 0x159
    LP_MCarnivalEnter = 0x15A
    LP_MCarnivalPersonalCP = 0x15B
    LP_MCarnivalTeamCP = 0x15C
    LP_MCarnivalResultSuccess = 0x15D
    LP_MCarnivalResultFail = 0x15E
    LP_MCarnivalDeath = 0x15F
    LP_MCarnivalMemberOut = 0x160
    LP_MCarnivalGameResult = 0x161
    LP_ArenaScore = 0x162
    LP_BattlefieldEnter = 0x163
    LP_BattlefieldScore = 0x164
    LP_BattlefieldTeamChanged = 0x165
    LP_WitchtowerScore = 0x166
    LP_HontaleTimer = 0x167
    LP_ChaosZakumTimer = 0x168
    LP_HontailTimer = 0x169
    LP_ZakumTimer = 0x16A
    # LP_END_ETCFIELDOBJ = 0x16A
    # LP_BEGIN_SCRIPT = 0x16B
    LP_ScriptMessage = 0x16B
    # LP_END_SCRIPT = 0x16B
    # LP_BEGIN_SHOP = 0x16C
    LP_OpenShopDlg = 0x16C
    LP_ShopResult = 0x16D
    # LP_END_SHOP = 0x16D
    # LP_BEGIN_ADMINSHOP = 0x16E
    LP_AdminShopResult = 0x16E
    LP_AdminShopCommodity = 0x16F
    # LP_END_ADMINSHOP = 0x16F
    LP_TrunkResult = 0x170
    # LP_BEGIN_STOREBANK = 0x171
    LP_StoreBankGetAllResult = 0x171
    LP_StoreBankResult = 0x172
    # LP_END_STOREBANK = 0x172
    LP_RPSGame = 0x173
    LP_Messenger = 0x174
    LP_MiniRoom = 0x175
    # LP_BEGIN_TOURNAMENT = 0x176
    LP_Tournament = 0x176
    LP_TournamentMatchTable = 0x177
    LP_TournamentSetPrize = 0x178
    LP_TournamentNoticeUEW = 0x179
    LP_TournamentAvatarInfo = 0x17A
    # LP_END_TOURNAMENT = 0x17A
    # LP_BEGIN_WEDDING = 0x17B
    LP_WeddingProgress = 0x17B
    LP_WeddingCremonyEnd = 0x17C
    LP_END_WEDDING = 0x17C
    LP_Parcel = 0x17D
    # LP_END_FIELD = 0x17D
    # LP_BEGIN_CASHSHOP = 0x17E
    LP_CashShopChargeParamResult = 0x17E
    LP_CashShopQueryCashResult = 0x17F
    LP_CashShopCashItemResult = 0x180
    LP_CashShopPurchaseExpChanged = 0x181
    LP_CashShopGiftMateInfoResult = 0x182
    LP_CashShopCheckDuplicatedIDResult = 0x183
    LP_CashShopCheckNameChangePossibleResult = 0x184
    LP_CashShopRegisterNewCharacterResult = 0x185
    LP_CashShopCheckTransferWorldPossibleResult = 0x186
    LP_CashShopGachaponStampItemResult = 0x187
    LP_CashShopCashItemGachaponResult = 0x188
    LP_CashShopCashGachaponOpenResult = 0x189
    LP_ChangeMaplePointResult = 0x18A
    LP_CashShopOneADay = 0x18B
    LP_CashShopNoticeFreeCashItem = 0x18C
    LP_CashShopMemberShopResult = 0x18D
    # LP_END_CASHSHOP = 0x18D
    # LP_BEGIN_FUNCKEYMAPPED = 0x18E
    LP_FuncKeyMappedInit = 0x18E
    LP_PetConsumeItemInit = 0x18F
    LP_PetConsumeMPItemInit = 0x190
    # LP_END_FUNCKEYMAPPED = 0x190
    LP_CheckSSN2OnCreateNewCharacterResult = 0x191
    LP_CheckSPWOnCreateNewCharacterResult = 0x192
    LP_FirstSSNOnCreateNewCharacterResult = 0x193
    LP_BEGIN_MAPLETV = 0x194
    LP_MapleTVUpdateMessage = 0x195
    LP_MapleTVClearMessage = 0x196
    LP_MapleTVSendMessageResult = 0x197
    LP_BroadSetFlashChangeEvent = 0x198
    LP_END_MAPLETV = 0x199
    # LP_BEGIN_ITC = 0x19A
    LP_ITCChargeParamResult = 0x19A
    LP_ITCQueryCashResult = 0x19B
    LP_ITCNormalItemResult = 0x19C
    # LP_END_ITC = 0x19C
    # LP_BEGIN_CHARACTERSALE = 0x19D
    LP_CheckDuplicatedIDResultInCS = 0x19D
    LP_CreateNewCharacterResultInCS = 0x19E
    LP_CreateNewCharacterFailInCS = 0x19F
    LP_CharacterSale = 0x1A0
    # LP_END_CHARACTERSALE = 0x1A0
    # LP_BEGIN_GOLDHAMMER = 0x1A1
    LP_GoldHammere_s = 0x1A1
    LP_GoldHammerResult = 0x1A2
    LP_GoldHammere_e = 0x1A3
    # LP_END_GOLDHAMMER = 0x1A3
    # LP_BEGIN_BATTLERECORD = 0x1A4
    LP_BattleRecord_s = 0x1A4
    LP_BattleRecordDotDamageInfo = 0x1A5
    LP_BattleRecordRequestResult = 0x1A6
    LP_BattleRecord_e = 0x1A7
    # LP_END_BATTLERECORD = 0x1A7
    # LP_BEGIN_ITEMUPGRADE = 0x1A8
    LP_ItemUpgrade_s = 0x1A8
    LP_ItemUpgradeResult = 0x1A9
    LP_ItemUpgradeFail = 0x1AA
    LP_ItemUpgrade_e = 0x1AB
    # LP_END_ITEMUPGRADE = 0x1AB
    # LP_BEGIN_VEGA = 0x1AC
    LP_Vega_s = 0x1AC
    LP_VegaResult = 0x1AD
    LP_VegaFail = 0x1AE
    LP_Vega_e = 0x1AF
    # LP_END_VEGA = 0x1AF
    LP_LogoutGift = 0x1B0
    LP_NO = 0x1B1