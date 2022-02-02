<?php
// -----------------------------------------------------------
require_once('../handle.php');

$ACAO = new Handle();
$ACAO->$headers = array('access-control-allow-origin', 'access-control-allow-credentials', 'access-control-expose-headers');
$ACAO->handle_request();
?>
