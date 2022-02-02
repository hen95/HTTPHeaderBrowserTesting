<?php
require_once('../handle.php');

$CSP = new Handle();
$CSP->$headers = array('content-security-policy');
$CSP->handle_request();
?>
