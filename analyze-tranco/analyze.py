import mariadb
import json


# [total count, duplicated header count, duplicated directives count one header, dupl dir merged header names]
# csp only frame-ancestors
global_headers = {
        'x-frame-options': [0,0,0,0],
        'strict-transport-security': [0,0,0,0],
        'content-security-policy': [0,0,0,0],
        'access-control-allow-origin': [0,0,0,0],
        'access-control-allow-credentials': [0,0,0,0],
        'access-control-allow-headers': [0,0,0,0],
        'access-control-allow-methods': [0,0,0,0],
        'access-control-expose-headers': [0,0,0,0],
        }

# headers are in this list, when their directives are separated via semicolon
semicolon_separated_headers = [
        'strict-transport-security',
        'content-security-policy',
        ]

# Format: [{"domain":"google.de","rank":1, "dupl_head":["X-FRAME-OPTIONS"],
# "dup_dir_single_head":[], "dup_dir_merged_head":[]}]
output = {
        "domain": None, 
        "rank": None,
        "dupl_header": [],
        "dupl_dir_single_head": [],
        "dupl_dir_merged_head": [],
        }


# specific rules for every header on how duplicate directives are count
def xfo_rules(directives):
    # pre parse allow-from, normalize it
    for i, directive in enumerate(directives):
        if "allow-from" in directive:
            directives[i] = 'allow-from'
    # for now just add easy duplicates
    if len(directives) > 1:
        return True
    return False
def hsts_rules(directives):
    # we count max-age=123 and max-age=456 as duplicates
    for i, directive in enumerate(directives):
        if "max-age" in directive:
            directives[i] = "max-age"
    # we dont cover invalid directives
    # if not "max-age" in directive:
    #     return True
    if len(directives) != len(set(directives)):
        return True
    return False
def csp_rules(directives):
    # check if directives are duplicated
    for i, directive in enumerate(directives):
        directives[i] = directive.split(' ')[0]
    if len(directives) != len(set(directives)):
        return True
    return False
def acao_rules(directives):
    if len(directives) > 1:
        return True
    return False
def acac_rules(directives):
    if len(directives) > 1:
        return True
    return False
def acah_rules(directives):
    if '*' in directives and len(directives) > 1:
        return True
    if len(directives) != len(set(directives)):
        return True
    return False
def acam_rules(directives):
    if '*' in directives and len(directives) > 1:
        return True
    if len(directives) != len(set(directives)):
        return True
    return False
def aceh_rules(directives):
    if '*' in directives and len(directives) > 1:
        return True
    if len(directives) != len(set(directives)):
        return True
    return False
    
# directive rules can be defined for every header on how duplicates are count
duplicated_directive_rules = {
    'x-frame-options' : xfo_rules,
    'strict-transport-security' : hsts_rules,
    'content-security-policy' : csp_rules,
    'access-control-allow-origin' : acao_rules,
    'access-control-allow-credentials' : acac_rules,
    'access-control-allow-headers' : acah_rules,
    'access-control-allow-methods' : acam_rules,
    'access-control-expose-headers' : aceh_rules,
    }

# input:    "header: xy"
# output:   "header"
def get_header_name(header):
    return header.split(':')[0].strip().lower()

# input:    "header: X,Y" or "header: X;Y"
# output:   ["X", "Y"]
def get_directives(header):
    directives = []
    hname = get_header_name(header)
    if hname in semicolon_separated_headers:
        directives = get_directives_semicolon(header)
    else:
        directives = get_directives_comma(header)
    return directives
def get_directives_comma(header):
    directives = header.split(':')[1].strip().lower().split(',')
    return [item.strip() for item in directives if item]
def get_directives_semicolon(header):
    directives = header.split(':')[1].strip().lower().split(';')
    return [item.strip() for item in directives if item]

# input:    ["header: XY, XY", "header2: X", "header: XY"]
# output:   -
def duplicated_directives_one(headers):
    for header in headers:
        hname = get_header_name(header)
        directives = get_directives(header)
        # special rules for every header
        if duplicated_directive_rules[hname](directives):
            global_headers[hname][2] += 1
            if hname not in output['dupl_dir_single_head']:
                output['dupl_dir_single_head'].append(hname)

# input:    {"header": ["XY", "XY"], "header2": ["X"], ..}
# output:   -
def duplicated_directives_merged(headers):
    for hname, directives in headers.items():
        if duplicated_directive_rules[hname](directives):
            global_headers[hname][3] += 1
            if hname not in output['dupl_dir_merged_head']:
                output['dupl_dir_merged_head'].append(hname)

