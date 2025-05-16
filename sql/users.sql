-- User.objects.all()
select "users_user"."id", "users_user"."password", "users_user"."username", "users_user"."email", "users_user"."phone" from "users_user" 

-- Freelancer.objects.all()
 select "users_freelancer"."user_id", "users_freelancer"."profile", "users_freelancer"."rating"
 from "users_freelancer"

 -- Client.objects.all()
 select "users_client"."user_id" from "users_client"

 --Skill.objects.filter(name__in = skill_list)
 select "services_skill"."id", "services_skill"."category_id", "services_skill"."name" 
 from "services_skill"
 where "service_skill"."name" IN ('HTML', 'CSS')

 --Freelancer.objects.create(user = user, profile = profile)
 insert into "users_freelancer" 
 ("freelancer_user", "freelancer_profile")
 values 
 (user_id,'profile_string')

 --freelancer_skills.set(skills)
 insert into "users_freelancer_skills"
 ("freelancer_id", "freelancer_skills")
 values
 ('listofskills')



