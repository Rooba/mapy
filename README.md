# MaPy

Maplestory emulator written in Python

## Requirements

- Postgresql (only tested with 11)
- Python 3.10+
- asyncpg
- pycryptodomex

## To-Do

- Inventory Operations

  - Move item slot
  - Drop Items
  - Loot Items
  - Proper serial handling for equips when transfering ownership
  - Increase/Decrease stack count

- Portal Navigation

  - Properly handle mob spawn / idle upon no map owner / despawn upon expiration
  - Field ground item lifetime

- Consumables

  - Potions
  - Equipment scrolls
  - Teleport scrolls
  - Follower consumables
  - Cash Effects
  - Chairs

- Followers (Pets, Shadow Partner, Mage summons, Archer Summons, Beholder)

  - Move Path
  - Field registration
  - Expiration

- Secondary Stat (Buff Stats)

Thank you to raj for basically teaching me all of this