# input:    [ "header: XY", "header2: Z", "header: XY" ]
# output:   { "header": [XY, XY],  "header2": [Z] }
def merge_headers(headers):
    headers_dict = {
            'x-frame-options': [],
            'strict-transport-security': [],
            'content-security-policy': [],
            'access-control-allow-origin': [],
            'access-control-allow-credentials': [],
            'access-control-allow-headers': [],
            'access-control-allow-methods': [],
            'access-control-expose-headers': [],
            }
    for header in headers:
        hname = get_header_name(header)
        if hname in headers_dict:
            headers_dict[hname].extend(get_directives(header))
    return headers_dict

# finds duplicate headers of one site
# input:    ["x-frame-options: deny", "HSTS: max-age", "ACAO: origin", "X-Frame-Options: deny" ..]
# output:   -
def duplicated_headers(headers):
    # count explicit for one site
    target_headers = {
            'x-frame-options': 0,
            'strict-transport-security': 0,
            'content-security-policy': 0,
            'access-control-allow-origin': 0,
            'access-control-allow-credentials': 0,
            'access-control-allow-headers': 0,
            'access-control-allow-methods': 0,
            'access-control-expose-headers': 0,
            }
    # go through all headers
    for header in headers:
        hname = get_header_name(header)
        # local header count +1
        target_headers[hname] += 1
    for header in target_headers:
        if target_headers[header] > 0:
            # global header count +1
            global_headers[header][0] += 1
            # if header is duplicated for one site
            if target_headers[header] > 1:
                # add global duplicate count for specific header
                global_headers[header][1] += 1
                if header not in output['dupl_head']:
                    output['dupl_head'].append(header)


# return list of relevant headers of one site
# input:    ["HTTP 301", "Header: XY", "HTTP 200", "Header: XY", ..]
# output:   ["x-frame-options: deny", "HSTS: bla", "ACAO: bums", ..]
def get_relevant_headers(data):
    valid = False
    relevant_headers = []
    headers = data.split("\r\n")
    for header in headers:
        hname = get_header_name(header)
        if valid == False and 'HTTP' in header and '200' in header:
            valid = True
        # just use HTTP 200 headers
        elif valid == True and  hname in global_headers and hname:
            # add header with directive to list for directive checks
            relevant_headers.append(header)
    return relevant_headers


