import bpy
from bpy_extras import keyconfig_utils
import sys

# Dump Blender keyconfig as HTML.
# How to use
# 1. Open this file in Blender's Text Editor.
# 2. Do "Run Script".
# 3. New Text "keyconfigs.html" will be added.
#    save it somewhere and open in web browser (recommends Safari, Chrome or Firefox).
# 
# JSON format
# [keyconfig0, keyconfig1, ...]
# keyconfig := {name:"name", keymap:[keymap0, keymap1, ...]}
# keymap := {name:"name", item:[item0, item1, ...]}
# item := {name:"name", modifier_keys:["like 'Ctrl' or empty", ...], key:"key", propvalue:"value"}

html1 = """<html><head>
<script>
"""

html2 = """
function init() {
  var tabul = document.getElementById('tabs');
	var tablecon = document.getElementById('tables');
	
	var contents = [];
	var createTabAction = function (tabindex) {
		return function () {
			for(var i = 0; i < contents.length; i++) {
				var tmp = contents[i];
				if(i == tabindex) {
					tmp.tab.className = 'selected';
					tmp.table.style.display = 'block';
				} else {
					tmp.tab.className = '';
					tmp.table.style.display = 'none';
				}
			}
		};
	};
	
	for(var i = 0; i < bl_keyconfs.length; i++) {
		var kc = bl_keyconfs[i];
		// create tab
		var tabelm = document.createElement('li');
		tabelm.className = 'tab';
		tabelm.innerHTML = kc.name;
		tabul.appendChild(tabelm);
		tabelm.addEventListener('click', createTabAction(i));
		
		// create table
		var tablegroup = document.createElement('div');
		tablecon.appendChild(tablegroup);
		
		for(var ikm = 0; ikm < kc.keymaps.length; ikm++) {
			var km = kc.keymaps[ikm];
			var keytatble = document.createElement('table');
			tablegroup.appendChild(keytatble);
			
			var caption = document.createElement('caption');
			caption.innerHTML = km.name;
			keytatble.appendChild(caption);
			
			for(var iki = 0; iki < km.items.length; iki++) {
				var ki = km.items[iki];
				var tr = document.createElement('tr');
				keytatble.appendChild(tr);
				// action description
				var td;
				td = document.createElement('td');
				td.style.width = '35%';
				td.innerHTML = (ki.name.length > 0)? ki.name : '-';
				tr.appendChild(td);
				// key
				td = document.createElement('td');
				td.style.width = '35%';
				var modkey = "";
				for(var imod = 0; imod < ki.modifier_keys.length; imod++) {
					modkey += ki.modifier_keys[imod] + ' + ';
				}
				td.innerHTML = modkey + ki.key;
				tr.appendChild(td);
				// misc
				td = document.createElement('td');
				td.innerHTML = (ki.propvalue.length > 0)? ki.propvalue : '-';
				tr.appendChild(td);
			}
		}
		contents.push({'tab':tabelm, 'table':tablegroup})
	}
	(createTabAction(0))();
}
window.addEventListener('load', init);
</script>
<style>

table {
	margin-top: 2ex;
	width: 100%;
	border-collapse: collapse;
}
td {
	margin: 0;
	padding: 4px 8px 4px 8px;
	border: 1px solid #000;
}
caption {
	text-align: left;
	font-size: 120%;
	font-weight: bold;
}

.tablewrapper {
	padding: 4px;
	border: 1px solid #000;
	border-top-width: 0;
	position: relatie;
	display: block;
}

.tablegroup {
	padding: 0;
	margin: 0;
}

.tabul {
	list-style: none;
	margin: 0;
	padding: 0;
	position:relative;
}
.tabul:after {
	position: absolute;
	content: "";
	width: 100%;
	bottom: 0;
	left: 0;
	border-bottom: 1px solid #000;
	z-index: 1;
}
.tabul li {
	background: #ccc;
	color: #000;
	position: relative;
	margin: 0 1px 0 0;
	padding: 4px 10px;
	border: 1px solid #000;
	display: inline-block;
	z-index: 0;
}
.tabul li.selected {
	background: #fff;
	color: #000;
	border-bottom-color: #fff;
	z-index: 2;
}
</style>
</head>
<body>
<h1>Blender Key Configs</h1>
<div id="conf">
<ul class="tabul" id="tabs"></ul>
<div class="tablewrapper" id="tables"></div>
</div>
</body>
</html>
"""

def create_keymapitem_json(ki):
    modkeys = []
    if ki.any:
        modkeys.append('Any')
    else:
        if ki.ctrl:
            modkeys.append('Ctrl')
        if ki.alt:
            modkeys.append('Alt')
        if ki.shift:
            modkeys.append('Shift')
        if ki.oskey:
            #modkeys.append('OSkey')
            modkeys.append('Cmd')
        if ki.key_modifier != 'NONE':
            modkeys.append(ki.key_modifier)
    json = '{{"name":"{}",'.format(ki.name)
    if len(modkeys) > 0:
        json += '"modifier_keys":["{}"]'.format('","'.join(modkeys))
    else:
        json += '"modifier_keys":[]'
    json += ',"key":"{}"'.format(ki.type)
    if ki.propvalue != 'NONE':
        json += ',"propvalue":"{}"'.format(ki.propvalue)
    else:
        json += ',"propvalue":""'
    json += '}'
    return json

def create_keymap_json(kc):
    json = '{{"name":"{}","items":['.format(kc.name)
    for i, ki in enumerate(kc.keymap_items):
        if i > 0: json += ','
        json += create_keymapitem_json(ki)
        json += '\n'
    json += ']}'
    return json

def create_keyconfig_json(kc):
    json = '{{"name":"{}","keymaps":['.format(kc.name)
    for i, km in enumerate(kc.keymaps):
        if i > 0: json += ','
        json += create_keymap_json(km)
        json += '\n'
    json += ']}'
    return json

wm = bpy.context.window_manager
#kc = wm.keyconfigs.default
#kc = wm.keyconfigs.addon
#kc = wm.keyconfigs.user
#kc = wm.keyconfigs.active
#keyconfig_utils.keyconfig_export(wm, kc, "./keys.txt")

keyconfs = []
for kc in wm.keyconfigs:
    keyconfs.append(create_keyconfig_json(kc))
kcjson = 'var bl_keyconfs=[' + ','.join(keyconfs) + '];'
#print(kcjson)
#f = open('./keys.js', 'w')
#f.write(kcjson)
#f.close()
#print("write to file. done");

exist_texts = set(i.name for i in bpy.data.texts)
bpy.ops.text.new()
cur_texts = set(i.name for i in bpy.data.texts)
added_texts = cur_texts - exist_texts
newtext = bpy.data.texts[added_texts.pop()]
newtext.name = 'keyconfigs.html'
newtext.from_string(html1 + kcjson + html2)
