-- 기존 테이블 삭제 (CASCADE 없이 pure DROP)
DROP TABLE IF EXISTS public.chat_message;
DROP TABLE IF EXISTS public.chat_session;
DROP TABLE IF EXISTS public.hk_dictionary;
DROP TABLE IF EXISTS public.prompt_history;
DROP TABLE IF EXISTS public.member_role;
DROP TABLE IF EXISTS public.member;
DROP TABLE IF EXISTS public.member_auth_jwt;

-- 기존 시퀀스 삭제
DROP SEQUENCE IF EXISTS public.hk_dictionary_seq_seq;
DROP SEQUENCE IF EXISTS public.chat_session_seq_seq;
DROP SEQUENCE IF EXISTS public.chat_message_seq_seq;
DROP SEQUENCE IF EXISTS public.prompt_history_seq_seq;
DROP SEQUENCE IF EXISTS public.member_role_seq_seq;
DROP SEQUENCE IF EXISTS public.member_seq_seq;
DROP SEQUENCE IF EXISTS public.member_auth_jwt_seq_seq;

--------------------------------------------------
-- 1. member_role (회원 역할)
--------------------------------------------------
CREATE SEQUENCE public.member_role_seq_seq
    START WITH 1
    INCREMENT BY 1;

CREATE TABLE public.member_role (
    member_role_seq BIGINT NOT NULL DEFAULT nextval('public.member_role_seq_seq'::regclass),
    member_role VARCHAR(20) NOT NULL,
    role_desc VARCHAR(500),
    reg_dt TIMESTAMPTZ,
    reg_member_seq INTEGER NOT NULL,
    mod_dt TIMESTAMPTZ,
    mod_member_seq INTEGER NOT NULL,
    CONSTRAINT pk_member_role PRIMARY KEY (member_role_seq),
    CONSTRAINT ux_member_role_member_role UNIQUE (member_role)
);

CREATE INDEX idx_member_role_member_role ON public.member_role (member_role);


--------------------------------------------------
-- 2. member (회원 정보)
--------------------------------------------------
CREATE SEQUENCE public.member_seq_seq
    START WITH 1
    INCREMENT BY 1;

CREATE TABLE public.member (
    seq BIGINT NOT NULL DEFAULT nextval('public.member_seq_seq'::regclass),
    member_id VARCHAR(100) NOT NULL,
    member_password VARCHAR(100) NOT NULL,
    member_first_name VARCHAR(100) NOT NULL,
    member_last_name VARCHAR(100) NOT NULL,
    member_email VARCHAR(100) NOT NULL,
    member_phone VARCHAR(100) NOT NULL,
    member_type_cd VARCHAR(10) NOT NULL,
    member_status_cd VARCHAR(10) NOT NULL,
    reg_dt TIMESTAMPTZ,
    reg_member_seq INTEGER NOT NULL,
    mod_dt TIMESTAMPTZ,
    mod_member_seq INTEGER NOT NULL,
    last_login_dt TIMESTAMPTZ,
    CONSTRAINT pk_member PRIMARY KEY (seq),
    CONSTRAINT ux_member_member_id_member_type_cd UNIQUE (member_id, member_type_cd)
);

CREATE INDEX idx_member_member_id ON public.member (member_id);
CREATE INDEX idx_member_member_first_name ON public.member (member_first_name);
CREATE INDEX idx_member_member_last_name ON public.member (member_last_name);
CREATE INDEX idx_member_member_email ON public.member (member_email);
CREATE INDEX idx_member_member_phone ON public.member (member_phone);
CREATE INDEX idx_member_member_type_cd ON public.member (member_type_cd);
CREATE INDEX idx_member_member_status_cd ON public.member (member_status_cd);


--------------------------------------------------
-- 3. member_auth_jwt (회원 인증 토큰)
--------------------------------------------------
CREATE SEQUENCE public.member_auth_jwt_seq_seq
    START WITH 1
    INCREMENT BY 1;

CREATE TABLE public.member_auth_jwt (
    seq BIGINT NOT NULL DEFAULT nextval('public.member_auth_jwt_seq_seq'::regclass),
    member_seq INTEGER NOT NULL,
    member_id VARCHAR(100) NOT NULL,
    access_token VARCHAR(1000) NOT NULL,
    refresh_token VARCHAR(1000) NOT NULL,
    expiration_dt TIMESTAMPTZ,
    reg_dt TIMESTAMPTZ,
    reg_member_seq INTEGER NOT NULL,
    mod_dt TIMESTAMPTZ,
    mod_member_seq INTEGER NOT NULL,
    CONSTRAINT pk_member_auth_jwt PRIMARY KEY (seq),
    CONSTRAINT ux_member_auth_jwt_member_seq UNIQUE (seq),
    CONSTRAINT ux_member_auth_jwt_member_id UNIQUE (member_id)
);

