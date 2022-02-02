<?php
require_once('../handle.php');
$XFOCSP = new Handle();
$XFOCSP->$headers = array('x-frame-options', 'content-security-policy');
$XFOCSP->handle_request();
?>
