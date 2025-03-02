"""Only allow whitelisted biomes to generate"""
import os
import sys
import shutil



OVERWORLD_BIOMES_FILE = "./out/reports/biome_parameters/minecraft/overworld/data.min.json"
NETHER_BIOMES_FILE = "./out/reports/biome_parameters/minecraft/nether/data.min.json"
OUTPUT_FILE_NAME = "filtered_biomes"
OUTPUT_FILE = "./"+OUTPUT_FILE_NAME+"/data/minecraft/worldgen/world_preset/normal.json"
LOG_FILE = "./"+OUTPUT_FILE_NAME+"/arguments.txt"


def main():
  '''Parse args and run everything else'''

  # Make sure there are arguments
  if (len(sys.argv) < 2):
    need_args()
    return 0
  # Parse args
  (allow, deny) = parse_args(sys.argv[1:])
  # Make sure there is something to work with
  if (len(allow) + len(deny) < 1):
    need_args()
    return 0

  # Read in biome parameters
  overworld_filtered = ""
  with open(OVERWORLD_BIOMES_FILE, 'r', encoding="utf-8") as fin:
    # Read file to list, filter the list, write to .json
    overworld_filtered = assemble(deny_filter(allow_filter(parse_file(fin.read()), allow), deny))
  nether_filtered = ""
  with open(NETHER_BIOMES_FILE, 'r', encoding="utf-8") as fin:
    # Read file to list, filter the list, write to .json
    nether_filtered = assemble(deny_filter(allow_filter(parse_file(fin.read()), allow), deny))

  # Write filtered biome parameters to file
  with open(OUTPUT_FILE, 'w', encoding="utf-8") as fout:
    # Overwrite line 9 `"preset": "minecraft:overworld"` in `normal.json`
    fout.write("""{\n  "dimensions": {\n    "minecraft:overworld": {\n      "type": "minecraft:overworld",\n      "generator": {\n        "type": "minecraft:noise",\n        "biome_source": {\n          "type": "minecraft:multi_noise",""")
    fout.write(overworld_filtered)
    # Overwrite line 30 `"preset": "minecraft:nether"` in `normal.json`
    fout.write("""\n        },\n        "settings": "minecraft:overworld"\n      }\n    },\n    "minecraft:the_end": {\n      "type": "minecraft:the_end",\n      "generator": {\n        "type": "minecraft:noise",\n        "biome_source": {\n          "type": "minecraft:the_end"\n        },\n        "settings": "minecraft:end"\n      }\n    },\n    "minecraft:the_nether": {\n      "type": "minecraft:the_nether",\n      "generator": {\n        "type": "minecraft:noise",\n        "biome_source": {\n          "type": "minecraft:multi_noise",\n""")
    fout.write(nether_filtered)
    fout.write("""\n        },\n        "settings": "minecraft:nether"\n      }\n    }\n  }\n}""")

  # Write arguments to file, for convenience
  with open(LOG_FILE, 'w', encoding="utf-8") as fout:
    fout.write("Allow:\n  ")
    fout.write(' '.join(allow))
    fout.write("\nDeny:\n  ")
    fout.write(' '.join(deny))
    fout.write("\n")

  # Generate datapack
  shutil.make_archive(OUTPUT_FILE_NAME, 'zip', "./"+OUTPUT_FILE_NAME)

  # done!
  return 0


def need_args():
  '''Tell the user we need arguments'''
  print("Usage: python " + sys.argv[0] + " biome_name another_biome -d biome_i_hate ...")
  print(" for example...")
  print("python " + sys.argv[0] + " deep_dark ocean mushroom_fields -d beach -d wood")
  print(" will include any biomes that have \"deep_dark\", \"ocean\", or \"mushroom_fields\" in their name")
  print("  but will exclude any biomes with \"beach\" or \"wood\" in their name")
  print("\n")
  return 0


def parse_args(args):
  '''Parse list of arguments into allowed and denied biomes'''
  allow = []
  deny = []
  deny_next = False
  for arg in args:
    if arg == "-d":
      deny_next = True
    else:
      if (deny_next):
        deny_next = False
        deny.append(arg)
      else:
        allow.append(arg)
  return (allow, deny)


def parse_file(string):
  ''' Take a string and break it up into a list of brackets '''

  # Hold each { .... } while we assemble it
  tmp = ""

  # The list to return
  out = []

  # How many brackets deep are we?
  depth = 0

  # Start at 11 as we assume the BIOMES_FILE starts with
  # {"biomes":[
  # We just don't want that first bracket

  # For each character in the string...
  for c in string[11:]:

    # Record it
    tmp += c

    # Each element in the list ends with a closing bracket.
    # Is this the closing bracket that matches with the opening bracket?
    if (c == "}"):
      depth -= 1

    # Each element in the list starts with an opening bracket.
    elif (c == "{"):
      depth += 1

    # Have we fully found a { ... } ?
    if (depth == 0):

      # Store it as a list element
      out.append(tmp)

      # Get ready for a new list element
      tmp = ""

  # Return the list!
  return out


def allow_filter(lst, filt):
  ''' Filter the list by a list of allowed elements '''

  # What to return
  out = []

  # For each element in the list to be filtered...
  for l in lst:

    # For each element in the filter...
    for f in filt:

      # If the list element contains an allowed biome...
      if (f in l):

        # Record it!
        out.append(l)

        # Save time
        break;

  # Return the filtered list
  return out


def deny_filter(lst, filt):
  ''' Filter the list by a list of disallowed elements '''

  # What to return
  out = []

  # Is this an allowed biome?
  good = True

  # For each element in the list to be filtered...
  for l in lst:

    # For each element in the filter...
    for f in filt:

      # If the list element contains any disallowed biome...
      if (f in l):

        # Don't allow this biome
        good = False

        # Save time
        break;

    # Was this biome not blacklisted?
    if (good and (len(l) != 1)):

      # Record it!
      out.append(l)

    # Reset good for the next element
    good = True

  # Return the filtered list
  return out


def assemble(lst):
  ''' Reassemble the string into something that looks like a .json '''

  # Start the .json off with "biomes": [
  out = "\"biomes\": ["

  if (len(lst) > 0):
    # For each { ... } element, except the last one
    for l in lst[:-1]:

      # Record it
      out += l

      # Add a comma
      out += ",\n"

    # Now add the last element, with no comma
    out += lst[-1]
  else:
    print("WARNING: dimension has no biomes. Did you forget to include Nether biomes?")

  # Add a newline and close the list
  out += "\n]"

  # Return it!
  return out


if __name__ == "__main__":
  main()
