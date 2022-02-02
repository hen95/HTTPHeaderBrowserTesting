
// more or less this: header list with all its values separated by a comma (https://tools.ietf.org/html/rfc7230)
// https://fetch.spec.whatwg.org/#concept-header-list-get
// returns the values of all headers which share the same names
var get_directive_list = function(headers, headername){
	var result = [];
	headername = new RegExp('^'+headername +':', "i");
	for(var i=0;i<headers.length;i++)
		if(headers[i].match(headername))
			result = result.concat(get_directive(headers[i]).toLowerCase().replace(/\s/g,"").split(','));
	return result;
}

// case-sensitive for ACAC
var get_directive_list_case_sensitive = function(headers, headername){
	var result = [];
	headername = new RegExp('^'+headername, "i");
	for(var i=0;i<headers.length;i++)
		if(headers[i].match(headername))
			result = result.concat(get_directive(headers[i]).replace(/\s/g,"").split(','));
	return result;
}

// get all values of one header instance
var get_directive = function(header){
	return header.replace(header.slice(0, header.indexOf(':')) + ':', '').trim();	
}
 

// for which header is only one allowed?
// probably those with just one directive
var single_header_allowed = [
	'Access-Control-Allow-Origin',
	'Access-Control-Allow-Credentials',
	'Access-Control-Max-Age',
]


var acah_abnf = function(header_with_val){
    return /^Access-Control-Allow-Headers:[\s]*(?:(?:[\w\-]+|\*)(?:[\s]*,[\s]*(?:[\w\-]+|\*))*)?$/i.test(header_with_val);
}

var acam_abnf = function(header_with_val){
	return /^Access-Control-Allow-Methods:[\s]*(?:\w+|\*)?(?:[\s]*,[\s]*(?:\w+|\*))?$/i.test(header_with_val);
}

var aceh_abnf = function(header_with_val){
	return /^Access-Control-Expose-Headers:[\s]*(?:\w+|\*)?(?:[\s]*,[\s]*(?:\w+|\*))?$/i.test(header_with_val);
}

// Extract header list values for
// AC-Allow-Methods, AC-Allow-Headers, AC-Max-Age
// https://fetch.spec.whatwg.org/#extract-header-list-values
var extract_header_list_values = function(headers, headername, single_header, abnf_rule){
	// Step 1:
	var contains=false;
	var count = 0;
	for(var i=0;i<headers.length;i++)
		if(headers[i].toLowerCase().split(':')[0] === headername.toLowerCase()){
			contains = true;
			count++;
		}
	// Note: return null => empty list will evaluate to false in the end
	if(!contains)
		return [];
	// Step 2:
	// Note: return false => empty list will evaluate to false in the end
	if(count > 1 && single_header)
		return false;
	// Step 3:
	var values = [];
	// Step 4:
	headername = new RegExp('^'+headername+ ':', "i");
	for(var i=0;i<headers.length;i++){
		if(headers[i].match(headername)){
			// Step 4.2
			if(abnf_rule !== undefined && !abnf_rule(headers[i]))
				return false;
			// Step 4.1 and Step 4.3
			values= values.concat(get_directive(headers[i]).toLowerCase().replace(/\s/g,"").split(','));
		}
	}
	return values;

}



// acao rules: https://fetch.spec.whatwg.org/#cors-check
var acao_rules = function(headers, credentials_mode){
	// Step 1:
	// (Note: fetch states getting origin as HEADER LIST.
	// But Step 3 & 4 are stating that origin has to be a single item, therefore a string.)
	// - "This intentionally does not use combine, as 0x20 following 0x2C is not the way this was implemented, for better or worse."
	// Cant be split via 0x2c 0x20 when there is no 0x2c 0x20
	var origin = get_directive_list(headers, "access-control-allow-origin");
	// only one element is allowed
	if(origin.length > 1)
		return false;
	origin = origin[0];
	// Step 2: "if origin is null" (null !== "null")
	if(origin === undefined || origin.length === 0)
		return false;
	// Step 3:
	if(credentials_mode !== 'include' && origin === '*')
		return true;
	// Step 4:
	if(origin !== document.location.origin)
		return false;
	// Step 5:
	if(credentials_mode === undefined || credentials_mode !== 'include')
		return true;
	// Step 6:
	var credentials = acac_rules(headers);
	// Step 7:
	if(credentials)
		return true;
	// Step 8:
	return false;
}

