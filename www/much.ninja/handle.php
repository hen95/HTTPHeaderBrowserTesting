<?php
header('Cache-Control: no-store');
define('BASE_PATH', realpath(dirname(__FILE__)));
require_once(BASE_PATH . '/db.php');
class Handle
{
	public $headers;

	// -----------------------------------------------------------
	// Takes the GET['pair'] which is a base64 encoded
	// combination of header: directives\r\nheader: directives etc.
	// and puts it in the right format to set these headers.
	// Set the allowed headers immediately.
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
			if(in_array(strtolower($header), $allowed_headers))
				header($header . ": " . $directives, False);
		}
	}

	// -----------------------------------------------------------
	public function set_headers(){
		$this->b64_to_header($_GET['pair'], $this->$headers);
	}

	public function save_to_db($data){
		global $dbh;
		if(!$this->get_result($data['category'],$data['browser'],$data['engine'],$data['os']))
			$query = $dbh->prepare("INSERT INTO results (browser, engine, os, result, category) VALUES (:browser, :engine, :os, :result, :category)");
		else
			$query = $dbh->prepare("UPDATE results SET result=:result WHERE browser=:browser and category=:category and engine=:engine and os=:os");
		$query->bindParam(":browser", $data['browser']);
		$query->bindParam(":engine", $data['engine']);
		$query->bindParam(":os", $data['os']);
		$query->bindParam(":result", json_encode($data['result']));
		$query->bindParam(":category", $data['category']);
		if(!$query->execute())
			http_response_code(500);
	}

	public function handle_post(){
		$data = json_decode(file_get_contents('php://input'), true);
		if(isset($data['delete']) && isset($data['id']))
			$this->delete_result($data['id']);
		if(isset($data['delete']) && isset($data['browser']))
			$this->delete_result(null, $data['browser']);
		if(isset($data['save']) && isset($data['browser']) && isset($data['category']) && isset($data['result']))
			$this->save_to_db($data);


	}

	public function get_result($category, $browser, $engine, $os){
		global $dbh;
		$query = $dbh->prepare('SELECT * from results WHERE browser=:browser and category=:category and engine=:engine and os=:os');
		$query->bindValue(':browser', $browser);
		$query->bindValue(':engine', $engine);
		$query->bindValue(':os', $os);
		$query->bindValue(':category', $category);
		$query->execute();
		return $query->fetch(PDO::FETCH_ASSOC);
	}	

	public function get_all_results($category = null, $browser = null, $engine = null, $os = null){
		global $dbh;
		if(isset($category)){
			$query = $dbh->prepare('SELECT * from results WHERE category=:category');
			$query->bindValue(':category', $category);
			$query->execute();
		}else{
			$query = $dbh->prepare('SELECT * from results;');
			$query->execute();
		}
		return $query->fetchAll(PDO::FETCH_ASSOC);
	}
	
	public function render_result($category = null, $browser = null, $engine = null, $os = null){
		// Show specific saved result for test suite and browser
		if(isset($category) && isset($browser)){
			$result = $this->get_result($category, $browser, $engine, $os);
			if(!$result){
				exit(1);
			}else $result['result'] = json_decode($result['result'], true);
			require_once(BASE_PATH . '/static/result.html');
		// Show all browsers who have saved results
		}else if(isset($category)){
			$results = $this->get_all_results($category);
			require_once(BASE_PATH . '/static/results.html');
		}
		exit(0);
	}

	public function delete_result($id = null, $browser = null){
		global $dbh;
		if(isset($id)){
			$query = $dbh->prepare('DELETE FROM results WHERE id=:id');
			$query->bindValue(':id', $id);
		}
		if(isset($browser)){
			$query = $dbh->prepare('DELETE FROM results WHERE browser=:browser');
			$query->bindValue(':browser', $browser);
		}
		if(!$query->execute())
			http_response_code(500);
	}

	// -----------------------------------------------------------
	public function handle_request(){
		$method = $_SERVER['REQUEST_METHOD'];
		switch ($method) {
			case 'GET':
				$this->handle_get();
				break;
			case 'OPTIONS':
				$this->handle_options();
				break;
			case 'PUT':
				http_response_code(404);
				break;
			case 'POST':
				$this->handle_post();
				break;
			case 'DELETE':
				http_response_code(404);
				break;
			default:
				exit("HTTP method not supported yet");
				break;
		}
	}

	// -----------------------------------------------------------
	public function handle_get(){
		// Checking if directives are passed.
		if(!isset($_GET['pair']) && !isset($_GET['show']))
			exit("No parameters passed");
		// Catch Base64 decode errors
		if(isset($_GET['pair'])){
			if(!base64_decode($_GET['pair']))
				exit("Can't Base64 decode the headers:directives");
			$this->set_headers();
			$this->response();
			}
		if(isset($_GET['show']) && isset($_GET['browser']))
			$this->render_result($_GET['show'], $_GET['browser'], $_GET['engine'], $_GET['os']);
		if(isset($_GET['show']))
			$this->render_result($_GET['show']);
		}

	// -----------------------------------------------------------
	public function response(){
		require_once(BASE_PATH . "/responseFrame/iframes.html");
		exit(0);
	}
	// -----------------------------------------------------------
	// to handle cors preflight
	public function handle_options(){
		header('Vary: Origin');
	    header("Access-Control-Max-Age: 0");
		$origin = array_key_exists("Origin", getallheaders()) ? (getallheaders()['Origin']) : "";
		$pattern = "/^https?:\/\/(?:sub\.)?much.ninja$/";
		if(!preg_match($pattern, $origin))
			exit(1);
	    if(array_key_exists("Access-Control-Request-Headers", getallheaders()))
	        header("Access-Control-Allow-Headers: " . getallheaders()["Access-Control-Request-Headers"]);
	    if(array_key_exists("Access-Control-Request-Method", getallheaders()))
	        header("Access-Control-Allow-Methods: " . getallheaders()["Access-Control-Request-Method"]);
	    header("Access-Control-Allow-Credentials: true");
	    // Reflect Origin.
	    header("Access-Control-Allow-Origin:" . $origin);
	    exit(0);
	}
}
?>
