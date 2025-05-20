-- order = Order.objects.filter(freelancer=freelancer).select_related("service", "client")

select "payments_order".*
       "payments_service".*
       "payments_client".*
from "payments_order"
join "services_service"
on "services_service"."id" = "payments_order"."service_id"
join "users_client"
on "users_client"."id" = "payments_order"."client_id"
where "payments_order"."id" = 1

-- order = Order.objects.get(id=order_id, client__user=user)
select "payments_order".*
from "payments_order"
join "users_client"
on "payments_order"."client_id" = "users_client"."id"
where "payments_order"."id" = order_id and "users_client"."user_id" = id

-- existing_payment = Payment.objects.filter(order=order, status="Pending").first()
select "payments_payment".*
from "payments_payment"
join "payments_order"
on "payments_order"."id" = "payments_payment"."order_id"
where "payments_payment".status = "Pending" 

-- --  payment = Payment.objects.create(
--             order=order,
--             user=user,
--             status="Pending",
--             payment_amount=order.total_amount,
--             payment_date=timezone.now()
--         )

insert into "payments_payment"
(order, user, status, payment_amount, payment_date)
values
(order, user, "Pending", payment_amount, payment_date)


-- order = get_object_or_404(Order, id=order_id)
select "payments_order".*
from "payments_order"
where "payments_order"."id" = order_id
