#!/usr/bin/python3

import base64
import urllib.parse
import json


XFO = [
	# basic headers
	['X-Frame-Options: deny'],
	['X-Frame-Options: sameorigin'],
	['X-Frame-Options: allowall'],
	['X-Frame-Options: allow-from http://much.ninja'],
	['X-Frame-Options: allow-from https://much.ninja'],
	['X-Frame-Options: allow-from http://random.ninja'],
	['X-Frame-Options: RANDOMDIRECTIVE'],
	# duplicated headers 
	['X-Frame-Options: deny', 'X-Frame-Options: deny'],
	['X-Frame-Options: sameorigin', 'X-Frame-Options: sameorigin'],
	['X-Frame-Options: allowall', 'X-Frame-Options: allowall'],
	['X-Frame-Options: allowall', 'X-Frame-Options: RANDOMDIRECTIVE'],
	['X-Frame-Options: allow-from TESTURI', 'X-Frame-Options: RANDOMDIRECTIVE'],
	['X-Frame-Options: allowall', 'X-Frame-Options: sameorigin'],
	['X-Frame-Options: allow-from TESTURI', 'X-Frame-Options: allowall'],
	['X-Frame-Options: allowall', 'X-Frame-Options: allow-from TESTURI'],
	['X-Frame-Options: allow-from http://randomorigin.com/', 'X-Frame-Options: allow-from http://randomorigin.com/'],
	['X-Frame-Options: allow-from http://randomorigin.com/', 'X-Frame-Options: allow-from TESTURI'],
	['X-Frame-Options: allow-from TESTURI', 'X-Frame-Options: allow-from http://randomorigin.com/'],
	['X-Frame-Options: deny', 'X-Frame-Options: sameorigin'],
	['X-Frame-Options: sameorigin', 'X-Frame-Options: deny'],
	['X-Frame-Options: deny', 'X-Frame-Options: allow-from TESTURI'],
	['X-Frame-Options: allow-from TESTURI', 'X-Frame-Options: deny'],
	['X-Frame-Options: sameorigin', 'X-Frame-Options: allow-from http://randomorigin.com/'],
	['X-Frame-Options: allow-from http://randomorigin.com/', 'X-Frame-Options: sameorigin'],
	# duplicated directives
	['X-Frame-Options: deny, deny'],
	['X-Frame-Options: sameorigin, sameorigin'],
	['X-Frame-Options: allow-from http://randomorigin.com/, allow-from http://randomorigin.com/'],
	['X-Frame-Options: allow-from http://randomorigin.com/, allow-from TESTURI'],
	['X-Frame-Options: allow-from TESTURI, allow-from http://randomorigin.com/'],
	['X-Frame-Options: deny, sameorigin'],
	['X-Frame-Options: allow-from http://randomorigin.com/, deny'],
	['X-Frame-Options: sameorigin, deny'],
	['X-Frame-Options: deny, allow-from TESTURI'],
	['X-Frame-Options: allow-from TESTURI, deny'],
	['X-Frame-Options: sameorigin, allow-from http://randomorigin.com'],
	['X-Frame-Options: allow-from http://randomorigin.com, sameorigin'],
	# semi colon instead of comma, Daniel Hartl shortend this cases. Dunno why.
	['X-Frame-Options: deny; deny'],
	['X-Frame-Options: sameorigin; sameorigin'],
	['X-Frame-Options: allow-from http://randomorigin.com/; allow-from http://randomorigin.com/'],
	['X-Frame-Options: allow-from TESTURI; allow-from http://randomorigin.com/'],
	['X-Frame-Options: deny; sameorigin'],
	['X-Frame-Options: sameorigin; deny'],
	['X-Frame-Options: deny; allow-from TESTURI'],
	['X-Frame-Options: allow-from TESTURI; deny']
]

