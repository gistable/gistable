    if kwargs.get('execute_as_chained_job'):
        if job.output_data and job.output_data.get('status') == 'error':
            # This can happen if create_partner_ads is executed as a chained
            # task# after creation of campaings, and if creation of campaings
            # failed for what ever reason
            return job.pk
