#define SENSOR_PIN A4  // Digital pin for the ear clip sensor

volatile unsigned long temp[21] = {0}; // Stores time of heartbeats
volatile int counter = 0;
volatile bool data_effect = true;
volatile int heart_rate = 0;
const unsigned long max_heartpulse_duty = 2000; // Max pulse interval

// Initialize time array
void arrayInit() {
    counter = 0;
    for (int i = 0; i < 21; i++) {
        temp[i] = 0;
    }
    temp[20] = millis();
}

void computeHRV() {
    float rr[20];
    float diff[19];
    float rr_sum = 0;
    float sq_diff_sum = 0;
    float sq_dev_sum = 0;

    // Check for valid data
    for (int i = 0; i < 21; i++) {
        if (temp[i] == 0) {
            Serial.println("Not enough valid data for HRV.");
            return;
        }
    }

    // Compute RR intervals
    for (int i = 1; i < 21; i++) {
        rr[i - 1] = temp[i] - temp[i - 1];
        if (rr[i - 1] <= 0 || rr[i - 1] > 2000) {
            Serial.println("Invalid RR interval detected.");
            return;
        }
        rr_sum += rr[i - 1];
    }

    // Mean RR
    float mean_rr = rr_sum / 20.0;

    // SDNN
    for (int i = 0; i < 20; i++) {
        sq_dev_sum += pow(rr[i] - mean_rr, 2);
    }
    float sdnn = sqrt(sq_dev_sum / 20.0);

    // RMSSD
    for (int i = 1; i < 20; i++) {
        diff[i - 1] = rr[i] - rr[i - 1];
        sq_diff_sum += pow(diff[i - 1], 2);
    }
    float rmssd = sqrt(sq_diff_sum / 19.0);

    Serial.print("SDNN: ");
    Serial.print(sdnn, 2);
    Serial.print(" ms, RMSSD: ");
    Serial.print(rmssd, 2);
    Serial.println(" ms");
}


// Calculate heart rate
void calculateHeartRate() {
    if (data_effect) {
        unsigned long total_time = temp[20] - temp[0];
        if (total_time == 0) {
            Serial.println("Total time is zero — can't compute HR.");
            return;
        }
        heart_rate = 1200000 / total_time;  // 20 intervals = 19 gaps, but 1200000 / ΔT is OK for 20 beats
        Serial.print("Heart Rate: ");
        Serial.print(heart_rate);
        Serial.println(" bpm");

        computeHRV();  // Now safe to call
    }
}


// Interrupt function for heartbeat detection
void pulseDetected() {
    unsigned long currentMillis = millis();
    temp[counter] = currentMillis;

    unsigned long sub;
    if (counter == 0) {
        sub = temp[counter] - temp[20];
    } else {
        sub = temp[counter] - temp[counter - 1];
    }

    if (sub > max_heartpulse_duty) {
        data_effect = false;
        counter = 0;
        arrayInit();
    }

    if (counter == 20 && data_effect) {
        counter = 0;
        calculateHeartRate();
    } else if (counter != 20 && data_effect) {
        counter++;
    } else {
        counter = 0;
        data_effect = true;
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(SENSOR_PIN, INPUT);
    attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), pulseDetected, RISING);

    Serial.println("Please place the sensor correctly");
    delay(4000);
    Serial.println("Starting measurement...");
    arrayInit();
}

void loop() {
   
}