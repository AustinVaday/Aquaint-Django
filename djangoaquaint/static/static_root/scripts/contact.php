<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if(!empty($_POST['contactname']) && !empty($_POST['contactemail']) && !empty($_POST['contactmessage'])) {
	$to = 'austin@aquaint.us, navid@aquaint.us'; // Your e-mail address here.
	$body = "\nName: {$_POST['contactname']}\nEmail: {$_POST['contactemail']}\n\n\n{$_POST['contactmessage']}\n\n";
#	mail($to, "New message from aquaint.us", $body, "From: {$_POST['contactemail']}"); // E-Mail subject here.

	// Until we get SMTP working on this server... append all messages to text file
	$txt = "---------------------------------\n";
	$txt .= "Date: ";
	$txt .= date('l jS \of F Y h:i:s A',mktime()); 
	$txt .= $body;
	$txt .= "---------------------------------\n";
 	$myfile = file_put_contents('mail.txt', $txt.PHP_EOL , FILE_APPEND | LOCK_EX);

    }
}
?>
