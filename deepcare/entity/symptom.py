# from setting import setting
# from deepcare.database.query import DC_Query
# from deepcare.entity.symptom import Symptom

class Symptom():
    
    def __init__(self, label=None, iri=None):
        self.label = label
        self.iri = iri
        self.related_diseases = None
        self.weight = 0
        self.related_symptoms = None
        self.position = None
        self.symptoms_where = None
        self.symptoms_when = None
        self.symptoms_how = None
        self.gender = None
        self.label_en = None

    def set_weight(self, weight):
        self.weight = weight

    def set_diseases(self, diseases):
        self.related_diseases = diseases

    def set_symptoms(self, symptoms):
        self.related_symptoms = symptoms
    
    def set_symptoms_where(self, symptoms):
        self.symptoms_where = symptoms
    
    def set_symptoms_when(self, symptoms):
        self.symptoms_when = symptoms

    def set_symptoms_how(self, symptoms):
        self.symptoms_how = symptoms

    def set_gender(self, gender):
        self.gender = gender   
    
    def set_label_en(self, label_en):
        self.label_en = label_en