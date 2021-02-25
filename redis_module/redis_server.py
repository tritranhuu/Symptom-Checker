import redis
import dill
import time

from redis_module.redis_supporter import RedisSymptomChecker



class RedisServer:
    def __init__(self, host, port, db):
        pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.connection = redis.Redis(connection_pool=pool)

    # def set_inference(self, key, obj):
    #     R_symtomchecker = RedisSymptomChecker()
    #     R_symtomchecker = set_from_symptom_checker(R_symtomchecker, obj)
    #     start_time = time.time()
    #     byte_format = dill.dumps(obj=R_symtomchecker)
    #     end_time = time.time()
    #     print("dump inference time", end_time - start_time)
    #     self.connection.set(key, byte_format)

    def set_obj(self, key, obj):
        # dill.detect.trace(True)
        # print(vars(obj))
        R_symtomchecker = RedisSymptomChecker()
        R_symtomchecker.set_from_symptom_checker(obj)
        byte_format = dill.dumps(obj=R_symtomchecker)
        self.connection.set(key, byte_format)

    def get_obj(self, key):
        byte_format = self.connection.get(key)
        if byte_format:
            obj = dill.loads(byte_format)
            return obj

    def clear_all_keys(self):
        for key in self.connection.keys():
            self.connection.delete(key)

    def clear_key_list(self, key_list):
        for key in key_list:
            self.connection.delete(key)

    def clear_key(self, key_name):
        self.connection.delete(key_name)

    def set_list(self, list_name, list_val):
        self.clear_key(key_name=list_name)
        for obj in list_val:
            self.connection.lpush(list_name, obj)
