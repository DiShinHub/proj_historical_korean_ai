from task_worker.module.postgres_module import PostgresModule
from typing import List, Dict, Any

class HkDictionaryDao:
    def __init__(self):
        self.postgres = PostgresModule()

    def add_hk_dictionary(
        self,
        modern_korean: str,
        historical_korean: str,
        reg_member_seq: int,
        historical_period_start_dt: str = None,
        historical_period_end_dt: str = None,
    ):
        """
        한글 고어 사전(hk_dictionary) 신규 데이터 등록
        """
        query = """
        INSERT INTO public.hk_dictionary
        (
            seq,
            modern_korean,
            historical_korean,
            historical_period_start_dt,
            historical_period_end_dt,
            reg_dt,
            reg_member_seq,
            mod_dt,
            mod_member_seq,
            delete_yn
        )
        VALUES
        (
            nextval('hk_dictionary_seq_seq'::regclass),
            %s,
            %s,
            %s,
            %s,
            now(),
            %s,
            now(),
            %s,
            'N'
        );
        """

        binds = [
            modern_korean,
            historical_korean,
            historical_period_start_dt,
            historical_period_end_dt,
            reg_member_seq,
            reg_member_seq,  # 최초 등록 시 수정자(mod_member_seq)도 등록자로 동일 설정
        ]
        return self.postgres.execute_query_with_commit(query=query, binds=binds)
    
    def bulk_add_hk_dictionary(
        self,
        items: List[Dict[str, Any]],
        reg_member_seq: int
    ):
        """
        한글 고어 사전 다건(Bulk) 등록
        
        :param items: [{'modern_korean': '...', 'historical_korean': '...', 'historical_period_start_dt': None, 'historical_period_end_dt': None}, ...]
        :param reg_member_seq: 등록자 회원 번호
        """
        if not items:
            return None

        values_template = "(nextval('hk_dictionary_seq_seq'::regclass), %s, %s, %s, %s, now(), %s, now(), %s, 'N', 'N')"
        values_clauses = [values_template] * len(items)
        
        query = f"""
        INSERT INTO public.hk_dictionary
        (
            seq,
            modern_korean,
            historical_korean,
            historical_period_start_dt,
            historical_period_end_dt,
            reg_dt,
            reg_member_seq,
            mod_dt,
            mod_member_seq,
            delete_yn,
            confirmed_yn
        )
        VALUES
        {', '.join(values_clauses)};
        """

        # 1차원 바인딩 리스트 바인딩 값 매핑
        binds = []
        for item in items:
            binds.extend([
                item.get('modern_korean'),
                item.get('historical_korean'),
                item.get('historical_period_start_dt'),
                item.get('historical_period_end_dt'),
                reg_member_seq,
                reg_member_seq
            ])

        return self.postgres.execute_query_with_commit(query=query, binds=binds)

hk_dictionary_dao = HkDictionaryDao()