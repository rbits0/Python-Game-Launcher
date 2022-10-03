import os, re, json


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
                                titles[id] = manifest_line.split('"')[3]

                app_ids = []
                library_path = None
                continue
            
            if library_path:
                app_ids.append(line.split('\t')[3][1:-1])
    
    return titles


def createLibrary(config_folder) -> dict:
    with open(os.path.join(config_folder, 'config.json'), 'r') as file:
        config = json.load(file)
        steam_path = config['steamPath']
    
    print('To finish, type \'q\'')

    steam_titles = getSteamTitles(steam_path)
    
    game_library = []
    
    for id, name in steam_titles.items():
        user_input = input(f'Add {name} to library? [Y/n]')
        
        if user_input.lower() == 'q':
            break

        if user_input.lower() != 'n':
            game_library.append({'name': name, 'appID': id})
            
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


if __name__ == '__main__':
    config_folder = os.path.expanduser('~/.config/PythonGameLauncher')
    
    if not os.path.exists(config_folder):
        os.mkdir(config_folder)

    if not os.path.exists(os.path.join(config_folder, 'config.json')):
        createConfig(config_folder)
    


    # testList = []
    # for item in steam_titles.items():
    #     # print(item)
    #     testList.append({'name': item[1], 'appID': item[0]})
    
    # with open(os.path.join(config_folder, 'games.json'), 'w') as file:
    #     file.write(json.dumps(testList, indent=4))
    
    game_library = getLibrary(config_folder)
    print(game_library)