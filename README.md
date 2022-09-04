# MaPy

Maplestory emulator written in Python

## Requirements

- Postgresql
- Python 3.10+
- pycryptodome
- asyncpg
- attrs
- more-itertools
- jinja2
- fastapi
- uvicorn
- pyyaml

## Optional

- itsdangerous
- pydantic
- loguru
- uvloop

## To-Do

- Multi-Version Compat

  - Template out packet handlers, opcodes, game objects, and client to have drop-in's per version
  - Map objects to relational tables for database generation

- Inventory Operations

  - Move item slot
  - Drop Items
  - Loot Items
  - Proper serial handling for equips when transferring ownership
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
