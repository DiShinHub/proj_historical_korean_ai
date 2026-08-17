from task_worker.module.postgres_module import PostgresModule


class ChatDao():
    
    def __init__(self):
        self.postgres = PostgresModule()

    def add_chat_message(
            self,
            chat_session_seq,
            model_name,
            role,
            content,
            ipa,
            audio_path,
            audio_expire_yn,
            response_time_ms
        ):
        query = """
        INSERT INTO public.chat_message
        (
            seq,
            chat_session_seq,
            model_name,
            role,
            content,
            ipa,
            audio_path,
            audio_expire_yn,
            response_time_ms,
            feedback_type,
            feedback_comment,
            feedback_dt,
            reg_dt,
            mod_dt
        )
        VALUES
        (
            nextval('chat_message_seq_seq'::regclass),
            %s, -- chat_session_seq
            %s, -- model_name
            %s, -- role
            %s, -- content
            %s, -- ipa
            %s, -- audio_path
            %s, -- audio_expire_yn
            %s, -- response_time_ms
            '', -- feedback_type
            '', -- feedback_comment
            NULL, -- feedback_dt
            now(),
            now()
        );
        """

        binds = [
            chat_session_seq,
            model_name,
            role,
            content,
            ipa,
            audio_path,
            audio_expire_yn,
            response_time_ms,
        ]
        return self.postgres.execute_query_with_commit(query=query, binds=binds)
    
    def count_chat_messages_by_session(self, chat_session_seq: int) -> int:
        """
        해당 세션에 존재하는 메시지 개수를 반환합니다.
        """
        query = """
        SELECT COUNT(seq)
        FROM public.chat_message
        WHERE chat_session_seq = %s;
        """
        binds = [chat_session_seq]
        
        # execute_query는 보통 tuple 목록이나 딕셔너리 형태의 결과를 반환합니다.
        result = self.postgres.read_one(query=query, binds=binds)
        
        if result and len(result) > 0:
            # 반환 타입(tuple/dict)에 맞게 첫 번째 칼럼 값 추출
            return result[0][0] if isinstance(result[0], (tuple, list)) else list(result[0].values())[0]
        
        return 0

    def update_chat_session_title(self, chat_session_seq: int, title: str) -> None:
        """
        세션의 타이틀 및 수정일시(mod_dt)를 업데이트합니다.
        """
        query = """
        UPDATE public.chat_session
        SET title = %s,
            mod_dt = now()
        WHERE seq = %s;
        """
        binds = [title, chat_session_seq]
        
        return self.postgres.execute_query_with_commit(query=query, binds=binds)
    
chat_dao = ChatDao()


