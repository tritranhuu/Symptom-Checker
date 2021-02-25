class User():
	def __init__(self, name, age, gender):
		self.name = name
		self.gender = gender
		self.age_num = age
		if age < 5:
			self.age = "Sơ_sinh"
		elif 5 <= age < 18:
			self.age = "Trẻ_em"
		elif 18 <= age < 40:
			self.age = "Trưởng_thành"
		elif 40 <= age < 60:
			self.age = "Trung_niên"
		else:
			self.age = "Già"