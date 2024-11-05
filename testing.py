import pytest
import os
from pathlib import Path
import sys

files = os.listdir("./sub_tests/good")
relative_paths = [os.path.relpath(os.path.join("sub_tests/good", file)) for file in files]

@pytest.mark.parametrize("file", relative_paths)
def test(file):
    original_argv = sys.argv.copy()
    sys.argv = [sys.argv[0]]
    sys.argv.extend(['prevent_help_diaglog'])
    
    from libs.subcleaner.settings.args import subtitles
    subtitles = [Path(file)]
    from libs.subcleaner.subtitle import Subtitle
    from libs.subcleaner import cleaner
    sys.argv = original_argv
    subtitle_file = subtitles[0]
    subtitle = Subtitle(subtitle_file)
    cleaner.unscramble(subtitle)
    cleaner.find_ads(subtitle)
    failed = False
    from helper import report
    for ad in subtitle.ad_blocks:
        hints = ad.hints
        for hint in hints:
            if hint.startswith("zh_"):
                print(f"\n\033[0;31mBad regex: {hint}\033[0m\n")
                print("==================")
                print(report([ad]))
                failed = True
    if failed:
        assert False

