<?php
// -----------------------------------------------------------
require_once('../handle.php');

class ExposeHeaders extends Handle {
	public function b64_to_header($b64, $allowed_headers){
		// Decode the $_GET['pair'] first.
		$b64_decoded = base64_decode($b64);
		// Every header: directive pair has to end with "\r\n".
		$parsed = explode("\\r\\n", $b64_decoded);
		// $parsed[] should have the format "header: directive" now.
		foreach($parsed as $pair){
			$pair_array = explode(":", $pair, 2);
			$header = $pair_array[0];
			$directives = $pair_array[1];
			if(in_array(strtolower($header), $allowed_headers)){
				header($header . ": " . $directives, False);
				if(strtolower($header) === 'access-control-expose-headers'){
					$test_headers = explode(',', $directives);
					foreach($test_headers as $h){
						if(in_array(trim(strtolower($h)), $allowed_headers))
							header(strtolower(trim($h)));
						if(trim($h) === '*')
							header('random');
					}
				}
			}
		}
	}
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
		header("test");
		header("test2");
		header("random");
		$this->b64_to_header($_GET['pair'], $this->$headers);
	}

	public function handle_options(){
		exit(1);
	}
}

$AEH = new ExposeHeaders();
$AEH->$headers = array('access-control-allow-origin', 'access-control-allow-credentials', 'access-control-expose-headers', 'test', 'test2');
$AEH->handle_request();
?>
