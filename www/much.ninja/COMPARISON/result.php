<?php
// -----------------------------------------------------------
// A lot of headers huh
require_once('../handle.php');

class Result extends Handle {
	public function get_all_results($category = null, $browser = null, $engine = null, $os = null){
		global $dbh;
		if(isset($browser)){
			$query = $dbh->prepare('SELECT DISTINCT browser from results ORDER BY browser');
			$query->execute();
		}else if(isset($os)){
			$query = $dbh->prepare('SELECT DISTINCT os from results ORDER BY os');
			$query->execute();
		}else if(isset($category)){
			$query = $dbh->prepare('SELECT DISTINCT category from results ORDER BY category');
			$query->execute();
		}else{
			$query = $dbh->prepare('SELECT * from results;');
			$query->execute();
		}
		return $query->fetchAll(PDO::FETCH_ASSOC);
	}
	public function render_result($category = null, $browser = null, $engine = null, $os = null){
		if(isset($category) && $category === "all"){
			$results = $this->get_all_results();
			header('Content-Type: application/json');
			echo json_encode($results);
		}
		if(isset($category) && $category === "category"){
			$results = $this->get_all_results(true);
			header('Content-Type: application/json');
			echo json_encode($results);
		}
		if(isset($category) && $category === "browser"){
			$results = $this->get_all_results(null, true);
			header('Content-Type: application/json');
			echo json_encode($results);
		}
		if(isset($category) && $category === "os_browser"){
			global $dbh;
			$query = $dbh->prepare('SELECT GROUP_CONCAT(DISTINCT browser order by browser) as browser, os from results GROUP BY os');
			$query->execute();
			$results = $query->fetchAll(PDO::FETCH_ASSOC);
			header('Content-Type: application/json');
			echo json_encode($results);
		}
		exit(0);
	}
	public function handle_request(){
		$method = $_SERVER['REQUEST_METHOD'];
		switch ($method) {
			case 'GET':
				$this->handle_get();
				break;
			case 'OPTIONS':
				http_response_code(404);
				break;
			case 'PUT':
				http_response_code(404);
				break;
			case 'POST':
				http_response_code(404);
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
		if(!isset($_GET['show']))
			exit("No parameters passed");
		if(isset($_GET['show']) && $_GET['show'] !== "")
			$this->render_result($_GET['show']);
		if(isset($_GET['show']))
			$this->response();
	}

	// -----------------------------------------------------------
	public function response(){
		require_once(BASE_PATH . "/static/comparison.html");
		exit(0);
	}
}


$comp = new Result();
$comp->$headers = array('');
$comp->handle_request();
?>
