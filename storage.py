import os, json
from typing import Optional, TypedDict, NotRequired, Any
from PySide6.QtGui import QPixmap

CONFIG_FOLDER = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'PythonGameLauncher')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'config.json')
GAMES_FILE = os.path.join(CONFIG_FOLDER, 'games.json')
ARTWORK_FOLDER = os.path.join(CONFIG_FOLDER, 'artwork')


class Config:
    def __init__(self) -> None:
        if not os.path.exists(CONFIG_FOLDER):
            os.mkdir(CONFIG_FOLDER)

        if not os.path.exists(ARTWORK_FOLDER):
            os.mkdir(ARTWORK_FOLDER)

        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w'):
                pass
        
        if not os.path.exists(GAMES_FILE):
            with open(GAMES_FILE, 'w'):
                pass
        

        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
        
        self.steamPath: str = config['steamPath']
        self.tags: list[str] = config['tags']
    
    def save(self) -> None:
        config = {
            'steamPath': self.steamPath,
            'tags': self.tags,
        }
        
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent='\t')
    
    def updateTags(self, tags: list[str]) -> None:
        self.tags = tags



class Game(TypedDict):
    name: str
    id: int
    source: str
    tags: list[str]
    description: NotRequired[str]
    data: dict[str, Any]
    

class Library:
    def __init__(self) -> None:
        self.games: list[Game]
        
        if os.path.getsize(GAMES_FILE) > 0:
            with open(GAMES_FILE, 'r') as file:
                game_library = json.load(file)
            
            self.games = game_library
        else:
            with open(GAMES_FILE, 'w') as file:
                json.dump([], file, indent='\t')

            self.games = []

    def save(self) -> None:
        self.games.sort(key = lambda x: x['name'].lower().replace('the ', ''))
        
        with open(GAMES_FILE, 'w') as file:
            json.dump(self.games, file, indent='\t')

    def addNativeGame(
        self,
        name: str,
        filepath: str,
        args: Optional[list[str]] = None,
        tags: Optional[list[str]] = None
    ) -> None:
        if tags is None:
            tags = []
        if args is None:
            args = []
        
        id = self.getNewID()

        game: Game = {
            'name': name,
            'id': id,
            'source': 'native',
            'tags': tags,
            'data': {
                'filepath': filepath,
                'args': args
            },
        }
        
        self.games.append(game)

    def getNewID(self) -> int:
        if len(self.games) == 0:
            return 0
        else:
            return max([x['id'] for x in self.games]) + 1


def getLibraryImage(id: int) -> Optional[QPixmap]:
    if os.path.exists(os.path.join(ARTWORK_FOLDER, f'{id}_library_image.jpg')):
        path = os.path.join(ARTWORK_FOLDER, f'{id}_library_image.jpg')
    elif os.path.exists(os.path.join(ARTWORK_FOLDER, f'{id}_library_image.png')):
        path = os.path.join(ARTWORK_FOLDER, f'{id}_library_image.png')
    else:
        return None

    return QPixmap(path)




