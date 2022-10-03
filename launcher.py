import os, re, json


def getSteamTitles(steam_path) -> list:
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


if __name__ == '__main__':
    steam_path = os.path.expanduser('~/.steam/steam')
    config_folder = os.path.expanduser('~/.config/PythonGameLauncher')

    steam_titles = getSteamTitles(steam_path)
