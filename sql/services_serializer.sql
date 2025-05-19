-- freelancer_skills = freelancer.skills.all()
-- Category.objects.filter(skills__in = freelancer_skills)

select "services_category"."id", "services_cateogory"."name", "services_category"."description"
from "services_category"
Join "services_skill" ON "services_skill"."category_id" = "services_category"."id"
where "services_skill"."id" In (
    select "users_freelancer_skills"."skills_id"
    from "users_freelancer_skills"
    where "users_freelancer_skills"."skills_id" = id
)

-- Service.objects.create(freelancer = freelancer, ** validated_data)
insert into ("services_service"."freelancer_id", "services_service"."title", "services_service"."description", "services_service"."price")
values (1,"hehe", "haha", 200)

-- get_freelancer obj.freelancer.user.username
select "users_user"."username"    
from "users_freelancer"
join "users_user" on "users_user"."id" = "users_freelancer"."user_id"
join "services_service" on "users_freelancer"."id" = "services_service"."freelancer_id"

-- get_skills obj.freelancer.skills.all()
select "services_skill"."name"
from "services_skill"
join "users_freelancer_skills" on "users_freelancer_skills"."skill_id" = "services_skill"."id"
where "users_freelancer_skills"."freelancer_id" = 1

-- get_categories category.name obj.categories.all()

select "services_category"."name"
from "services_category"
join "services_service_categories"
on "services_category"."id" = "services_service_categories"."category_id"

