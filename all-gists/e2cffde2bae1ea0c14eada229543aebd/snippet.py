def init(id, cfg):
    return True

def deinit(id):
    return True

def inform_super(id, qstate, superqstate, qdata):
    return True

domains = [
    "netflix.com.",
    "nflxso.net.",
]

def operate(id, event, qstate, qdata):
    if event == MODULE_EVENT_NEW or event == MODULE_EVENT_PASS:
        if qstate.qinfo.qtype != RR_TYPE_AAAA:
            qstate.ext_state[id] = MODULE_WAIT_MODULE
            return True

        for domain in domains:
            if qstate.qinfo.qname_str == domain or qstate.qinfo.qname_str.endswith("." + domain):
                msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)
                if not msg.set_return_msg(qstate):
                    qstate.ext_state[id] = MODULE_ERROR
                    return True
                # We don't need validation, result is valid
                qstate.return_msg.rep.security = 2
                qstate.return_rcode = RCODE_NOERROR
                qstate.ext_state[id] = MODULE_FINISHED
                log_info("no-aaaa: blocking AAAA request for %s" % qstate.qinfo.qname_str)
                return True

        qstate.ext_state[id] = MODULE_WAIT_MODULE
        return True

    if event == MODULE_EVENT_MODDONE:
        qstate.ext_state[id] = MODULE_FINISHED
        return True

    qstate.ext_state[id] = MODULE_ERROR
    return True

log_info("pythonmod: script loaded")
