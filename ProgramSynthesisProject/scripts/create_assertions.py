import csv

with open("data/processed/policy_examples.csv") as inputFile:
    with open("sketch_assertions.txt", "w") as outputFile:
        reader = csv.DictReader(inputFile)
        
        for row in reader:
            port = row["port"]
            decision = row["decision"].strip().upper()
            
            outputFile.write(f"assert policy({port}) == {decision};\n")

print("Wrote output to sketch_assertions.txt")