HSTS = [
    # basic headers
    ['Strict-Transport-Security: max-age=60'],
    ['Strict-Transport-Security: max-age=60; includeSubDomains'],
    ['Strict-Transport-Security: max-age=60; includeSubDomains; preload'],
    # duplicated headers
    ['Strict-Transport-Security: max-age=60', 'Strict-Transport-Security: max-age=60'],
    ['Strict-Transport-Security: max-age=60', 'Strict-Transport-Security: max-age=120'],
    ['Strict-Transport-Security: max-age=60', 'Strict-Transport-Security: max-age=0'],
    ['Strict-Transport-Security: max-age=0', 'Strict-Transport-Security: max-age=60'],
    ['Strict-Transport-Security: max-age=60; includeSubDomains', 'Strict-Transport-Security: max-age=60; includeSubDomains'],
    ['Strict-Transport-Security: max-age=60', 'Strict-Transport-Security: max-age=60; includeSubDomains'],
    ['Strict-Transport-Security: max-age=60; includeSubDomains', 'Strict-Transport-Security: max-age=60'],
    ['Strict-Transport-Security: max-age=60', 'Strict-Transport-Security: includeSubDomains'],
    ['Strict-Transport-Security: includeSubDomains', 'Strict-Transport-Security: max-age=60'],
    ['Strict-Transport-Security: max-age=60; preload', 'Strict-Transport-Security: max-age=60; preload'],
    ['Strict-Transport-Security: preload', 'Strict-Transport-Security: max-age=60'],
    ['Strict-Transport-Security: max-age=60', 'Strict-Transport-Security: preload'],
    ['Strict-Transport-Security: max-age=60; includeSubDomains; preload', 'Strict-Transport-Security: max-age=60; includeSubDomains; preload'],
    # duplicated directives
    ['Strict-Transport-Security: max-age=60; max-age=60'],
    ['Strict-Transport-Security: max-age=60; max-age=120'],
    ['Strict-Transport-Security: max-age=0; max-age=60'],
    ['Strict-Transport-Security: max-age=60; max-age=0'],
    ['Strict-Transport-Security: max-age=60; includeSubDomains; includeSubDomains'],
    ['Strict-Transport-Security: max-age=60; preload; preload'],
    ['Strict-Transport-Security: max-age=60; someDirective; someDirective'],
    # duplicated directives with lists
    ['Strict-Transport-Security: max-age=60; includeSubDomains, max-age=60; includeSubDomains'],
    ['Strict-Transport-Security: max-age=60; preload, max-age=60; preload'],
    ['Strict-Transport-Security: max-age=60; someDirective, max-age=60; someDirective'],
    ['Strict-Transport-Security: max-age=60; ,'],
    ['Strict-Transport-Security: max-age=60, includeSubdomains'],
    ['Strict-Transport-Security: random, includeSubdomains; max-age=60; includeSubdomains'],
    ['Strict-Transport-Security: max-age=60, max-age=60'],
    ['Strict-Transport-Security: max-age=60, max-age=120'],
    ['Strict-Transport-Security: max-age=0, max-age=60'],
    ['Strict-Transport-Security: max-age=60, max-age=0'],
    ['Strict-Transport-Security: max-age=60, x; max-age=60; includeSubdomains'],
    ['Strict-Transport-Security: x, max-age=60; max-age=60; includeSubdomains'],
    ['Strict-Transport-Security: max-age=60,; includeSubdomains'],
    ['Strict-Transport-Security: max-age=60, max-age=60; max-age=60; includeSubdomains'],
    ['Strict-Transport-Security: max-age=60, includeSubdomains; max-age=60; includeSubdomains'],
    ['Strict-Transport-Security: max-age=60; includeSubdomains; max-age=60, includeSubdomains'],
    ['Strict-Transport-Security: max-age=60; includeSubdomains, max-age=60'],
    ['Strict-Transport-Security: max-age=60; max-age=60, includeSubdomains'],
]


