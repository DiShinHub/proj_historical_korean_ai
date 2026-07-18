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
            %s,
            %s,
            %s,
            %s,
            %s,
            '',
            '',
            NULL,
            now(),
            now()
        );
        """

        binds = [
            chat_session_seq,
            model_name,
            role,
            content,
            response_time_ms,
        ]
        return self.postgres.execute_query_with_commit(query=query, binds=binds)
                
chat_dao = ChatDao()