CREATE INDEX idx_member_auth_jwt_member_seq ON public.member_auth_jwt (member_seq);
CREATE INDEX idx_member_auth_jwt_member_id ON public.member_auth_jwt (member_id);


--------------------------------------------------
-- 4. hk_dictionary (한글 고어 사전)
--------------------------------------------------
CREATE SEQUENCE public.hk_dictionary_seq_seq
    START WITH 1
    INCREMENT BY 1;

CREATE TABLE public.hk_dictionary (
    seq BIGINT NOT NULL DEFAULT nextval('public.hk_dictionary_seq_seq'::regclass),
    modern_korean VARCHAR(255) NOT NULL,
    historical_korean VARCHAR(255) NOT NULL,
    historical_period_start_dt TIMESTAMPTZ,
    historical_period_end_dt TIMESTAMPTZ,
    reg_dt TIMESTAMPTZ,
    reg_member_seq INTEGER NOT NULL,
    mod_dt TIMESTAMPTZ,
    mod_member_seq INTEGER NOT NULL,
    delete_yn VARCHAR(1) NOT NULL DEFAULT 'N',
    confirmed_yn VARCHAR(1) DEFAULT 'N',
    CONSTRAINT pk_hk_dictionary PRIMARY KEY (seq)
);

CREATE INDEX idx_hk_dictionary_modern_korean ON public.hk_dictionary (modern_korean);
CREATE INDEX idx_hk_dictionary_period_start ON public.hk_dictionary (historical_period_start_dt);
CREATE INDEX idx_hk_dictionary_period_end ON public.hk_dictionary (historical_period_end_dt);


--------------------------------------------------
-- 5. chat_session (채팅 세션)
--------------------------------------------------
CREATE SEQUENCE public.chat_session_seq_seq
    START WITH 1
    INCREMENT BY 1;

CREATE TABLE public.chat_session (
    seq BIGINT NOT NULL DEFAULT nextval('public.chat_session_seq_seq'::regclass),
    member_seq INTEGER NOT NULL,
    title VARCHAR(300),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    reg_dt TIMESTAMPTZ,
    mod_dt TIMESTAMPTZ,
    activate_dt TIMESTAMPTZ,
    use_yn VARCHAR(1) NOT NULL DEFAULT 'Y',
    CONSTRAINT pk_chat_session PRIMARY KEY (seq)
);

CREATE INDEX idx_chat_session_member_seq ON public.chat_session (member_seq);


--------------------------------------------------
-- 6. chat_message (채팅 메시지)
--------------------------------------------------
CREATE SEQUENCE public.chat_message_seq_seq
    START WITH 1
    INCREMENT BY 1;

CREATE TABLE public.chat_message (
    seq BIGINT NOT NULL DEFAULT nextval('public.chat_message_seq_seq'::regclass),
    chat_session_seq INTEGER NOT NULL,
    model_name VARCHAR(100),
    role VARCHAR(20) NOT NULL,
    content TEXT[],
    ipa TEXT[],
    audio_path TEXT[],
    audio_expire_yn VARCHAR(1) DEFAULT 'N',
    response_time_ms INTEGER,
    feedback_type VARCHAR(20),
    feedback_comment TEXT,
    feedback_dt TIMESTAMPTZ,
    reg_dt TIMESTAMPTZ,
    mod_dt TIMESTAMPTZ,
    CONSTRAINT pk_chat_message PRIMARY KEY (seq)
);

CREATE INDEX idx_chat_message_chat_session_seq ON public.chat_message (chat_session_seq);
CREATE INDEX idx_chat_message_role ON public.chat_message (role);


--------------------------------------------------
-- 7. prompt_history (프롬프트 이력)
--------------------------------------------------
CREATE SEQUENCE public.prompt_history_seq_seq
    START WITH 1
    INCREMENT BY 1;

CREATE TABLE public.prompt_history (
    seq BIGINT NOT NULL DEFAULT nextval('public.prompt_history_seq_seq'::regclass),
    llm_model_name VARCHAR(100),
    prompt_template_name VARCHAR(255),
    prompt_core TEXT,
    response TEXT,
    member_seq INTEGER,
    reg_dt TIMESTAMPTZ,
    CONSTRAINT pk_prompt_history PRIMARY KEY (seq)
);

CREATE INDEX idx_prompt_history_member_seq ON public.prompt_history (member_seq);

INSERT INTO member (member_id,member_password,member_first_name,member_last_name,member_email,member_phone,member_type_cd,member_status_cd,reg_dt,reg_member_seq,mod_dt,mod_member_seq,last_login_dt) VALUES
	 ('admin0','$2b$12$lgC1XPpUsjm6vW/529XGi.xPh1hBc1AJbY5Hm/p1FhCrUC4rc16Y6','admin','admin','admin@google.com','010-0000-0000','MBT111','MBS111','2026-06-22 22:38:18.989883+09',0,'2026-06-22 22:38:18.989883+09',0,'2026-06-22 22:38:18.989883+09');

