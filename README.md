# MaPy

Maplestory emulator written in Python

## Requirements

- Postgresql
- Python 3.10+
- pycryptodome>=3.14.1
- asyncpg>=0.25.0
- attrs>=21.4.0
- more-itertools>=8.12.0
- jinja2>=3.1.1
- fastapi>=0.75.1
- uvicorn>=0.17.6
- pyyaml>=6.0

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
