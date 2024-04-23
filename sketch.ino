#include <Servo.h>

// Define servo motor pins
const int studentServoPin = 8;   // Change these to match your setup
const int staffServoPin = 9;     // Change these to match your setup
const int teacherServoPin = 10;  // Change these to match your setup

// Create instances of the Servo class for each servo motor
Servo studentServo;
Servo staffServo;
Servo teacherServo;

void setup() {
  // Attach servo motors to pins
  studentServo.attach(studentServoPin);
  staffServo.attach(staffServoPin);
  teacherServo.attach(teacherServoPin);

  // Start serial communication
  Serial.begin(9600);
  Serial.println("Started Simulation\n");

}

void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming number
    int inputNumber = Serial.parseInt();
    
    // Check the received number and open the corresponding barrier
    if (inputNumber == 1) {
      Serial.println("Opening Barrier 1.");
      openBarrier(studentServo);
    } else if (inputNumber == 2) {
      Serial.println("Opening Barrier 2.");
      openBarrier(staffServo);
    } else if (inputNumber == 3) {
      Serial.println("Opening Barrier 3.");
      openBarrier(teacherServo);
    } else {
       
    }
  }
}

void openBarrier(Servo& servo) {
  // Move servo motor to open the barrier
  servo.write(0); // Adjust the angle as needed
  Serial.println("Barrier Opened.");

  // Add a delay to simulate the car passing through
  delay(2000); // Adjust the delay time (in milliseconds) as needed
  
  // Move the servo motor to close the barrier
  servo.write(90); // Adjust the angle to close the barrier
  Serial.println("Barrier Closed.");
}
