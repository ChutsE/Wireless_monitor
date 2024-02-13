#include <WiFi.h>
#include <WebServer.h>
#include <WiFiUdp.h>

              //MSB                         LSB
int pinouts[] = {12, 14, 27, 26, 33, 32, 35, 34};
int len = sizeof(pinouts)/sizeof(*pinouts);

float T_us = 62.5;
int samples = 1024;

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

void send_audio(){
  WiFiClient client = server.client();
  IPAddress IPClientAddr = client.remoteIP();
  Serial.println(IPClientAddr);

  for (int i = 0; i < server.args(); i++){
    if (server.argName(i) == "T_us"){
      T_us = server.arg(i).toFloat();
    }
    if (server.argName(i) == "UDP_samples"){
      samples = server.arg(i).toInt();
    }
  }
  
  server.send(200, "text/html", "AUD_CONF PASS");
  Serial.println("T_us: " + String(T_us) + "  samples:" + String(samples));
  
  while(1){
    Udp.beginPacket(IPClientAddr, 4321);
    for(int i = 0;i < samples; i++){
      float t0 = micros();
      int depth = 0;
      for(int i = 0; i < len; i++){
        depth = (depth << 1) | digitalRead(pinouts[i]);
      }
      Udp.write(depth);
      while(micros() - t0 < T_us);
    }
    Udp.endPacket();
  }
}

void loop() {
  server.handleClient();
}
