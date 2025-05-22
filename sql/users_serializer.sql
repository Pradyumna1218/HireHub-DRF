--REGISTER

-- User.objects.all()
select "users_user"."id", "users_user"."password", "users_user"."username", "users_user"."email", "users_user"."phone" from "users_user" 

-- Freelancer.objects.all()
 select "users_freelancer"."id", "users_freelancer"."user_id", "users_freelancer"."profile", "users_freelancer"."rating"
 from "users_freelancer"

 -- Client.objects.all()
 select "users_client"."user_id" "users_client"."id", "users_client"."preferrred_categories" from "users_client"

 --Skill.objects.filter(name__in = skill_list)
 select "services_skill"."id", "services_skill"."category_id", "services_skill"."name" 
 from "services_skill"
 where "service_skill"."name" IN ('HTML', 'CSS')

 --Freelancer.objects.create(user = user, profile = profile)
 insert into "users_freelancer" 
 ("users_freelancer"."id", "users_freelancer"."user_id", "users_freelancer"."profile","users_freelancer"."rating")
 values 
 (id, user_id, 'profile_string', 0.0)

 --freelancer_skills.set(skills)
delete from "users_freelancer_skills"
where freelancer = freelancer

insert into "users_freelancer_skills"
("users_freelancer_skills"."id", "users_freelancer_skills"."skill_id")
values
(id1, skills1)
(id2, skills2)
(id3, skills3)

 -- Category.objects.filter(name__in = value)
 select "services_category"."id", "services_category"."name", "services_category"."description"
 from "services_category"
 where "services_category"."name" IN value 

-- Client.objects.create(user=user)
insert into "users_client"
("user_id")
values
(user_id)

-- client.preferred_categories.set(preferred_categories)
delete from "users_client_preferred_categories"
where "client_id" = client_id

insert into "users_client_preferred_categories"
("client_id", "cateogry_id")
values
(client_id1, preferred_categories1),
(client_id2, preferred_categories2),
(client_id3, preferred_categories3)


-- PROFILE

-- freelancer get_categories
-- obj.skills.all()
select "services_skill"."id","services_skill"."name","services_skill"."category_id"
from "services_skill"
Join "users_freelancer_skills"
On "services_skill"."id" = "users_freelancer_skills"."skill_id" 

--skill.category.name if skill.category
select "services_category"."name"
from "services_category" 
where "services_category"."id" = id

-- freelancer get_skills
select "services_skill"."id", "services.skill".'name', "services_skill"."category_id"
from "services_skill"
join "users_freelancer_skills" 
on "users_freelanacer_skills"."skill_id" = "services_skill"."id"

--client profile
-- get_Preferred_categories

select "services_category"."id", "services_category"."name", "services_category"."description"
from "services_category"
join "users_client_preferred_categories" 
on "users_client_preferred_categories"."category_id" = "services_category"."id"

--password
--User.objects.filter(email = email).exists

select exists (
    select *
    from "users_user"
    where "users_user"."email" = email
) 

-- User.objects.get(pk = user_id)
select "users_user"."id", "users_user"."password", "users_user"."username", "users_user"."email", "users_user"."phone"
from "users_user"
where "users_user"."id" = user_id