csp_fa = [
	# basic headers
	['Content-Security-Policy: frame-ancestors much.ninja;'],
	['Content-Security-Policy: frame-ancestors http://*.ninja http://randomorigin.com;'],
	['Content-Security-Policy: frame-ancestors *.ninja;'],
	['Content-Security-Policy: frame-ancestors http:;'],
	['Content-Security-Policy: frame-ancestors https:;'],
	["Content-Security-Policy: frame-ancestors 'self';"],
	["Content-Security-Policy: frame-ancestors 'none';"],
	# duplicated headers
	['Content-Security-Policy: frame-ancestors http://much.ninja;', 'Content-Security-Policy: frame-ancestors http://randomorigin.com;'],
	['Content-Security-Policy: frame-ancestors http://randomorigin.com;', 'Content-Security-Policy: frame-ancestors http://much.ninja;'],

	["Content-Security-Policy: frame-ancestors http://much.ninja;", "Content-Security-Policy: frame-ancestors 'none';"],
	["Content-Security-Policy: frame-ancestors 'none';", "Content-Security-Policy: frame-ancestors http://much.ninja;"],

	["Content-Security-Policy: frame-ancestors http://randomorigin.com;", "Content-Security-Policy: frame-ancestors 'self';"],
	["Content-Security-Policy: frame-ancestors 'self';", "Content-Security-Policy: frame-ancestors http://randomorigin.com;"],

	["Content-Security-Policy: frame-ancestors 'self';", "Content-Security-Policy: frame-ancestors 'none';"],
	["Content-Security-Policy: frame-ancestors 'none';", "Content-Security-Policy: frame-ancestors 'self';"],

	["Content-Security-Policy: frame-ancestors 'self';", "Content-Security-Policy: frame-ancestors 'self';"],
	["Content-Security-Policy: frame-ancestors 'none';", "Content-Security-Policy: frame-ancestors 'none';"],
	# duplicated directives
	["Content-Security-Policy: frame-ancestors http://randomorigin.com 'self';"],
	["Content-Security-Policy: frame-ancestors 'self' http://randomorigin.com;"],

	["Content-Security-Policy: frame-ancestors http://much.ninja 'none';"],
	["Content-Security-Policy: frame-ancestors 'none' http://much.ninja;"],

	["Content-Security-Policy: frame-ancestors 'none' 'self';"],
	["Content-Security-Policy: frame-ancestors 'self' 'none';"],

	["Content-Security-Policy: frame-ancestors 'self' 'self';"],
	["Content-Security-Policy: frame-ancestors 'none' 'none';"],
	# weird delimiter
	["Content-Security-Policy: frame-ancestors http://much.ninja, http://randomorigin.com;"],
	["Content-Security-Policy: frame-ancestors http://randomorigin.com, http://much.ninja;"],
	["Content-Security-Policy: frame-ancestors 'self', 'none';"],
	["Content-Security-Policy: frame-ancestors 'none', 'self';"],

	["Content-Security-Policy: frame-ancestors http://much.ninja; http://randomorigin.com;"],
	["Content-Security-Policy: frame-ancestors http://randomorigin.com; http://much.ninja;"],
	["Content-Security-Policy: frame-ancestors 'self'; 'none';"],
	["Content-Security-Policy: frame-ancestors 'none'; 'self';"],

	["Content-Security-Policy: frame-ancestors http://much.ninja, frame-ancestors http://randomorigin.com;"],
	["Content-Security-Policy: frame-ancestors http://randomorigin.com, frame-ancestors http://much.ninja;"],
	["Content-Security-Policy: frame-ancestors 'self', frame-ancestors 'none';"],
	["Content-Security-Policy: frame-ancestors 'none', frame-ancestors 'self';"],

	["Content-Security-Policy: frame-ancestors http://much.ninja; frame-ancestors http://randomorigin.com;"],
	["Content-Security-Policy: frame-ancestors http://randomorigin.com; frame-ancestors http://much.ninja;"],
	["Content-Security-Policy: frame-ancestors 'self'; frame-ancestors 'none';"],
	["Content-Security-Policy: frame-ancestors 'none'; frame-ancestors 'self';"],
	# misspelling and weird cases
	["Content-Security-Policy: frame-ancestors random;"],
	["Content-Security-Policy: frame-ancestors 'random';"],
	["Content-Security-Policy: frame-ancestors http://much.ninja 'random';"],
	["Content-Security-Policy: frame-ancestors 'none';'"],
	["Content-Security-Policy: frame-ancestors //;"],
	["Content-Security-Policy: frame-ancestors ://;"],
	["Content-Security-Policy: frame-ancestors ;"],
	["Content-Security-Policy: frame-ancestors;"],
	["Content-Security-Policy: frame-ancestors"],
	["Content-Security-Policy: frameancestors 'self';"],

]

