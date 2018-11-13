<?php
/* This script calculate AQI value based on ATMO method : 
Source : https://fr.wikipedia.org/wiki/Indice_de_qualit%C3%A9_de_l%27air
Pour le dioxyde de soufre, le dioxyde d'azote et l'ozone, on note pour chaque heure de la journée le maximum de la concentration du polluant dans l'air, puis on fait la moyenne de ces maxima.
Pour les particules fines, on calcule la concentration moyenne, sur la journée, de particules dont le diamètre aérodynamique est inférieur à 10 µm (PM10).
*/
$airQuality;
  
function airQualityLevel($airQuality){
  switch ($airQuality->index) {
    case 10: 
      $airQuality->level  = 'SEVERE';
      $airQuality->color  = '#ff2039';
      break;
    case 9:
      $airQuality->level  = 'HEAVY';
      $airQuality->color  = '#ff2039';
      break;
    case 8:
      $airQuality->level  = 'HEAVY';
      $airQuality->color  = '#ff2039';
      break;  
    case 7:
      $airQuality->level  = 'MODERATE';
      $airQuality->color  = '#ffab00';
      break;
    case 6:
      $airQuality->level  = 'MODERATE';
      $airQuality->color  = '#ffab00';
      break;   
    case 5:
      $airQuality->level  = 'ACCEPTABLE';
      $airQuality->color  = '#ffab00';
      break;
    case 4:
      $airQuality->level  = 'GOOD';
      $airQuality->color  = '#02d935';
      break;
    case 3:
      $airQuality->level  = 'GOOD';
      $airQuality->color  = '#02d935';
      break;
    case 2:
      $airQuality->level  = 'EXCELLENT';
      $airQuality->color  = '#02d935';
      break;
    case 1:
      $airQuality->level  = 'EXCELLENT';
      $airQuality->color  = '#02d935';
      break;           
    case 0:
      $airQuality->level = 'NO DATA';
      $airQuality->color  = '#000000';
      break;
    }
}
 
// PM10
function subIndexOfPM10($pm10){
  if ( $pm10 == 0) {
    return 0; 
  } else if ( $pm10 <= 6) {
    return 1;
  } else if ( $pm10 > 6 && $pm10 <= 13 ) {
    return 2;
  } else if ( $pm10 > 13 && $pm10 <= 20 ) {
    return 3;
  } else if ( $pm10 > 20 && $pm10 <= 27 ) {
    return 4;
  } else if ( $pm10 > 27 && $pm10 <= 34 ) {
    return 5;
  } else if ( $pm10 > 34 && $pm10 <= 41 ) {
    return 6;
  } else if ( $pm10 > 41 && $pm10 <= 49 ) {
    return 7;
  } else if ( $pm10 > 49 && $pm10 <= 64 ) {
    return 8;
  } else if ( $pm10 > 64 && $pm10 <= 79 ) {
    return 9;
  } else {
    return 10;
  }  
}

// Ozone 
function subIndexOfO3($o3){
  if ( $o3 == 0) {
    return 0; 
  } else if ( $o3 <= 29) {
    return 1;
  } else if ( $o3 > 29 && $o3 <= 54 ) {
    return 2;
  } else if ( $o3 > 54 && $o3 <= 79 ) {
    return 3;
  } else if ( $o3 > 79 && $o3 <= 104 ) {
    return 4;
  } else if ( $o3 > 104 && $o3 <= 129 ) {
    return 5;
  } else if ( $o3 > 129 && $o3 <= 149 ) {
    return 6;
  } else if ( $o3 > 149 && $o3 <= 179 ) {
    return 7;
  } else if ( $o3 > 179 && $o3 <= 209 ) {
    return 8;
  } else if ( $o3 > 209 && $o3 <= 239 ) {
    return 9;
  } else {
    return 10;
  }  
}

// Dioxyde d'azote
function subIndexOfNO2( $no2){
  if ( $no2 == 0) {
    return 0; 
  } else if ( $no2 <= 29) {
    return 1;
  } else if ( $no2 > 29 && $no2 <= 54 ) {
    return 2;
  } else if ( $no2 > 54 && $no2 <= 84 ) {
    return 3;
  } else if ( $no2 > 84 && $no2 <= 109 ) {
    return 4;
  } else if ( $no2 > 109 && $no2 <= 134 ) {
    return 5;
  } else if ( $no2 > 134 && $no2 <= 164 ) {
    return 6;
  } else if ( $no2 > 164 && $no2 <= 199 ) {
    return 7;
  } else if ( $no2 > 199 && $no2 <= 274 ) {
    return 8;
  } else if ( $no2 > 274 && $no2 <= 399 ) {
    return 9;
  } else {
    return 10;
  }  
}
// Dioxyde de soufre 
function subIndexOfSO2($so2){
  if ( $so2 == 0) {
    return 0; 
  } else if ( $so2 <= 39) {
    return 1;
  } else if ( $so2 > 39 && $so2 <= 79 ) {
    return 2;
  } else if ( $so2 > 79 && $so2 <= 119 ) {
    return 3;
  } else if ( $so2 > 119 && $so2 <= 159 ) {
    return 4;
  } else if ( $so2 > 159 && $so2 <= 199 ) {
    return 5;
  } else if ( $so2 > 199 && $so2 <= 249 ) {
    return 6;
  } else if ( $so2 > 249 && $so2 <= 299 ) {
    return 7;
  } else if ( $so2 > 299 && $so2 <= 399 ) {
    return 8;
  } else if ( $so2 > 399 && $so2 <= 499 ) {
    return 9;
  } else {
    return 10;
  }  
}

function getAQI($pm10, $o3, $no2, $so2){
  $airQuality = new \stdClass();
  $airQuality->index = max(
    subIndexOfPM10($pm10),
    // Other sensors are not available yet 
    subIndexOfO3($o3),
    subIndexOfNO2($no2),
    subIndexOfSO2($so2)
  );
  airQualityLevel($airQuality);
  return $airQuality;
}

function dbQuery($bdd, $id, $table, $pollutant,  $limit){
   $response = $bdd->query("SELECT AVG(value) as avg FROM $table WHERE typeId IN (SELECT id FROM POLLUTANT WHERE POLLUTANT.name = \"$pollutant\") and date > (NOW() - INTERVAL 1 DAY) AND systemId=\"$id\" ")
                   ->fetch(PDO::FETCH_OBJ);
  return $response->avg;
}


// connection to database 
try
{
	$bdd = new PDO('mysql:host=db;dbname=capteur_multi_pollutions;charset=utf8', 'Server', 'Server');
	$id = $_GET['id'];
}
catch(Exception $e)
{
  die('Erreur : '.$e->getMessage());
}


$dailyAvgPm10= dbQuery($bdd, $id, AVG_HOUR, pm10, 24);
// $dailyAvgMaxO3  = dbQuery($bdd, MAX_HOUR, o3, 24);
// $dailyAvgMaxNO2 = dbQuery($bdd, MAX_HOUR, no2, 24);
// $dailyAvgMaxSO2 = dbQuery($bdd, MAX_HOUR, so2, 24);

 
//echo json_encode(getAQI($dailyAvgPm10, $dailyAvgMaxO3 , $dailyAvgMaxNO2, $dailyAvgMaxSO2));
echo json_encode(getAQI($dailyAvgPm10, 0 , 0, 0));


// close db connection 
$bdd = null;
?>