// well this is easy i guess. just care: CASE-SENSITIVE
// Step 6: in https://fetch.spec.whatwg.org/#cors-check
var acac_rules = function(headers){
	var directive = get_directive_list_case_sensitive(headers, "access-control-allow-credentials");
	// only one element is allowed
	if(directive.length > 1)
		return false;
	if(directive[0] === 'true')
		return true;
	return false;
}

// https://fetch.spec.whatwg.org/#cors-preflight-fetch
var acah_rules = function(res_headers, req_headers, credentials){
	// Step 7.2:
	var headerNames = extract_header_list_values(res_headers, "access-control-allow-headers", false, acah_abnf);
	if(!headerNames)
		return false;
	// Step 7.3:
	if(headerNames === undefined || headerNames.length === 0)
		return false;
	// Step 7.6:
	var requested_headers = get_directive_list(req_headers, "access-control-request-headers");
	if(requested_headers.indexOf('authorization') !== -1 && headerNames.indexOf('authorization') === -1)
		return false;
	// Step 7.7:
	// Credentials are in parameters
	var wildcard = (headerNames.indexOf('*') !== -1) ? true : false;
	var check_acah = function(elem, index, arr){
		return (headerNames.indexOf(elem) !== -1) ? true : false;
	}
	return (requested_headers.every(check_acah) || (!credentials && wildcard));
}

// https://fetch.spec.whatwg.org/#cors-preflight-fetch
var acam_rules = function(res_headers, req_method, credentials){
	var simple_methods = ['get', 'head', 'post'];
	// Step 7.1:
	var methods = extract_header_list_values(res_headers, "access-control-allow-methods", false, acam_abnf);
	// Step 7.3:
	if(!methods)
		return false;
	// Step 7.4: Caching stuff. Not part of this.
	// Step 7.5:
	return (methods.indexOf(req_method.toLowerCase()) !== -1 || (methods.indexOf('*') !== -1 && credentials !== 'include') || simple_methods.indexOf(req_method.toLowerCase()) !== -1) ? true : false;
}

// https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers
var safelisted_resp_headers = [
	'cache-control',
	'content-language',
	'content-length',
	'content-type',
	'expires',
	'last-modified',
	'pragma'
];
// https://fetch.spec.whatwg.org/#main-fetch Step 4.14.1.1 - 4.14.1.3
// Given: extracting values of ACEH, and response header list
// Parameter 0: headers who should be exposed, parameter 1: exposed response headers
var aceh_rules = function(exp_headers, res_headers, credentials){
	// Step 4.14.1.1
	var headerNames = extract_header_list_values(exp_headers, "access-control-expose-headers", false, aceh_abnf);
	if(!headerNames)
		headerNames = [];
	// These headers are allowed to be exposed.
	headerNames = headerNames.concat(safelisted_resp_headers);
	// Step 4.14.1.2 "contains *"
	if(!credentials && headerNames.indexOf('*') !== -1){
		// get unique, no duplicates
		var unique_headers = [];	
		for(var i=0;i<res_headers.length;i++){
			if(unique_headers.indexOf(res_headers[i]) === -1)
				unique_headers.push(res_headers[i]);
		}
		return unique_headers;
	}
	// Step 4.14.1.3
	// https://fetch.spec.whatwg.org/#concept-response-cors-exposed-header-name-list
	// https://fetch.spec.whatwg.org/#concept-filtered-response-cors
	headerNames = res_headers.filter(function(elem){
		return (headerNames.indexOf(elem) !== -1) ? true : false;
	});
	return headerNames;
}

