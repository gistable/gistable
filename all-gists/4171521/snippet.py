import ledger
journal = ledger.read_journal(" LEDGER FILE PATH HERE  ")
print """<html>
<head>
	<title>Rental Ledger</title>
	<link rel="stylesheet" href="javascript/jquery.tablesorter/themes/blue/style.css" type="text/css" id="" media="print, projection, screen" />
	<script type="text/javascript" src="javascript/jquery.js"></script> 
	<script type="text/javascript" src="javascript/jquery.tablesorter/jquery.tablesorter.js"></script>
	<script type="text/javascript" id="js">
		$(document).ready(function() {
			// call the tablesorter plugin
			$("table").tablesorter();
			$('#bill').hide();
			
		}); 
	</script>
	<style type="text/css">
		.date {
			width: 75px;
		}
		.house {
			width: 75px;
		}
		.reconciled {
			width: 20px;
		}
		.checknum {
			width: 50px;
		}
		.payee {
			width: 280px;
		}
		#transactions {
			float: left;
			width: 30%;
		}
		#bill {
			float: right;
			width: 60%;
		}
		table.tablesorter tbody tr { 
			background-color: white;
		}
		.post {
			font-size: 8pt;
			background-color: inherit;
		}
		.postaccount {
			width: 200px;
		}
	</style>
	<script type="text/javascript" >
		var lastrow;
		function show_bill(row, path) {
			$(row).css('background-color', '#F4F4F4');
			if (lastrow && lastrow != row) {
				$(lastrow).css('background-color', 'white');
			}
			if (path == '') {
				$('#bill').hide();
			}
			else 
			{
				$('#bill').show();
				$('#bill').attr("src", "../" + path);
			}		
			lastrow = row;
		}
	</script>
</head>
<body>
	<h1>Rental Ledger</h1>

	<table id="transactions" class="tablesorter">
		<thead>
			<tr><th class="date">Date</th><th class="house">House</th><th  class="reconciled">*</th><th class="checknum">Check</th><th class="payee">Payee</th></tr>
		</thead>
		<tbody>
"""
for xact in sorted(journal, key=lambda x: x.date):
	print "\t\t\t<tr onclick=\"show_bill(this, '%s')\"><td class=\"date\">%s</td><td class=\"house\">%s</td><td class=\"reconciled\">%s</td><td class=\"checknum\">%s</td><td class=\"payee\">%s" % (( xact.get_tag("image") if xact.has_tag("image") else ""), xact.date, (xact.get_tag("house") if xact.has_tag("house") else ""), "*", ("" if xact.code is None else xact.code), xact.payee)
	if xact.has_tag("image"):
		print "\t\t<!-- IMAGE: %s -->" % (xact.get_tag("image"))
	print "\t\t\t\t<table class=\"post\">"
	for post in xact: 
	    print "\t\t\t\t\t<tr><td class=\"postaccount\">%s</td><td>%s</td></tr>" % (post.account, post.amount)
	print "\t\t\t\t</table>\n\t\t\t</td></tr>"

print """
		</tbody>
	</table>

	<img id="bill" />

</body>
</html>
"""