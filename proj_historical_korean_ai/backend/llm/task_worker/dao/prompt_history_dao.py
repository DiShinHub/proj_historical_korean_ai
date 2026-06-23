from task_worker.module.postgres_module import PostgresModule

class PromptHistoryDao():
    
    def __init__(self):
        self.postgres = PostgresModule()
    
    def insert_prompt_history(
            self,
            llm_model_name,
            prompt_template_name,
            prompt_core,
            response
        ):
        
        query = """
            INSERT INTO public.prompt_history
            (prompt_history_seq, llm_model_name,  prompt_template_name, prompt_core, response, reg_dt)
            VALUES(nextval('prompt_history_prompt_history_seq_seq'::regclass), %s, %s, %s, %s, %s, now());

        """
        
        binds = [
            llm_model_name,
            prompt_template_name,
            prompt_core,
            response
        ]
        return self.postgres.execute_query_with_commit(query=query, binds=binds)
                
prompt_history_dao = PromptHistoryDao()