// XFO: https://tools.ietf.org/html/rfc7034#section-2.3.2
// "If an XFO header field prohibits framing, deny"
// https://html.spec.whatwg.org/#the-x-frame-options-header
var xfo_rules = function(headers, framed_same_origin){
	// Step 3, 4, 5 (getting and parsing directives):
	var directives_list = get_directive_list(headers, "x-frame-options");
	// Step 4, 5 (converting list to set):
	var directives = [];
	for (var i=0;i<directives_list.length;i++)
		if(directives.indexOf(directives_list[i]) === -1)
			directives.push(directives_list[i]);
	// Step 6 (conflicting directives):
	// note: multiple directives with the same value would NOT evaluate to false
	// because we are using a set (every directive is unique)
	var deny = directives.indexOf("deny") !== -1 ? true : false;
	var sameorigin = directives.indexOf("sameorigin") !== -1 ? true : false;
	var allowall = directives.indexOf("allowall") !== -1 ? true : false;
	if(directives.length > 1 && (deny || sameorigin || allowall))
		return false;
	// Step 7 (multiple invalid values => invalid XFO => allow framing):
	if(directives.length > 1)
		return true;
	// Step 8:
	if(directives[0] === 'deny')
		return false;
	// Step 9:
	// note: the testcases dont cover nested framing,
	// therefore this step is not really needed.

	// instead check if the framed_same_origin is sameorigin
	// EMBEDDING ELEMENT: framed_same_origin
	// EMBEDDED ELEMENT: Either framed_same_origin (domain) or !framed_same_origin (subdomain)
	// => check from subdomain is !framed_same_origin
	// 		=> if XFO on subdomain contains 'sameorigin' then false
	if(directives[0] === 'sameorigin' && !framed_same_origin)
		return false;
	// Step 10:
	return true;
}

// for hsts
// remove whitespaces, make all directives lower case, split by comma (;)
var get_directive_list_hsts = function(header, headername){
	var result = [];
	headername = new RegExp('^'+headername, "i");
	if(header.match(headername))
		result = result.concat(get_directive(header).toLowerCase().replace(/\s/g,"").split(';'));
	return result;
}
// https://tools.ietf.org/id/draft-ietf-websec-strict-transport-sec-14.txt#:~:text=6.1.%20%20Strict-Transport-Security%20HTTP%20Response%20Header%20Field
var hsts_rules = function(headers){
	// https://tools.ietf.org/id/draft-ietf-websec-strict-transport-sec-14.txt#:~:text=If%20a%20UA%20receives%20more%20than%20one%20STS%20header%20field
	// If multiple HSTS are present, then check only the first 
	var header = headers;
	var false_result = [false, false];
	// if header == O object, then we have an array => more than one hsts header
	// only take the first one
	if(typeof(header) === 'object')
		header = headers[0];
	if(typeof(header) !== 'string')
		return false_result;

	// Order of appearance of directives is not significant
	// All directives MUST appear only once
	// Directives are case-insensitive
	var directives = get_directive_list_hsts(header, 'strict-transport-security');
	var max_age_present = false;
	var max_age_zero = false;
	var include_subdomains_present = false;
	// max-age value can be quoted
	var max_age_regex = /^max-age=["]?(\d+)["]?$/;
	for(var i=0;i<directives.length;i++){
		if(max_age_regex.test(directives[i])){
			// All directives MUST appear only once
			if(max_age_present)
				return false_result;
			max_age_present = true;
			var match = max_age_regex.exec(directives[i]);
			if(match[1] == '0')
				max_age_zero = true;
			continue;
		}
		if(directives[i] === 'includesubdomains'){
			// All directives MUST appear only once
			if(include_subdomains_present)
				return false_result;
			include_subdomains_present = true;
			continue;
		}
	// Ignore unknown directives / directive values
		// check directive name for unknown directive
		// something like this:
		//CTL = <any US-ASCII control character
		//         (octets 0 - 31) and DEL (127)>
		//
		//token          = 1*<any CHAR except CTLs or separators>
		//separators     = "(" | ")" | "<" | ">" | "@"
		//               | "," | ";" | ":" | "\" | <">
		//               | "/" | "[" | "]" | "?" | "="
		//               | "{" | "}" | SP | HT
		// yea who cares about Space and horizontal tab
		var separators = [
		   	"(", ")", "<", ">", "@",
		   	",", ";", ":", ">", '"',
		   	"/", "[", "]", "?", "=",
		   	"{", "}", " ", "\t" ];
		for(var j=0;j<directives[i].length;j++){
		   	var ascii = directives[i][j].charCodeAt(0);
		   	var a = directives[i][j];
		   	if(ascii < 32 || ascii > 126 || separators.indexOf(a) !== -1)
		   		return [false, false];
		   }
	}
	// [ true if HTTPS, true if HTTPS on sudomain ]
	var HTTPS_domain = (max_age_present && !max_age_zero) ? true : false;
	var HTTPS_subdomain = (HTTPS_domain && include_subdomains_present) ? true : false;
	return [HTTPS_domain, HTTPS_subdomain];
}
// -------------------------------------------------------------------------
// CSP frame-ancestors
// -------------------------------------------------------------------------

