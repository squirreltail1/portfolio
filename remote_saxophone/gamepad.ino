#include <Arduino.h>
#include <BleGamepad.h>

// Define shift register pins
#define DATA_PIN 22   // Shift Register Q7
#define CLOCK_PIN 19  // Shift Register CP
#define LATCH_PIN 21  // Shift Register PL
#define NUM_BITS 24   // Set to 8 * number of shift registers

// Define joystick pins
#define JOYSTICK_X_PIN 33
#define JOYSTICK_Y_PIN 34
#define JOYSTICK_BUTTON_PIN 32

// Calibration offsets
int JOYSTICK_X_OFFSET = 0;
int JOYSTICK_Y_OFFSET = 0;


// Joystick thresholds and scaling
#define DEADZONE_X 10  // Deadzone for X-axis
#define DEADZONE_Y 35  // Deadzone for Y-axis
#define SENSITIVITY 1  // Adjust scaling factor

// Smooth analog readings by averaging
int averageAnalogRead(int pin, int samples = 10) {
    long total = 0;
    for (int i = 0; i < samples; i++) {
        total += analogRead(pin);
        delay(1); // Small delay between samples
    }
    return total / samples;
}
// Apply dynamic deadzone
int applyDynamicDeadzone(int value, int threshold) {
    if (abs(value) < threshold) return 0;
    
    return value;
}




// BLE Gamepad object
BleGamepad bleGamepad("BLE Gamepad", "ESP32", 100);

// Read shift register values and construct a 24-bit value
uint32_t readShiftRegister() {
    uint32_t value = 0;

    // Step 1: Sample
    digitalWrite(LATCH_PIN, LOW);
    digitalWrite(LATCH_PIN, HIGH);

    // Step 2: Shift
    for (int i = 0; i < NUM_BITS; i++) {
        int bit = digitalRead(DATA_PIN);
        value = (value << 1) | (bit == HIGH ? 0 : 1); // Shift in bits
        digitalWrite(CLOCK_PIN, HIGH); // Shift out the next bit
        digitalWrite(CLOCK_PIN, LOW);
    }

    return value;
}

void setup() {
    
    // Initialize serial monitor
    Serial.begin(115200);

    // Initialize BLE Gamepad
    bleGamepad.begin();
    Serial.println("BLE Gamepad started successfully");

    // Initialize shift register pins
    pinMode(DATA_PIN, INPUT);
    pinMode(CLOCK_PIN, OUTPUT);
    pinMode(LATCH_PIN, OUTPUT);

    // Initialize joystick input pins
    pinMode(JOYSTICK_BUTTON_PIN, INPUT_PULLUP);
    pinMode(JOYSTICK_X_PIN, INPUT);
    pinMode(JOYSTICK_Y_PIN, INPUT);

    JOYSTICK_X_OFFSET = averageAnalogRead(JOYSTICK_X_PIN);
    JOYSTICK_Y_OFFSET = averageAnalogRead(JOYSTICK_Y_PIN);
    Serial.print("Calibrated X offset: ");
    Serial.println(JOYSTICK_X_OFFSET);
    Serial.print("Calibrated Y offset: ");
    Serial.println(JOYSTICK_Y_OFFSET);


}

void loop() {
    if (bleGamepad.isConnected()) {
        // Smooth joystick readings
        int xVal = averageAnalogRead(JOYSTICK_X_PIN) - JOYSTICK_X_OFFSET;
        int yVal = averageAnalogRead(JOYSTICK_Y_PIN) - JOYSTICK_Y_OFFSET;

        // Invert Y-axis for natural control
        yVal = -yVal;

        // Apply deadzone for X and Y axes
        xVal = applyDynamicDeadzone(xVal, DEADZONE_X);
        yVal = applyDynamicDeadzone(yVal, DEADZONE_Y);

        // Map joystick values to full range (-127 to 127)
        xVal = map(xVal, -25, 25, -127, 127); // Replace -25, 25 with observed X range
        yVal = map(yVal, -30, 20, -127, 127); // Replace -30, 20 with observed Y range

        // Debug mapped joystick values
        Serial.print("Mapped X: ");
        Serial.print(xVal);
        Serial.print(", Mapped Y: ");
        Serial.println(yVal);

        // Send joystick movement to the gamepad
        bleGamepad.setLeftThumb(xVal, yVal);

        // Read shift register and get a 24-bit value
        uint32_t shiftRegisterValue = readShiftRegister();

        // Debug: Print the 24-bit value
        Serial.print("Shift Register 24-bit Value: ");
        Serial.println(shiftRegisterValue, BIN);

        
        int buttonState = shiftRegisterValue & 0xFF; // Lower 8 bits for buttons

        // Send joystick movement to the gamepad
        bleGamepad.setLeftThumb(xVal, yVal);
        
        if (digitalRead(JOYSTICK_BUTTON_PIN) == LOW) {
            Serial.println("Button pressed");
            bleGamepad.press(BUTTON_5); // Map to Button 1
        }
        

        bool sensor1 = false;
        bool sensor2 = false;
        bool sensor3 = false;
        bool sensor4 = false; 
        // Update sensor states
        sensor1 = (buttonState & (1 << 0)) != 0;
        sensor2 = (buttonState & (1 << 1)) != 0;
        sensor3 = (buttonState & (1 << 2)) != 0;
        sensor4 = (buttonState & (1 << 3)) != 0;
        if (sensor1 && !sensor3 && !sensor4) {
          bleGamepad.press(BUTTON_8);
        } else {
          bleGamepad.release(BUTTON_8);
        }
        if (sensor2) {
          bleGamepad.press(BUTTON_9);
        } else {
          bleGamepad.release(BUTTON_9);
        }
        if (sensor3 && sensor1) {
          bleGamepad.press(BUTTON_10);
          bleGamepad.release(BUTTON_6);
        } else {
          bleGamepad.release(BUTTON_10);
        }
        if (sensor4 && sensor1) {
          bleGamepad.press(BUTTON_11);
          bleGamepad.release(BUTTON_6);
        } else {
          bleGamepad.release(BUTTON_6);
        }

        // Notify gamepad of updated state2
        bleGamepad.sendReport();
    } else {
        Serial.println("Waiting for BLE connection...");
        delay(1000);
    }

    // Small delay for stability
    delay(10);
}
