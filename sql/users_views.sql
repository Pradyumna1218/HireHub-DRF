-- get_obj_or_404(freelancer.objects>select_related("user"), user = request.user)

select "users_freelancer".*
        "users_user".*
from "users_freelancer"
join "users_user"
on "users_user"."id" = "users_freelancer"."user_id"
where "users_user"."id" = request.user
