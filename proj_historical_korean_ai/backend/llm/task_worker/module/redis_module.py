
from task_worker.tool.log_tool import LogTool
from task_worker.config.redis_config.redis_config_runner import RedisConfigRunner

import inspect
import json
import redis

class RedisModule():
    
    def __init__(self):
        self.__logger = LogTool.get_logger(self.__class__.__name__) 
        self.redis= None
        self.connect_redis()
           
    def connect_redis(self):
        
        properties_dict: dict = RedisConfigRunner().get_properties()

        redis_host: str = properties_dict.get("redis_host")
        redis_port: str = properties_dict.get("redis_port")
        redis_db: int = properties_dict.get("redis_db")
        
        with redis.StrictRedis(host=redis_host, 
                               port=redis_port,
                               db=redis_db) as conn:
            
            self.redis = conn
            
        return self.redis

    def get_keys(self, match, count):

        try : 
            match = f"*{match}*"

            key_list = []
            for key in self.redis.scan_iter(match, count):
                key_list.append(str(key.decode('utf-8')))

            return key_list

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, match : {match}, count : {count}, error : {str(ex)}")

    def set_data(self, key, val, expire):

        try : 
            self.redis.set(key, val, expire)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, val : {val}, expire : {expire}, error : {str(ex)}")

    def get_data(self, key):

        try : 
            data = self.redis.get(key)
            if data is None:
                return {}

            ttl = self.redis.ttl(key)
            data_dict = {
                "val" : str(data.decode('utf-8')),
                "expire" : str(ttl)
            }
            return data_dict
    
        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, error : {str(ex)}")

    def get_json_data(self, key):

        try : 
            data = self.redis.get(key)
            if data is None:
                return {}
            
            val = json.loads(data.decode('utf-8'))
            return val
    
        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, error : {str(ex)}")

    def update_data(self, key, val, expire):

        try : 
            if self.redis.get(key):
                self.redis.delete(key)

            self.redis.set(key, val, expire)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, val : {val}, expire : {expire}, error : {str(ex)}")

    def delete_data(self, key):

        try : 
            if self.get_data(key):
                self.redis.delete(key)
        
        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, error : {str(ex)}")
    
    def hset_data(self, key, field, val):

        try : 
            if key and field and val:
                self.redis.hset(key, field, val)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, field : {field}, val : {val}, error : {str(ex)}")

    def hget_data(self, key, field):

        try : 

            data = self.redis.hget(key, field)
            if data is None:
                return None
            
            return bytes.decode(data)
    
        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, field : {field}, error : {str(ex)}")

    def hgetall_data(self, key):

        try : 

            data = self.redis.hgetall(key)
            if data is None:
                return None

            # 이진 데이터를 문자열로 변환하고 딕셔너리를 생성
            result = {field.decode('utf-8'): value.decode('utf-8') for field, value in data.items()}
            return result
    
        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, error : {str(ex)}")

    def hget_json_data(self, key, field):

        try : 
            data = self.redis.hget(key, field)
            if data is None:
                return {}
            
            val = json.loads(data.decode('utf-8'))
            return val
    
        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, field : {field}, error : {str(ex)}")

    def hdel_data(self, key, field):
        
        try : 
            if self.redis.hget(key, field):
                self.redis.hdel(key, field)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, field : {field}, error : {str(ex)}")
    
    def hupd_date(self, key, field, val):   

        try : 
            if key and field and val:
                self.hset_data(key, field, val)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, field : {field}, val : {val}, error : {str(ex)}")
        
    def lpush(self, key, val):

        try : 
            if key and val:
                self.redis.lpush(key, val)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, val : {val}, error : {str(ex)}")

        return 
    
    def lrange_all(self, key):

        try : 
            if key:
                return self.redis.lrange(key, 0, -1)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key}, error : {str(ex)}")

        return 
    
    def lpop(self, key):

        try : 
            if key:
                return self.redis.lpop(key)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key},  error : {str(ex)}")
    
    def blpop(self, key, timeout):

        try : 
            if key:
                return self.redis.blpop(key, timeout=timeout)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key},  error : {str(ex)}")
    
    def rpop(self, key):

        try : 
            if key:
                return self.redis.rpop(key)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key},  error : {str(ex)}")
    
    def brpop(self, key, timeout):

        try : 
            if key:
                return self.redis.brpop(key, timeout=timeout)

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, key : {key},  error : {str(ex)}")

    def flushall(self):

        try : 
            self.redis.flushdb()

        except Exception as ex :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, error : {str(ex)}")
    
    def replace_hyphen(self, target):

        if "-" in target:
            return target.replace("-", "_")

        return target
    
    def convert_bytes_to_dict(self, data):
        """
        바이트 스트링 데이터를 디코딩하여 dict형태로 변환

        Parameters
        ----------
        data : 원본 데이터 (byte str)

        Returns
        -------
        data : 컨버팅 된 데이터 (dict)
        """
        try:
            # 데이터 역직렬화
            deserialized_data = json.loads(data)
            return deserialized_data
        
        except Exception as e:
            self.__logger.info(f"def : {inspect.currentframe().f_code.co_name}, convert fail, error : {str(e)}")
