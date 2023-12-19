import os


async def get_full_folder_path(folder_path: str):
    list_folder_path = list(filter(lambda x: x != '' and x is not None, folder_path.split('/')))
    result = []
    for path in list_folder_path:
        if len(result):
            result.append(os.path.join(result[-1], path))
        else:
            result.append(path)
    return result
