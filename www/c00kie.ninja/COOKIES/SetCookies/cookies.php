<?php
require_once('../../handle.php');

class Cookies extends Handle {
	public function response(){
		if(isset($_GET['redirect'])){
			$this->$redirect = $_GET['redirect'];
			require_once('./redirect.html');		
		}
	}	
}
// set all type of samesite cookies
// U2V0LUNvb2tpZTogZGVmYXVsdD0xOyBQYXRoPS9cclxuU2V0LUNvb2tpZTogbm9uZT0yOyBQYXRoPS87IFNhbWVTaXRlPU5vbmU7IFNlY3VyZVxyXG5TZXQtQ29va2llOiBsYXg9MzsgUGF0aD0vOyBTYW1lU2l0ZT1MYXhcclxuU2V0LUNvb2tpZTogc3RyaWN0PTQ7IFBhdGg9LzsgU2FtZVNpdGU9U3RyaWN0

// unset these cookies
// U2V0LUNvb2tpZTogZGVmYXVsdD0xOyBFeHBpcmVzPVRodSBKYW4gMjcgMjAxMSAxNzozNDozNCBHTVQrMDEwMFxyXG5TZXQtQ29va2llOiBub25lPTI7ICBFeHBpcmVzPVRodSBKYW4gMjcgMjAxMSAxNzozNDozNCBHTVQrMDEwMDsgU2FtZVNpdGU9Tm9uZTsgU2VjdXJlXHJcblNldC1Db29raWU6IGxheD0zOyBFeHBpcmVzPVRodSBKYW4gMjcgMjAxMSAxNzozNDozNCBHTVQrMDEwMDsgU2FtZVNpdGU9TGF4XHJcblNldC1Db29raWU6IHN0cmljdD00OyBFeHBpcmVzPVRodSBKYW4gMjcgMjAxMSAxNzozNDozNCBHTVQrMDEwMDsgU2FtZVNpdGU9U3RyaWN0


$cook = new Cookies();
$cook->$headers = array('set-cookie');
$cook->handle_request();

?>
