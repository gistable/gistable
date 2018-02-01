class CheckoutView(View):
    form_class = CheckoutForm
    template = 'account/checkout.html'
    email_template_name = 'account.checkout_success'

    def create_sub(self, user, customer, plan, quantity):
        subscription = customer.subscriptions.create(plan=plan, quantity=quantity)
        user.stripe_subscription_id = subscription.id
        user.save()

    def get(self, request, *args, **kwargs):
        data = {
            'sub_type': settings.STRIPE_SUBTYPE_MONTHLY,
        }
        user = request.user

        for field in self.form_class(type=user.account_type).fields:
            if hasattr(user, field) and getattr(user, field) is not None:
                    data.update({field: getattr(user, field).__str__()})

        return render(
            request, 
            self.template,
            {
                'form': self.form_class(type=user.account_type, initial=data), 
                'stripe_key': settings.STRIPE_PUBLISHABLE
            }
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, type=request.user.account_type)
        if form.is_valid():
            user = request.user
            stripe.api_key = settings.STRIPE_SECRET
            token = form.cleaned_data['stripe_token']
            quantity = form.cleaned_data.get('quantity', 1)
            try:
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
            except stripe.InvalidRequestError, e:
                if e.__str__() == "No such customer: " + user.stripe_customer_id:
                    logger.exception('Invalid request on stripe customer retrieve, no customer... creating.')
                    customer = stripe.Customer.create(
                        email=user.email,
                        metadata={
                            'account_type': user.account_type
                        }
                    )
                    user.stripe_subscription_id = None
                    user.stripe_customer_id = customer.id
                    user.save()
                else:
                    logger.exception('Invalid request on stripe customer retrieve, unknown error!')

            customer.card = token
            customer.save()

            if form.cleaned_data['sub_type'] == settings.STRIPE_SUBTYPE_YEARLY:
                license_range = settings.STRIPE_YEARLY_RANGE
                price = settings.STRIPE_YEARLY_COST
                period = settings.STRIPE_YEARLY_PERIOD
            else:
                license_range = settings.STRIPE_MONTHLY_RANGE
                price = settings.STRIPE_MONTHLY_COST
                period = settings.STRIPE_MONTHLY_PERIOD

            context = {
                'shortName': user.get_short_name(),
                'period': period,
                'last_4': form.cleaned_data['cc_last_4'],
                'license_cost': price,
            }

            if user.stripe_subscription_id is None:
                self.create_sub(user, customer, form.cleaned_data['sub_type'], quantity)
                if user.account_type == settings.ACCOUNT_PERSONAL:
                    license = License.objects.create_license(user, license_range, user)
                    license.save()

                    context.update(
                        {
                            'license_count': 1,
                            'total_cost': price*1,
                            'next_charge_date': license.get_expiration_date()
                        }
                    )

                else:
                    License.objects.create_multiple_licenses(quantity, user, license_range)
                    license = user.get_unassigned_licenses()[0]
                    context.update(
                        {
                            'license_count': quantity,
                            'total_cost': price*quantity,
                            'next_charge_date': license.get_expiration_date()
                        }
                    )

            else:
                subscription = customer.subscriptions.retrieve(user.stripe_subscription_id)

                original_plan = subscription.plan.id
                selected_plan = form.cleaned_data['sub_type']

                if original_plan == selected_plan:
                    original_quantity = subscription.quantity
                    subscription.quantity = original_quantity + quantity
                    subscription.save()
                    License.objects.create_multiple_licenses(quantity, user, license_range)
                    license = user.get_unassigned_licenses()[0]
                    context.update(
                        {
                            'license_count': quantity,
                            'total_cost': price*quantity,
                            'next_charge_date': license.get_expiration_date()
                        }
                    )
                else:
                    License.objects.delete_user_licenses(user)
                    subscription.delete()
                    self.create_sub(user, customer, form.cleaned_data['sub_type'], quantity)
                    License.objects.create_multiple_licenses(quantity, user, license_range)
                    license = user.get_unassigned_licenses()[0]
                    context.update(
                        {
                            'license_count': quantity,
                            'total_cost': price*quantity,
                            'next_charge_date': license.get_expiration_date()
                        }
                    )

            # Update User Data
            for key in form.cleaned_data.keys():
                if hasattr(user, key):
                    setattr(user, key, form.cleaned_data[key])

            user.save()

            send_templated_email('Thank you for your order.', [user.email, ], self.email_template_name, context)

            return redirect('account:checkout_success')

        return render(request, self.template, {'form': form, 'stripe_key': settings.STRIPE_PUBLISHABLE})