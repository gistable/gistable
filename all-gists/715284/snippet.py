from google.appengine.api import (
    apiproxy_stub_map,
    quota
)
import logging

def _log_api_pre_call(service, call, request, response, rpc):
    logging.debug('RPC(pre) %s.%s', service, call)

def _log_api_post_call(service, call, request, response, rpc, error):
    try:
        if service == 'datastore_v3' and call in ('Put', 'Touch', 'Delete', 'Commit'):
            cost = response.cost()
            cost_info = ' idx_writes=%d entity_writes=%d entity_bytes=%d' % (
                cost.index_writes(), cost.entity_writes(), cost.entity_write_bytes())
        else:
            cost_info = ''

        logging.info('RPC(post) %s.%s %.3fapi_cpu_ms%s',
                     service, call,
                     quota.megacycles_to_cpu_seconds(rpc.cpu_usage_mcycles),
                     cost_info)
    except Exception, e:
        logging.exception(e)

apiproxy_stub_map.apiproxy.GetPreCallHooks().Append(
    '_log_api_pre_call', _log_api_pre_call)

apiproxy_stub_map.apiproxy.GetPostCallHooks().Append(
    '_log_api_post_call', _log_api_post_call)
