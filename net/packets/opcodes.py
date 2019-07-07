from enum import Enum

class OpCodes(Enum):
    pass

class InterOps(OpCodes):
    RegistrationRequest = 0x00
    RegistrationResponse = 0x01
    UpdateChannel = 0x02
    UpdateChannelID = 0x03
    UpdateChannelPopulation = 0x04
    CharacterEntriesRequest = 0x05
    CharacterEntriesResponse = 0x06
    CharacterCreationRequest = 0x07
    CharacterCreationResponse = 0x08
    MigrationRegisterRequest = 0x09
    MigrationRegisterResponse = 0x0A
    CharacterNameCheckRequest = 0x0B
    CharacterNameCheckResponse = 0x0C
    MigrationRequest = 0x0D
    MigrationResponse = 0x0E
    ChannelPortRequest = 0x0F
    ChannelPortResponse = 0x10
    ClientConnect = 0xFF

class CRecvOps(OpCodes):
    CheckPassword = 0x01

class CSendOps(OpCodes):
    CheckPasswordResult = 0x00