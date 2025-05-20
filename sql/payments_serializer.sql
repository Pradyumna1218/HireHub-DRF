-- order serializer   
-- get freelancer
-- obj.freealancer.user.username

select "users_user"."username"
from "users_user"
join "users_freelancer"
on "users_freelancer"."user_id" = "users_user"."id"
join "payments_order"
on "payments_order"."freelancer_id" = "users_freelancer"."id"
where "payments_order"."id" = id

-- get client
-- obj.client.user.username
select "users_user"."username"
from "users_user"
join "users_freelancer"
on "users_user"."id" = "users_freelancer"."user_id"
join "payments_order"
on "payments_order"."freelancer_id" = "users_freelancer"."id"
where "payments_order"."id" = id

--get service

-- obj.service.id

select "services_service".id
from "services_service"
join "payments_order"
on "payments_order"."service_id" = "services_service"."id"
where "payments_order" = id

--get service

-- obj.service.title

select "services_service".title
from "services_service"
join "payments_order"
on "payments_order"."service_id" = "services_service"."id"
where "payments_order"."id" = id

