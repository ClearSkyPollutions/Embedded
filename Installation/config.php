<?php
/* Content to PUT request HTTP*/
$data_json = file_get_contents("php://input");

/* Decode Json data */
$data = json_decode($data_json);

/* Verification Data */
$col = ["Sensors","Frequency","Duration","DBAccess","SSID","Password","Alert"];


foreach ($col as $c){
    if (!$data->{$c}){
        return http_response_code(206);
    }
}
/* Encode data in Json*/
$data_enc = json_encode($data);

/* Open and write in file */
$fp = fopen("config.json", "w");
fwrite($fp,$data_enc);

/* Close file */
fclose($fp);
fclose($putdata);
?>