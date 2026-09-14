from task_worker.tool.log_tool import LogTool
from task_worker.config.minio_config.minio_config_runner import MinioConfigRunner

from minio import Minio
from minio.error import S3Error

import datetime
import os, sys
import inspect

class MinioModule():

    def __init__(self):
        self.__logger = LogTool.get_logger(self.__class__.__name__) 

        properties_dict: dict = MinioConfigRunner().get_properties()

        self.minio_external_url: str = properties_dict.get("minio_external_url")
        self.minio_service_port: str = properties_dict.get("minio_service_port")
        self.minio_access_key: str = properties_dict.get("minio_access_key")
        self.minio_secret_key: str = properties_dict.get("minio_secret_key")
        self.minio_bucket: str = properties_dict.get("minio_bucket")
        self.minio_local: str = properties_dict.get("minio_local")

        self.external_client = None
        
        self.set_minio_client()
        self.init_workspace()
        
    def set_minio_client(self):

        self.external_client = Minio(
            f"{self.minio_external_url}:{self.minio_service_port}",
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False,
        )
    
    def init_workspace(self):
        """
        def description : 로컬폴더와 버켓 생성
        
        """
        
        # 로컬 폴더 여부 확인 후 없으면 생성
        if not os.path.exists(f"{self.minio_local}"):
            os.makedirs(self.minio_local)
        
        # 버킷 존재 여부 확인 후 없으면 생성
        if not self.external_client.bucket_exists(self.minio_bucket):
            self.external_client.make_bucket(self.minio_bucket)
    
    """
    basic
    """
    def read_file(self, minio_file_path):
        """
        def description : 파일 리드

        Parameters
        ----------
        minio_file_path : 오브젝트 스토리지 경로 (str)

        Returns
        -------
        file : 파일 (obj)
        
        """
        
        try:
            file = self.external_client.get_object(self.minio_bucket, minio_file_path)
            return file
            
        except Exception as e:
            self.__logger.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            
    def upload_file(self, minio_file_path, local_file_path, content_type=None, metadata=None):
        """
        def description : 파일 업로드

        Parameters
        ----------
        minio_file_path : 파일을 저장 할 오브젝트 스토리지 경로 (str)
        local_file_path : 파일이 저장 된 로컬 경로 (str)
        """
        
        try:
            self.external_client.fput_object(
                self.minio_bucket, 
                minio_file_path, 
                local_file_path,
                content_type=content_type,
                metadata=metadata
            )
            
        except Exception as e:
            self.__logger.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    def download_file(self, minio_file_path, local_file_path):
        """
        def description : 파일 다운로드

        Parameters
        ----------
        minio_file_path : 파일이 저장 된 오브젝트 스토리지 경로 (str)
        local_file_path : 파일을 저장 할 로컬 경로 (str)
        """
        
        try:
            self.external_client.fget_object(self.minio_bucket, minio_file_path, local_file_path) 
            
        except Exception as e:
            self.__logger.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            
    def is_file_exist(self, file_path):
        """
        def description : 파일조회
        
        Parameters
        ----------
        file_path : 파일 경로 (str)
        
        Returns
        -------
        bool
        """
        try:
            # 폴더 정보조회
            response = self.external_client.stat_object(self.minio_bucket, file_path)
            return True
            
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            
            else:
                self.__logger.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
                raise

        except Exception as e:
            self.__logger.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
            raise
    
    """
    folder recursive
    """
    def read_files_in_folder(self, minio_folder_path, name_search=None):
        """
        def description : 파일 리드

        Parameters
        ----------
        minio_folder_path : 오브젝트 스토리지 폴더 경로 (str)
        name_search : 파일이름 검색 (str)

        Returns
        -------
        file_list : 파일 리스트 (list)
        """
        
        try:
            file_list = []

            # 폴더상에 있는 데이터 리스트를 조회
            minio_file_path_list = self.external_client.list_objects(self.minio_bucket, prefix=minio_folder_path, recursive=True)
            for minio_file_path in minio_file_path_list:
                if minio_file_path.is_dir:  # 폴더 자체는 무시
                    continue

                # 파일 가져오기
                if name_search == None:
                    file = self.read_file(minio_file_path.object_name)
                    file_list.append(file)

                else:
                    if name_search in minio_file_path.object_name:
                        file = self.read_file(minio_file_path.object_name)
                        file_list.append(file)

            return file_list
            
        except Exception as e:
            self.__logger.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")
    
    def download_files_in_folder(self, minio_folder_path, name_search=None):
        """
        def description : 파일 다운로드

        Parameters
        ----------
        minio_folder_path : 오브젝트 스토리지 폴더 경로 (str)
        name_search : 파일이름 검색 (str)

        Returns
        -------
        file_list : 파일 리스트 (list)
        """
        
        try:
            file_list = []

            # 폴더상에 있는 데이터 리스트를 조회
            minio_file_path_list = self.external_client.list_objects(self.minio_bucket, prefix=minio_folder_path, recursive=True)
            for minio_file_path in minio_file_path_list:
                if minio_file_path.is_dir:  # 폴더 자체는 무시
                    continue

                # 파일 가져오기
                if name_search == None:
                    file = self.download_file(minio_file_path.object_name, f"{minio_file_path.object_name}")
                    file_list.append(file)

                else:
                    if name_search in minio_file_path.object_name:
                        file = self.download_file(minio_file_path.object_name, f"{minio_file_path.object_name}")
                        file_list.append(file)

            return file_list
            
        except Exception as e:
            self.__logger.info(f"class : {self.__class__.__name__}, method : {inspect.currentframe().f_code.co_name}, error : {str(e)}")

    """
    helper
    """
    def generate_local_path(self, file_exe):
        """
        def description : 로컬 임시 저장 경로 셋팅

        Parameters
        ----------
        file_exe : 파일 확장자 (str)

        Returns
        -------
        local_download_path : 로컬의 임시 저장 경로 (str)
        
        """
        
        now = datetime.datetime.now()
        local_download_path = f"{self.minio_local}/{now.strftime('%Y%m%d%H%M%S%f')}{now.microsecond}.{file_exe}" 
        
        return local_download_path

minio_module = MinioModule()