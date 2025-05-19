-- category.objects.all()

select "services_category"."id", "services_category"."name", "services_category"."description"
from "services_category"

-- queryset = service.objects.filter(is_active= True)
select "services_service".*
from "services_service"
where "services_service"."is_active" = 'True'

-- queryset.filter(categories__name__in = data['categories'])
select "services_service".*
from "services_service"
where "services_service"."category" IN (data['categories'])

--get_object_or_404(Service, id=pk, freelancer__user=request.user)
select "services_service".*
from "services_service"
join "users_freelancer" on "users_freelancer"."id" = "services_service"."freelancer_id"
where "services_service"."id" = pk AND "users_freelancer"."user_id" = <request.user.id>

 --proposals = Proposal.objects.filter(freelancer = freelancer).select_related("service", "client")

select  "services_proposal".*
        "services_service".*
        "users_client".*
from "services_proposal"
join "services_service" on "services_service"."id" = "services_proposal"."service_id"
join "users_client" on "users_client"."client_id" = "services_proposal"."client_id"
where "services_proposal"."freelancer_id" = freelancer

-- Order.objects.create(
--      proposal=proposal,
--      client=proposal.client,
--      freelancer=proposal.freelancer,
--      service=proposal.service,
--      total_amount=proposal.proposed_price,
--      delivery_date=timezone.now() + timedelta(days=7)
--   )

insert into "payments_order"
("payments_order"."proposal_id", "payments_order"."client_id","payments_order"."freelancer_id", "payments_order"."service_id", "payments_order"."total_amount","payments_order"."delivery_date")
values
(proposal, proposal.client, proposal.service, proposal_price, date)

--proposal.client
select "services_proposal"."client_id"
from "services_proposal"
where "services_proposal"."id" = id