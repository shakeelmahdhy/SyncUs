


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE OR REPLACE FUNCTION "public"."rls_auto_enable"() RETURNS "event_trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    SET "search_path" TO 'pg_catalog'
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$$;


ALTER FUNCTION "public"."rls_auto_enable"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."applications" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "job_id" "uuid",
    "job_seeker_id" "uuid",
    "resume_id" "uuid",
    "status" "text" DEFAULT 'applied'::"text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."applications" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."employers" (
    "id" "uuid" NOT NULL,
    "company_name" "text",
    "company_description" "text",
    "industry" "text",
    "is_verified" boolean DEFAULT false,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."employers" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."job_seeker_skills" (
    "job_seeker_id" "uuid" NOT NULL,
    "skill_id" "uuid" NOT NULL
);


ALTER TABLE "public"."job_seeker_skills" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."job_seekers" (
    "id" "uuid" NOT NULL,
    "first_name" "text",
    "last_name" "text",
    "education" "text",
    "major" "text",
    "years_of_experience" integer DEFAULT 0,
    "is_active" boolean DEFAULT false,
    "academic_units" "text"[] DEFAULT '{}'::"text"[],
    "created_at" timestamp with time zone DEFAULT "now"(),
    "phone" "text"
);


ALTER TABLE "public"."job_seekers" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."jobs" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "employer_id" "uuid",
    "title" "text" NOT NULL,
    "description" "text" NOT NULL,
    "required_skills" "text"[],
    "location" "text",
    "work_mode" "text",
    "experience_required" integer DEFAULT 0,
    "status" "text" DEFAULT 'draft'::"text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."jobs" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."matches" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "job_id" "uuid",
    "job_seeker_id" "uuid",
    "score" numeric,
    "breakdown_json" "jsonb",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."matches" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."resumes" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "job_seeker_id" "uuid" NOT NULL,
    "resume_name" "text" NOT NULL,
    "file_url" "text" NOT NULL,
    "is_primary" boolean DEFAULT false,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."resumes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."skills" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text"
);


ALTER TABLE "public"."skills" OWNER TO "postgres";


ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."employers"
    ADD CONSTRAINT "employers_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."job_seeker_skills"
    ADD CONSTRAINT "job_seeker_skills_pkey" PRIMARY KEY ("job_seeker_id", "skill_id");



ALTER TABLE ONLY "public"."job_seekers"
    ADD CONSTRAINT "job_seekers_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."matches"
    ADD CONSTRAINT "matches_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."resumes"
    ADD CONSTRAINT "resumes_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."skills"
    ADD CONSTRAINT "skills_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."skills"
    ADD CONSTRAINT "skills_pkey" PRIMARY KEY ("id");



CREATE UNIQUE INDEX "one_primary_resume_per_user" ON "public"."resumes" USING "btree" ("job_seeker_id") WHERE ("is_primary" = true);



ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("id");



ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_job_seeker_id_fkey" FOREIGN KEY ("job_seeker_id") REFERENCES "public"."job_seekers"("id");



ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_resume_id_fkey" FOREIGN KEY ("resume_id") REFERENCES "public"."resumes"("id");



ALTER TABLE ONLY "public"."employers"
    ADD CONSTRAINT "employers_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_seeker_skills"
    ADD CONSTRAINT "job_seeker_skills_job_seeker_id_fkey" FOREIGN KEY ("job_seeker_id") REFERENCES "public"."job_seekers"("id");



ALTER TABLE ONLY "public"."job_seeker_skills"
    ADD CONSTRAINT "job_seeker_skills_skill_id_fkey" FOREIGN KEY ("skill_id") REFERENCES "public"."skills"("id");



ALTER TABLE ONLY "public"."job_seekers"
    ADD CONSTRAINT "job_seekers_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_employer_id_fkey" FOREIGN KEY ("employer_id") REFERENCES "public"."employers"("id");



ALTER TABLE ONLY "public"."matches"
    ADD CONSTRAINT "matches_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("id");



ALTER TABLE ONLY "public"."matches"
    ADD CONSTRAINT "matches_job_seeker_id_fkey" FOREIGN KEY ("job_seeker_id") REFERENCES "public"."job_seekers"("id");



ALTER TABLE ONLY "public"."resumes"
    ADD CONSTRAINT "resumes_job_seeker_id_fkey" FOREIGN KEY ("job_seeker_id") REFERENCES "public"."job_seekers"("id") ON DELETE CASCADE;



CREATE POLICY "Users can view own resumes" ON "public"."resumes" FOR SELECT USING (("auth"."uid"() = "job_seeker_id"));



ALTER TABLE "public"."applications" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."employers" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."job_seeker_skills" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."job_seekers" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."jobs" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."matches" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."resumes" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."skills" ENABLE ROW LEVEL SECURITY;




ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";






















































































































































GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "anon";
GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "service_role";


















GRANT ALL ON TABLE "public"."applications" TO "anon";
GRANT ALL ON TABLE "public"."applications" TO "authenticated";
GRANT ALL ON TABLE "public"."applications" TO "service_role";



GRANT ALL ON TABLE "public"."employers" TO "anon";
GRANT ALL ON TABLE "public"."employers" TO "authenticated";
GRANT ALL ON TABLE "public"."employers" TO "service_role";



GRANT ALL ON TABLE "public"."job_seeker_skills" TO "anon";
GRANT ALL ON TABLE "public"."job_seeker_skills" TO "authenticated";
GRANT ALL ON TABLE "public"."job_seeker_skills" TO "service_role";



GRANT ALL ON TABLE "public"."job_seekers" TO "anon";
GRANT ALL ON TABLE "public"."job_seekers" TO "authenticated";
GRANT ALL ON TABLE "public"."job_seekers" TO "service_role";



GRANT ALL ON TABLE "public"."jobs" TO "anon";
GRANT ALL ON TABLE "public"."jobs" TO "authenticated";
GRANT ALL ON TABLE "public"."jobs" TO "service_role";



GRANT ALL ON TABLE "public"."matches" TO "anon";
GRANT ALL ON TABLE "public"."matches" TO "authenticated";
GRANT ALL ON TABLE "public"."matches" TO "service_role";



GRANT ALL ON TABLE "public"."resumes" TO "anon";
GRANT ALL ON TABLE "public"."resumes" TO "authenticated";
GRANT ALL ON TABLE "public"."resumes" TO "service_role";



GRANT ALL ON TABLE "public"."skills" TO "anon";
GRANT ALL ON TABLE "public"."skills" TO "authenticated";
GRANT ALL ON TABLE "public"."skills" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";



































drop extension if exists "pg_net";


