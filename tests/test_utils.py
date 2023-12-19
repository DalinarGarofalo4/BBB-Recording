import pytest

from app.utils.recording_util import get_full_folder_path


@pytest.mark.asyncio
@pytest.mark.parametrize('folder_path, result', [
    ("", []),
    ("///", []),
    ("folder_1", ["folder_1"]),
    ("folder_1/folder_2", ["folder_1", "folder_1/folder_2"]),
    ("folder_1/folder_2/folder_3", ["folder_1", "folder_1/folder_2", "folder_1/folder_2/folder_3"]),
    ("folder_1///folder_2///folder_3///", ["folder_1", "folder_1/folder_2", "folder_1/folder_2/folder_3"]),
])
async def test_get_full_folder_path(folder_path: str, result: list):
    assert result == await get_full_folder_path(folder_path)