// https://www.w3.org/TR/CSP3/#match-schemes
// 6.6.2.7 Note: http: matches https: but https: does not match http: !
var scheme_part_match = function(A, B){
	if(!A || !B)
		return false;
	var a = A.toLowerCase();
	var b = B.toLowerCase();
	if(
		a === b ||
		( a === 'http' && b === 'https' ) ||
		( a === 'ws' && ( b === 'wss' || b === 'http' || b === 'wss' )) ||
		( a === 'wss' && b === 'https' )
	) return true;
	return false;
}

// https://www.w3.org/TR/CSP3/#host-part-match
// 6.6.2.8
var host_part_match = function(A, B){
	if(!A || !B)
		return false;
	if(A[0] === '*'){
		var remaining = A.slice(1);
		if(B.toLowerCase().indexOf(remaining, B.length - remaining.length) !== -1)
			return true;
	}
	if(A.toLowerCase() !== B.toLowerCase())
		return false;
	// Step 3: Disallow IPv4 and IPv6. Test cases does not include ips
	return true;
}

// https://www.w3.org/TR/CSP3/#port-part-matches
// 6.6.2.9
var port_part_match = function(A, B, B_scheme){
	var default_port_list = {
	    'file': null,
	    'ftp': 21,
	    'http': 80,
	    'https' : 443,
	    'ws': 80,
	    'wss' : 443,
	};

	if(!A || A === ''){
		if(B_scheme in default_port_list && (B == default_port_list[B_scheme] || !B || B === ''))
			return true;
	return false;
	}
	if(A === '*')
		return true;
	if(A === B)
		return true;
	if(!B || B === ''){
		if(B_scheme in default_port_list && default_port_list[B_scheme] == A)
			return true;
	}
	return false;
}

// https://www.w3.org/TR/CSP3/#path-part-matches
// 6.6.2.10
var path_part_match = function(A, B){
	if(!A || A.length === 0)
		return true;
	if(A.length === 1 && A[0] === '/' && (!B || B.length === 0))
		return true;
	var exact_match = (A[A.length-1] === '/') ? false : true;
	var path_list_a = A.split('/');
	if(!B || B.length === 0)
		B = '';
	var path_list_b = B.split('/');
	if(path_list_a.length > path_list_b)
		return false;
	if(exact_match && path_list_a.length !== path_list_b.length)
		return false;
	if(!exact_match){
		console.assert(path_list_a[path_list_a.length-1] === '', "CSP PATH Error: Last element of Path is not '/'");
		path_list_a = path_list_a.slice(0, path_list_a.length-1);
	}
	for(var i=0;i<path_list_a.length;i++){
		var piece_A = decodeURIComponent(path_list_a[i]);
		var piece_B = decodeURIComponent(path_list_b[i]);
		if(piece_A !== piece_B)
			return false;
	}
	return true;
}

