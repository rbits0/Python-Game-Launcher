import os, re, json
import shutil

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


def getSteamTitles() -> dict:
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
                for appID in app_ids:
                    with open(os.path.join(library_path, 'steamapps', 'appmanifest_' + appID + '.acf'), 'r') as app_manifest:
                        for manifest_line in app_manifest:
                            if manifest_line.count('"name"') > 0:
                                titles[appID] = (manifest_line.split('"')[3], library_path)

                app_ids = []
                library_path = None
                continue
            
            if library_path:
                app_ids.append(line.split('\t')[3][1:-1])
    
    return titles


def addGame(game_library, name, appID, library_path, game_id = None):
    # First, find available id
    if not game_id:
        if len(game_library) == 0:
            game_id = 0
        else:
            game_id = max([x['id'] for x in game_library]) + 1
    
    game_library.append({'name': name, 'appID': appID, 'libraryPath': library_path, 'id':game_id})


def addGames(game_library, games, library_path):
    # First, find available id
    if len(game_library) == 0:
        game_id = 0
    else:
        game_id = max([x['id'] for x in game_library]) + 1

    for appID, data in games.items():
        game_library.append({'name': data[0], 'appID': appID, 'libraryPath': library_path, 'id': game_id})
        getSteamArtwork(appID, game_id)

        game_id += 1
   


def saveLibrary(game_library):
    game_library.sort(key = lambda x: x['name'].lower().replace('the ', ''))
    
    with open(GAMES_FILE, 'w') as file:
        json.dump(game_library, file, indent='\t')


def updateLibrary(game_library):
    steam_titles = getSteamTitles()
    
    games = {}

    for appID, data in steam_titles.items():
        name = data[0]
        library_path = data[1]

        if appID in [i['appID'] for i in game_library]:
            continue
        
        user_input = input(f'Add {name} to library? [Y/n]')

        if user_input.lower() == 'q':
            break

        if user_input.lower() != 'n':
            games[appID] = data
    
    addGames(game_library, games, library_path)
    saveLibrary(game_library)


def getLibrary() -> dict:

    if os.path.exists(GAMES_FILE) and os.path.getsize(GAMES_FILE) > 0:
        with open(GAMES_FILE, 'r') as file:
            game_library = json.load(file)
        
        return game_library
    
    with open(GAMES_FILE, 'w') as file:
        json.dump([], file, indent='\t')
    return []


def getSteamArtwork(appID, game_id):
    library_image_path = os.path.join(steam_path, 'appcache', 'librarycache', appID + '_library_600x900.jpg')
    library_banner_path = os.path.join(steam_path, 'appcache', 'librarycache', appID + '_library_hero.jpg')
    if os.path.exists(library_image_path):
        try:
            shutil.copyfile(library_image_path, os.path.join(ARTWORK_FOLDER, str(game_id) + '_library_image.jpg'))
        except shutil.SameFileError:
            pass
    
    if os.path.exists(library_banner_path):
        try:
            shutil.copyfile(library_banner_path, os.path.join(ARTWORK_FOLDER, str(game_id) + '_library_banner.jpg'))
        except shutil.SameFileError:
            pass


def getLibrarySteamArtwork(game_library):
    for game in game_library:
        getSteamArtwork(game['appID'], game['id'])
        

if __name__ == '__main__':
    if not os.path.exists(CONFIG_FOLDER):
        os.mkdir(CONFIG_FOLDER)

    if not readConfig():
        steam_path = input('Please enter the path to the steam directory (default = ~/.steam/steam)')
        steam_path = createConfig(steam_path)
    
    game_library = getLibrary()
    updateLibrary(game_library)
    print([i['name'] for i in game_library])
    print(game_library)