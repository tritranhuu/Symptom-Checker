from deepcare.bayesian_network.model import DC_Bayesian_Network, DC_Bayesian_General_Network
from deepcare.database.query import DC_Query

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD, State
from pgmpy.inference import VariableElimination
from pgmpy.readwrite import BIFWriter, BIFReader
from pgmpy.sampling import GibbsSampling, BayesianModelSampling

from configs import data_file
import pickle as pkl 
import time

def query_time(start_time, end_time):
    elapsed_time = end_time - start_time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
    return elapsed_mins, elapsed_secs

if __name__ == "__main__":

    query = DC_Query(data_file.APP_ONTOLOGY)
    disease_groups = query.get_all_disease_groups()
    # print(disease_groups)
    # for d in disease_groups:
    #     print(d)
    # bayesian = DC_Bayesian_Network(query, disease_group='Bệnh hệ hô hấp', proportion_dir=data_file.APP_PROPORTION_DIR)
    # model = bayesian.build()

    ba = DC_Bayesian_General_Network(query)
    model = ba.build()
        # gibbs_chain = BayesianModelSampling(model)
        # gen = gibbs_chain.rejection_sample(size=500)
    
    # reader = BIFReader('bayes.bif')
    # model = reader.get_model()
    # print(model.check_model())
    # with open("bayes.pkl", 'wb') as f:
    #     pkl.dump(model, f, protocol=pkl.HIGHEST_PROTOCOL)
    
    # print(bayesian.symptom_disease_dict.keys())
    # solver = VariableElimination(model)
    # print("querying")
    # result = solver.map_query(variables=["<http://deepcare.io/2213353c_05c7_4071_a75d_6771b874e060>"], evidence={"Age":0, "Gender":0, "<http://deepcare.io/0d48b52f_99af_42cd_8c14_167c9913e8b7>":1})
    # print(result.values())
    # print("querying 2")
    # result = solver.query(variables=["<http://deepcare.io/2213353c_05c7_4071_a75d_6771b874e060>"], evidence={"Age":0, "Gender":0, "<http://deepcare.io/0d48b52f_99af_42cd_8c14_167c9913e8b7>":0})
    # print(result)
    
    gibbs_chain = BayesianModelSampling(model)
    start_time = time.time()
    gen = gibbs_chain.rejection_sample(size=500)
    end_time = time.time()
    # print(gen)
    epoch_mins, epoch_secs = query_time(start_time, end_time)
    print(gen.sum().nlargest(n=5))
    print(f'Time: {epoch_mins}m {epoch_secs}s')
    # writer = BIFWriter(model)
    # writer.write_bif("bayes_general.bif")