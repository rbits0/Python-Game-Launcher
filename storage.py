import os, json
from PySide6.QtGui import QPixmap

CONFIG_FOLDER = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'PythonGameLauncher')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'config.json')
GAMES_FILE = os.path.join(CONFIG_FOLDER, 'games.json')
ARTWORK_FOLDER = os.path.join(CONFIG_FOLDER, 'artwork')

def getConfig() -> dict:
    if not os.path.exists(ARTWORK_FOLDER):
        os.mkdir(ARTWORK_FOLDER)

    if not os.path.exists(CONFIG_FILE):
        return False
    
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    
    return config

def saveConfig(config: dict) -> None:
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent='\t')


def addTags(config: dict, tags: list) -> None:
    config['tags'] = tags


def getLibrary() -> list[dict]:
    if os.path.exists(GAMES_FILE) and os.path.getsize(GAMES_FILE) > 0:
        with open(GAMES_FILE, 'r') as file:
            game_library = json.load(file)
        
        return game_library
    else:
        with open(GAMES_FILE, 'w') as file:
            json.dump([], file, indent='\t')
        return []

def saveLibrary(library: list[dict]) -> None:
    library.sort(key = lambda x: x['name'].lower().replace('the ', ''))
    
    with open(GAMES_FILE, 'w') as file:
        json.dump(library, file, indent='\t')


def getLibraryImage(id: int) -> QPixmap:
    if os.path.exists(os.path.join(ARTWORK_FOLDER, f'{id}_library_image.jpg')):
        path = os.path.join(ARTWORK_FOLDER, f'{id}_library_image.jpg')
    elif os.path.exists(os.path.join(ARTWORK_FOLDER, f'{id}_library_image.png')):
        path = os.path.join(ARTWORK_FOLDER, f'{id}_library_image.png')
    else:
        return None

    return QPixmap(path)


def addNativeGame(library: list[dict], name: str, filepath: str, args: list = None, tags: list = None) -> None:
    id = getNewID(library)
    game = {'name': name, 'filepath': filepath, 'id': id, 'source': 'native'}
    if args is not None and len(args) > 0:
        game['args'] = args
    if tags is not None and len(tags) > 0:
        game['tags'] = tags
    
    library.append(game)

def getNewID(library: dict) -> int:
    if len(library) == 0:
        return 0
    else:
        return max([x['id'] for x in library]) + 1

