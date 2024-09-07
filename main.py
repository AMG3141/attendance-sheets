from attendanceSheets import *
'''
Arguments:
- URL of data or file containing URL
- Path to instruments file
- Location of content.tex (set as "" to print instead)
- Location to save tex for tables (set as "" to print instead)
- Any sections to omit
'''

# Load data
print("Loading data")
memberData = download(sys.argv[1], sys.argv[1][:4] == "http")
instData = pd.read_csv(sys.argv[2])
print("Done")

# Do not generate sheets for these sections
exclude = sys.argv[5:]

# Assign sections
assignSections(memberData, instData)

# Generate tex and print if necessary
print("Generating tables")
contentPath, tablesPath = sys.argv[3], sys.argv[4]
if contentPath == "" or tablesPath == "":
	contentPath, tablesPath = None, None

output = generateTex(memberData, exclude, contentPath, tablesPath)

if contentPath == None:
	[print(table) for table in output]
print("Done")