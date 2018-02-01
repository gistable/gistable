class LoggingMixin(object):
    def dispatch(self, request_type, request, **kwargs):
        logger.debug(
            '%s %s %s' %
            (request.method, request.get_full_path(), request.raw_post_data))

        try:
            response = super(LoggingMixin, self).dispatch(
                request_type, request, **kwargs)
        except (BadRequest, fields.ApiFieldError), e:
            logger.debug(
                'Response 400 %s' % e.args[0])
            raise
        except ValidationError, e:
            logger.debug(
                'Response 400 %s' % e.messages)
            raise
        except Exception, e:
            if hasattr(e, 'response'):
                logger.debug(
                    'Response %s %s' %
                    (e.response.status_code, e.response.content))
            else:
                logger.debug('Response 500')
            raise

        logger.debug(
            'Response %s %s' % (response.status_code, response.content))
        return response
