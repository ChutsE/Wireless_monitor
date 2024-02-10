#include <WiFi.h>
#include <WebServer.h>
#include <esp32cam.h>
#include <WiFiUdp.h>

              //MSB                         LSB
int pinouts[] = {12, 14, 27, 26, 33, 32, 35, 34};
int len = sizeof(pinouts)/sizeof(*pinouts) - 1;

#define Fs 16000 //Hz

static const char* WIFI_SSID = "TP-FES";
static const char* WIFI_PASS = "FES38613921";

WebServer server(80);
WiFiUDP Udp;

static auto Res = esp32cam::Resolution::find(640, 480);

void setup() {
  Serial.begin(115200); 
  for(int i = 0; i <= len; i++){
    pinMode(pinouts[i], INPUT);
  }
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(Res);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);
 
    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
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
  Serial.println("  /picture");
  Serial.println("  /getaudio");
 
  server.on("/getpicture", get_picture);
  server.on("/getaudio", get_audio);
  server.begin();
}

void get_picture()
{
  if (!esp32cam::Camera.changeResolution(Res)) {
    Serial.println("SET-RES FAIL");
  }
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));
 
  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void get_audio(){
  Udp.beginPacket("192.168.0.185",4321);
  for(int i=0;i<1024;i++){
    float t0 = micros();
    int depth = 0;
    for(int i = 0; i <= len; i++){
      depth = (depth << 1) | digitalRead(pinouts[i]);
    }
    Udp.write(depth);
    //Serial.println(depth);
    while(micros() - t0 < 1000000/Fs);
  }
  Udp.endPacket();
}

void loop() {
  server.handleClient();
}
