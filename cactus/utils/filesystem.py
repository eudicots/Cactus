import os


def fileList(paths, relative=False, folders=False):
    """
    Generate a recursive list of files from a given path.
    """

    if not isinstance(paths, list):
        paths = [paths]

    files = []

    for path in paths:
        for fileName in os.listdir(path):

            if fileName.startswith('.'):
                continue

            filePath = os.path.join(path, fileName)

            if os.path.isdir(filePath):
                if folders:
                    files.append(filePath)
                files += fileList(filePath)
            else:
                files.append(filePath)

        if relative:
            files = map(lambda x: x[len(path) + 1:], files)

    return files