def print_output(count, results):
    print(f"""
Total Scans: {count}

X-Frame-Options
Total                               {results["x-frame-options"][0]:16}{results["x-frame-options"][0]*100/count:16.2f}%
Duplicated Headers                  {results["x-frame-options"][1]:16}{results["x-frame-options"][1]*100/results["x-frame-options"][0]:16.2f}%
Conflicting Directives              {results["x-frame-options"][2]:16}{results["x-frame-options"][2]*100/results["x-frame-options"][0]:16.2f}%
Conflicting Directives (Merged)     {results["x-frame-options"][3]:16}{results["x-frame-options"][3]*100/results["x-frame-options"][0]:16.2f}%

Strict-Transport-Security
Total                               {results["strict-transport-security"][0]:16}{results["strict-transport-security"][0]*100/count:16.2f}%
Duplicated Headers                  {results["strict-transport-security"][1]:16}{results["strict-transport-security"][1]*100/results["strict-transport-security"][0]:16.2f}%
Conflicting Directives              {results["strict-transport-security"][2]:16}{results["strict-transport-security"][2]*100/results["strict-transport-security"][0]:16.2f}%
Conflicting Directives (Merged)     {results["strict-transport-security"][3]:16}{results["strict-transport-security"][3]*100/results["strict-transport-security"][0]:16.2f}%

Content-Security-Policy
Total                               {results["content-security-policy"][0]:16}{results["content-security-policy"][0]*100/count:16.2f}%
Duplicated Headers                  {results["content-security-policy"][1]:16}{results["content-security-policy"][1]*100/results["content-security-policy"][0]:16.2f}%
Conflicting Directives              {results["content-security-policy"][2]:16}{results["content-security-policy"][2]*100/results["content-security-policy"][0]:16.2f}%
Conflicting Directives (Merged)     {results["content-security-policy"][3]:16}{results["content-security-policy"][3]*100/results["content-security-policy"][0]:16.2f}%

Access-Control-Allow-Origin
Total                               {results["access-control-allow-origin"][0]:16}{results["access-control-allow-origin"][0]*100/count:16.2f}%
Duplicated Headers                  {results["access-control-allow-origin"][1]:16}{results["access-control-allow-origin"][1]*100/results["access-control-allow-origin"][0]:16.2f}%
Conflicting Directives              {results["access-control-allow-origin"][2]:16}{results["access-control-allow-origin"][2]*100/results["access-control-allow-origin"][0]:16.2f}%
Conflicting Directives (Merged)     {results["access-control-allow-origin"][3]:16}{results["access-control-allow-origin"][3]*100/results["access-control-allow-origin"][0]:16.2f}%

Access-Control-Allow-Credentials
Total                               {results["access-control-allow-credentials"][0]:16}{results["access-control-allow-credentials"][0]*100/count:16.2f}%
Duplicated Headers                  {results["access-control-allow-credentials"][1]:16}{results["access-control-allow-credentials"][1]*100/results["access-control-allow-credentials"][0]:16.2f}%
Conflicting Directives              {results["access-control-allow-credentials"][2]:16}{results["access-control-allow-credentials"][2]*100/results["access-control-allow-credentials"][0]:16.2f}%
Conflicting Directives (Merged)     {results["access-control-allow-credentials"][3]:16}{results["access-control-allow-credentials"][3]*100/results["access-control-allow-credentials"][0]:16.2f}%

Access-Control-Allow-Headers
Total                               {results["access-control-allow-headers"][0]:16}{results["access-control-allow-headers"][0]*100/count:16.2f}%
Duplicated Headers                  {results["access-control-allow-headers"][1]:16}{results["access-control-allow-headers"][1]*100/results["access-control-allow-headers"][0]:16.2f}%
Conflicting Directives              {results["access-control-allow-headers"][2]:16}{results["access-control-allow-headers"][2]*100/results["access-control-allow-headers"][0]:16.2f}%
Conflicting Directives (Merged)     {results["access-control-allow-headers"][3]:16}{results["access-control-allow-headers"][3]*100/results["access-control-allow-headers"][0]:16.2f}%

Access-Control-Allow-Methods
Total                               {results["access-control-allow-methods"][0]:16}{results["access-control-allow-methods"][0]*100/count:16.2f}%
Duplicated Headers                  {results["access-control-allow-methods"][1]:16}{results["access-control-allow-methods"][1]*100/results["access-control-allow-methods"][0]:16.2f}%
Conflicting Directives              {results["access-control-allow-methods"][2]:16}{results["access-control-allow-methods"][2]*100/results["access-control-allow-methods"][0]:16.2f}%
Conflicting Directives (Merged)     {results["access-control-allow-methods"][3]:16}{results["access-control-allow-methods"][3]*100/results["access-control-allow-methods"][0]:16.2f}%

Access-Control-Expose-Headers
Total                               {results["access-control-expose-headers"][0]:16}{results["access-control-expose-headers"][0]*100/count:16.2f}%
Duplicated Headers                  {results["access-control-expose-headers"][1]:16}{results["access-control-expose-headers"][1]*100/results["access-control-expose-headers"][0]:16.2f}%
Conflicting Directives              {results["access-control-expose-headers"][2]:16}{results["access-control-expose-headers"][2]*100/results["access-control-expose-headers"][0]:16.2f}%
Conflicting Directives (Merged)     {results["access-control-expose-headers"][3]:16}{results["access-control-expose-headers"][3]*100/results["access-control-expose-headers"][0]:16.2f}%
    """)

def prepare_output(rank, hostname):
    output['rank'] = rank
    output['domain'] = hostname
    output['dupl_head'] = []
    output['dupl_dir_single_head'] = []
    output['dupl_dir_merged_head'] = []


def analyze(data):
    # parse data
    # check duplicated headers
        # get header part with status 200
        # parse headers
    relevant_headers = get_relevant_headers(data)
    duplicated_headers(relevant_headers)
    # check duplicate directives for each header
    duplicated_directives_one(relevant_headers)
    # merge duplicate headers now and check duplicate directives
    mheaders = merge_headers(relevant_headers)
    duplicated_directives_merged(mheaders)
    # check for mistaken headers (martins task)
    # check for errors in directives
    # save results in file

# connect to db and fetch rows
alt_host = '127.0.0.1'
host = 'db'
conn = mariadb.connect(user='root', password='lightinthehead', database='crawler', host=alt_host)
cur = conn.cursor()

# get number of result entries to fetch it in chunks
cur.execute("SELECT count(*) from results")
count = cur.fetchone()[0]
print(f"Number of entries {count}")
chunk_size = 100000

f = open('output.json', 'w')
f.write('[\n')

# check code first
#count = 1000
#chunk_size = 1000
for offset in range(0, count, chunk_size):
    cur.execute("SELECT rank, hostname, raw from results limit %s offset %s", (chunk_size, offset))
    for row in cur:
        prepare_output(row[0], row[1])
        analyze(row[2])
        f.write('\t')
        f.write(json.dumps(output))
        f.write(',\n')

print_output(count, global_headers)
print(global_headers)
conn.close()

f.seek(f.tell() -2, 0)
f.write('\n]\n')
f.close()
