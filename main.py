
# id - HP:0000000
# alt_id - HP:0000000 -> Can be multiple
# name - "Male blah blah"
# def - "Decreased blah blah [HPO:probinson]"
# is_a - HP:0000000 ! "Name" -> Can be multiple
# created_by - "peter"
# creation_date - "2008-02-27T02:20:00Z"
# property_value - HP:0040005 "`Dysfunction` (PATO:0001641) of the `urinary bladder` (FMA:15900)." 
# comment - "The urinary tract comprises the kidneys, ureters, a bladder, and a urethra."
# xref - UMLS:C1848145 "Poor bladder function" -> can be multiple
# synonym - "High arched palate" EXACT [] -> can be multiple

# EXAMPLE
# [Term]
# id: HP:0000218
# name: High palate
# alt_id: HP:0000156
# alt_id: HP:0009080
# alt_id: HP:0009082
# alt_id: HP:0009097
# def: "Height of the palate more than 2 SD above the mean (objective) or palatal height at the level of the first permanent molar more than twice the height of the teeth (subjective)." [pmid:19125428]
# comment: The measuring device for this assessment is described in (Hall JG, Froster-Iskenius UG, Allanson JE, Gripp K, Slavotinek A. 2006. Handbook of Normal Physical Measurements. 2nd edition. Oxford Medical, publishers). A high palate is often associated with a narrow palate. However, a narrow palate can easily give a false appearance of a high palate. Height and width of the palate should be assessed and coded separately. We do not recommend the subjective determination because this term can be overused and\napplied inaccurately.
# synonym: "High arched palate" EXACT []
# synonym: "High narrow palate" EXACT []
# synonym: "High, arched palate" EXACT []
# synonym: "High-arched palate" EXACT []
# synonym: "Narrow and high arched palate" EXACT []
# synonym: "Narrow, high-arched palate" EXACT []
# synonym: "Narrow, highly arched palate" EXACT []
# synonym: "Palate high-arched" EXACT []
# xref: UMLS:C0240635 "High arched palate"
# xref: UMLS:C1398297 "High palate"
# is_a: HP:0000174 ! Abnormality of the palate

# STEPS:
# break by [term]
# break by line
# if line starts with "id: " grab the rest of the line as id
# if line starts with "name: " grab the rest of the line as name
# if line starts with "is_a: " grab the what's between "is_a: " and " !" and push into list

from pprint import pprint
import re
import jsonpickle
import sys
sys.setrecursionlimit(30000) # 10000 is an example, try with different values

class Phenotype:
	def __init__(self):
		# single values
		self.id = None
		self.name = None
		# self.defn = None # note the change from def
		# self.created_by = None
		# self.creation_date = None
		# self.property_value = None
		# self.comment = None

		# multi values
		# self.alt_id = []
		self.is_a_string = []
		# self.is_a = []
		# self.xref = []
		# self.synonym = []
		self.child = [] # added to create tree stucture from data links

# goal is to read through the data dump,
# extract the terms, fill their attributes
# into a class structure, and then generate
# a json dump.
def main():
	phenoDic = {}
	phenoSingleAttrTupleList = [('id', 'id: '),
						('name', 'name: ')#,
						# ('defn', 'def: '), # note the change in name
						# ('created_by', 'created_by: '),
						# ('creation_date', 'creation_date: '),
						# ('property_value', 'property_value: '), 
						# ('comment', 'comment: ')
						]

	phenoMultiAttrTupleList = [#('alt_id', 'alt_id: '),
						('is_a_string', 'is_a: '),
						# ('xref', 'xref: '),
						# ('synonym', 'synonym: ')
						]

	# read into data file				  
	f = open('hp.obo', 'r')
	phenoFile = f.read().split('[Term]')
	phenoFile.pop(0) # remove leading junk

	# create linear list of terms
	for term in phenoFile:
		pheno = Phenotype()
		prop = term.split('\n')
		prop = [x for x in prop if x != '']

		# extract and fill all single values
		for func, attr in phenoSingleAttrTupleList:
			temp = [x for x in prop if attr in x]
			if temp:
				temp = re.sub(attr, '', temp[0])
				setattr(pheno, func, temp)

		for func, attr in phenoMultiAttrTupleList:
			temp = [x for x in prop if attr in x]
			if temp:
				for item in temp:
					item = re.sub(attr, '', item)

					# get current attr list
					templist = getattr(pheno, func)
					if templist: # if there's items already
						setattr(pheno, func, templist + [item])
					else: # no items yet
						setattr(pheno, func, [item])

		phenoDic[pheno.id] = pheno

	# build the is_a relationship object structure structure
	# also build the tree structure from the reverse. TODO
	for key in phenoDic:
		is_a_list = phenoDic[key].is_a_string # list of string is_a's
											  # i.e. ["HP:340234 ! fsdf", "..."]	
		for item in is_a_list: # i.e. "HP:340234 ! fsdf"
			item = item[:10] # clean the item to just be the HP:0000000

			# templist = getattr(phenoDic[key], "is_a") # retrieve that pheno's is_a
			# if templist: # if there's items already
			# 	setattr(phenoDic[key], "is_a", templist + [phenoDic[item]])
			# else: # no items yet
			# 	setattr(phenoDic[key], "is_a", [phenoDic[item]])

			# now go to targetted "super pheno"
			tempchildlist = getattr(phenoDic[item], "child")
			if tempchildlist: # if there's children already
				setattr(phenoDic[item], "child", tempchildlist + [phenoDic[key]])
			else: # no items yet
				setattr(phenoDic[item], "child", [phenoDic[key]])

	# dump to json TODO: Need to create root down structure into data.

	test = jsonpickle.encode(phenoDic["HP:0000001"])

	out = open("data.json", "w+")
	out.write(test)

if __name__ == '__main__':
	main()