// url match source list
// https://www.w3.org/TR/CSP3/#match-url-to-source-list
// Return "Matches" (true) if the URL matches one or more source expressions in source list, else "Does Not Match" (false)
var url_match_source_list = function(url, source_list, origin, redirect_count){
	// Step 1:
	console.assert(source_list !== null && source_list !== undefined, "CSP: Source list is null.");
	// Step 2:
	if(source_list.length === 0)
		return false;
	// Step 3:
	// Note: An empty source list (just frame-ancestors without directive values) is equivalent to 'none' 	
	if(source_list.length === 1 && source_list[0].toLowerCase() === "'none'")
		return false;
	// Step 4:
	for(var i=0;i<source_list.length;i++){
		if(url_match_expr_origin(url, source_list[i], origin, redirect_count))
			return true;
	}
	return false;
}


var match_scheme_source = function(input_str){
	// https://www.w3.org/TR/CSP3/#framework-directive-source-list
	var source_list_scheme = /[a-zA-Z][\w\+\-\.]*/;
	var source_list_scheme_source = /^[a-zA-Z][\w\+\-\.]*:$/;
	
	if(!source_list_scheme_source.test(input_str))
		return false;
	var scheme_match = source_list_scheme.exec(input_str.split(':')[0]);
	var match_source_scheme = (scheme_match[0] === scheme_match['input']) ? true : false;
	if(match_source_scheme)
		return true;
	return false;
}

