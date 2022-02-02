<?php
header("Access-Control-Allow-Origin: *");
// -----------------------------------------------------------
// A lot of headers huh
require_once('../handle.php');

class HSTS extends Handle {
	public function set_headers(){
		if(isset($_GET['setHSTS'])){
			$this->b64_to_header($_GET['pair'], $this->$headers);
		}
	}
}



$HSTS = new HSTS();
$HSTS->$headers = array('strict-transport-security');
$HSTS->handle_request();
?>