xfo_csp = [
	["Content-Security-Policy: frame-ancestors 'self';", 'X-Frame-Options: deny'],
	["Content-Security-Policy: frame-ancestors 'random'", 'X-Frame-Options: sameorigin'],
	["Content-Security-Policy: frame-ancestors 'none'", 'X-Frame-Options: sameorigin'],

	['X-Frame-Options: deny', "Content-Security-Policy: frame-ancestors 'self'"],
	['X-Frame-Options: sameorigin', "Content-Security-Policy: frame-ancestors 'random'"],
	['X-Frame-Options: sameorigin', "Content-Security-Policy: frame-ancestors 'none'"],

	["X-Content-Security-Policy: frame-ancestors 'self';", 'X-Frame-Options: deny'],
	['X-Frame-Options: deny',"X-Content-Security-Policy: frame-ancestors 'self';"],

	["X-WebKit-CSP: frame-ancestors 'self';", 'X-Frame-Options: deny'],
	['X-Frame-Options: deny',"X-WebKit-CSP: frame-ancestors 'self';"],
	["Content-Security-Policy: frame-ancestors 'none'; 'none'", 'X-Frame-Options: sameorigin'],
	["Content-Security-Policy: frame-ancestors;", 'X-Frame-Options: sameorigin'],
]

acao = [
	# test general stuff, what is accepted by browsers?
	["Access-Control-Allow-Origin: *"],
	["Access-Control-Allow-Origin: //"],
	["Access-Control-Allow-Origin: //much.ninja"],
	["Access-Control-Allow-Origin: ://"],
	["Access-Control-Allow-Origin: ://much.ninja"],
	["Access-Control-Allow-Origin: https://"],
	["Access-Control-Allow-Origin: null"],
	["Access-Control-Allow-Origin: "],
	# test protocol, what is accepted by browsers?
	["Access-Control-Allow-Origin: https://much.ninja"],
	["Access-Control-Allow-Origin: http://much.ninja"],
	# test undercase acao header
	["access-control-allow-origin: https://random.ninja"],
	["access-control-allow-origin: https://much.ninja"],
	# test duplicated acao headers
	["Access-Control-Allow-Origin: https://random.ninja", "Access-Control-Allow-Origin: https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Origin: https://random.ninja"],
	# only exploitable misconfiguration
	["access-control-allow-origin: *", "Access-Control-Allow-Origin: https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja", "access-control-allow-origin: *"],

	# test duplicated acao headers with wildcard
	["Access-Control-Allow-Origin: *", "Access-Control-Allow-Origin: https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Origin: *"],
	# test duplicated acao headers with special case null 
	["Access-Control-Allow-Origin: null", "Access-Control-Allow-Origin: https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Origin: null"],
	# test duplicated acao directives with [wildcard, domain, null]
	["Access-Control-Allow-Origin: *, https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja, *"],
	["Access-Control-Allow-Origin: https://random.ninja, https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja, https://random.ninja"],
	["Access-Control-Allow-Origin: null, https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja, null"],
	# test special cases, what is accepted by browsers?
	# [(duplicated headers, empty acao), (duplicated directives no whitespace), (different delimiter, semicolon)]
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Origin: "],
	["Access-Control-Allow-Origin: ", "Access-Control-Allow-Origin: https://much.ninja"],
	["Access-Control-Allow-Origin: https://random.ninja,https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja,https://random.ninja"],
	["Access-Control-Allow-Origin: https://random.ninja; https://much.ninja"],
	["Access-Control-Allow-Origin: https://much.ninja; https://random.ninja"],
]

