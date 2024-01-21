## Group 6 AOOP Project
This repository aims to create a clone of Boomerang Fu using Pygame.

- Objective
    - Movement    
        - Flash
    - Weapons
        - Melee
            - Auto-attack      
        - Projectile
            - Boomerang     
            - Normal projectile
    - Obstacle/Collision
    - Multiplayer
    <!-- - Environment
        - Death
        - Respawn (?)
    - Menu
    - UI(might be rough or just CLI) -->

### Install dependencies
```sh
$ pip install -r requirements.txt
```

### Play locally(2 players)
```sh
$ python main.py
```

### Start a server
```sh
$ python server.py [--max-players MAX_PLAYERS] [--host HOST] [--port PORT]
```
Wait until all players join the server, then enter `start` to initiate the game server.

### Join a server 
```sh
$ python main.py -m [--host HOST] [--port PORT]
```

<!-- ### Starter Kit 
We forked these references in our organization.  

This project use '15 - fixes audio' from [Zelda](https://github.com/clear-code-projects/Zelda) as the starter kit.   -->

### Tools / packages used
- pygame
- asyncio (for networking)
- ZeroTier (for LAN networking)

<!-- ### To-dos
- [x] Skeleton
- [x] Description of this project
- [x] Single-player mode
- [x] Multiplayer connectivity
- [ ] UML diagram -->
<!-- - [ ] UI
- [ ] meet PEP8 / add docstring / write tests -->

### Server/Client Class & Architecture 
```mermaid
---
title: Server/Client class diagram
---
classDiagram
BaseProtocol <|-- DatagramProtocol
DatagramProtocol <|-- GameServer
DatagramProtocol <|-- GameClient
class BaseProtocol {
    +connection_made()
    +connection_lost()
    +pause_writing()
    +resume_writing()
}
class DatagramProtocol {
	+datagram_received()
	+error_received()
}
class GameServer {
    - uuid_map: map
    - server_address: str
    - port: int
    - max_players: int
    - player_count: int
    - transport
    +send_message(message, addr)
    +send_status(status, addr)
    +create_udp_server() static
}

class GameClient {
    - uuid: str
    - datagram_received_cb: function
    - transport
    +send_message(message, addr)
    +send_status(status, addr)
    +create_udp_client() static
    +join_game() static
}
```

```mermaid
---
title: Server/Client flow
---
stateDiagram-v2
    s1: Server start
    s2: Wait for players
    s3: Start game server
    s4: Start game server
    s5: Game server running...
    s6: Client start
    s7: Waiting for the game to begin...
    s8: Game playing... 

    s1 --> s2: Create lobby(TCP)
    s2 --> s2
    s2 --> s3: Enter "start" command
    s3 --> [*]: Send the udp port of the game server 

    s4 --> s5: Create game server(UDP)
    s5 --> s5

    s6 --> s7: Join lobby
    s7 --> s8: Join the game
    s8 --> s8
```

```mermaid
---
title: Server/Client interaction
---
sequenceDiagram
    Client->>Server: Join lobby
    Server->>Client: Send uuid
    Client-->>Server: Wait(persist connection)
    Server->>Client: Start game(send the port of game server)
    Client->>Server: Join game
    Client->>Server: Update status...
    Server->>Client: 
```

```mermaid
---
title: Main Game Diagram
---
classDiagram
class Level {
    +create_map
    +create_attack
    +create_magic
    +player_attack_logic
}

class YSortGroup{
    +draw
    +update
}
class Entity{
    +move
    +collision
}
class Player{
    +from_keyboard
    +cooldowns
    +update
    +animate
}
class Magic{
    +attack
    +dump_to_network
    +load_from_network
}

class pygame_sprite

class Tile 

class weapon 

class boomerang{
    +move
    +actions
    +animate
    +update
}

class AnimationPlayer{
    +reflect_image
    +create_grass_particles
    +create_particle
}


Level --> YSortGroup
Entity <|-- Player
Player --> Magic
Player --> weapon
Player --> boomerang
Magic --> boomerang
Tile --> Level
AnimationPlayer --> Level
pygame_sprite<|--YSortGroup
pygame_sprite<|--Entity
pygame_sprite<|--Magic
pygame_sprite<|--Tile
pygame_sprite<|--weapon
pygame_sprite<|--Player
pygame_sprite <|-- boomerang
```

