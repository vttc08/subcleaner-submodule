import logging 
from pathlib import Path
from argparse import ArgumentParser
from libs.subcleaner.subtitle import Subtitle
from libs.subcleaner import cleaner

logger = logging.getLogger(__name__)

def report(blocks: list[Subtitle]) -> str:
    card = "Removed Content: \n"
    for block in blocks:
        card += f"{block.original_index}\n{block}\n\n"
    return card 

if __name__ == "__main__":
    parser = ArgumentParser(description="Helper script to deal with false positives and negatives detected by subcleaner.")
    parser.add_argument("file", type=str, help="Path to subtitles.")
    parser.add_argument("mode", type=str, help="Mode to run script in. 'x' for except mode, will re-run the cleaner and remove all detected ads except the ones provided. 'c' for cut mode, will remove only the ones provided, including non-detected ads.", choices=["x", "c"])
    parser.add_argument("line_number", type=int, help="Line number to remove from subtitle.", nargs="*")
    args = parser.parse_args()
    file = args.file
    mode = args.mode
    line_number = args.line_number # for except mode (uses original index)
    list_number = {i-1 for i in line_number if i > 0} # for cut mode (uses python list index)

    subtitle_file = Path(file)
    subtitle = Subtitle(subtitle_file)
    cleaner.unscramble(subtitle)
    
    removed = [] # Removed line numbers
    removed_blocks = [] # Removed blocks from except mode
    sub_blocks = [] # Removed blocks from cut mode
    if mode == "x": # except mode, remove all detected except the ones provided
        cleaner.find_ads(subtitle)
        for block in subtitle.ad_blocks:
            if block.original_index in line_number:
                pass
            else:
                removed.append(str(block.original_index))
                subtitle.blocks.remove(block)
                removed_blocks.append(block)
        subtitle.ad_blocks.clear()
        logger.info(report(removed_blocks))
        
    elif mode == "c": # cut mode, remove only the ones provided
        for i in list_number:
            try:
                sub_blocks.append(subtitle.blocks[i])
                removed.append(str(i+1))          
            except IndexError:
                logger.error(f"Block {i} does not exist. Every other block has been removed.")
        for block in sub_blocks:
            subtitle.blocks.remove(block)
        logger.info(report(sub_blocks))
    
    subtitle.reindex()
    logger.info(f"Removed line numbers: {', '.join(removed)}")
    with subtitle_file.open("w", encoding="UTF-8") as file:
        file.write(subtitle.to_content())

