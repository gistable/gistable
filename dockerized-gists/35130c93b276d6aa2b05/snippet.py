def changePassword(user_dn, old_password, new_password):
	ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
	l = ldap.initialize("LDAPS://DOMAIN.COM")
	l.set_option(ldap.OPT_REFERRALS,0)
	l.set_option(ldap.OPT_PROTOCOL_VERSION,3)
	l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
	l.set_option(ldap.OPT_X_TLS_DEMAND,True)
	l.set_option(ldap.OPT_DEBUG_LEVEL,255)
	l.simple_bind_s("ACCOUNTWITHRIGHTS@DOMAIN.COM", "PASSWORD")

	# Reset Password
	unicode_pass = unicode('\"' + str(new_password) + '\"', 'iso-8859-1')
	password_value = unicode_pass.encode('utf-16-le')
	add_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [password_value])]

	l.modify_s(user_dn,add_pass)

	# Its nice to the server to disconnect and free resources when done
	l.unbind_s()