/*
 *  properties.h - BCU 2 properties of EIB objects.
 *
 *  Copyright (c) 2014 Stefan Taferner <stefan.taferner@gmx.at>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License version 3 as
 *  published by the Free Software Foundation.
 */
#ifndef sblib_properties_h
#define sblib_properties_h
#if BCU_TYPE >= 20

#include <sblib/eib/property_types.h>

/**
 * Find a property definition in a properties table.
 *
 * @param id - the ID of the property to find.
 * @param table - the properties table. The last table element must be PROPERTY_DEF_TABLE_END
 *
 * @return Pointer to the property definition, 0 if not found.
 */
const PropertyDef* findProperty(PropertyID id, const PropertyDef* table);

/**
 * Interface object type ID
 */
enum ObjectType
{
    /** Device object. */
    OT_DEVICE = 0,

    /** Address table object. */
    OT_ADDR_TABLE = 1,

    /** Association table object. */
    OT_ASSOC_TABLE = 2,

    /** Application program object. */
    OT_APPLICATION = 3
};

#endif /*BCU_TYPE >= 20*/
#endif /*sblib_properties_h*/
