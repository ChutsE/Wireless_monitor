#include <WiFi.h>
#include <WebServer.h>
#include <esp32cam.h>

static const char* WIFI_SSID = "Totalplay-2.4G-b1c8";
static const char* WIFI_PASS = "mp9xcUBY7ySeZxmb";

WebServer server(80);

int w = 1600, h = 1200;
auto Res = esp32cam::Resolution::find(w, h);

void setup() {
  Serial.begin(115200); 
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
  Serial.println("  /getpicture");
  Serial.println("  /setresolution");
 
  server.on("/getpicture", send_picture);
  server.on("/setresolution", set_resolution);
  server.begin();
}

void set_resolution(){
  if (server.argName(0) == "res"){
    String value = server.arg(0);
    if (value == "320x240"){
      w = 320; h = 240;
    }
    else if(value == "800x600"){
      w = 800; h = 600;
    }
    else if(value == "1152x864"){
      w = 1152; h = 864;
    }
    else if(value == "1400x1050"){
      w = 1400; h = 1050;
    }
    else if(value == "1600x1200"){
      w = 1600; h = 1200;
    }
    else{
      server.send(503, "text/html", "SET-RES FAIL");
      return;
    }
  }
  auto Res = esp32cam::Resolution::find(w, h);
  if (!esp32cam::Camera.changeResolution(Res)) {
    server.send(503, "text/html", "SET-RES FAIL");
    return;
  }
  else{
    server.send(200, "text/html", "SET-RES PASS");
  }
}

void send_picture()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    server.send(503, "text/htm", "CAPTURE FAIL");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));
  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void loop() {
  server.handleClient();
}