# ACAO has also to be set to make it work
acac = [
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: true"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: True"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: "],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: *"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: true", "Access-Control-Allow-Credentials: true"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: true", "Access-Control-Allow-Credentials: false"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: false", "Access-Control-Allow-Credentials: true"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: true, true"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: true, false"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: false, true"],
	["Access-Control-Allow-Origin: https://much.ninja", "Access-Control-Allow-Credentials: true;"],
]

acah = [
	# duplicate headers
	[["Access-Control-Allow-Headers: Test", "Access-Control-Allow-Headers: Test"], ["Access-Control-Request-Headers: Test"]],
	[["Access-Control-Allow-Headers: Test", "Access-Control-Allow-Headers: Test2"], ["Access-Control-Request-Headers: Test, Test2"]],
	[["Access-Control-Allow-Headers: Test2", "Access-Control-Allow-Headers: Test"], ["Access-Control-Request-Headers: Test, Test2"]],
	[["Access-Control-Allow-Headers: *", "Access-Control-Allow-Headers: Test"], ["Access-Control-Request-Headers: Test, Random-Header"]],
	[["Access-Control-Allow-Headers: Test", "Access-Control-Allow-Headers: *"], ["Access-Control-Request-Headers: Test, Random-Header"]],
	# duplicate directives
	[["Access-Control-Allow-Headers: Test, Test2", "Access-Control-Allow-Headers: *"], ["Access-Control-Request-Headers: Test, Test2, Random-Header"]],
	[["Access-Control-Allow-Headers: *", "Access-Control-Allow-Headers: Test, Test2"], ["Access-Control-Request-Headers: Test, Test2, Random-Header"]],
	# special stuff
	[["Access-Control-Allow-Headers: Test; Test2"], ["Access-Control-Request-Headers: Test, Test2"]],
	[["Access-Control-Allow-Headers: Test Test2"], ["Access-Control-Request-Headers: Test, Test2"]],
	[["Access-Control-Allow-Headers: ;"], ["Access-Control-Request-Headers: Test"]],
	[["Access-Control-Allow-Headers: "], ["Access-Control-Request-Headers: Test"]],
]


