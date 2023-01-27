CREATE TABLE IF NOT EXISTS public.monsters
(
    id integer NOT NULL DEFAULT nextval('monsters_id_seq'::regclass),
    founder integer NOT NULL,
    data jsonb NOT NULL,
    geom geometry,
    create_at timestamp with time zone NOT NULL DEFAULT now(),
    hidden boolean NOT NULL DEFAULT false,
    CONSTRAINT monsters_pkey PRIMARY KEY (id)
)
	
CREATE TABLE IF NOT EXISTS public.token_table
(
    email character varying COLLATE pg_catalog."default" NOT NULL,
    token character varying COLLATE pg_catalog."default" NOT NULL,
    token_expire timestamp with time zone NOT NULL
)
	
CREATE TABLE IF NOT EXISTS public.users
(
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username character varying COLLATE pg_catalog."default" NOT NULL,
    email character varying COLLATE pg_catalog."default" NOT NULL,
    password character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.comments
(
    id integer NOT NULL DEFAULT nextval('comments_id_seq'::regclass),
    author integer NOT NULL,
    data jsonb NOT NULL,
    create_at timestamp with time zone NOT NULL DEFAULT now(),
    monster_id integer NOT NULL,
    CONSTRAINT comments_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.comments
    OWNER to postgres;

ALTER TABLE public.monsters
    OWNER to postgres;
	
ALTER TABLE public.token_table
    OWNER to postgres;
	
ALTER TABLE public.users
    OWNER to postgres;