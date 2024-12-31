import csv

def find_duplicates(file_path):
  duplicates = {}

  count = 0

  with open(file_path, 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)

    for row in reader:
      for entry in row:
        entry_lower = entry.lower()
        if entry_lower in duplicates:
          duplicates[entry_lower].append(entry)
        else:
          duplicates[entry_lower] = [entry]
  
  with open('duplicates.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for entry, occurences in duplicates.items():
      if len(occurences) > 1:
        for occurence in occurences:
          if occurence != entry:
            writer.writerow([occurence])

if __name__ == "__main__":
  file_path = "export.csv"
  find_duplicates(file_path)