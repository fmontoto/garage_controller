char kSonarTrigerPin = 4;
char kSonarEchoPin = 2;
char kGarageDoorButtonPin = 7;

short kPushSpeedMilli = 200;  // Time to keep pushed the button.

float get_distance_in_cm()
{
  float distance;
  long echo_time;
  char delay_microseconds = 10;
  // 343[m/s] * 100/1[cm/m] * 1/1000000[sec/usec]
  const static float speed_of_sound_cm_usec = 0.0343;
  // Activate the sensor.
  digitalWrite(kSonarTrigerPin, HIGH);
  delayMicroseconds(delay_microseconds);
  digitalWrite(kSonarTrigerPin, LOW);

  // Measure the echo pulse.
  echo_time = pulseIn(kSonarEchoPin, HIGH);

  distance = echo_time * speed_of_sound_cm_usec;
  return distance / 2; // Interested in one trip, not round trip.
}

void push_button()
{
  digitalWrite(kGarageDoorButtonPin, HIGH);
  delay(kPushSpeedMilli);
  digitalWrite(kGarageDoorButtonPin, LOW);
}

void setup()
{
  pinMode(kSonarTrigerPin, OUTPUT);
  pinMode(kSonarEchoPin, INPUT);
  pinMode(kGarageDoorButtonPin, OUTPUT);
  digitalWrite(kGarageDoorButtonPin, LOW);

  Serial.begin(9600);
}

void loop()
{
  while (Serial.available() < 2) {
    delay(300);
  }
  process_command();
}

bool is_door_open()
{
  float threshold_distance_cm = 123;
  float distance = get_distance_in_cm();
  if (distance > threshold_distance_cm) {
    return true;
  } else {
    return false;
  }
}

void send_door_signal()
{
  push_button();
}

void cmd_is_alive()
{
  Serial.print("YES");
}

void cmd_is_door_open()
{
  if (is_door_open()) {
    Serial.print("YES");
  } else {
    Serial.print("NOT");
  }
}

void cmd_open_door()
{
  if (is_door_open()) {
    Serial.print("NOT");
  } else {
    Serial.print("YES");
    send_door_signal();
  }
}

void cmd_close_door()
{
  if (is_door_open()) {
    Serial.print("YES");
    send_door_signal();
  } else {
    Serial.print("NOT");
  }
}

void process_command()
{
  char input[2];
  Serial.readBytes(input, 2);
  if (strncmp(input, "AL", 2) == 0) {
    cmd_is_alive();
  } else if (strncmp(input, "IO", 2) == 0) {
    cmd_is_door_open();
  } else if (strncmp(input, "OD", 2) == 0) {
    cmd_open_door();
  } else if (strncmp(input, "CD", 2) == 0) {
    cmd_close_door();
  }
}
