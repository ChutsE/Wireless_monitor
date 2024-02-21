#include <WiFi.h>
#include <WebServer.h>
#include <esp32cam.h>

static const char* WIFI_SSID = "TP-FES";
static const char* WIFI_PASS = "FES38613921";

WebServer server(80);

esp32cam::Resolution Res;

void setup() {
  Serial.begin(115200);
  Serial.println();
  delay(2000);

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(400);
  }
  Serial.println("WiFi connected");
  {
    using namespace esp32cam;
    Res = esp32cam::Resolution::find(1600, 1200);
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(Res);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
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

void set_resolution() {
  int w, h;
  for (int i = 0; i < server.args(); i++) {
    if (server.argName(i) == "width") {
      w = server.arg(i).toInt();
    } else if (server.argName(i) == "height") {
      h = server.arg(i).toInt();
    } else {
      server.send(503, "text/html", "RES-ARG " + server.argName(i) + " NO EXIST");
      return;
    }
  }
  Res = esp32cam::Resolution::find(w, h);
  if (esp32cam::Camera.changeResolution(Res)) {
    server.send(200, "text/html", "SET-RES " + String(w) + "x" + String(h) + " PASS");
  }
  else {
    server.send(503, "text/html", "SET-RES " + String(w) + "x" + String(h) + " FAIL");
  }
  Serial.println("set_resolution ended");
}

void send_picture() {
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "text/html", "CAPTURE FAIL");
  }
  else {
    server.setContentLength(frame->size()); //ensure recibe the data size correct
    server.send(200, "image/jpeg");
    WiFiClient client = server.client();
    frame->writeTo(client);
  }
  Serial.println("send_picture ended");
}

void loop() {
  server.handleClient();
}
