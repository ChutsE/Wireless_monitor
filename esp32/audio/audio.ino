#include <WiFi.h>
#include <WebServer.h>
#include <WiFiUdp.h>

              //MSB                         LSB
int pinouts[] = {12, 14, 27, 26, 33, 32, 35, 34};
int len = sizeof(pinouts)/sizeof(*pinouts);

#define fs 16000 //Hz
#define samples 1024

static const char* WIFI_SSID = "Totalplay-2.4G-b1c8";
static const char* WIFI_PASS = "mp9xcUBY7ySeZxmb";

WebServer server(80);
WiFiUDP Udp;

void setup() {
  Serial.begin(115200); 
  for(int i = 0; i < len; i++){
    pinMode(pinouts[i], INPUT);
  }
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(400);
  }
  Serial.println();
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /getaudio");
  
  server.on("/getaudio", send_audio);
  server.begin();
}

String ESP32_config = "fs:" + String(fs) + 
                      ",samples:" + String(samples) + 
                      ",format:" + String(len*4);

void send_audio(){
  String IPClient = "192.168.100.9"; 
  int Port = 4321;
  for (int i = 0; i < server.args(); i++){
    if (server.argName(i) == "IPClient"){
      IPClient = server.arg(i);
    }
    if (server.argName(i) == "Port"){
      Port = server.arg(i).toInt();
    }
  }
  
  server.send(200, "text/html", ESP32_config);
  Serial.println(IPClient + String(Port));
  
  IPAddress IPClientAddr;
  IPClientAddr.fromString(IPClient); //String to 4 bytes
  
  while(1){
    Udp.beginPacket(IPClientAddr, Port);
    for(int i = 0;i < samples; i++){
      float t0 = micros();
      int depth = 0;
      for(int i = 0; i < len; i++){
        depth = (depth << 1) | digitalRead(pinouts[i]);
      }
      Udp.write(depth);
      while(micros() - t0 < 1000000/fs);
    }
    Udp.endPacket();
  }
}

void loop() {
  server.handleClient();
}
