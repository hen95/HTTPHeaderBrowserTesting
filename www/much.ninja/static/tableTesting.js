// Create table skeleton for testing.
// Input: ["header1", "header2", ..]
// Output: -
var createTable = function(headers){
	var tbl = document.createElement('table');
	tbl.setAttribute('class', 'table table-hover table-sm');
	var tblhead = document.createElement('thead');
	tblhead.setAttribute('class', 'thead-dark');
	tbl.appendChild(tblhead);
	var tblbody = document.createElement('tbody');
	tblbody.id = 'results';
	tbl.appendChild(tblbody);
	var anc = document.getElementById('table') ? document.getElementById('table') : document.body;
	anc.appendChild(tbl);

	// Now add all headers to the first row.
	var headtr = tblhead.insertRow();
	// We get an array of strings, hopefully.
	if(typeof(headers) !== 'object') return;
	for(var i=0;i<headers.length;i++){
		var th = document.createElement('th');
		th.innerText=headers[i];
		headtr.appendChild(th);
	}

}

// Create table entry (row) if doesn't exist.
// Otherwise update entry status.
// Input:
//	id: String of the test case to identify the table row.
//	content: Array of strings to write to the table row. If undefined, nothing is written.
//	attributes: Object of attributes. Key is the attribute name, value is the attribute value. If undefined, nothing is written.
//	stat: Status of the table entry. 'create', 'success', 'warning', 'danger' to update the table row.
// Output: true, if editing the table row was successful, false otherwise.
var updateTableEntry = function(id, content, attributes, stat){
	var tblentry = document.getElementById(id);
	switch(stat){
		case 'create':
			var tblbody = document.getElementById('results');
			if(tblentry) return false;
			tblentry = tblbody.insertRow();				
			tblentry.id = id;
			tblentry.className = "bg-secondary"
			// Create table entry cells here. We write them later anyways.
			for(var i=0;i<content.length;i++)
				tblentry.insertCell()
			break;
		case 'success':
			// Without id we can't update anything.
			if(!tblentry) return false;
			// We don't want to overwrite findings.
			//if(tblentry.className.indexOf("danger") !== -1 || tblentry.className.indexOf("warning") !== -1) return false;
			tblentry.className = "alert alert-success";
			break;
		case 'warning':
			// Without id we can't update anything.
			if(!tblentry) return false;
			// We don't want to overwrite findings.
			//if(tblentry.className.indexOf("danger") !== -1) return false;
			tblentry.className = "alert alert-warning";
			break;
		case 'danger':
			// Without id we can't update anything.
			if(!tblentry) return false;
			tblentry.className = "alert alert-danger";
			break;
		default:
			break;
	}
	// If no content is given, then we don't write anything.
	if(typeof(content) === 'object' && content !== null)
		for(var i=0;i<content.length;i++)
			if(content[i] && content[i] !== '')
				tblentry.children[i].innerText = content[i];
	if(typeof(attributes) === 'object' && attributes !== null)
		for(var i=0;i<Object.keys(attributes).length;i++)
			tblentry.setAttribute(Object.keys(attributes)[i], attributes[Object.keys(attributes)[i]])

	return true;
}
