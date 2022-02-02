<?php
// -----------------------------------------------------------
require_once('../handle.php');

class Preflight extends Handle {
	// simple reflect all cors headers
	// if Preflight was successful, then rip
	public function set_headers(){
        header('Vary: Origin');
        $origin = array_key_exists("Origin", getallheaders()) ? (getallheaders()['Origin']) : "";
        $pattern = "/^https?:\/\/(?:sub\.)?much.ninja$/";
        if(!preg_match($pattern, $origin))
            exit(1);
        // Reflect Origin.
        header("Access-Control-Allow-Origin:" . $origin);
		// Allow everything
        header("Access-Control-Allow-Credentials: true");
	}

	public function handle_options(){
		header('Vary: Origin');
		$origin = array_key_exists("Origin", getallheaders()) ? getallheaders()['Origin'] : "";
		$acrh = array_key_exists("Access-Control-Request-Headers", getallheaders()) ? getallheaders()['Access-Control-Request-Headers'] : "";
		$acrm = array_key_exists("Access-Control-Request-Method", getallheaders()) ? getallheaders()['Access-Control-Request-Method'] : "";
		$b64_val = urldecode(explode('=', $_SERVER['QUERY_STRING'])[1]);
		if(!base64_decode($b64_val))
			exit(1);
		$base64_decoded = base64_decode($b64_val);
		if(strpos(strtolower($base64_decoded),"access-control-max-age") === false)
			header("Access-Control-Max-Age: 0");
		if(strpos(strtolower($base64_decoded),"access-control-allow-origin") === false)
			header("Access-Control-Allow-Origin: $origin");
		if(strpos(strtolower($base64_decoded),"access-control-allow-credentials") === false)
			header("Access-Control-Allow-Credentials: true");
		if(strpos(strtolower($base64_decoded),"access-control-allow-headers") === false)
			header("Access-Control-Allow-Headers: " . strtolower($acrh));

		$this->b64_to_header($b64_val, $this->$headers);
		exit(0);
	}

    public function handle_request(){
        $method = $_SERVER['REQUEST_METHOD'];
        switch ($method) {
            case 'GET':
                $this->handle_get();
                break;
            case 'OPTIONS':
                $this->handle_options();
                break;
            case 'POST':
                $this->handle_post();
				$this->set_headers();
				$this->response();
                break;
            case 'PUT':
				$this->set_headers();
				$this->response();
                break;
            case 'DELETE':
				$this->set_headers();
				$this->response();
                break;
            case 'HEAD':
				$this->set_headers();
				$this->response();
                break;
            default:
                exit("HTTP method not supported yet");
                break;
        }
    }

}

$CORS = new Preflight();
$CORS->$headers = array('access-control-allow-origin', 'access-control-allow-credentials', 'access-control-allow-headers' , 'access-control-allow-methods', 'access-control-max-age');
$CORS->handle_request();
?>
