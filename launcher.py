import os, re, json
import shutil
from venv import create

steam_path = None
CONFIG_FOLDER = os.path.expanduser('~/.config/PythonGameLauncher')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'config.json')
GAMES_FILE = os.path.join(CONFIG_FOLDER, 'games.json')
ARTWORK_FOLDER = os.path.join(CONFIG_FOLDER, 'artwork')


def readConfig():
    global steam_path
    if not os.path.exists(ARTWORK_FOLDER):
        os.mkdir(ARTWORK_FOLDER)

    if not os.path.exists(CONFIG_FILE):
        return False
    
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
        steam_path = config['steamPath']
    
    return True

def createConfig(steam_path):
    if steam_path == '':
        steam_path = os.path.expanduser('~/.steam/steam')
    else:
        steam_path = os.path.expanduser(steam_path)
    
    config = {'steamPath': steam_path}

    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent='\t')
    
    return steam_path


def getSteamTitles(steam_path) -> dict:
    libraryfolders_path = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')

    with open(libraryfolders_path, 'r') as file:
        app_ids = []
        titles = {}
        library_path = None

        for line in file:
            if line.count('"path"') > 0:
                library_path = line[11:-2]
                for i in range(7):
                    file.readline()
                # print(file.readline().split('\t'))

                continue
            
            if line == '\t\t}\n':
                for id in app_ids:
                    with open(os.path.join(library_path, 'steamapps', 'appmanifest_' + id + '.acf'), 'r') as app_manifest:
                        for manifest_line in app_manifest:
                            if manifest_line.count('"name"') > 0:
                                titles[id] = (manifest_line.split('"')[3], library_path)

                app_ids = []
                library_path = None
                continue
            
            if library_path:
                app_ids.append(line.split('\t')[3][1:-1])
    
    return titles


def createLibrary() -> dict:
    print('To finish, type \'q\'')

    steam_titles = getSteamTitles(steam_path)
    
    game_library = []
    
    game_id = 0
    
    for id, data in steam_titles.items():
        name = data[0]
        library_path = data[1]

        user_input = input(f'Add {name} to library? [Y/n]')
        
        if user_input.lower() == 'q':
            break

        if user_input.lower() != 'n':
            game_library.append({'name': name, 'appID': id, 'libraryPath': library_path, 'id': game_id})
            game_id += 1
            
            with open(os.path.join(CONFIG_FOLDER, 'games.json'), 'w') as file:
                json.dump(game_library, file, indent='\t')

    return game_library


def getLibrary() -> dict:

    if os.path.exists(GAMES_FILE) and os.path.getsize(GAMES_FILE) > 0:
        with open(GAMES_FILE, 'r') as file:
            game_library = json.load(file)
        
        return game_library
    
    with open(GAMES_FILE, 'w') as file:
        json.dump([], file, indent='\t')
    return []


def getSteamArtwork(game):
    library_image_path = os.path.join(steam_path, 'appcache', 'librarycache', game['appID'] + '_library_600x900.jpg')
    library_banner_path = os.path.join(steam_path, 'appcache', 'librarycache', game['appID'] + '_library_hero.jpg')
    if os.path.exists(library_image_path):
        try:
            shutil.copyfile(library_image_path, os.path.join(ARTWORK_FOLDER, str(game['id']) + '_library_image.jpg'))
        except shutil.SameFileError:
            pass
    
    if os.path.exists(library_banner_path):
        try:
            shutil.copyfile(library_banner_path, os.path.join(ARTWORK_FOLDER, str(game['id']) + '_library_banner.jpg'))
        except shutil.SameFileError:
            pass



def getLibrarySteamArtwork(game_library):
    for game in game_library:
        getSteamArtwork(game)
        

if __name__ == '__main__':
    if not os.path.exists(CONFIG_FOLDER):
        os.mkdir(CONFIG_FOLDER)

    if not readConfig():
        steam_path = input('Please enter the path to the steam directory (default = ~/.steam/steam)')
        steam_path = createConfig(steam_path)
    
    game_library = getLibrary()
    if len(game_library) == 0:
        game_library = createLibrary()
    # print(game_library)
    
    getLibrarySteamArtwork(game_library)