<?php
require_once('../handle.php');

$XFO = new Handle();
$XFO->$headers = array('x-frame-options');
$XFO->handle_request();
?>
