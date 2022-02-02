<?php
	$user = "member";
	$pass = "EVERYONE_C4N_R34D_TH15!";
	$dbname = "results";
	$host = "db";
	try{
		$dbh = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
		$dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	}catch(PDOException $e){
		echo "ERROR: " . $e->getMessage() . "<br/>";
	}
	$query = $dbh->prepare("CREATE TABLE IF NOT EXISTS results (
										id INTEGER AUTO_INCREMENT PRIMARY KEY,
										browser TEXT NOT NULL,
										engine TEXT NOT NULL,
										os TEXT NOT NULL,
										result JSON NOT NULL,
										category TEXT NOT NULL
										) DEFAULT CHARSET=utf8;");
	$query->execute();
?>
