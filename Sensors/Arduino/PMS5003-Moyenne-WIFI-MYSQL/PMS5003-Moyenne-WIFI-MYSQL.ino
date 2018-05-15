#include <WiFi.h>                  // Use this for WiFi instead of Ethernet.h
#include <MySQL_Connection.h>
#include <MySQL_Cursor.h>

#define PMS5003_SET_PIN 8 //if high -> normal mode if low  -> sleeping mode

IPAddress server_addr(192,168,4,1);   // IP of the MySQL *server* here
char user[] = "arduinoDUE";                 // MySQL user login username
char password[] = "arduinoDUE";        // MySQL user login password

// WiFi card example
char ssid[] = "RpiWifi";    // your SSID
char pass[] = "pollution";       // your SSID Password

// WiFi client
WiFiClient client_mysql;            // Use this for WiFi instead of EthernetClient
WiFiClient client_php;
MySQL_Connection conn((Client *)&client_mysql);

String Datetime;

// query
char INSERT_SQL_ComPM[200];

//Sensor
int comp = 0;
uint16_t pm10_sum = 0;
uint16_t pm25_sum = 0; 
uint16_t pm100_sum = 0; 
float pm10_moy = 0;
float pm25_moy = 0;
float pm100_moy = 0; 

void setup() {
  Serial.begin(9600);

  //Sensor off
  pinMode(PMS5003_SET_PIN, OUTPUT);
  digitalWrite(PMS5003_SET_PIN,LOW);

  // Begin WiFi section
  int status = WiFi.begin(ssid, pass);
  if ( status != WL_CONNECTED) {
    Serial.println("Couldn't get a wifi connection");
    while(true);
  }
  // print out info about the connection:
  else {
    Serial.println("Connected to network");
    IPAddress ip = WiFi.localIP();
    Serial.print("My IP address is: ");
    Serial.println(ip);
  }
  // End WiFi section

  Serial.println("Connecting...");
  if (conn.connect(server_addr, 3306, user, password)) {
    delay(1000);
  }
  else {
    Serial.println("Connection failed."); 
  }

  delay(1000);
  digitalWrite(PMS5003_SET_PIN,HIGH);

      // wait 40s for PMS5003 to warm up
  for (int i = 1; i <= 40; i++)
  {
    delay(1000); // 1s
    Serial.print(i);
    Serial.println(" s (wait 40s for PMS5003 to warm up)");
  }
  
}

struct pms5003data {
  uint16_t framelen;
  uint16_t pm10_standard, pm25_standard, pm100_standard;
  uint16_t pm10_env, pm25_env, pm100_env;
  uint16_t particles_03um, particles_05um, particles_10um, particles_25um, particles_50um, particles_100um;
  uint16_t unused;
  uint16_t checksum;
};
 
struct pms5003data data;

void loop() {

  if (readPMSdata()) {
    pm10_sum += data.pm10_env;
    pm25_sum += data.pm25_env;
    pm100_sum += data.pm100_env;
    comp ++;
    if (comp >=60)
    {
      Datetime.remove(0);
      Serial.println(client_php.connected());
      if (!client_php.connected())
      {
        if (client_php.connect(server_addr, 80)) {
          Serial.println("connected to server");
          // Make a HTTP request:
          client_php.print("GET /date.php");
          client_php.println();
        }
      }
      while (!client_php.available());
      while (client_php.available()) {
        Datetime.concat((char)client_php.read());
        delay(500);
      }
      Serial.println(Datetime);
      
      pm10_moy = (float) pm10_sum/comp;
      pm25_moy = (float) pm25_sum/comp;
      pm100_moy = (float) pm100_sum/comp;

      
      sprintf(INSERT_SQL_ComPM,"INSERT INTO capteur_multi_pollution.Concentration_pm (date_mesure,pm2_5,pm10) VALUES(\'%s\', \'%.2f\', \'%.2f\')",Datetime.c_str(),pm25_moy,pm100_moy);

      // Initiate the query class instance
      MySQL_Cursor *cur_mem = new MySQL_Cursor(&conn);
      // Execute the query
      cur_mem->execute(INSERT_SQL_ComPM);
      // Note: since there are no results, we do not need to read any data
      // Deleting the cursor also frees up memory used
      delete cur_mem;

      Serial.println("Concentration Units Mean (environmental)");
      Serial.print("PM 1.0: "); Serial.print(pm10_moy);
      Serial.print("\t\tPM 2.5: "); Serial.print(pm25_moy);
      Serial.print("\t\tPM 10: "); Serial.println(pm100_moy);
      Serial.println("---------------------------------------");
      
      pm10_sum = 0;
      pm25_sum = 0;
      pm100_sum = 0;
      comp = 0;
    }
  }
  
  //conn.close(); 
}

boolean readPMSdata() {
  if (! Serial.available()) {
    return false;
  }
  
  // Read a byte at a time until we get to the special '0x42' start-byte
  if (Serial.peek() != 0x42) {
    Serial.read();
    return false;
  }
 
  // Now read all 32 bytes
  if (Serial.available() < 32) {
    return false;
  }
    
  uint8_t buffer[32];    
  uint16_t sum = 0;
  Serial.readBytes(buffer, 32);
 
  // get checksum ready
  for (uint8_t i=0; i<30; i++) {
    sum += buffer[i];
  }

 /*
   //debugging
  for (uint8_t i=2; i<32; i++) {
    Serial.print("0x"); Serial.print(buffer[i], HEX); Serial.print(", ");
  }
  Serial.println();
  */
  
  // The data comes in endian'd, this solves it so it works on all platforms
  uint16_t buffer_u16[15];
  for (uint8_t i=0; i<15; i++) {
    buffer_u16[i] = buffer[2 + i*2 + 1];
    buffer_u16[i] += (buffer[2 + i*2] << 8);
  }
 
  // put it into a nice struct :)
  memcpy((void *)&data, (void *)buffer_u16, 30);
 
  if (sum != data.checksum) {
    Serial.println("Checksum failure");
    return false;
  }
  // success!
  return true;
}
