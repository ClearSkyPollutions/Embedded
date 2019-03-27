<?php
/* Content to PUT request HTTP*/
$data_json = file_get_contents("php://input");

/* Decode Json data */
$data = json_decode($data_json);
   
/* Data verification */
$col = ["sensors","frequency","raspberryPiAddress","serverAddress","isDataShared","latitude","longitude"];

foreach ($col as $c){
    if(!array_key_exists($c,$data)){
        return http_response_code(206);
    }
    /*if (is_null($data->{$c})){
        echo($c);
        return http_response_code(206);
    }*/
}

/* Encode data in Json*/
$data_enc = json_encode($data);

/* Open and write in file */
$fp = fopen("config.json", "w");
fwrite($fp,$data_enc);

echo($data_enc);

/* Close file */
fclose($fp);
?>
