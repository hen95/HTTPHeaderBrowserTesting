var table_to_json = function(table){
	var data = {}
	var headers = []
	for(var i=0;i<table.rows[0].cells.length;i++)
		headers.push(table.rows[0].cells[i].innerText)
	var rows = {}
	for(var i=1;i<table.rows.length;i++){
		rows[i] = []
		for(var j=0;j<table.rows[i].cells.length;j++){
			rows[i].push(table.rows[i].cells[j].innerText);
		}
		rows[i].push({'color': table.rows[i].className});
	}
	data['header'] = headers;
	data['rows'] = rows;
	return data;
}

var save_result = function(category, table, url){
	var parser = new UAParser();

	var result_data = {}
	// insert category
	result_data['category'] = category;
	result_data['save'] = true;
	result_data['result'] = table_to_json(table);
	result_data['browser'] = parser.getBrowser()['name'] + ' ' + parser.getBrowser()['version'];
	result_data['engine'] = parser.getEngine()['name'] + ' ' + parser.getEngine()['version'];
	result_data['os'] = parser.getOS()['name'] + ' ' +  parser.getOS()['version'];

	var request = new XMLHttpRequest();
	request.open("POST", url);
	request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	request.send(JSON.stringify(result_data));
}

var json_to_table = function(data){
	var num_column = data['header'].length;
	var tbl = document.createElement('TABLE');
	tbl.className = "table table-hover table-sm";
	// thead
	var header = document.createElement('thead');
	header.className = "thead-dark";
	tbl.appendChild(header);
	var header_row = header.insertRow();
	for(var i=0;i<num_column;i++){
		var th_row = document.createElement('th');
		th_row.innerText=data['header'][i];
		header_row.appendChild(th_row);
	}

	// tbody
	var body = document.createElement('tbody');
	tbl.appendChild(body);
	body.id = "results";
	for(var i in data['rows']){
		console.log(i);
		var row = body.insertRow();
		for(var j=0;j<num_column;j++){
			row.insertCell().innerText = data['rows'][i][j];
		}
		if(data['rows'][i][num_column] !== undefined)
			row.className = data['rows'][i][num_column]['color'];
	}
	return tbl;
}
