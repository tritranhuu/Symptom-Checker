from owlready2 import *
from deepcare.entity.base import BaseEntity
from deepcare.entity.symptom import Symptom
from deepcare.entity.disease import Disease

class DC_Query():
    def __init__(self, ontopath:str):
        self.owl_prefix = "http://www.w3.org/2002/07/owl#"
        self.owl_on_property = self.owl_prefix + 'onProperty'
        self.owl_some_values = self.owl_prefix + 'someValuesFrom'

        self.has_symptom = self.owl_prefix + "has_symptom"
        self.has_main_symptom = self.owl_prefix + "has_main_symptom"
        self.probably_has_symptom = self.owl_prefix + "probably_has_symptom"

        self.can_be_caused_by = self.owl_prefix + "can_be_caused_by"
        self.can_happen_with = self.owl_prefix + "can_happen_with"


        self.world = World()
        self.world.get_ontology(ontopath).load()
        sync_reasoner(self.world)
        
        self.graph = self.world.as_rdflib_graph()
        self.graph.serialize(format="n3")

    def get_icd10_by_iri(self, iri:str):
        res = list(self.graph.query("""SELECT ?icd WHERE
            { %s ?p ?icd .
              ?p rdfs:label "icd10" . }""" % iri))
        try:
            return res[0][0].n3().split("\"")[1]
        except:
            return res[0][0].n3()

    def get_iri_by_label(self, label:str):
        res = list(self.graph.query("""SELECT ?p WHERE
            { ?p rdfs:label "%s".}""" % label))
        return res[0][0].n3()
    
    def get_label_by_iri(self, iri:str):
        res = list(self.graph.query("""SELECT ?label WHERE {<%s> rdfs:label ?label .}""" % iri))
        return res[0][0].n3()

    def get_see_also_by_iri(self, iri:str):
        res = list(self.graph.query("""SELECT ?seeAlso WHERE {<%s> rdfs:seeAlso ?seeAlso .}""" % iri))
        return res[0][0].n3()

    def get_subclass_by_iri(self, iri:str):
        res = list(self.graph.query("""SELECT ?iri WHERE {?iri rdfs:subClassOf+ <%s> .}""" % iri))
        if len(res) == 0:
            return 0
        else:
            return [row[0].n3() for row in res]
  
    def get_position_subclass_by_label(self, label:str):
        position_iri = self.get_iri_by_label("Vị_trí")
        query = """SELECT ?label WHERE {?iri rdfs:label \"%s\" .
                                        ?s rdfs:subClassOf+ %s .
                                        ?s rdfs:subClassOf ?iri . 
                                        ?s rdfs:label ?label .}""" % (label, position_iri)
        res = list(self.graph.query(query))
        if len(res) == 0:
            return 0
        else:
            return [row[0].n3().split("\"")[1] for row in res]

    def get_symptoms_by_position(self, position_label:str):
        position_rela = self.owl_prefix + "at_position"
        query = """SELECT ?label WHERE {?s rdfs:label ?label .
                                        ?s rdfs:subClassOf ?restriction .
                                        ?restriction <%s> <%s> .
                                        ?restriction <%s> ?p .
                                        ?p rdfs:label "%s" . }""" % (self.owl_on_property, position_rela, self.owl_some_values, position_label)
        res = list(self.graph.query(query))
        if len(res) == 0:
            return 0
        else:
            return [row[0].n3().split("\"")[1] for row in res]

    def get_relation_of_disease(self, disease_label:str, relation:str):
        property_rela = self.owl_prefix + relation
        disease_iri = self.get_iri_by_label("Bệnh_và_các_Chuyên_khoa")
        if relation == "common_gender":
            property_rela = "http://deepcare.io/RC3DI2JOyoraEeeaEoHtzoL"
        elif relation == "only_in_gender":
            property_rela = "http://deepcare.io/RBRAQgToSKHdJPEiCFV5UWc"
        elif relation == "lab_tests":
            property_rela = "http://deepcare.io/ROlImFu7UhXI68Arrri9UH"
        query = """SELECT ?label ?s WHERE {?d rdfs:label "%s" . 
                                        ?d rdfs:subClassOf ?restriction . 
                                        ?restriction <%s> <%s> .
                                        ?restriction <%s> ?s .
                                        ?s rdfs:label ?label .
                                        FILTER NOT EXISTS { ?s rdfs:subClassOf+ %s . }
                                        }

                """ % (disease_label, self.owl_on_property, property_rela, self.owl_some_values, disease_iri)
        
        result = self.graph.query(query)
        entity = []
        for row in result:
            entity.append(BaseEntity(label=row[0].n3().split("\"")[1], iri=row[1].n3()))
            parents = self.get_parent_symptoms_by_iri(row[1].n3())
            if parents!= 0:
                for parent in parents:
                    entity.append(BaseEntity(parent[0], parent[1]))
        return entity

    def get_disease_flag_by_iri(self, d_iri):
        property_rela = 'http://webprotege.stanford.edu/RBtP2Xc07E7dCLMbQ7Bi4ju'
        query = """SELECT ?label ?s WHERE {
                                        %s rdfs:subClassOf ?restriction . 
                                        ?restriction <%s> <%s> .
                                        ?restriction <%s> ?s .
                                        ?s rdfs:label ?label .
                                        }

                """ % (d_iri, self.owl_on_property, property_rela, self.owl_some_values)
        result = self.graph.query(query)
        if len(result) > 0:
            return result[0][0].n3()
        else:
            return None

    def get_parent_symptoms_by_iri(self, iri:str):

        sign_iri = self.get_iri_by_label("Triệu_chứng")
        position_iri = self.get_iri_by_label("Vị_trí")
        position_rela = self.owl_prefix + "at_position"

        query = """SELECT ?label ?iri WHERE {%s rdfs:subClassOf+ ?iri .
                                      ?iri rdfs:label ?label .
                                      ?iri rdfs:subClassOf %s .
                                      ?iri rdfs:subClassOf ?restriction .
                                      ?restriction <%s> <%s> .
                                      }""" % (iri, sign_iri, self.owl_on_property, position_rela)
        
        # query = """SELECT ?label ?iri WHERE {%s rdfs:subClassOf+ ?iri .
        #                               ?iri rdfs:label ?label .
        #                               ?iri rdfs:subClassOf+ %s .
        #                               }""" % (iri, sign_iri)

        res = list(self.graph.query(query))
        if len(res) == 0:
            return 0
        else:
            return [(row[0].n3().split("\"")[1], row[1].n3()) for row in res]

    def get_relation_of_symptom(self, symptom_label:str, relation:str):
        property_rela = self.get_iri_by_label(relation)
        query = """SELECT ?label ?s WHERE {?sp rdfs:label "%s" .
                                           ?s rdfs:subClassOf ?restriction .
                                           ?restriction <%s> %s .
                                           ?restriction <%s> ?sp . 
                                           ?s rdfs:label ?label .}     
        """ % (symptom_label, self.owl_on_property, property_rela, self.owl_some_values)
        result = self.graph.query(query)
        entity = []
        for row in result:
            entity.append(BaseEntity(label=row[0].n3().split("\"")[1], iri=row[1].n3()))
        return entity

    def get_symptom_gender(self, symptom_label:str):
        property_rela = self.get_iri_by_label("only_in_gender")
        query = """SELECT ?label ?s WHERE {?sp rdfs:label "%s" .
                                           ?sp rdfs:subClassOf ?restriction .
                                           ?restriction <%s> %s .
                                           ?restriction <%s> ?s . 
                                           ?s rdfs:label ?label .}     
        """ % (symptom_label, self.owl_on_property, property_rela, self.owl_some_values)
        result = self.graph.query(query)
        entity = []
        for row in result:
            entity.append(BaseEntity(label=row[0].n3().split("\"")[1], iri=row[1].n3()))
        return entity

    def get_disease_of_symptom(self, symptom_label:str):
        entity = []
        for rela in ["has_symptom", "has_main_symptom"]:
            property_rela = self.owl_prefix + rela
            query = """SELECT ?label ?d WHERE {?d rdfs:label ?label . 
                                            ?d rdfs:subClassOf ?restriction . 
                                            ?restriction <%s> <%s> .
                                            ?restriction <%s> ?s .
                                            ?s rdfs:label "%s" .}
                    """ % (self.owl_on_property, property_rela, self.owl_some_values, symptom_label)
            result = self.graph.query(query)
            for row in result:
                entity.append(BaseEntity(label=row[0].n3().split("\"")[1], iri=row[1].n3()))  
        if len(entity) < 3:
            for rela in ["probably_has_symptom", "serious_symptom"]:
                property_rela = self.owl_prefix + rela
                query = """SELECT ?label ?d WHERE {?d rdfs:label ?label . 
                                            ?d rdfs:subClassOf ?restriction . 
                                            ?restriction <%s> <%s> .
                                            ?restriction <%s> ?s .
                                            ?s rdfs:label "%s" .}
                        """ % (self.owl_on_property, property_rela, self.owl_some_values, symptom_label)
                result = self.graph.query(query)
                for row in result:
                    entity.append(BaseEntity(label=row[0].n3().split("\"")[1], iri=row[1].n3()))
                if len(entity) >=5:
                    break
        return list(set(entity))    

    def get_related_symptoms(self, symptom_label:str):
        property_rela = self.owl_prefix + "can_happen_with"
        query = """SELECT ?label ?sr WHERE {?s rdfs:label "%s" . 
                                        ?s rdfs:subClassOf ?restriction . 
                                        ?restriction <%s> <%s> . 
                                        ?restriction <%s> ?sr . 
                                        ?sr rdfs:label ?label .}
        """ % (symptom_label, self.owl_on_property, property_rela, self.owl_some_values)
        result = self.graph.query(query)
        entity = []
        for row in result:
            entity.append(BaseEntity(label=row[0].n3().split("\"")[1], iri=row[1].n3()))        
        return entity

    def get_all_diseases(self):
        disease_iri = self.get_iri_by_label("Bệnh_và_các_Chuyên_khoa")
        query = """SELECT ?label ?d WHERE {
                        ?d rdfs:subClassOf+ %s .
                        ?d rdfs:label ?label .
                }
                """ % (disease_iri)
        result = self.graph.query(query)
        diseases = {}
        for row in result:
            diseases[row[1].n3()] = Disease(label=row[0].n3().split("\"")[1], iri=row[1].n3())
        return diseases
    
    def get_all_symptoms(self):
        sign_iri = self.get_iri_by_label("Triệu_chứng")
        position_iri = self.get_iri_by_label("Vị_trí")
        position_rela = self.owl_prefix + "at_position"

        # query = """SELECT ?label ?s WHERE {
        #                 ?s rdfs:subClassOf+ %s .
        #                 ?s rdfs:label ?label .
        #                 ?s rdfs:subClassOf ?restriction .
        #                 ?restriction <%s> <%s> . 
        #         }
        #         """ % (sign_iri, self.owl_on_property, position_rela)
        query = """SELECT ?label ?s WHERE {
                        ?s rdfs:subClassOf+ %s .
                        ?s rdfs:label ?label .
                }
                """ % (sign_iri)
        result = self.graph.query(query)
        symptoms = {}
        for row in result:
            symptoms[row[1].n3()] = Symptom(label=row[0].n3().split("\"")[1], iri=row[1])
        return symptoms

    def get_all_position(self):
        position_iri = self.get_iri_by_label("Vị_trí")
        query = """SELECT ?label WHERE {
                        ?p rdfs:subClassOf %s .
                        ?p rdfs:label ?label .
                }
                """ % (position_iri)
        result = self.graph.query(query)
        return [row[0].n3().split("\"")[1] for row in result]
    
    def get_instance_subclass_by_iri(self, iri:str):
        query = """SELECT ?s WHERE {
                        ?s rdfs:subClassOf %s .
                }
                """ % (iri)
        result = self.graph.query(query)
        return [row[0].n3() for row in result]    

    def get_disease_group_by_iri(self, iri:str):
        disease_iri = self.get_iri_by_label("Bệnh_và_các_Chuyên_khoa")
        query = """SELECT ?label WHERE {?d_g rdfs:label ?label .
                    ?d_g rdfs:subClassOf %s . 
                    %s rdfs:subClassOf+ ?d_g . }      
                """ % (disease_iri, iri)
        result = list(self.graph.query(query))
        if len(result) > 0:
            try:
                return result[0][0].n3().split("\"")[1]
            except:
                return result[0][0].n3()
        return ""

    def get_disease_group_iri_by_iri(self, iri:str):
        disease_iri = self.get_iri_by_label("Bệnh_và_các_Chuyên_khoa")
        query = """SELECT ?d_g WHERE {
                    ?d_g rdfs:subClassOf %s . 
                    %s rdfs:subClassOf+ ?d_g . }      
                """ % (disease_iri, iri)
        result = list(self.graph.query(query))
        if len(result) > 0:
            return result[0][0].n3()
        return ""

    def get_diseases_by_group(self, group_label:str):
        group_iri = self.get_iri_by_label(group_label)
        query = """SELECT ?label ?d WHERE {
                        ?d rdfs:subClassOf+ %s .
                        ?d rdfs:label ?label .
                }
                """ % (group_iri)
        result = list(self.graph.query(query))
        diseases = []
        for row in result:
            diseases.append(row[1].n3())
        return diseases

    def get_diseases_by_group_iri(self, group_iri:str):
        query = """SELECT ?label ?d WHERE {
                        ?d rdfs:subClassOf+ %s .
                        ?d rdfs:label ?label .
                }
                """ % (group_iri)
        result = list(self.graph.query(query))
        diseases = []
        for row in result:
            diseases.append(row[1].n3())
        return diseases
    
    def get_all_disease_groups(self):
        disease_iri = self.get_iri_by_label("Bệnh_và_các_Chuyên_khoa")
        query = """SELECT ?label WHERE {
            ?d_g rdfs:subClassOf %s .
            ?d_g rdfs:label ?label
        }
        """ %(disease_iri)
        result = list(self.graph.query(query))
        return [r[0].n3().split('"')[1] for r in result]
    
    def get_all_disease_groups_iri(self):
        disease_iri = self.get_iri_by_label("Bệnh_và_các_Chuyên_khoa")
        query = """SELECT ?d_g WHERE {
            ?d_g rdfs:subClassOf %s .
        }
        """ %(disease_iri)
        result = list(self.graph.query(query))
        return [r[0].n3() for r in result]
    
    def get_all_symptom_groups_iri(self):
        symptom_iri = self.get_iri_by_label("Triệu_chứng")
        query = """SELECT ?d_g WHERE {
            ?d_g rdfs:subClassOf %s .
        }
        """ %(symptom_iri)
        result = list(self.graph.query(query))
        return [r[0].n3() for r in result]

    def __del__(self):
        self.graph.close()
        self.world.close()