acam = [
	[["Access-Control-Allow-Methods: "], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: *"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: GET"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE", "Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: GET", "Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE", "Access-Control-Allow-Methods: GET"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: *", "Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE", "Access-Control-Allow-Methods: *"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: RANDOM, GET", "Access-Control-Allow-Methods: RANDOM, DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: RANDOM, DELETE", "Access-Control-Allow-Methods: RANDOM, GET"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE, DELETE", "Access-Control-Allow-Methods: GET, GET"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: GET", "Access-Control-Allow-Methods: PUT"], ["Access-Control-Request-Method: DELETE"]],
	[["NOT-Access-Control-Allow-Methods"], ["Access-Control-Request-Method: DELETE"]],

	[["Access-Control-Allow-Methods: "], ["Access-Control-Request-Method: PUT"]],
	[["Access-Control-Allow-Methods: PUT"], ["Access-Control-Request-Method: PUT"]],
	[["Access-Control-Allow-Methods: *"], ["Access-Control-Request-Method: PUT"]],
	[["Access-Control-Allow-Methods: *", "Access-Control-Allow-Methods: PUT"], ["Access-Control-Request-Method: PUT"]],
	[["Access-Control-Allow-Methods: PUT", "Access-Control-Allow-Methods: *"], ["Access-Control-Request-Method: PUT"]],
	[["Access-Control-Allow-Methods: PUT, PUT"], ["Access-Control-Request-Method: PUT"]],
	[["NOT-Access-Control-Allow-Methods"], ["Access-Control-Request-Method: PUT"]],

	[["Access-Control-Allow-Methods: "], ["Access-Control-Request-Method: GET"]],
	[["Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: GET"]],
	[["NOT-Access-Control-Allow-Methods"], ["Access-Control-Request-Method: GET"]],

	[["Access-Control-Allow-Methods: "], ["Access-Control-Request-Method: POST"]],
	[["Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: POST"]],
	[["NOT-Access-Control-Allow-Methods"], ["Access-Control-Request-Method: POST"]],

	[["Access-Control-Allow-Methods: "], ["Access-Control-Request-Method: HEAD"]],
	[["Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: HEAD"]],
	[["NOT-Access-Control-Allow-Methods"], ["Access-Control-Request-Method: HEAD"]],

	[["Access-Control-Allow-Methods: DELETE,DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE; DELETE", "Access-Control-Allow-Methods: GET, GET"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: GET, GET", "Access-Control-Allow-Methods: DELETE; DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE; DELETE", "Access-Control-Allow-Methods: *"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE? DELETE, DELETE", "Access-Control-Allow-Methods: GET"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: DELETE? DELETE", "Access-Control-Allow-Methods: DELETE"], ["Access-Control-Request-Method: DELETE"]],
	[["Access-Control-Allow-Methods: GET? GET", "Access-Control-Allow-Methods: GET"], ["Access-Control-Request-Method: DELETE"]],
]

aceh = [
	[["Access-Control-Expose-Headers: Test"]],
	[["Access-Control-Expose-Headers: Test", "Access-Control-Expose-Headers: Test"]],
	[["Access-Control-Expose-Headers: Test", "Access-Control-Expose-Headers: Test2"]],
	[["Access-Control-Expose-Headers: Test2", "Access-Control-Expose-Headers: Test"]],
	[["Access-Control-Expose-Headers: *", "Access-Control-Expose-Headers: Test"]],
	[["Access-Control-Expose-Headers: Test", "Access-Control-Expose-Headers: *"]],
	[["Access-Control-Expose-Headers: Test, Test"]],
	[["Access-Control-Expose-Headers: Test2, Test"]],
	[["Access-Control-Expose-Headers: Test, Test2"]],
	[["Access-Control-Expose-Headers: *, Test"]],
	[["Access-Control-Expose-Headers: Test, *"]],
	[["Access-Control-Expose-Headers: ;"]],
	[["Access-Control-Expose-Headers: Test; *"]],
]

testcases = [XFO]

result = []
testuri_xfo = "https://much.ninja/"
for testsuite in testcases:
	for testcase in testsuite:
            if "X-Frame-Options" in testcase[0]:
                encoded = urllib.parse.quote(base64.b64encode('\\r\\n'.join(testcase).replace("TESTURI", testuri_xfo).encode('ascii')).decode('ascii'))
                result.append([testcase, encoded])
            elif type(testcase[0]) is list and ("Access-Control-Allow-Headers" in testcase[0][0] or "Access-Control-Allow-Methods" in testcase[0][0] or "Access-Control-Expose-Headers" in testcase[0][0]):
                encoded = urllib.parse.quote(base64.b64encode('\\r\\n'.join(testcase[0]).encode('ascii')).decode('ascii'))
                testcase.insert(1, encoded)
                result.append(testcase)
                #result.append([testcase[0], encoded, testcase[1]])
            else:
                encoded = urllib.parse.quote(base64.b64encode('\\r\\n'.join(testcase).encode('ascii')).decode('ascii'))
                result.append([testcase, encoded])

print(json.dumps(result))
