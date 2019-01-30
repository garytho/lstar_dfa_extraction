import argparse

class mat:

	def __init__(self, alphabet, dfa):
		self.dfa = dfa
		self.alphabet = alphabet

	def member_query(self, test_str):
		curr_state = "q0"
		for char in test_str:
			curr_state = self.dfa[curr_state][char]
		
		if curr_state in self.dfa["f"]:
			#print("       \t\t\t\t\t\t\t\t\tYES")
			return 1
		else:
			#print("       \t\t\t\t\t\t\t\t\tNO")
			return 0


	def equiv_query(self, test_dfa):

		actual_states = list(self.dfa.keys())
		actual_states.remove("f")
		test_states = list(test_dfa.keys())
		test_states.remove("f")
		state_num = len(actual_states) + len(test_states)

		not_equiv = []


		for state1 in self.dfa["f"]:
			for state2 in actual_states:
				if not state2 in self.dfa["f"]:
					not_equiv += [[state1, state2]]
			
			for state2 in test_states:
				if not state2 in test_dfa["f"]:
					not_equiv += [[state1, "t" + state2]]

		for state1 in test_dfa["f"]:
			for state2 in test_states:
				if not state2 in test_dfa["f"]:
					not_equiv += [["t" + state1, "t" + state2]]
			for state2 in actual_states:
				if not state2 in self.dfa["f"]:
					not_equiv += [["t" + state1, state2]]


		temp_equiv = [] + not_equiv

		counter_ex = []
		
		while temp_equiv:
			new_equiv = []

			ex_d = {}

			for pair in temp_equiv:
				#find every parent of each state, if they have the same transition character, add to temp_equiv
				parents = [{}, {}]
				x = 0
				for child in pair:

					if child[0] == "t":
						for letter in self.alphabet:
							parents[x][letter] = []
						for state in test_states:
							for letter in self.alphabet:
								if test_dfa[state][letter] == child[1:]:
									parents[x][letter] += ["t" + state]
					else:
						for letter in self.alphabet:
							parents[x][letter] = []
						for state in actual_states:
							for letter in self.alphabet:
								if self.dfa[state][letter] == child:
									parents[x][letter] += [state]
					x += 1

				

				for letter in self.alphabet:
					for p1 in parents[0][letter]:
						for p2 in parents[1][letter]:
							if not ([p1, p2] in not_equiv or [p2, p1] in not_equiv):
								new_equiv += [[p1, p2]]
								ex_d[p1 + p2] = [pair, letter]

			counter_ex = [ex_d] + counter_ex

			not_equiv += new_equiv
			temp_equiv = [] + new_equiv

		if ["q0", "tq0"] in not_equiv or ["tq0", "q0"] in not_equiv:
			print("       \t\t\t\t\t\t\t\t\tNOT EQUIVALENT")
			
			found = False
			state = ""
			ex_str = ""
			for x in counter_ex:
				if not found:
					if "q0tq0" in x:
						found = True
						state = ''.join(x["q0tq0"][0])
						ex_str += x["q0tq0"][1]
					elif "tq0q0" in x:
						found = True
						state = ''.join(x["tq0q0"][0])
						ex_str += x["tq0q0"][1]							
				else:
					ex_str += x[state][1]
					state = ''.join(x[state][0])

			print("       \t\t\t\t\t\t\t\t\t" + ex_str)
			return (0, ex_str)

		else:
			print("       \t\t\t\t\t\t\t\t\tEQUIVALENT")
			return (1, None)

class learner:


	def __init__(self, alphabet, mat):
		self.alphabet = alphabet
		self.mat = mat
		self.S = [""]
		self.E = [""]
		self.T = [[] for x in range(len(self.S))]
		self.T[0] += [self.member_query("")]

	def member_query(self, test_str):
		#print("IS MEMBER? " + "\'" + test_str + "\'")
		return self.mat.member_query(test_str)

	def row(self, s):
		return [self.member_query(s + e) for e in self.E]

	def is_closed(self):
		for s in self.S:
			for a in self.alphabet:
				for s2 in range(len(self.S)):
					if self.row(s + a) == self.row(self.S[s2]):
						break;
					if s2 == len(self.S) - 1:
						return 0
		return 1


	def is_consistent(self):
		for s in self.S:
			for s2 in self.S:
				if self.row(s) == self.row(s2):
					for a in self.alphabet:
						if self.row(s + a) != self.row(s2 + a):
							return 0
		return 1

	def learn_dfa(self):
		while True:		

			if not self.is_closed():
				for s in self.S:
					for a in self.alphabet:
						for s2 in range(len(self.S)):
							if self.row(s + a) == self.row(self.S[s2]):
								break;
							if s2 == len(self.S) - 1:
								self.S += [s + a]
								self.T.append([self.row(s + a)])
				continue

			if not self.is_consistent():
				for s in self.S:
					for s2 in self.S:
						if self.row(s) == self.row(s2):
							for a in self.alphabet:
								for e in self.E:
									if self.member_query(s + a + e) != self.member_query(s2 + a + e):
										self.E += [a + e]
										for ind in range(len(self.S)):
											self.T[ind].append(self.member_query(self.S[ind] + a + e))
				continue

			#case: consistent and closed
			t_dfa = {}
			t_dfa["f"] = []
			for row in self.T:
				t_dfa[''.join(map(str, row))] = {}
			
				if row[0] == 1:
					t_dfa["f"] += [''.join(map(str, row))]
			
			for row in range(len(self.T)):
				for a in self.alphabet:
					t_dfa[''.join(map(str, self.T[row]))][a] = ''.join(map(str, self.row(self.S[row] + a)))

			
			q0 = ''.join(map(str, self.T[0]))

			t_dfa["q0"] = t_dfa[q0]
			del t_dfa[q0]


			for key in t_dfa.keys():
				for a in self.alphabet:
					
					if key == "f":
						break

					if t_dfa[key][a] == q0:
						t_dfa[key][a] = "q0"

			if q0 in t_dfa["f"]:
				t_dfa["f"].remove(q0)
				t_dfa["f"].append("q0")


			result = self.mat.equiv_query(t_dfa)		

			if result[0] == 1:
				print("CORRECT DFA LEARNED")
				print("STUDENT DFA")
				print(t_dfa)
				print("TEACHER DFA")
				print(self.mat.dfa)
				break
			else:
				for x in range(len(result[1])):
					self.S.append(result[1][x:])
					self.T.append(self.row(result[1][x:]))






#test case dfas

alphabet1 = ["a", "b"]

mat1 = mat(	alphabet1,
		{"q0": {"a": "q1", "b": "q2"},
		"q1": {"a": "q2", "b": "q1"},
		"q2": {"a": "q1", "b": "q3"},
		"q3": {"a": "q2", "b": "q1"},
		"f": ["q3"]}	
		)

mat2 = mat(	alphabet1,
		{"q0": {"a": "q1", "b": "q1"},
		"q1": {"a": "q2", "b": "q2"},
		"q2": {"a": "q3", "b": "q3"},
		"q3": {"a": "q3", "b": "q3"},
		"f": ["q3"]}	
		)

dfa1 = {"q0": {"a": "q0", "b": "q0"},
	"f": []}



#execution


print("LEARNER\t\t\t\t\t\t\t\t\tTEACHER")
print("~~~~~~~\t\t\t\t\t\t\t\t\t~~~~~~~")

print("Test 1")
test = learner(alphabet1, mat2)
test.learn_dfa()

print("Test 2")
test = learner(alphabet1, mat1)
test.learn_dfa()



