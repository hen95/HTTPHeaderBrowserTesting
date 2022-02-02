<?php
header('Cache-Control: no-store');
define('BASE_PATH', realpath(dirname(__FILE__)));

session_start();
function logged_in(){
	return isset($_SESSION['logged_in']);
}
function logout(){
	session_destroy();
	die("Logged out");
}
function login(){
	if(empty($_GET['name']) || !isset($_GET['login']))
		return false;
	$_SESSION['logged_in'] = 1;
	$_SESSION['user'] = strval($_GET['name']);
	$_SESSION['users'] = array(
		strval($_GET['name']) => 1000,
		"Oscar" => 1000,
	);
	$_SESSION['transactions'] = array();
	return true;
}



class Handle
{
	public function CSRF_PROTECC(){
		$origin = array_key_exists("Origin", getallheaders()) ? (getallheaders()['Origin']) : false;
		if(!$origin)
			return True;
		// If the Origin header is present, then its normally a cross origin request
		$own_origin = "/^https?:\/\/c00kie.ninja$/";
		if(preg_match($own_origin , $origin))
			return True;
		// Check for X-CSRF-Token header
		$csrf_protecc = array_key_exists("X-Csrf-Token", getallheaders());
		if($csrf_protecc)
			return True;
		var_dump(getallheaders());
		// Forbidden!
		http_response_code(403);
		die("Access Denied!");
	}

	public function handle_post(){
		if(!logged_in())
			die("Not logged in!");
		//$data = json_decode(file_get_contents('php://input'), true);
		//var_dump($_POST);
		if(isset($_POST['send']) && isset($_POST['from']) && isset($_POST['to']) && isset($_POST['amount'])){
			$name1 = $_POST['from'];
			$name2 = $_POST['to'];
			$amount = intval($_POST['amount']);
			$_SESSION['users'][$name1] -= $amount;
			$_SESSION['users'][$name2] += $amount;
			$transaction = "$amount: From $name1 To $name2";
			if($_SESSION['user'] === $name1 || $_SESSION['user'] === $name2)
				array_push($_SESSION['transactions'], $transaction);
		}
		$this->response();
	}
	// -----------------------------------------------------------
	public function handle_request(){
		$method = $_SERVER['REQUEST_METHOD'];
		switch ($method) {
			case 'GET':
				$this->CSRF_PROTECC();
				$this->handle_get();
				break;
			case 'OPTIONS':
				$this->handle_options();
				break;
			case 'PUT':
				http_response_code(404);
				break;
			case 'POST':
				$this->CSRF_PROTECC();
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
		if(!logged_in()){
			if(!empty($_GET['name']) && isset($_GET['login'])){
				if(!login())
					die("name and login in parameter missing");
			}else{
				die("Not logged in!");
			}
		}
		if(isset($_GET['logout']))
			logout();
		$this->response();	
	}

	// -----------------------------------------------------------
	public function response(){
		if(isset($_GET['redirect']))
			$this->$redirect = str_replace('\\&"',' ',$_GET['redirect']);
		require_once(BASE_PATH . "/transfer.html");
		exit(0);
	}
	// -----------------------------------------------------------
	// to handle cors preflight
	public function handle_options(){
		header('Vary: Origin');
	    header("Access-Control-Max-Age: 0");
		// Next level origin reflection boom.
		$origin = array_key_exists("Origin", getallheaders()) ? (getallheaders()['Origin']) : "";
		$pattern = "/^https?:\/\/(?:sub\.)?much.ninja$/";
		if(!preg_match($pattern, $origin))
			exit(1);
	    header("Access-Control-Allow-Origin:" . $origin);

	    if(array_key_exists("Access-Control-Request-Headers", getallheaders()))
	        header("Access-Control-Allow-Headers: X-API-SWAG; Hello-im-under-the-water-how-are-you");
	    if(array_key_exists("Access-Control-Request-Method", getallheaders()))
	        header("Access-Control-Allow-Methods: " . getallheaders()["Access-Control-Request-Method"]);
		// Todo: Play with ACAC Header
	    header("Access-Control-Allow-Credentials: true");
	    exit(0);
	}
}
if($_SERVER['REQUEST_METHOD'] != 'OPTIONS'){
	$origin = array_key_exists("Origin", getallheaders()) ? (getallheaders()['Origin']) : "";
	header('Access-Control-Allow-Origin: ' . $origin);
	header('Access-Control-Allow-Credentials: true');
	// Let the world see what is configured!
	header('Access-Control-Expose-Headers: *');
}
$handle = new Handle();
$handle->handle_request();
?>
