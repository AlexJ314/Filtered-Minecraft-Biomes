Install `mcgen`
  `pip install mcgen`
  If you're using version 1.21.4, you can skip this step as I've included the file it creates


Run `mcgen` to generate biome parameters
  `python -m mcgen --jarpath ./jar --rawpath ./raw --outpath ./out --version 1.21.4`
  The path from which you run this cannot include spaces
  If you're using version 1.21.4, you can skip this step as I've included the file it creates


Run `filter.py` with a list of words to generate the datapack
  Only biomes that have at least one of these words (or characters) will be included
  You may include `-d <biome_name>` to exlude that biome


A zipped datapack will be generated.
  Before a new world has been generated, add and enable this pack
  After enabling the pack, click through the world type options until you're back to `Default`
    This cycle must happen for the pack to be applied
    You may need to change the version number in `pack.mcmeta` if you're not running 1.21.4
      The datapack should still work, regardless of minecraft's warning
