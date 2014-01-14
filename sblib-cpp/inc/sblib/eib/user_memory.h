/*
 *  user_memory.h - BCU user RAM and user EEPROM.
 *
 *  Copyright (c) 2014 Stefan Taferner <stefan.taferner@gmx.at>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License version 3 as
 *  published by the Free Software Foundation.
 */
#ifndef sblib_user_memory_h
#define sblib_user_memory_h

#include <sblib/types.h>
#include <sblib/eib/bcu_type.h>

class UserRam;
class UserEeprom;


/**
 * The user RAM.
 */
extern UserRam& userRam;

/**
 * The user EEPROM.
 */
extern UserEeprom& userEeprom;


/**
 * The user RAM.
 *
 * The user RAM can be accessed by name, like userRam.status and as an array, like
 * userRam[addr]. Please note that the start address of the RAM is subtracted.
 */
class UserRam
{
public:
    byte progRunning;    //!< 0x0050: Application program active (Selfbus extension)
    byte data1[0x0e];    //!< 0x0051: Reserved (registers)
    byte status;         //!< 0x0060: BCU/system status. See enum BcuStatus below.
    byte data2[USER_RAM_SIZE - 0x60];

    /**
     * Access the user RAM like an ordinary array. The start address is subtracted
     * when accessing the RAM.
     *
     * @param idx - the index of the data byte to access.
     * @return The data byte.
     */
    byte& operator[](int idx);
};


/**
 * The user EEPROM.
 *
 * The user EEPROM can be accessed by name, like userEeprom.status and as an array, like
 * userEeprom[addr]. Please note that the start address of the EEPROM is subtracted. That means
 * userEeprom[0x107] is the correct address for userEeprom.version; not userEeprom[0x07].
 */
class UserEeprom
{
public:
    byte optionReg;      //!< 0x0100: EEPROM option register
    byte manuDataH;      //!< 0x0101: Manufacturing data high byte
    byte manuDataL;      //!< 0x0102: Manufacturing data low byte
    byte manufacturerH;  //!< 0x0103: Software manufacturer high byte
    byte manufacturerL;  //!< 0x0104: Software manufacturer low byte
    byte deviceTypeH;    //!< 0x0105: Device type high byte
    byte deviceTypeL;    //!< 0x0106: Device type low byte
    byte version;        //!< 0x0107: Software version
    byte checkLimit;     //!< 0x0108: EEPROM check limit
    byte peiTypeExpectd; //!< 0x0109: PEI type that the software requires
    byte syncRate;       //!< 0x010a: Baud rate for serial synchronous PEI
    byte portCDDR;       //!< 0x010b: Port C DDR settings (PEI type 17)
    byte portADDR;       //!< 0x010c: Port A DDR settings
    byte runError;       //!< 0x010d: Runtime error flags
    byte routeCnt;       //!< 0x010e: Routing count constant
    byte maxRetransmit;  //!< 0x010f: INAK and BUSY retransmit limit
    byte confDesc;       //!< 0x0110: Configuration descriptor
    byte assocTabPtr;    //!< 0x0111: Low byte of the pointer to association table (BCU1 only)
    byte commsTabPtr;    //!< 0x0112: Low byte of the pointer to communication objects table (BCU1 only)
    byte usrInitPtr;     //!< 0x0113: Low byte of the pointer to user initialization function (BCU1 only)
    byte usrProgPtr;     //!< 0x0114: Low byte of the pointer to user program function (BCU1 only)
#if BCU_TYPE == 0x10
    byte usrSavePtr;     //!< 0x0115: Low byte of the pointer to user save function (BCU1 only)
    byte addrTabSize;    //!< 0x0116: Size of the address table
    byte addrTab[2];     //!< 0x0117+: Address table, 2 bytes per entry. Real array size is addrTabSize*2
    byte user[220];      //!< 0x0116: User EEPROM: 220 bytes (BCU1)
    byte checksum;       //!< 0x01ff: EEPROM checksum (BCU1 only)
#elif BCU_TYPE == 0x20
    byte appType;        //!< 0x0115: Application program type: 0=BCU2, else BCU1
    byte addrTabSize;    //!< 0x0116: Size of the address table ?
    byte addrTab[2];     //!< 0x0117+:Address table, 2 bytes per entry. Real array size is addrTabSize*2
    byte user[856];      //!< 0x0119+:User EEPROM: 856 bytes (BCU2)
                         //!< ------  System EEPROM below
    byte appLoaded;      //!< 0x0470: Application load control state (BCU2, Selfbus extension)
    byte appRunning;     //!< 0x0471: Application run control state (BCU2, Selfbus extension)
    byte addrTabLoaded;  //!< 0x0472: Address table load control state (BCU2, Selfbus extension)
    byte assocTabLoaded; //!< 0x0473: Association table load control state (BCU2, Selfbus extension)
    word serviceControl; //!< 0x0474: Service control (BCU2, Selfbus extension)
    byte system[137];    //!< 0x0476: Rest of the system EEPROM (BCU2 only)
#endif /*BCU_TYPE*/

    /**
     * Access the user EEPROM like an ordinary array. The start address is subtracted
     * when accessing the EEPROM. So use userEeprom[0x107] to access userEeprom.version.
     *
     * @param idx - the index of the data byte to access.
     * @return The data byte.
     */
    byte& operator[](int idx);

    /**
     * Mark the user EEPROM as modified. The EEPROM will be written to flash when the
     * bus is idle, all telegrams are processed, and no direct data connection is open.
     */
    void modified();

    /**
     * Test if the user EEPROM is modified.
     */
    bool isModified() const;
};


/**
 * BCU status bits for userRam.status (at 0x0060).
 * See BCU1 / BCU2 help for detailed description.
 */
enum BcuStatus
{
    BCU_STATUS_PROG= 0x01,    //!< BCU status: programming mode: 0=normal mode, 1=programming mode
    BCU_STATUS_LL  = 0x02,    //!< BCU status: link layer mode
    BCU_STATUS_TL  = 0x04,    //!< BCU status; transport layer enabled
    BCU_STATUS_AL  = 0x08,    //!< BCU status: application layer enabled
    BCU_STATUS_SER = 0x10,    //!< BCU status: serial PEI enabled
    BCU_STATUS_USR = 0x20,    //!< BCU status: application program enabled
    BCU_STATUS_DWN = 0x40,    //!< BCU status: download mode enabled
    BCU_STATUS_PARITY = 0x80  //!< BCU status: parity bit: even parity for bits 0..6)
};


//
//  Inline functions
//

inline byte& UserRam::operator[](int idx)
{
    return *(((byte*) this) + idx - USER_RAM_START);
}

inline byte& UserEeprom::operator[](int idx)
{
    return *(((byte*) this) + idx - USER_EEPROM_START);
}

inline void UserEeprom::modified()
{
    extern byte userEepromModified;
    userEepromModified = 1;
}

inline bool UserEeprom::isModified() const
{
    extern byte userEepromModified;
    return userEepromModified;
}

#endif /*sblib_user_memory_h*/