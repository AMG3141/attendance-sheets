import pandas as pd
import numpy as np
import sys

# Download most recent version of member data
# str is location, either the url or a file containing the url
def download(str, url = True):
	if url:
		memberData = pd.read_csv(str)
	else:
		f = open(str, "r")
		link = f.read()
		f.close()
		memberData = pd.read_csv(link)

	memberData["Date of Birth"] = pd.to_datetime(memberData["Date of Birth"], format = "%d/%m/%Y")
	memberData.sort_values(by = ["Last Name", "First Name", "Date of Birth"], inplace = True)

	# Clean stuff up
	memberData["Instrument"] = [s.lower() for s in memberData["Instrument"]] # Making lowercase just solves problems later on
	memberData["First Name"] = [s.strip()[0].upper() + s.strip()[1:] for s in memberData["First Name"]] # Some people can't use capital letters
	memberData["Last Name"] = [s.strip()[0].upper() + s.strip()[1:] for s in memberData["Last Name"]]

	return memberData

# Assign a section to each member, based on their "main instrument"
def assignSections(memberData, instData):
	# Deal with people who only play one instrument first
	for instrument in instData["Instrument"]:
		memberData.loc[memberData["Instrument"] == instrument, "Section"] = instData[instData["Instrument"] == instrument]["Section"].to_numpy()[0]

	# Main instruments chosen based on what I assume would be their main instrument (goes alphabetically in case of a tie)
	unknownInstruments = memberData[memberData["Section"].isna()]["Instrument"]
	assignedSections = []

	for i, input in enumerate(unknownInstruments):
		insts = input.split(", ")
		insts = [s.strip().lower() for s in insts]
		np.sort(insts)
		ranks = np.zeros(len(insts))
		for j, inst in enumerate(insts):
			try:
				ranks[j] = instData[instData["Instrument"] == inst]["Priority"].iloc[0]
			except:
				print("Invalid instrument", inst)
		assignedInst = insts[np.argmin(ranks)]
		assignedSections.append(instData[instData["Instrument"] == assignedInst]["Section"].iloc[0])

	memberData.loc[memberData["Section"].isna(), "Section"] = assignedSections

# Generate tex for all tables which are not excluded
# contentFilePath is path to content.tex, if None return tex as list of string instead
# targetDir is path to directory to save tables to, if None return tex as list of string instead
def generateTex(memberData, exclude, contentFilePath = None, targetDir = None):
	if contentFilePath == None and targetDir != None or contentFilePath != None and targetDir == None:
		print("Unclear if tex should be written to file or returned. Fix `contentFilePath` and `targetDir`. Exiting.")
		return

	if contentFilePath == None and targetDir == None: tablesTex = []
	if contentFilePath != None: contentFile = open(contentFilePath, "w")

	for section in np.sort(pd.unique(memberData["Section"])):
		if section in exclude: continue

		# Get full names for players in this section
		sectionData = memberData[memberData["Section"] == section]
		sectionNames = sectionData["First Name"] + np.array([" "] * len(sectionData)) + sectionData["Last Name"]

		# Write out each section to its own file
		sectionSheet = pd.DataFrame({"Name": sectionNames, "Present": np.array([""] * len(sectionData))})
		filename = f"{np.datetime64('today')}-{section}.tex"
		sectionTex = sectionSheet.to_latex(index = False, na_rep = "", column_format = "|l|l|", longtable = True)

		# Make table look nice
		sectionTexLines = sectionTex.split("\n")
		for i, line in enumerate(sectionTexLines):
			# Add bold text to header
			sectionTexLines[i] = sectionTexLines[i].replace("Name", r"\textbf{Name}")
			sectionTexLines[i] = sectionTexLines[i].replace("Present", r"\textbf{Present}")

			# Add in horizontal lines
			if line == r"\toprule":
				sectionTexLines[i] = "\hline"
				continue
			if line == r"\midrule" or line == r"\bottomrule":
				sectionTexLines[i] = ""
				continue
			sectionTexLines[i] = sectionTexLines[i].replace(r"\\", r"\\ \hline")

			# Remove footer
			if line == r"\multicolumn{2}{r}{Continued on next page} \\":
				sectionTexLines[i] = ""

		# Colour header
		sectionTexLines.insert(2, r"\rowcolor{grey}")

		# Write table to file or add to list
		if targetDir == None:
			tablesTex.append("\n".join(sectionTexLines))
		else:
			f = open(f"{targetDir}/{filename}", "w")
			f.writelines("\n".join(sectionTexLines))
			f.close()

		# Put the tables in the document (if necessary)
		if contentFilePath != None:
			contentFile.write(r"\pagestyle{" + section + r"}" + "\n")
			# contentFile.write(r"\section*{" + section + r"}" + "\n")
			contentFile.write(r"\input{tables/" + filename + r"}" + "\n")
			contentFile.write(r"\newpage" + "\n")

	if contentFilePath != None: contentFile.close()
	else: return tablesTex