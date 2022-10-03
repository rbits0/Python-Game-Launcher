import os, re, json
import shutil

steam_path = None


def readConfig(config_folder):
    global steam_path
    if not os.path.exists(os.path.join(config_folder, 'config.json')):
        createConfig(config_folder)
    
    if not os.path.exists(os.path.join(config_folder, 'artwork')):
        os.mkdir(os.path.join(config_folder, 'artwork'))
    
    with open(os.path.join(config_folder, 'config.json'), 'r') as file:
        config = json.load(file)
        steam_path = config['steamPath']


def createConfig(config_folder):
    steam_path = input('Please enter the path to the steam directory (default = ~/.steam/steam)')
    if steam_path == '':
        steam_path = os.path.expanduser('~/.steam/steam')
    else:
        steam_path = os.path.expanduser(steam_path)
    
    config = {'steamPath': steam_path}

    with open(os.path.join(config_folder, 'config.json'), 'w') as file:
        json.dump(config, file, indent='\t')
    
    return


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


def createLibrary(config_folder) -> dict:
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
            
            with open(os.path.join(config_folder, 'games.json'), 'w') as file:
                json.dump(game_library, file, indent='\t')

    return game_library


def getLibrary(config_folder) -> dict:
    games_json_path = os.path.join(config_folder, 'games.json')

    if os.path.exists(games_json_path) and os.path.getsize(games_json_path) > 0:
        with open(os.path.join(config_folder, 'games.json'), 'r') as file:
            game_library = json.load(file)
        
        return game_library
    
    game_library = createLibrary(config_folder)
    return game_library


def getSteamArtwork(game_library, config_folder):
    for game in game_library:
        library_image_path = os.path.join(steam_path, 'appcache', 'librarycache', game['appID'] + '_library_600x900.jpg')
        library_banner_path = os.path.join(steam_path, 'appcache', 'librarycache', game['appID'] + '_library_hero.jpg')
        if os.path.exists(library_image_path):
            try:
                shutil.copyfile(library_image_path, os.path.join(config_folder, 'artwork', str(game['id']) + '_library_image.jpg'))
            except shutil.SameFileError:
                pass
        
        if os.path.exists(library_banner_path):
            try:
                shutil.copyfile(library_banner_path, os.path.join(config_folder, 'artwork', str(game['id']) + '_library_banner.jpg'))
            except shutil.SameFileError:
                pass


if __name__ == '__main__':
    config_folder = os.path.expanduser('~/.config/PythonGameLauncher')
    
    if not os.path.exists(config_folder):
        os.mkdir(config_folder)

    readConfig(config_folder)
    
    game_library = getLibrary(config_folder)
    print(game_library)
    
    getSteamArtwork(game_library, config_folder)