var match_host_source = function(input_str){
	// EASY REGEX
	var source_list_host_source = /^(?:[a-zA-Z][\w\+\-\.]*\:\/\/)?(?:\*|\*\.)?[a-zA-Z\-]+(?:\.[a-zA-Z\-]*)*(?:\:(?:\d+|\*))?(?:\/(?:[\w\-\.\-\~]|(?:\%[0-9a-fA-F]{2})|[\!\$\&\'\(\)\*\+\=]|\:|\@)*(?:\/(?:[\w\-\.\-\~]|(?:\%[0-9a-fA-F]{2})|[\!\$\&\'\(\)\*\+\=]|\:|\@)*)*)?$/;
	var host_match = source_list_host_source.exec(input_str);
	if(host_match === null || host_match[0] === undefined)
		return false;
	var match_source_host = (host_match[0] === host_match['input']) ? true : false;
	if(match_source_host)
		return true;
	return false;

}

// Custom helper function
var get_url_parts = function(input_str, part){
	// All definitions from https://w3c.github.io/webappsec-csp/#grammardef-host-part
	// Sadly it is getting really ugly and .exec matches a bit weird with it.
	var host_source = /(?:([a-zA-Z][\w\+\-\.]*:)(?:\/\/)?)?((?:\*|\*\.)?[a-zA-Z\-]+(?:\.[a-zA-Z\-]*)*)(\:(?:\d+|\*))?(\/(?:[\w\-\.\-\~]|(?:\%[0-9a-fA-F]{2})|[\!\$\&\'\(\)\*\+\=]|\:|\@)*(?:\/(?:[\w\-\.\-\~]|(?:\%[0-9a-fA-F]{2})|[\!\$\&\'\(\)\*\+\=]|\:|\@)*)*)?/;
	var matches = host_source.exec(input_str);
	try { 
		switch(part){
			case 'scheme':
				// We need this hacky thing in order to match "data:" in the scheme instead of "data" in the host part.
				var scheme = /(?:([a-zA-Z][\w\+\-\.]*:)(?:\/\/)?)/;
				matches = scheme.exec(input_str);
				return (matches[1] !== undefined) ? matches[1].split(':')[0] : false;
			case 'host':
				return (matches[2] !== undefined) ? matches[2] : false;
			case 'port':
				return (matches[3] !== undefined) ? matches[3].split(':')[1] : false;
			case 'path':
				return (matches[4] !== undefined) ? matches[4] : false;
			case 'all':
			default:
				return (matches[0] !== undefined) ? matches[0] : false;
		}
	} catch(e){
		 return false;
	}
}

// url match expression in origin
// https://www.w3.org/TR/CSP3/#match-url-to-source-expression
// Output: true ("Matches") if url matches expression, false ("Does Not Match") otherwise
var url_match_expr_origin = function(url, expr, origin, redirect_count){
	// https://fetch.spec.whatwg.org/#url
	// is this meant in 1.1 with "network scheme"?
	var http_s_scheme = ['http', 'https'];
	var network_scheme = ['about', 'blob', 'data', 'file'].concat(http_s_scheme);
	var url_scheme = get_url_parts(url, 'scheme');
	var expr_scheme = get_url_parts(expr, 'scheme');
	var origin_scheme = get_url_parts(origin, 'scheme');
	// https://url.spec.whatwg.org/#default-port
	var default_port_list = {
		'file': null,
		'ftp': 21,
		'http': 80,
		'https' : 443,
		'ws': 80,
		'wss' : 443,
	};
	// Step 1:
	// just a wildcard is given as value
	if(expr === '*'){
		if(http_s_scheme.indexOf(url_scheme) !== -1 && url_scheme === origin_scheme)
			return true;
	}
	// Step 2:
	// check schemes first
	// scheme only for example: https:
	if(match_scheme_source(expr) || match_host_source(expr)){
		// Step 2.1
		if(get_url_parts(expr, 'scheme') && !scheme_part_match(expr_scheme, url_scheme))
			return false;
		// Step 2.2
		if(match_scheme_source(expr))
			return true;
	}
	// Step 3:
	// hostname is given as directive value
	if(match_host_source(expr)){
		// Step 3.1:
		// Note: Wouldnt go here if no HOST is found.
		if(!get_url_parts(url, 'host'))
			return false;
		// Step 3.2:
		if(!get_url_parts(expr, "scheme") && !scheme_part_match(origin_scheme, url_scheme))
			return false;
		// Step 3.3:
		if(!host_part_match(get_url_parts(expr,'host'),get_url_parts(url,'host')))
			return false;
		// Step 3.4: Note: false instead of null
		var port_part = get_url_parts(expr, 'port');
		var url_port = get_url_parts(url, 'port');
		if(!port_part_match(port_part, url_port, url_scheme))
			return false;
		// Step 3.6:
		if(get_url_parts(expr,'path') !== false && redirect_count === 0){
			var path = get_url_parts(url,'path');
			if(!path_part_match(get_url_parts(expr,'path'), path))
				return false;
		}
		// Step 3.7:
		return true;
	}
	// Step 4:
	// 'self' part
	if(expr.toLowerCase() === "'self'"){
		var url_origin = get_url_parts(url, 'scheme') + '://' + get_url_parts(url, 'host') + ':' + get_url_parts(url, 'port');
		// https://url.spec.whatwg.org/#default-port
		var default_port_list = {
			'file': null,
			'ftp': 21,
			'http': 80,
			'https' : 443,
			'ws': 80,
			'wss' : 443,
		};
		if(
			origin === url_origin ||
			( get_url_parts(url, 'host') === get_url_parts(origin, 'host') &&
			  // if ports are not the same the default port has to be the same
			 (
				// ports are either the same, if both ports are not given it would equal to true, therefore check if one isnt false
				(get_url_parts(url, 'port') === get_url_parts(origin, 'port') && get_url_parts(origin, 'port') !== false) ||
				(
				  // check if the port is equal through the default ports
				  default_port_list[get_url_parts(url, 'scheme')] === default_port_list[get_url_parts(origin, 'scheme')] &&
				  (
					// 4.1.1 & 4.1.2 more checks
					get_url_parts(url, 'scheme') === 'https' || get_url_parts(url, 'scheme') === 'wss' ||
				  	(get_url_parts(origin, 'scheme') === 'http' && (get_url_parts(url, 'scheme') === 'http' || get_url_parts(url, 'scheme') === 'ws'))
				  )
			    )
			  )
			)
		){
		return true;
		}
	}
	// Step 5:
	return false;
}


// serialized directives: 'self' 'none'

// https://www.w3.org/TR/CSP3/#parse-serialized-policy-list
// serialized CSP: frame-ancestors 'self' 'none'; frame-ancestors http://much.ninja
// Input: serialized CSP, source = header(this one)/meta, disposition = enforce (in this test cases)/report
// Output: CSP object, note: if serialized cannot be parsed: the object's directive set will be empty
var parse_serialized_CSP = function(serialized_CSP, source, disposition){
	// Step 1:
	var policy = {'directive_set':{}, 'source': source, 'disposition': disposition};
	// Step 2:
	var ser_CSP = serialized_CSP.split(';');
	for(var i=0;i<ser_CSP.length;i++){
		// Step 2.1:
		var token = ser_CSP[i].trim();
		// Step 2.2:
		if(token === undefined || token.length === 0)
			continue;
		// Step 2.3:
		var directive_name = token.split(' ')[0];
		// Step 2.4:
		directive_name = directive_name.toLowerCase();
		// Step 2.5:
		if(directive_name in policy['directive_set'])
			continue;
		// Step 2.6:
		var directive_value = token.split(' ').slice(1);
		// Addition: Filter out empty elements
		for(var j=0;j<directive_value.length;j++)
			if(directive_value[j] === '' || directive_value[j] === undefined || directive_value[j] === null)
				directive_value.splice(directive_value.indexOf(directive_value[j]),1);
		// Step 2.7:
		policy['directive_set'][directive_name] = [];
		// Step 2.8:
		policy['directive_set'][directive_name] = directive_value;
	}
	// Step 3:
	return policy;
}



// https://www.w3.org/TR/CSP3/#parse-serialized-policy-list
// serialized CSP list: frame-ancestors 'self' 'none'; frame-ancestors http://much.ninja, frame-ancestors 'self' 'none'
// Input: serialized CSP list, source = header(this one)/meta, disposition = enforce (in this test cases)/report
// Output: list of CSP objects, note: if list cannot be parsed: return empty list
var parse_serialized_CSP_list = function(serialized_CSP_list, source, disposition){
	// Step 1:
	var policies = [];
	// Step 2:
	var ser_CSP = serialized_CSP_list.split(',');
	for(var i=0;i<ser_CSP.length;i++){
		var token = ser_CSP[i].trim();
		// Step 2.1:
		var policy = parse_serialized_CSP(token, source, disposition);
		// Step 2.2:
		if(policy === undefined || Object.keys(policy).length === 0)
			continue;
		// Step 2.3:
		policies.push(policy);
	}
	// Step 3:
	return policies;
}

// check frame-ancestors with given functions from spec
// this function is NOT from spec since i couldnt find it :,)
// Input: ["CSP: frame-ancestors 'self' 'none'; frame-ancestors *.domain.com", "CSP: frame-ancestors 'self'"]
// Output: true (framing allowed), false (framing not allowed)
var check_frame_ancestors = function(CSP_list, url, origin, redirect_count){
	for(var i=0;i<CSP_list.length;i++){
		var directive = get_directive(CSP_list[i]);
		var policies = parse_serialized_CSP_list(directive, 'header', 'enforce');
		for(var j=0;j<policies.length;j++){
			if('frame-ancestors' in policies[j]['directive_set']){
				if(!url_match_source_list(url, policies[j]['directive_set']['frame-ancestors'], origin, redirect_count))
					return false;
			}
		}
	}
	return true;
} 

