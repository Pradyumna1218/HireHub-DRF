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
 ("freelancer_user", "freelancer_profile","rating")
 values 
 (user_id,'profile_string', 0.0)

 --freelancer_skills.set(skills)
 delete from "users_freelancer_skills"
 where freelancer_id = freelancer_id

 insert into "users_freelancer_skills"
 ("freelancer_id", "skill_id")
 values
 (freelancerid, skill id1)
 (freelancerid, skill id2)
 (freelancerid, skill id3)

 -- Category.objects.filter(name__in = value)
 select "services_category"."id", "services_category"."name", "services_category"."description"
 from "services_category"
 where "services_category"."name" IN value 

-- Client.objects.create(user=user)
insert into "users_client"
("client_id")
values
(client_id)

-- client.preferred_categories.set(preferred_categories)
delete from "users_client_preferred_categories"
where "client_id" = client_id

insert into "users_client_preferred_categories"
("client_id", "preferred_categories")
values
(client_id1, preferred_categories1)
(client_id2, preferred_categories2)
(client_id3, preferred_categories3)





