<?php
$apiKey = '53b8b90bf41eaefeaf471825e67e456a-us13'; // your mailchimp API KEY here
$listId = '267d0103bb'; // your mailchimp LIST ID here
$double_optin=false;
$send_welcome=true;
$email_type = 'html';
$email = $_POST['newsletter_email'];
//replace us# with your actual datacenter
$submit_url = "http://us13.api.mailchimp.com/1.3/?method=listSubscribe";
$data = array(
    'email_address'=>$email,
    'apikey'=>$apiKey,
    'id' => $listId,
    'double_optin' => $double_optin,
    'send_welcome' => $send_welcome,
    'email_type' => $email_type
);
$payload = json_encode($data);
 
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $submit_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, urlencode($payload));
 
$result = curl_exec($ch);
curl_close ($ch);
$data = json_decode($result);
if ($data->error){
    echo $data->error;
} else {
    echo 'Thanks for signing up! We\'ll be in touch with an invitation to Aquaint soon.';
}
?>